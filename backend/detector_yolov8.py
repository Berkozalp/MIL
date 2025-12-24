import cv2
import numpy as np
from typing import List
from detector_base import DetectorBase, Detection

class YOLOv8Detector(DetectorBase):
    """YOLOv8 object detector implementation using Ultralytics"""
    
    def __init__(self, confidence: float = 0.25, iou_threshold: float = 0.45, 
                 model_size: str = 'n'):
        try:
            from ultralytics import YOLO
            self.YOLO = YOLO
        except ImportError:
            raise ImportError(
                "Ultralytics not installed. Install with: pip install ultralytics"
            )
        
        self.confidence = confidence
        self.iou_threshold = iou_threshold
        self.model_size = model_size
        
        # Load YOLOv8 model
        model_name = f'yolov8{model_size}.pt'
        print(f"Loading YOLOv8 model: {model_name}")
        self.model = self.YOLO(model_name)
        
        # COCO class names - person is class 0
        self.person_class_id = 0
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect objects using YOLOv8"""
        # Run inference
        results = self.model(
            frame, 
            conf=self.confidence,
            iou=self.iou_threshold,
            verbose=False
        )
        
        detections = []
        
        # Process results
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class id
                cls_id = int(box.cls[0])
                
                # Filter for person only (class 0 in COCO)
                if cls_id != self.person_class_id:
                    continue
                
                # Get bounding box coordinates (xyxy format)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x, y = int(x1), int(y1)
                w, h = int(x2 - x1), int(y2 - y1)
                
                # Get confidence score
                score = float(box.conf[0])
                
                # Calculate center
                cx, cy = x + w // 2, y + h // 2
                
                detections.append(Detection(
                    bbox=(x, y, w, h),
                    category='person',
                    score=score,
                    center=(cx, cy)
                ))
        
        return detections
    
    def update_settings(self, settings: dict):
        """Update YOLOv8 settings"""
        reload_model = False
        
        if 'confidence' in settings:
            self.confidence = settings['confidence']
        if 'iou_threshold' in settings:
            self.iou_threshold = settings['iou_threshold']
        if 'model_size' in settings and settings['model_size'] != self.model_size:
            self.model_size = settings['model_size']
            reload_model = True
        
        # Reload model if size changed
        if reload_model:
            model_name = f'yolov8{self.model_size}.pt'
            print(f"Reloading YOLOv8 model: {model_name}")
            self.model = self.YOLO(model_name)
    
    def get_settings(self) -> dict:
        """Get current settings"""
        return {
            'confidence': self.confidence,
            'iou_threshold': self.iou_threshold,
            'model_size': self.model_size
        }
