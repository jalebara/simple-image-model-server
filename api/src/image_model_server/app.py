from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dataclasses import asdict
import json

import os
from uuid import uuid4
import uvicorn

# Project Imports

from database import get_db, ImageModel
from model import DefaultYolo


app = FastAPI()

model = DefaultYolo()

UPLOAD_DIRECTORY = "/data/image-uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    file_extension = file.filename.split(".")[-1] in ("jpg", "jpeg", "png")
    if not file_extension:
        raise HTTPException(status_code=400, detail="Invalid file format")

    file_id = str(uuid4())
    file_path = os.path.join(
        UPLOAD_DIRECTORY, f"{file_id}.{file.filename.split('.')[-1]}"
    )

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    db.add(
        ImageModel(
            id=file_id,
            image_name=file.filename,
            image_path=file_path,
            detection_json="",
        )
    )
    db.commit()
    return {"file_id": file_id}


@app.get("/download/{file_id}")
async def download_image(file_id: str, db: Session = Depends(get_db)):
    file_path = None
    # query the database to get the image path
    image = db.query(ImageModel).filter(ImageModel.id == file_id).first()
    if image:
        file_path = image.image_path
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


@app.get("/list-images/")
async def list_images(db: Session = Depends(get_db)):
    images = db.query(ImageModel).all()
    return [asdict(image) for image in images]


# Model serving code
@app.post("/detect/{file_id}")
async def detect_objects(file_id: str, db: Session = Depends(get_db)):
    image = db.query(ImageModel).filter(ImageModel.id == file_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="File not found")

    # see if we have already detected objects
    if image.detection_json:
        return image.detection_json

    # detect objects
    detections = model.detect_objects(image.image_path)
    detection_json = [asdict(detection) for detection in detections]
    detection_json = json.dumps(detection_json)

    image.detection_json = detection_json
    db.add(image)
    db.commit()
    return detection_json


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
