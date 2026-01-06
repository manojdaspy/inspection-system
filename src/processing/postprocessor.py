"""
Postprocessor - Detection result processing and quality scoring
"""

import time
from typing import Dict, Any, List

from src.utils.logger import setup_logger


class Postprocessor:
    """
    Processes inference results, filters detections, and calculates quality scores.
    """
    
    CONFIDENCE_THRESHOLD = 0.7
    SEVERITY_THRESHOLDS = {
        "minor": (0.7, 0.8),
        "major": (0.8, 0.9),
        "critical": (0.9, 1.0)
    }
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        
    def process(self, inference_result: Dict[str, Any], camera_id: str) -> Dict[str, Any]:
        """
        Post-process inference results.
        
        Args:
            inference_result: Raw inference results
            camera_id: Camera identifier
            
        Returns:
            Processed results with filtered detections and quality score
        """
        start_time = time.time()
        
        detections = inference_result.get("detections", [])
        
        # Filter low-confidence detections
        filtered = self._filter_detections(detections)
        
        # Classify severity
        classified = self._classify_severity(filtered)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(classified)
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        self.logger.debug(f"Post-processed {camera_id}: {len(classified)}/{len(detections)} "
                         f"detections passed threshold (Score: {quality_score:.2f})")
        
        return {
            "camera_id": camera_id,
            "timestamp": inference_result["timestamp"],
            "detections": classified,
            "quality_score": quality_score,
            "total_detections": len(detections),
            "filtered_detections": len(classified),
            "postprocessing_time_ms": elapsed_ms
        }
        
    def _filter_detections(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter detections below confidence threshold.
        
        Args:
            detections: Raw detection list
            
        Returns:
            Filtered detection list
        """
        return [
            det for det in detections 
            if det["confidence"] >= self.CONFIDENCE_THRESHOLD
        ]
        
    def _classify_severity(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Classify defect severity based on confidence.
        
        Args:
            detections: Filtered detection list
            
        Returns:
            Detections with severity classification
        """
        classified = []
        for det in detections:
            confidence = det["confidence"]
            
            # Determine severity
            severity = "minor"
            for sev_level, (low, high) in self.SEVERITY_THRESHOLDS.items():
                if low <= confidence < high:
                    severity = sev_level
                    break
                    
            det_copy = det.copy()
            det_copy["severity"] = severity
            classified.append(det_copy)
            
        return classified
        
    def _calculate_quality_score(self, detections: List[Dict[str, Any]]) -> float:
        """
        Calculate overall quality score for the frame.
        
        Args:
            detections: Classified detection list
            
        Returns:
            Quality score between 0 and 1 (higher is better)
        """
        if not detections:
            return 1.0
            
        # Weight by severity
        severity_weights = {"minor": 0.1, "major": 0.3, "critical": 0.6}
        
        total_penalty = sum(
            severity_weights.get(det["severity"], 0.2) 
            for det in detections
        )
        
        # Cap at 0.0
        quality_score = max(0.0, 1.0 - total_penalty)
        
        return round(quality_score, 3)