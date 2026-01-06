"""
Preprocessor - Image preprocessing and enhancement
"""

import time
import random
from typing import Dict, Any

from src.utils.logger import setup_logger


class Preprocessor:
    """
    Handles image preprocessing including normalization and enhancement.
    Mock implementation simulating real preprocessing operations.
    """
    
    PROCESSING_TIME_RANGE = (0.02, 0.04)  # 20-40ms
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        
    def process(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess frame data.
        
        Args:
            frame: Raw frame data from camera
            
        Returns:
            Preprocessed frame data
        """
        start_time = time.time()
        
        # Simulate preprocessing operations
        self._mock_normalize(frame)
        self._mock_enhance(frame)
        
        # Simulate processing time
        process_time = random.uniform(*self.PROCESSING_TIME_RANGE)
        time.sleep(process_time)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.logger.debug(f"Preprocessed frame from {frame['camera_id']} ({elapsed_ms:.0f}ms)")
        
        preprocessed = {
            "camera_id": frame["camera_id"],
            "timestamp": frame["timestamp"],
            "frame_number": frame["frame_number"],
            "preprocessed_data": f"<normalized_enhanced_{frame['resolution'][0]}x{frame['resolution'][1]}>",
            "preprocessing_applied": [
                "normalization",
                "noise_reduction",
                "contrast_enhancement"
            ],
            "preprocessing_time_ms": elapsed_ms
        }
        
        return preprocessed
        
    def _mock_normalize(self, frame: Dict[str, Any]) -> None:
        """Mock normalization operation"""
        # In real implementation: convert to float, normalize to [0, 1]
        pass
        
    def _mock_enhance(self, frame: Dict[str, Any]) -> None:
        """Mock enhancement operation"""
        # In real implementation: apply filters, adjust contrast
        pass