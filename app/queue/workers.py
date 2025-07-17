from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os
from dotenv import load_dotenv
import base64
from openai import OpenAI
from ..utils.email import send_resume_analysis_email

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def process_file(id: str, file_path: str):
    # Get file record from database to access job_role and email
    file_record = await files_collection.find_one({"_id": ObjectId(id)})
    if not file_record:
        print(f"Error: File record with ID {id} not found")
        return
    
    job_role = file_record.get("job_role", "")
    user_email = file_record.get("email", "")
    
    await files_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": {"status": "processing"}}
    )
    print(f"Processing file for job role: {job_role}...")

    # Convert pdf to image
    store_images = []
    try:
        # Convert PDF to a list of PIL Image objects
        images = convert_from_path(file_path)

        # Save each page as an image file
        for i, image in enumerate(images):
            image_save_path = f"/mnt/uploads/images/{id}/image-{i + 1}.png"
            os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
            image.save(image_save_path, "PNG")
            store_images.append(image_save_path)

        await files_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"status": "Successfully converted to images"}},
        )

        print(f"Successfully converted {len(images)} pages from {file_path} to images.")
    except Exception as e:
        print(f"Error during PDF conversion: {e}")

    base64_image = [encode_image(img) for img in store_images]

    # Create a detailed prompt for resume analysis against job role in JSON format
    content = [
        {
            "type": "text",
            "text": f"""Analyze this resume for the role of {job_role}. 
            
Provide your analysis in the following JSON structure:

```json
{{
  "job_description": "A brief description of the job role requirements",
  "strength": [
    "Strength point 1",
    "Strength point 2",
    "..."
  ],
  "weakness": [
    "Weakness point 1",
    "Weakness point 2",
    "..."
  ],
  "changes_needed": [
    "Recommendation 1",
    "Recommendation 2",
    "..."
  ],
  "overall_summary": "A brief overall assessment of the candidate's suitability for the role, including match percentage"
}}
```

Make sure your response is ONLY the valid JSON object, with no additional text before or after. Each section should be detailed and specific to help the candidate understand their fit for the role.
"""
        }
    ]

    # Add all images to the content
    for i, img_base64 in enumerate(base64_image):
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_base64}"},
            }
        )

    response = client.chat.completions.create(
        model="gemini-2.0-flash-exp",  # Use available model
        messages=[{"role": "user", "content": content}],
    )
    
    analysis_result = response.choices[0].message.content
    
    # Parse JSON response or handle text response
    import json
    import re
    
    # Try to extract JSON from the response if it's not already JSON
    # This handles cases where model might wrap the JSON in markdown code blocks
    json_match = re.search(r'```json\s*([\s\S]*?)\s*```', analysis_result)
    if json_match:
        # Extract JSON from code block
        json_str = json_match.group(1)
        try:
            analysis_json = json.loads(json_str)
        except json.JSONDecodeError:
            # If extraction fails, use original response
            analysis_json = {"overall_summary": analysis_result}
    else:
        # Try parsing directly
        try:
            analysis_json = json.loads(analysis_result)
        except json.JSONDecodeError:
            # If parsing fails, use original response in summary field
            analysis_json = {"overall_summary": analysis_result}
    
    # Save the structured analysis in the database
    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"result": analysis_json, "status": "completed"}}
    )
    
    # Send email with analysis results
    if user_email:
        email_response = send_resume_analysis_email(
            recipient_email=user_email,
            analysis_result=analysis_json,
            job_role=job_role
        )
        email_status = "Email sent successfully" if not email_response.get("error") else f"Email sending failed: {email_response.get('error')}"
        
        # Update email status in the database
        await files_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"email_status": email_status}}
        )
    else:
        email_status = "No email provided"

    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "status": "processed successfully",
                "result": analysis_result,
                "email_status": email_status
            }
        },
    )

    try:
        os.remove(file_path)
        for img in store_images:
            os.remove(img)
    except Exception as e:
        print(f"Error deleting files: {e}")

    # TODO: E-mail the result to the user
