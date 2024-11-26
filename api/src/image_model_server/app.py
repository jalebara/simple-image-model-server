from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from dataclasses import asdict
from collections import defaultdict
import json

import cv2
import os
from uuid import uuid4
import uvicorn
from pathlib import Path

# Project Imports

from database import get_db, ImageModel
from model import DefaultYolo


app = FastAPI()

model = DefaultYolo()

UPLOAD_DIRECTORY = "/data/image-uploads"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

def get_image_detections(image_path:ImageModel) -> dict:

    # see if we have already detected objects
    if image.detection_json:
        return json.loads(image.detection_json)

    # detect objects
    detections = model.detect_objects(image.image_path)
    detection_dict = [asdict(detection) for detection in detections]
    image.detection_json = json.dumps(detection_dict)
    db.add(image)
    de.commit()
    return detection_dict


@app.post("/upload/")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # TODO: Upload post request with form-data image file
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
    get_image_detections(image)
    image = db.query(ImageModel).filter(ImageModel.id == file_id).first()
    data = {
        'image_name': image.image_name,
        'trait_value': image.detection_json,
        'train_name': "detections",
        'image_link': f"/image/detections/{file_id}"
    }
    return data


# TODO: Add a route to provide counts and <s>average confidence</s> of detected objects
@app.get("/object-count/{file_id}")
async def object_count(file_id: str, db: Session = Depends(get_db)):
    image = db.query(ImageModel).filter(ImageModel.id == file_id).first()
    detections = get_image_detections(image)
    class_counts = defaultdict(int)
    for detection in detections:
        class_name = detection["class_name"]
        class_counts[class_name] += 1
    data = []
    for class_name in class_counts.keys():
        data.append(
            {
                'image_name': file_id,
                'trait_value': class_counts[class_name]
                'trait_name': class_name,
                'image_link': file_id
            }
        )
    return data


# TODO: Add a route that returns a modified image with bounding boxes around detected objects
# image path is path to generated image
@app.get("/image/detections/{file_id}")
async def draw_detections(file_id: str, db: Session = Depends(get_db)):
    image = db.query(ImageModel).filter(ImageModel.id == file_id).first()
    if not image:
        raise HTTPException(status_code=404, detail="File not found")

    detections = get_image_detections(image)

    if image.modified_image_path:
        return FileResponse(image.modified_image_path)

    image_path = Path(image.image_path)
    image = cv2.imread(image_path)
    for detection in detections:
        box = detection["box"]
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (255, 0, 0), 1)

    bounded_image_path = image_path.with_name(image_path.name + "_with_detections")
    cv2.imwrite(bounded_image_path, image)
    image.modified_image_path = bounded_image_path
    return FileResponse(bounded_image_path)


# JSON format for the response of the detect_objects route
# {
#                'image_name' => 'Sr9GHXyXCN_nrVV13r.JPG',
#                'trait_value' => '33.75',
#                'image_link' => 'http://unet.mcrops.org/api_results/Sr9GHXyXCN_nrVV13r.png',
#                'trait_name' => 'CBSDpct | CO_334:0002078' # trait name is TBD
# };

# Postgres database connection

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
