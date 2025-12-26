import cv2
import numpy as np

class TrackedObject:
    def __init__(self, obj_id, centroid, bbox):
        self.obj_id = obj_id
        self.centroid = np.array(centroid, dtype=np.float32)
        self.bbox = bbox  # (x1, y1, x2, y2)
        self.history = [self.centroid]
        self.disappeared_count = 0
        self.age = 0
        self.current_speed = 0.0
        self.speed_history = []
        
        # Kalman Filter for smoothing (Optimized Parameters)
        self.kalman = cv2.KalmanFilter(4, 2)
        # Measurement matrix (we only measure x, y)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        # Transition matrix (constant velocity model)
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        
        # Process noise: assume objects can change velocity reasonably fast
        self.kalman.processNoiseCov = np.array([
            [0.1, 0, 0, 0], 
            [0, 0.1, 0, 0], 
            [0, 0, 0.2, 0], 
            [0, 0, 0, 02.]
        ], np.float32) * 0.05
        
        # Measurement noise: detectors are usually pretty accurate, but can jitter
        self.kalman.measurementNoiseCov = np.array([
            [0.5, 0],
            [0, 0.5]
        ], np.float32) * 0.1
        
        # Initial state
        self.kalman.statePre = np.array([[centroid[0]], [centroid[1]], [0], [0]], np.float32)
        self.kalman.statePost = np.array([[centroid[0]], [centroid[1]], [0], [0]], np.float32)

    def predict(self):
        prediction = self.kalman.predict()
        self.centroid = np.array([prediction[0, 0], prediction[1, 0]], dtype=np.float32)
        self.history.append(self.centroid)
        if len(self.history) > 50: # Limit history length
            self.history.pop(0)
        return self.centroid

    def update(self, measurement, bbox):
        self.disappeared_count = 0
        self.age += 1
        self.bbox = bbox
        mes = np.array([[np.float32(measurement[0])], [np.float32(measurement[1])]])
        self.kalman.correct(mes)
        
        # Update centroid with corrected state (smoothed)
        self.centroid = np.array([self.kalman.statePost[0, 0], self.kalman.statePost[1, 0]], dtype=np.float32)
        # Update latest history point to the smoothed one
        self.history[-1] = self.centroid

