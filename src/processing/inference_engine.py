"""
Inference Engine - Mock ML model inference
"""

import time
import random
from typing import Dict, Any, List

from src.utils.logger import setup_logger


class InferenceEngine:
    """
    Mock ML inference engine for defect detection.
    Simulates GPU processing and generates realistic detection results.
    """
    
    INFERENCE_TIME_RANGE = (0.10, 0.20)  # 100-200ms
    DEFECT_TYPES = ["scratch", "dent", "discoloration", "crack", "contamination"]
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.inference_count = 0
        
    def infer(self, preprocessed_data: Dict[str, Any], camera_id: str) -> Dict[str, Any]:
        """
        Run inference on preprocessed data.
        
        Args:
            preprocessed_data: Preprocessed frame data
            camera_id: Camera identifier
            
        Returns:
            Detection results with bounding boxes and confidences
        """
        start_time = time.time()
        
        # Simulate GPU processing time
        inference_time = random.uniform(*self.INFERENCE_TIME_RANGE)
        time.sleep(inference_time)
        
        # Generate mock detections
        detections = self._generate_detections()
        
        elapsed_ms = (time.time() - start_time) * 1000
        self.inference_count += 1
        
        self.logger.debug(f"Inference complete for {camera_id}: "
                         f"{len(detections)} detections ({elapsed_ms:.0f}ms)")
        
        return {
            "camera_id": camera_id,
            "timestamp": preprocessed_data["timestamp"],
            "detections": detections,
            "inference_time_ms": elapsed_ms,
            "model_version": "defect_detector_v2.1"
        }
        
    def _generate_detections(self) -> List[Dict[str, Any]]:
        """
        Generate mock detection results.
        
        Returns:
            List of detection dictionaries
        """
        # Random number of detections (0-4, weighted towards fewer)
        num_detections = random.choices([0, 1, 2, 3, 4], weights=[30, 35, 20, 10, 5])[0]
        
        detections = []
        for i in range(num_detections):
            detection = {
                "detection_id": f"det_{self.inference_count}_{i}",
                "bbox": [
                    random.randint(100, 1700),  # x
                    random.randint(100, 900),   # y
                    random.randint(50, 200),    # width
                    random.randint(50, 200)     # height
                ],
                "confidence": random.uniform(0.5, 0.99),
                "class": random.choice(self.DEFECT_TYPES),
                "raw_score": random.uniform(0.4, 1.0)
            }
            detections.append(detection)
            
        return detections