from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os
from dotenv import load_dotenv
import base64
from openai import OpenAI

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
    await files_collection.update_one(
        {"_id": ObjectId(id)}, {"$set": {"status": "processing"}}
    )
    print("Processing file...")

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

    content = [
        {
            "type": "text",
            "text": "Based on the given resume pages below, roast the resume. Analyze all pages comprehensively.",
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

    await files_collection.update_one(
        {"_id": ObjectId(id)},
        {
            "$set": {
                "status": "processed sucessfully",
                "result": response.choices[0].message.content,
            }
        },
    )

    try:
        os.remove(file_path)
        for img in store_images:
            os.remove(img)
    except Exception as e:
        print(f"Error deleting files: {e}")

    # TODO: Analyse the resume for a job description taken as a input by user and check if he is fit for the job
    # TODO: E-mail the result to the user
