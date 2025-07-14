from fastapi import FastAPI, UploadFile
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.workers import process_file


app = FastAPI()


@app.get("/")
def hello():
    return {"status": "Hello World!"}


@app.post("/upload")
async def upload_file(file: UploadFile):
    db_file = await files_collection.insert_one(
        document=FileSchema(name=file.filename, status="saving")  # type:ignore
    )

    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"
    await save_to_disk(file=await file.read(), file_path=file_path)

    # Save to MongoDB
    await files_collection.update_one(
        {"_id": db_file.inserted_id}, {"$set": {"status": "queued"}}
    )

    # Push to the queue
    q.enqueue(process_file, str(db_file.inserted_id), file_path)

    return {
        "status": "File uploaded successfully",
        "file_id": str(db_file.inserted_id)
    }
