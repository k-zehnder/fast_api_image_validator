from fastapi import FastAPI, Form, File, UploadFile, HTTPException
import uvicorn
from pydantic import BaseModel, Json, Field
from typing import Type, List
import cv2
import logging

from PIL import Image
import io
import sys
import logging


from custom_validator_classes import SimilarityAnalyzer, BlackWhiteThresholdAnalyzer

validators_dictionary = {
    "SimilarityAnalyzer" : SimilarityAnalyzer,
    "BlackWhiteThresholdAnalyzer" : BlackWhiteThresholdAnalyzer
}

class TestModelResponse(BaseModel):
    pass

class TestModel(BaseModel):
    username: str
    validators: List[str]
    threshold: float = Field(default=.1, description="The threshold")
    

app = FastAPI()

@app.post("/validate")
async def validate(upload_file: UploadFile = File(...), model: Json[TestModel] = Form(...)):
    try:
        filename = model.username + ".png"
        with open(filename, "wb") as fh:
            contents = await upload_file.read()
            fh.write(contents)
            image = Image.open(io.BytesIO(contents)).convert('RGB')
            
        # predicted_class = image_classifier.predict(image)
        results = {}
        for validator_key in model.validators:
            validity_object = validators_dictionary[validator_key]()
            results[f"{validator_key}"] = validity_object.isValidImage(image)
        
        return {
            "filename": upload_file.filename,
            "contentype": upload_file.content_type,
            "username" : model.username, 
            "results" : results
        }
    except Exception as error:
        logging.exception(error)
        e = sys.exc_info()[1]
        raise HTTPException(status_code=500, detail=str(e))
    