import cv2
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import os
from tracker import CentroidTracker
from camera_geometry import CameraProjector
from calibration import load_calibration
from detector_base import DetectorBase
from detector_mediapipe import MediaPipeDetector
from detector_yolov8 import YOLOv8Detector

@dataclass
class AnalyticState:
    total_in: int = 0
    total_out: int = 0
    currently_tracked: int = 0
    fps: float = 0.0

class UrbanFlowAnalyzer:
    def __init__(self, detector_type: str = "mediapipe", detector_settings: dict = None):
        """
        Initialize analyzer with specified detector
        
        Args:
            detector_type: 'mediapipe' or 'yolov8'
            detector_settings: dict of detector-specific settings
        """
        # Initialize detector
        self.detector_type = detector_type
        self.detector = self._create_detector(detector_type, detector_settings or {})
        
        from tracker_advanced import AdvancedTracker
        self.tracker = AdvancedTracker(max_disappeared=40, max_distance=100)
        
        from camera_motion import CameraMotionEstimator
        self.motion_estimator = CameraMotionEstimator()
        
        self.state = AnalyticState()
        self.roi_polygon = None 
        self.calibration_matrix = None # Homography matrix
        
        # Initialize Projector with Defaults or Calibration
        calib = load_calibration()
        self.projector = CameraProjector(
            fov_vertical=calib.cam_fov or 50.0,
            cam_height=calib.cam_height or 15.0,
            pitch_deg=calib.cam_pitch or -30.0
        )
    
    def _create_detector(self, detector_type: str, settings: dict) -> DetectorBase:
        """Create detector instance based on type"""
        if detector_type == "mediapipe":
            return MediaPipeDetector(
                score_threshold=settings.get('score_threshold', 0.25),
                max_results=settings.get('max_results', 20)
            )
        elif detector_type == "yolov8":
            return YOLOv8Detector(
                confidence=settings.get('confidence', 0.25),
                iou_threshold=settings.get('iou_threshold', 0.45),
                model_size=settings.get('model_size', 'n')
            )
        else:
            raise ValueError(f"Unknown detector type: {detector_type}")
    
    def set_detector(self, detector_type: str, settings: dict = None):
        """Switch to a different detector"""
        print(f"Switching detector to: {detector_type}")
        self.detector_type = detector_type
        self.detector = self._create_detector(detector_type, settings or {})


    def update_settings(self, settings: dict):
        if 'maxDistance' in settings:
            self.tracker.max_distance = settings['maxDistance']
        if 'maxDisappeared' in settings:
            self.tracker.max_disappeared = settings['maxDisappeared']
        if 'scoreThreshold' in settings:
            self.score_threshold = settings['scoreThreshold']

    def update_roi(self, points: List[dict]):
        self.roi_polygon = [(int(p['x']), int(p['y'])) for p in points]
        
    def update_calibration(self, matrix):
        self.calibration_matrix = matrix

    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, AnalyticState]:
        h_orig, w_orig = frame.shape[:2]
        
        # 1. Estimate Camera Motion
        camera_shift = self.motion_estimator.estimate_motion(frame)
        
        # 2. Run Detection using current detector
        detected_objects = self.detector.detect(frame)
        
        detections = [] # List of ((cx, cy), bbox)
        
        mask = None
        if self.roi_polygon and len(self.roi_polygon) > 2:
            mask = np.zeros((h_orig, w_orig), dtype=np.uint8)
            roi_pts = np.array([[(p[0] * w_orig // 100, p[1] * h_orig // 100)] for p in self.roi_polygon], dtype=np.int32)
            cv2.fillPoly(mask, [roi_pts], 255)

        for detection in detected_objects:
            x, y, w, h = detection.bbox
            cx, cy = detection.center
            
            # ROI Filter
            if mask is not None:
                if mask[min(cy, h_orig-1), min(cx, w_orig-1)] == 0:
                    continue

            # Format for tracker: ((cx, cy), (x, y, x+w, y+h))
            detections.append(((cx, cy), (x, y, x+w, y+h)))
            
        # Update tracker with Motion Compensation
        # Pass projector for speed estimation
        tracked_objects = self.tracker.update(detections, camera_shift, self.projector, w_orig, h_orig, fps=25)
        
        annotated_frame = frame.copy()
        
        # Visualize Camera Motion (Optional Debug)
        # if camera_shift != (0,0):
        #     cv2.arrowedLine(annotated_frame, (w_orig//2, h_orig//2), 
        #                     (int(w_orig//2 + camera_shift[0]), int(h_orig//2 + camera_shift[1])), (0, 0, 255), 2)
        
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
                
            # Speed Calculation
            real_speed_kmh = getattr(obj, 'current_speed', 0.0)
            
            # Draw ID
            cv2.putText(annotated_frame, f"ID: {obj_id}", (cx - 10, cy - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        
            # Draw Speed
            speed_text = f"{real_speed_kmh:.1f} km/h"
            cv2.putText(annotated_frame, speed_text, (cx - 20, cy - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                        
            cv2.circle(annotated_frame, (cx, cy), 4, (0, 255, 0), -1)

        return annotated_frame, self.state
