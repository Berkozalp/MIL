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
