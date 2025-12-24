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
        # Kalman Filter for smoothing (Simple implementation)
        self.kalman = cv2.KalmanFilter(4, 2)
        self.kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        self.kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        self.kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.03
        
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

    def update(self, detections):
        """
        updates track with new detections.
        detections: list of tuples (centroid, bbox)
            centroid: (x, y)
            bbox: (x1, y1, x2, y2) normalized 0-1
        """
        
        # 1. Predict new positions for existing objects
        for obj_id, obj in self.objects.items():
            obj.predict()
            obj.disappeared_count += 1

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

            # Calculate distances (Euclidean)
            D = self._dist_matrix(object_centroids, input_centroids)

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
    
    def _dist_matrix(self, A, B):
        # A: (N, 2), B: (M, 2) -> returns (N, M) distance matrix
        return np.linalg.norm(A[:, None, :] - B[None, :, :], axis=2)
