from fastapi import FastAPI, UploadFile
from uuid import uuid4
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema


app = FastAPI()


@app.get("/")
def hello():
    return {"status": "Hello World!"}


@app.post("/upload")
async def upload_file(file: UploadFile):
    db_file = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename, status="saving"
        )
    )
    
    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"
    await save_to_disk(file=await file.read(), file_path=file_path)

    # Save to MongoDB
    await files_collection.update_one(
        {"_id": db_file.inserted_id},
        {"$set": {"status": "queued"}}
    )

    # Push to the queue
    return {"status": "File uploaded successfully", "file_id": str(db_file.inserted_id)}
