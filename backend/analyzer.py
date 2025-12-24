import cv2
import mediapipe as mp
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
import os
from tracker import CentroidTracker

# MediaPipe Tasks API
BaseOptions = mp.tasks.BaseOptions
ObjectDetector = mp.tasks.vision.ObjectDetector
ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

@dataclass
class DetectionResult:
    id: int
    bbox: Tuple[int, int, int, int] # x, y, w, h
    category: str
    score: float
    center: Tuple[int, int]

@dataclass
class AnalyticState:
    total_in: int = 0
    total_out: int = 0
    currently_tracked: int = 0
    fps: float = 0.0

class UrbanFlowAnalyzer:
    def __init__(self, model_path: str = "efficientdet_lite0.tflite"):
        if not os.path.exists(model_path):
            print(f"Warning: Model {model_path} not found. Object detection will fail.")

        # Use new MediaPipe Tasks API
        import mediapipe as mp
        BaseOptions = mp.tasks.BaseOptions
        ObjectDetector = mp.tasks.vision.ObjectDetector
        ObjectDetectorOptions = mp.tasks.vision.ObjectDetectorOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            max_results=20,
            score_threshold=0.4,
            running_mode=VisionRunningMode.IMAGE
        )
        self.detector = ObjectDetector.create_from_options(options)
        
        from tracker_advanced import AdvancedTracker
        self.tracker = AdvancedTracker(max_disappeared=40, max_distance=100)
        
        self.state = AnalyticState()
        self.roi_polygon = None 
        self.score_threshold = 0.4

    def update_settings(self, settings: dict):
        if 'maxDistance' in settings:
            self.tracker.max_distance = settings['maxDistance']
        if 'maxDisappeared' in settings:
            self.tracker.max_disappeared = settings['maxDisappeared']
        if 'scoreThreshold' in settings:
            self.score_threshold = settings['scoreThreshold']

    def update_roi(self, points: List[dict]):
        self.roi_polygon = [(int(p['x']), int(p['y'])) for p in points]

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, AnalyticState]:
        h_orig, w_orig = frame.shape[:2]
        
        # Convert to RGB and MP Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        detection_result = self.detector.detect(mp_image)
        
        detections = [] # List of ((cx, cy), bbox)
        
        # Apply ROI Mask if defined (Optimization: Mask frame before detection? 
        # MP Tasks doesn't support mask input directly easily without image manipulation.
        # We process all, then filter.)
        mask = None
        if self.roi_polygon and len(self.roi_polygon) > 2:
            mask = np.zeros((h_orig, w_orig), dtype=np.uint8)
            roi_pts = np.array([[(p[0] * w_orig // 100, p[1] * h_orig // 100)] for p in self.roi_polygon], dtype=np.int32)
            cv2.fillPoly(mask, [roi_pts], 255)

        for detection in detection_result.detections:
            category = detection.categories[0]
            # Filter for PERSON only
            if category.category_name != 'person':
                continue
            if category.score < self.score_threshold:
                continue
                
            bbox = detection.bounding_box
            x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
            
            cx, cy = x + w//2, y + h//2
            
            # ROI Filter
            if mask is not None:
                if mask[min(cy, h_orig-1), min(cx, w_orig-1)] == 0:
                    continue

            # Format for tracker: ((cx, cy), (x, y, x+w, y+h))
            detections.append(((cx, cy), (x, y, x+w, y+h)))
            
        # Update tracker
        tracked_objects = self.tracker.update(detections)
        
        annotated_frame = frame.copy()
        
        # Draw ROI overlay
        if self.roi_polygon and len(self.roi_polygon) > 2:
            roi_pts = np.array([[(p[0] * w_orig // 100, p[1] * h_orig // 100)] for p in self.roi_polygon], dtype=np.int32)
            cv2.polylines(annotated_frame, [roi_pts], True, (0, 255, 0), 2)
        
        # Filter logic: Count IN vs OUT based on ROI?
        # For now, just count tracked objects
        self.state.currently_tracked = len(tracked_objects)
        
        # Draw Objects
        for obj_id, obj in tracked_objects.items():
            cx, cy = int(obj.centroid[0]), int(obj.centroid[1])
            
            # Draw trail
            if len(obj.history) > 1:
                pts = np.array(obj.history, np.int32)
                pts = pts.reshape((-1, 1, 2))
                cv2.polylines(annotated_frame, [pts], False, (0, 255, 255), 2)
            
            # Draw BBox
            if obj.bbox:
                bx1, by1, bx2, by2 = obj.bbox
                cv2.rectangle(annotated_frame, (bx1, by1), (bx2, by2), (0, 255, 0), 2)
                
            # Draw ID
            cv2.putText(annotated_frame, f"ID: {obj_id}", (cx - 10, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(annotated_frame, (cx, cy), 4, (0, 255, 0), -1)

        return annotated_frame, self.state
