import click
import requests
from pathlib import Path

SERVER_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{SERVER_URL}/upload"
DETECT_ENDPOINT = f"{SERVER_URL}/detect"


@click.command()
@click.option("-in", "--image-path", required=True, type=Path)
def updetect(image_path: Path):
    """Upload an image to the server and detect objects in it"""

    # Upload the image
    with open(image_path, "rb") as buffer:
        response = requests.post(UPLOAD_ENDPOINT, files={"file": buffer})
    response.raise_for_status()
    file_id = response.json()["file_id"]

    # Detect objects in the image
    response = requests.post(f"{DETECT_ENDPOINT}/{file_id}")
    response.raise_for_status()
    detections = response.json()
    print(detections)


if __name__ == "__main__":
    updetect()
