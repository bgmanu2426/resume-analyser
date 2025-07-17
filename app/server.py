from fastapi import FastAPI, UploadFile, Path, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from .utils.file import save_to_disk
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.workers import process_file
from bson import ObjectId
import os


app = FastAPI()

# Mount static files directory
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.post("/upload")
async def upload_file(
    file: UploadFile, 
    job_role: str = Form(...), 
    email: str = Form(...)
):
    db_file = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename, 
            status="saving", 
            job_role=job_role, 
            email=email
        )  # type:ignore
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
        "email_status": file["email_status"] if "email_status" in file else None,
    }
