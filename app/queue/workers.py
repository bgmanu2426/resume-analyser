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

    # Create a detailed prompt for resume analysis against job role
    content = [
        {
            "type": "text",
            "text": f"""Analyze this resume for the role of {job_role}. Provide a detailed analysis including:
1. Match percentage: Provide a numerical assessment (0-100%) of how well the resume matches the requirements for the job role.
2. Strengths: What aspects of the resume align well with the job role?
3. Weaknesses: What's missing or could be improved in the resume for this specific role?
4. Recommendations: Specific suggestions to improve the resume for this job role.
5. Overall assessment: A brief conclusion on the candidate's suitability for the role.
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
    
    # Send email with analysis results
    if user_email:
        email_response = send_resume_analysis_email(
            recipient_email=user_email,
            analysis_result=analysis_result,
            job_role=job_role
        )
        email_status = "Email sent successfully" if not email_response.get("error") else f"Email sending failed: {email_response.get('error')}"
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
