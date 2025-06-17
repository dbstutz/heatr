from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from back import just_ret_data, dict_to_string
import json

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

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.post("/getdata")
def getdata(data: InputData):
    name = data.name
    school = data.school
    if not name or not school:
        return {"message": "Name and school must be provided."}
    try:
        result = dict_to_string(just_ret_data(school, name))
        return {"message": result}
    except Exception as e:
        return {"message": f"Error: {str(e)}"}