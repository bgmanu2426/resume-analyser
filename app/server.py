from fastapi import FastAPI, UploadFile, Path
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.workers import process_file
from bson import ObjectId


app = FastAPI()


@app.get("/")
def hello():
    return {"status": "Hello World!"}


@app.get("/{file_id}")
async def get_file_by_id(
    file_id: str = Path(..., description="The ID of the file to retrieve"),
):
    file = await files_collection.find_one({"_id": ObjectId(file_id)})
    if not file:
        return {"status": "File not found"}
    return {
        "message": "File found",
        "id": str(file["_id"]),
        "FileName": file["name"],
        "status": file["status"],
        "result": file["result"] if "result" in file else None,
    }


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

    return {"status": "File uploaded successfully", "file_id": str(db_file.inserted_id)}
