import io
import os
import sys
import logging
import uvicorn
from fastapi import FastAPI, Form, File, UploadFile, HTTPException

from pydantic import BaseModel, Json, Field
from typing import Type, List, Dict
from PIL import Image

# import your image validator classes
from custom_validator_classes import SimilarityAnalyzer, BlackWhiteThresholdAnalyzer

class Config(BaseModel):
    threshold: float = Field(default=.1, description="The threshold")

class ImageFormOut(BaseModel):
    filename: str
    username: str
    results: Dict

class ImageFormIn(BaseModel):
    username: str
    validators: List[str] = ["SimilarityAnalyzer", "BlackWhiteThresholdAnalyzer"]
    config: Config
    
app = FastAPI()

@app.post("/validate", response_model=ImageFormOut)
async def validate(upload_file: UploadFile = File(...), model: Json[ImageFormIn] = Form(...)):
    try:
        filename = os.path.join("images", model.username + "_" + upload_file.filename)
        with open(filename, "wb") as fh:
            contents = await upload_file.read()
            fh.write(contents)
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            
        # predicted_class = image_classifier.predict(image)
        vao = ValidatorObjectAggregator(*model.validators)
        results = vao.processAll(image)
        
        return {
            "filename": upload_file.filename,
            "username" : model.username, 
            "results" : results
        }
    except Exception as error:
        logging.exception(error)
        e = sys.exc_info()[1]
        raise HTTPException(status_code=500, detail=str(e))
    
