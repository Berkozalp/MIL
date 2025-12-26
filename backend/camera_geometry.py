import numpy as np

class CameraProjector:
    def __init__(self, fov_vertical=45.0, aspect_ratio=16/9, cam_height=10.0, pitch_deg=-30.0, yaw_deg=0.0):
        self.set_params(fov_vertical, aspect_ratio, cam_height, pitch_deg, yaw_deg)

    def set_params(self, fov_vertical, aspect_ratio, cam_height, pitch_deg, yaw_deg):
        self.fov_v = np.radians(fov_vertical)
        self.aspect = aspect_ratio
        self.fov_h = 2 * np.arctan(np.tan(self.fov_v / 2) * self.aspect)
        
        self.h = cam_height
        self.pitch = np.radians(pitch_deg)
        self.yaw = np.radians(yaw_deg)
        
        # Precompute rotation matrix (assuming roll is 0)
        # We want to transform World -> Camera
        # World: Y-up, X-right, Z-forward (or standard 3D convention)
        pass

    def pixel_to_ground(self, u, v, width, height):
        """
        Convert pixel coordinates (u, v) to ground plane coordinates (x, z).
        Assumes the ground is at y = 0.
        u: pixel x coordinate (0 to width)
        v: pixel y coordinate (0 to height)
        """
        # Normalized Device Coordinates (NDC) -1 to 1
        # In computer vision typically y is down, but for 3D projection we match the virtual camera
        
        # 1. Convert to Normalized Image Coordinates
        x_ndc = (2.0 * u / width) - 1.0
        y_ndc = 1.0 - (2.0 * v / height) # Y is up in 3D cam
        
        # 2. Ray in Camera Space
        # tan(fov/2) is the scale factor
        cam_x = x_ndc * np.tan(self.fov_h / 2)
        cam_y = y_ndc * np.tan(self.fov_v / 2)
        cam_z = -1.0 # Forward in camera space (OpenGL convention is -Z forward)
        
        ray_cam = np.array([cam_x, cam_y, cam_z])
        
        # 3. Rotate Ray to World Space
        # Pitch (Rotation around X)
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(self.pitch), -np.sin(self.pitch)],
            [0, np.sin(self.pitch), np.cos(self.pitch)]
        ])
        
        # Yaw (Rotation around Y)
        Ry = np.array([
            [np.cos(self.yaw), 0, np.sin(self.yaw)],
            [0, 1, 0],
            [-np.sin(self.yaw), 0, np.cos(self.yaw)]
        ])
        
        # Combined rotation: World_Ray = Ry * Rx * Cam_Ray
        ray_world = Ry @ (Rx @ ray_cam)
        
        # 4. Intersect with Ground Plane (Y = 0)
        # Ray Origin: Camera Position (0, h, 0) - wait, camera assumes origin is at (0,h,0) relative to ground point?
        # Actually simplest: Let Camera be at (0, h, 0).
        # Ray = Origin + t * Direction
        # Origin = [0, h, 0]
        # Ray_y = h + t * dy = 0  => t = -h / dy
        
        if abs(ray_world[1]) < 1e-6: # Ray is parallel to ground
            return None
            
        t = -self.h / ray_world[1]
        
        if t < 0: # Intersection is behind camera or sky
            return None
            
        intersect_point = np.array([0, self.h, 0]) + t * ray_world
        
        return intersect_point[0], intersect_point[2] # Return X, Z on ground

    def ground_to_pixel(self, x, z, width, height):
        """
        Convert ground coordinates (x, z) back to pixel coordinates (u, v).
        Assumes ground is at y = 0.
        """
        # 1. Point in World Space
        P_world = np.array([x, 0, z])
        
        # 2. Transform to Camera Space
        # Camera is at (0, h, 0). 
        # P_cam_rel = P_world - Cam_Pos
        P_rel = P_world - np.array([0, self.h, 0])
        
        # Invert rotation: Cam_P = Rx_inv * Ry_inv * P_rel
        # Rx_inv = transpose(Rx), Ry_inv = transpose(Ry)
        Rx = np.array([
            [1, 0, 0],
            [0, np.cos(self.pitch), -np.sin(self.pitch)],
            [0, np.sin(self.pitch), np.cos(self.pitch)]
        ])
        Ry = np.array([
            [np.cos(self.yaw), 0, np.sin(self.yaw)],
            [0, 1, 0],
            [-np.sin(self.yaw), 0, np.cos(self.yaw)]
        ])
        
        P_cam = Rx.T @ (Ry.T @ P_rel)
        
        # 3. Project to Image Plane
        # OpenGL convention: forward is -Z
        if P_cam[2] >= 0: # Point is behind camera
            return None
            
        # x_img = cam_x / (-cam_z * tan(fov_h/2))
        x_ndc = P_cam[0] / (-P_cam[2] * np.tan(self.fov_h / 2))
        y_ndc = P_cam[1] / (-P_cam[2] * np.tan(self.fov_v / 2))
        
        # 4. Convert NDR to Pixels
        u = (x_ndc + 1.0) * width / 2.0
        v = (1.0 - y_ndc) * height / 2.0
        
        return int(u), int(v)
