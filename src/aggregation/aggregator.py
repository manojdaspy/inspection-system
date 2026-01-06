"""
Result Aggregator - Combines multi-camera results
"""

from typing import Dict, Any, List

from src.utils.logger import setup_logger


class ResultAggregator:
    """
    Aggregates results from multiple cameras into unified assessment.
    """
    
    PASS_THRESHOLD = 0.75  # Minimum score to pass inspection
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        
    def aggregate(self, camera_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate results from all cameras.
        
        Args:
            camera_results: Dictionary mapping camera_id to results
            
        Returns:
            Aggregated result with overall decision
        """
        if not camera_results:
            raise ValueError("No camera results to aggregate")
            
        # Extract scores and detections
        scores = []
        all_detections = []
        camera_summaries = {}
        
        for camera_id, result in camera_results.items():
            score = result.get("quality_score", 0.0)
            detections = result.get("detections", [])
            
            scores.append(score)
            all_detections.extend(detections)
            
            camera_summaries[camera_id] = {
                "score": score,
                "defects": len(detections),
                "severities": self._count_severities(detections)
            }
            
        # Calculate aggregated score (using minimum - strictest)
        # Alternative strategies: average, weighted average, voting
        aggregated_score = self._calculate_aggregated_score(scores)
        
        # Make pass/fail decision
        decision = "PASS" if aggregated_score >= self.PASS_THRESHOLD else "FAIL"
        
        # Count total defects by severity
        severity_counts = self._count_severities(all_detections)
        
        result = {
            "aggregated_score": round(aggregated_score, 3),
            "decision": decision,
            "camera_summaries": camera_summaries,
            "total_defects": len(all_detections),
            "severity_counts": severity_counts,
            "cameras_used": len(camera_results)
        }
        
        self.logger.debug(f"Aggregated {len(camera_results)} cameras: "
                         f"{decision} (Score: {aggregated_score:.2f})")
        
        return result
        
    def _calculate_aggregated_score(self, scores: List[float]) -> float:
        """
        Calculate final aggregated score from camera scores.
        Using minimum (strictest) strategy.
        
        Args:
            scores: List of quality scores from cameras
            
        Returns:
            Aggregated score
        """
        if not scores:
            return 0.0
            
        # Use minimum score (strictest standard)
        # Could also use: average, weighted average, etc.
        return min(scores)
        
    def _count_severities(self, detections: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count detections by severity level.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            Dictionary of severity counts
        """
        counts = {"minor": 0, "major": 0, "critical": 0}
        
        for det in detections:
            severity = det.get("severity", "minor")
            if severity in counts:
                counts[severity] += 1
                
        return counts