"""
Camera Interface - Mock camera implementation
"""

import time
import random
from datetime import datetime
from typing import Dict, Any, Tuple

from src.utils.logger import setup_logger


class Camera:
    """
    Mock camera implementation simulating frame capture.
    Includes realistic timing and occasional failures.
    """
    
    CAPTURE_LATENCY_RANGE = (0.05, 0.15)  # 50-150ms
    FAILURE_RATE = 0.05  # 5% chance of capture failure
    
    def __init__(self, camera_id: str, resolution: Tuple[int, int] = (1920, 1080)):
        self.camera_id = camera_id
        self.resolution = resolution
        self.logger = setup_logger(f"{__name__}.{camera_id}")
        self.frame_count = 0
        
    def capture(self) -> Dict[str, Any]:
        """
        Capture a frame from the camera.
        
        Returns:
            Frame data dictionary
            
        Raises:
            RuntimeError: If capture fails
        """
        # Simulate capture latency
        latency = random.uniform(*self.CAPTURE_LATENCY_RANGE)
        time.sleep(latency)
        
        # Simulate occasional failures
        if random.random() < self.FAILURE_RATE:
            raise RuntimeError(f"{self.camera_id}: Capture failed - sensor timeout")
            
        self.frame_count += 1
        
        # Generate mock frame data
        frame_data = self._generate_mock_frame()
        
        self.logger.debug(f"Captured frame #{self.frame_count} ({latency*1000:.0f}ms)")
        
        return frame_data
        
    def _generate_mock_frame(self) -> Dict[str, Any]:
        """
        Generate mock frame data.
        
        Returns:
            Frame data structure
        """
        return {
            "camera_id": self.camera_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "frame_number": self.frame_count,
            "resolution": self.resolution,
            "frame_data": f"<mock_image_data_{self.resolution[0]}x{self.resolution[1]}>",
            "metadata": {
                "exposure_ms": random.uniform(8, 12),
                "gain": random.uniform(1.0, 2.0),
                "temperature_c": random.uniform(35, 45)
            }
        }
        
    def get_info(self) -> Dict[str, Any]:
        """Get camera information"""
        return {
            "camera_id": self.camera_id,
            "resolution": self.resolution,
            "frames_captured": self.frame_count
        }


class CameraFactory:
    """Factory for creating camera instances"""
    
    @staticmethod
    def create_camera(camera_id: str, resolution: Tuple[int, int] = (1920, 1080)) -> Camera:
        """
        Create a camera instance.
        
        Args:
            camera_id: Unique camera identifier
            resolution: Camera resolution (width, height)
            
        Returns:
            Camera instance
        """
        return Camera(camera_id, resolution)