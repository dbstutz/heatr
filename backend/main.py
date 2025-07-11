from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from back import just_ret_data, insights_gpt, scan_athletes_gpt, scan_no_data
import json
import shutil
import os

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow any origin during development
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers
)

class InputData(BaseModel):
    name: str
    school: str


class InputDataWithPRs(BaseModel):
    athName: str
    personalRecords: list


@app.get("/ping")
def ping():
    return {"message": "pong"}


@app.post("/getinsights")
def getinsights(data: InputDataWithPRs):
    name = data.athName
    prs = data.personalRecords
    try:
        insights = insights_gpt(name, prs)
        return {"success": True, "data": insights}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/getsingledata")
def getsingledata(data: InputData):
    name = data.name
    school = data.school
    if not name:
        return {"success": False, "error": "Name must be provided."}
    try:
        result = just_ret_data(school, name)
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/imagescanonly")
def imagescanonly(file: UploadFile = File(...)):
    try:
        temp_dir = "uploaded_images"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        pairs = scan_athletes_gpt(file_path)
        os.remove(file_path)
        return {"success": True, "data": pairs}
    except Exception as e:
        return {"success": False, "error": str(e)}