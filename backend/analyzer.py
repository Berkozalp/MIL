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
            raise FileNotFoundError(f"Model not found at {model_path}")

        options = ObjectDetectorOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            max_results=20,
            score_threshold=0.4,
            running_mode=VisionRunningMode.IMAGE
        )
        self.detector = ObjectDetector.create_from_options(options)
        self.tracker = CentroidTracker(maxDisappeared=50, maxDistance=100)
        
        # Dictionary to store category names for each object ID
        # objectID -> category_name
        self.object_categories = {} 
        
        self.state = AnalyticState()
        
        # ROI and Detection Settings
        self.roi_polygon = None # List of (x, y) tuples in percentages
        self.score_threshold = 0.4

    def update_settings(self, settings: dict):
        if 'maxDistance' in settings:
            self.tracker.maxDistance = settings['maxDistance']
        if 'maxDisappeared' in settings:
            self.tracker.maxDisappeared = settings['maxDisappeared']
        if 'scoreThreshold' in settings:
            self.score_threshold = settings['scoreThreshold']

    def update_roi(self, points: List[dict]):
        # Convert List[dict] {'x': 20, 'y': 30} to List[Tuple[int, int]]
        self.roi_polygon = [(int(p['x']), int(p['y'])) for p in points]

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, AnalyticState]:
        h_orig, w_orig = frame.shape[:2]
        
        # Apply ROI Masking if defined
        mask = None
        if self.roi_polygon and len(self.roi_polygon) > 2:
            mask = np.zeros((h_orig, w_orig), dtype=np.uint8)
            roi_pts = np.array([[(p[0] * w_orig // 100, p[1] * h_orig // 100)] for p in self.roi_polygon], dtype=np.int32)
            cv2.fillPoly(mask, [roi_pts], 255)
            # Mask the frame for detection (optional, but helps focus detector)
            # frame_to_detect = cv2.bitwise_and(frame, frame, mask=mask)
        
        # Convert to MP Image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        detection_result = self.detector.detect(mp_image)
        
        rects = []
        temp_categories = []
        
        for detection in detection_result.detections:
            category = detection.categories[0]
            if category.score < self.score_threshold:
                continue
                
            bbox = detection.bounding_box
            x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
            
            # ROI Filter: Center of bbox must be inside mask
            cx_box, cy_box = x + w//2, y + h//2
            if mask is not None:
                if mask[min(cy_box, h_orig-1), min(cx_box, w_orig-1)] == 0:
                    continue

            rects.append((x, y, x + w, y + h))
            temp_categories.append(category.category_name)
            
        # Update tracker
        objects = self.tracker.update(rects)
        
        annotated_frame = frame.copy()
        
        # Draw ROI overlay on annotated frame
        if self.roi_polygon and len(self.roi_polygon) > 2:
            roi_pts = np.array([[(p[0] * w_orig // 100, p[1] * h_orig // 100)] for p in self.roi_polygon], dtype=np.int32)
            cv2.polylines(annotated_frame, [roi_pts], True, (0, 255, 0), 2)
        
        # Update currently tracked count
        self.state.currently_tracked = len(objects)
        
        # Clean up metadata
        current_ids = set(objects.keys())
        stored_ids = set(self.object_categories.keys())
        for missing_id in stored_ids - current_ids:
            del self.object_categories[missing_id]
        
        for (objectID, centroid) in objects.items():
            matched_detection = False
            closest_dist = 99999
            closest_idx = -1
            
            for i, rect in enumerate(rects):
                rx, ry, rx2, ry2 = rect
                rcx, rcy = (rx+rx2)//2, (ry+ry2)//2
                d = np.linalg.norm(np.array(centroid) - np.array([rcx, rcy]))
                if d < 80 and d < closest_dist:
                    closest_dist = d
                    closest_idx = i
            
            if closest_idx != -1:
                rx, ry, rx2, ry2 = rects[closest_idx]
                w, h = rx2 - rx, ry2 - ry
                category = temp_categories[closest_idx]
                self.object_categories[objectID] = {
                    "category": category,
                    "bbox_size": (w, h),
                    "last_seen_bbox": (rx, ry, rx2, ry2)
                }
                matched_detection = True
            
            meta = self.object_categories.get(objectID, {"category": "Object", "bbox_size": (50, 50)})
            w, h = meta["bbox_size"]
            c_x, c_y = centroid
            
            start_x, start_y = int(c_x - w/2), int(c_y - h/2)
            end_x, end_y = int(c_x + w/2), int(c_y + h/2)
            
            color = (0, 255, 0) if matched_detection else (0, 255, 255)
            cv2.rectangle(annotated_frame, (start_x, start_y), (end_x, end_y), color, 2)
            label = f"{meta['category']} {objectID}"
            cv2.putText(annotated_frame, label, (start_x, start_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            cv2.circle(annotated_frame, (c_x, c_y), 4, color, -1)

        return annotated_frame, self.state

        return annotated_frame, self.state
