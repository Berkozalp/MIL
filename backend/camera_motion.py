import cv2
import numpy as np

class CameraMotionEstimator:
    def __init__(self, min_features=100):
        self.prev_gray = None
        self.min_features = min_features
        # Feature params for Shi-Tomasi corner detection
        self.feature_params = dict(maxCorners=200,
                                   qualityLevel=0.01,
                                   minDistance=30,
                                   blockSize=3)
        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict(winSize=(15, 15),
                              maxLevel=2,
                              criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    def estimate_motion(self, curr_frame):
        """
        Estimates global camera motion (dx, dy) between previous and current frame.
        Returns (0, 0) if no previous frame or motion could not be determined.
        """
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)

        if self.prev_gray is None:
            self.prev_gray = curr_gray
            return (0, 0)

        # 1. Detect features in previous frame
        p0 = cv2.goodFeaturesToTrack(self.prev_gray, mask=None, **self.feature_params)

        if p0 is None or len(p0) < 10:
            # Not enough features, reset
            self.prev_gray = curr_gray
            return (0, 0)

        # 2. Calculate Optical Flow
        p1, st, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, curr_gray, p0, None, **self.lk_params)

        # 3. Select good points
        if p1 is None:
             self.prev_gray = curr_gray
             return (0, 0)

        good_new = p1[st == 1]
        good_old = p0[st == 1]
        
        if len(good_new) < 10:
            self.prev_gray = curr_gray
            return (0, 0)

        # 4. Calculate movement (shift) for each point
        movement = good_new - good_old
        dx_vals = movement[:, 0]
        dy_vals = movement[:, 1]
        
        # 5. Use Median to filter out outliers (moving objects like players)
        # The background usually occupies the majority of the view, so median represents background motion
        median_dx = np.median(dx_vals)
        median_dy = np.median(dy_vals)

        self.prev_gray = curr_gray
        
        # We return the shift of the SCENE relative to the camera.
        # If camera pans RIGHT, the scene shifts LEFT (negative dx).
        return (median_dx, median_dy)
