from typing import TypedDict, Optional
from pydantic import Field
from pymongo.asynchronous.collection import AsyncCollection
from ..db import database


class FileSchema(TypedDict):
    name: str = Field(..., description="Name of the file")
    status: str = Field(..., description="Status of the file")
    job_role: Optional[str] = Field(None, description="Job role the user is applying for")
    email: Optional[str] = Field(None, description="User's email address for sending results")
    result: Optional[str] = Field(
        None, description="Result of the file processing")


COLLECTION_NAME = "files"
files_collection: AsyncCollection = database[COLLECTION_NAME]
