import cv2
import mediapipe as mp
import numpy as np
from typing import List
from detector_base import DetectorBase, Detection
import os

class MediaPipeDetector(DetectorBase):
    """MediaPipe object detector implementation"""
    
    def __init__(self, model_path: str = "efficientdet_lite0.tflite", 
                 score_threshold: float = 0.25, max_results: int = 20):
        if not os.path.exists(model_path):
            print(f"Warning: Model {model_path} not found.")
        
        # MediaPipe Tasks API
        BaseOptions = mp.tasks.BaseOptions
        ObjectDetector = mp.tasks.vision.ObjectDetector
        ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        self.score_threshold = score_threshold
        self.max_results = max_results
        
        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            max_results=max_results,
            score_threshold=score_threshold,
            running_mode=VisionRunningMode.IMAGE
        )
        self.detector = ObjectDetector.create_from_options(options)
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Detect objects using MediaPipe"""
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        detection_result = self.detector.detect(mp_image)
        
        detections = []
        for detection in detection_result.detections:
            category = detection.categories[0]
            
            # Filter for person only
            if category.category_name != 'person':
                continue
            if category.score < self.score_threshold:
                continue
            
            bbox = detection.bounding_box
            x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
            cx, cy = x + w // 2, y + h // 2
            
            detections.append(Detection(
                bbox=(x, y, w, h),
                category='person',
                score=category.score,
                center=(cx, cy)
            ))
        
        return detections
    
    def update_settings(self, settings: dict):
        """Update MediaPipe settings"""
        if 'score_threshold' in settings:
            self.score_threshold = settings['score_threshold']
        if 'max_results' in settings:
            self.max_results = settings['max_results']
        
        # Recreate detector with new settings
        BaseOptions = mp.tasks.BaseOptions
        ObjectDetector = mp.tasks.vision.ObjectDetector
        ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode
        
        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path="efficientdet_lite0.tflite"),
            max_results=self.max_results,
            score_threshold=self.score_threshold,
            running_mode=VisionRunningMode.IMAGE
        )
        self.detector = ObjectDetector.create_from_options(options)
    
    def get_settings(self) -> dict:
        """Get current settings"""
        return {
            'score_threshold': self.score_threshold,
            'max_results': self.max_results
        }
