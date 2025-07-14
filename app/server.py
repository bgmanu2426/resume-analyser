from fastapi import FastAPI, UploadFile
from uuid import uuid4


app = FastAPI()


@app.get("/")
def hello():
    return {"status": "Hello World!"}


@app.post("/upload")
def upload_file(file: UploadFile):
    id = uuidv4()
    
    file_path
