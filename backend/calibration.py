import json
import os
from typing import List, Optional
from pydantic import BaseModel

class Point(BaseModel):
    x: float
    y: float

class CalibrationSettings(BaseModel):
    points: List[Point] = []
    # Legacy/Future support (optional)
    real_width: Optional[float] = 10.0 # Real world width in meters
    real_height: Optional[float] = 20.0 # Real world height in meters
    
    # Camera Extrinsics/Intrinsics for Ground Projection
    cam_height: Optional[float] = 15.0 # meters
    cam_pitch: Optional[float] = -30.0 # degrees
    cam_fov: Optional[float] = 50.0 # degrees vertical

CALIBRATION_FILE = "calibration_config.json"

def load_calibration():
    if os.path.exists(CALIBRATION_FILE):
        try:
            with open(CALIBRATION_FILE, "r") as f:
                data = json.load(f)
                return CalibrationSettings(**data)
        except:
            pass
    return CalibrationSettings()

def save_calibration(settings: CalibrationSettings):
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(settings.dict(), f, indent=4)
