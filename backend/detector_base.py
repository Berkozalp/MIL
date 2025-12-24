from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class Detection:
    """Standardized detection result"""
    bbox: Tuple[int, int, int, int]  # x, y, w, h
    category: str
    score: float
    center: Tuple[int, int]

class DetectorBase(ABC):
    """Abstract base class for object detectors"""
    
    @abstractmethod
    def detect(self, frame) -> List[Detection]:
        """
        Detect objects in a frame
        
        Args:
            frame: numpy array (BGR format)
            
        Returns:
            List of Detection objects
        """
        pass
    
    @abstractmethod
    def update_settings(self, settings: dict):
        """Update detector-specific settings"""
        pass
    
    @abstractmethod
    def get_settings(self) -> dict:
        """Get current detector settings"""
        pass
