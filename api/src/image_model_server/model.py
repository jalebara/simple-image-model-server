from abc import ABCMeta, abstractmethod
import numpy as np
from typing import List, Dict, Union, Iterable
from ultralytics import YOLO
from pathlib import Path
import json
from dataclasses import dataclass


@dataclass
class ObjectDetection:
    class_name: str
    confidence: float
    box: Iterable[int]

    def to_json(self):
        return json.dumps(self.__dict__)


class ObjectDetectionProvider(metaclass=ABCMeta):
    @abstractmethod
    def detect_objects(
        self, image: Union[np.ndarray, Path]
    ) -> List[ObjectDetection]: ...


class DefaultYolo(ObjectDetectionProvider):
    def __init__(self, version="yolo11n.pt"):
        self.model = YOLO(version)

    def detect_objects(self, image: Union[np.ndarray, Path]) -> List[ObjectDetection]:
        if isinstance(image, Path):
            image = str(image)
        result = self.model([image])[0]
        names = result.names
        boxes = result.boxes
        detections = []
        for i in range(len(boxes.cls)):
            class_name = names[int(boxes.cls[i])]
            confidence = float(boxes.conf[i])
            box = np.asarray(boxes.xyxy[i].cpu()).tolist()
            d = ObjectDetection(class_name, confidence, box)
            detections.append(d)
        return detections