class AdvancedTracker:
    def __init__(self, max_disappeared=40, max_distance=100):
        self.next_obj_id = 0
        self.objects = {}  # id -> TrackedObject
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance

    def register(self, centroid, bbox):
        self.objects[self.next_obj_id] = TrackedObject(self.next_obj_id, centroid, bbox)
        self.next_obj_id += 1

    def deregister(self, obj_id):
        del self.objects[obj_id]

        return self.objects

    def update(self, detections, camera_shift=(0, 0), projector=None, frame_width=1280, frame_height=720, fps=30):
        """
        updates track with new detections.
        detections: list of tuples (centroid, bbox)
            centroid: (x, y)
            bbox: (x1, y1, x2, y2) normalized 0-1
        camera_shift: (dx, dy) how much the background moved since last frame
        projector: CameraProjector instance for 3D projection
        """
        
        # 1. Predict new positions for existing objects
        # Compensation: shift existing tracks by the camera movement
        for obj_id, obj in self.objects.items():
            # Apply camera compensation to the state BEFORE prediction
            # If scene moved by (dx, dy), the object should also move by (dx, dy) 
            # effectively keeping it 'still' relative to the world, but moving in pixel coords
            
            # Update history to shift with camera
            obj.history = [(h[0] + camera_shift[0], h[1] + camera_shift[1]) for h in obj.history]
            
            # Shift centroid and Kalman state
            shift_matrix = np.array([[camera_shift[0]], [camera_shift[1]], [0], [0]], np.float32)
            obj.kalman.statePost += shift_matrix
            
            obj.predict()
            obj.disappeared_count += 1
            
            # Decay speed if not updated
            obj.current_speed = getattr(obj, 'current_speed', 0) * 0.95

        if len(detections) == 0:
            # If no detections, mark all as disappeared
            for obj_id in list(self.objects.keys()):
                if self.objects[obj_id].disappeared_count > self.max_disappeared:
                    self.deregister(obj_id)
            return self.objects

        # 2. Match detections to existing objects
        input_centroids = np.array([d[0] for d in detections])
        
        if len(self.objects) == 0:
            for i in range(len(detections)):
                self.register(input_centroids[i], detections[i][1])
        else:
            object_ids = list(self.objects.keys())
            object_centroids = np.array([obj.centroid for obj in self.objects.values()])

            # Calculate robust distance matrix (Euclidean + IoU)
            D = self._dist_matrix(object_centroids, object_bboxes, input_centroids, input_bboxes)

            # hungarian algorithm like matching (simple greedy here based on sort)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]

            used_rows = set()
            used_cols = set()

            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue

                if D[row, col] > self.max_distance:
                    continue

                object_id = object_ids[row]
                
                # --- SPEED CALCULATION START ---
                # We use the corrected centroid vs new input centroid, removing camera shift influence
                # The 'prev_c' from the tracker is where the object WAS in the previous frame's coordinate system.
                # 'new_c' is where it IS in the current frame's coordinate system.
                # BUT, the camera itself moved. 'camera_shift' tells us how much the WORLD moved in the camera view (roughly).
                # Actually, simpler logic:
                # 1. Take previous centroid (before this frame update, but ALREADY COMPENSATED for camera move?)
                # NO. The tracker prediction step (above) shifted the old centroid by `camera_shift`.
                # So `self.objects[object_id].centroid` is now an ESTIMATE of where the object should be 
                # in the CURRENT frame coordinates if it didn't move in the world.
                # `new_c` is where it actually IS in the CURRENT frame coordinates.
                # So the difference `new_c - obj.centroid` is the motion of the object RELATIVE TO THE GROUND (in pixels).
                
                prev_c_compensated = self.objects[object_id].centroid 
                new_c = input_centroids[col]
                
                # Pixel vector
                vec_px = new_c - prev_c_compensated
                
                real_speed_kmh = 0.0
                
                if projector and frame_width > 0:
                    # Project both points to ground
                    # Point A: Estimated position if it stood still (Compensated Old Pos)
                    p1_ground = projector.pixel_to_ground(prev_c_compensated[0], prev_c_compensated[1], frame_width, frame_height)
                    # Point B: Actual new position
                    p2_ground = projector.pixel_to_ground(new_c[0], new_c[1], frame_width, frame_height)
                    
                    if p1_ground is not None and p2_ground is not None:
                        # Distance in meters
                        dx = p2_ground[0] - p1_ground[0]
                        dz = p2_ground[1] - p1_ground[1]
                        dist_m = np.sqrt(dx*dx + dz*dz)
                        
                        # Speed = Distance / Time
                        # FPS is frames per second. 
                        # Frame time = 1/FPS
                        # Speed (m/s) = dist_m * FPS
                        speed_mps = dist_m * fps
                        real_speed_kmh = speed_mps * 3.6
                else:
                    # Fallback to pixel speed estimation (rough)
                    pixel_speed = np.linalg.norm(vec_px)
                    # Rough scale: 100px ~ 1m? Very inaccurate without depth
                    real_speed_kmh = pixel_speed * 0.1 # dummy scale
                
                # Smooth speed using helpers (rolling average)
                self.objects[object_id].speed_history.append(real_speed_kmh)
                if len(self.objects[object_id].speed_history) > 10:
                    self.objects[object_id].speed_history.pop(0)
                
                self.objects[object_id].current_speed = np.mean(self.objects[object_id].speed_history)
                
                # --- SPEED CALCULATION END ---

                self.objects[object_id].update(input_centroids[col], detections[col][1])

                used_rows.add(row)
                used_cols.add(col)

            # Register new objects
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)
            for col in unused_cols:
                self.register(input_centroids[col], detections[col][1])

            # Deregister missing objects
            for obj_id in list(self.objects.keys()):
                 if self.objects[obj_id].disappeared_count > self.max_disappeared:
                    self.deregister(obj_id)

        return self.objects
    
    def _dist_matrix(self, object_centroids, object_bboxes, input_centroids, input_bboxes):
        # Euclidean distance matrix
        D_euc = np.linalg.norm(object_centroids[:, None, :] - input_centroids[None, :, :], axis=2)
        
        # IoU distance matrix (1.0 - IoU)
        N = len(object_bboxes)
        M = len(input_bboxes)
        D_iou = np.zeros((N, M), dtype=np.float32)
        
        for i in range(N):
            for j in range(M):
                D_iou[i, j] = 1.0 - self._calculate_iou(object_bboxes[i], input_bboxes[j])
        
        # Combined metric: weighted sum of Euclidean and IoU distance
        # Normalize Euclidean by max_distance to keep them in similar range
        D_euc_norm = D_euc / self.max_distance
        
        # If IoU is good, we strongly prefer it. If IoU is 0 (no overlap), Euclidean takes over.
        return 0.5 * D_euc_norm + 0.5 * D_iou

    def _calculate_iou(self, bbox1, bbox2):
        """Calculate Intersection over Union of two bounding boxes (x1, y1, x2, y2)"""
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        xi1 = max(x1_1, x1_2)
        yi1 = max(y1_1, y1_2)
        xi2 = min(x2_1, x2_2)
        yi2 = min(y2_1, y2_2)
        
        inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
        
        bbox1_area = (x2_1 - x1_1) * (y2_1 - y1_1)
        bbox2_area = (x2_2 - x1_2) * (y2_2 - y1_2)
        
        union_area = bbox1_area + bbox2_area - inter_area
        return inter_area / union_area if union_area > 0 else 0
