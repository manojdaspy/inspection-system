"""
Metrics Collector - Performance and operational metrics
"""

import threading
from typing import Dict, Any, List
from collections import defaultdict

from src.utils.logger import setup_logger


class MetricsCollector:
    """
    Thread-safe metrics collection for inspection system.
    Tracks cycle performance, defects, and errors.
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self._lock = threading.Lock()
        
        # Metrics storage
        self.cycle_times = []
        self.decisions = []
        self.defect_counts = []
        self.quality_scores = []
        self.camera_failures = defaultdict(int)
        self.total_failures = 0
        
    def record_cycle(self, report: Dict[str, Any]) -> None:
        """
        Record metrics from completed cycle.
        
        Args:
            report: Inspection report
        """
        with self._lock:
            self.cycle_times.append(report['total_time_ms'])
            self.decisions.append(report['decision'])
            self.defect_counts.append(report['defects_found'])
            self.quality_scores.append(report['aggregated_score'])
            
    def record_camera_failure(self, camera_id: str) -> None:
        """
        Record camera capture failure.
        
        Args:
            camera_id: Identifier of failed camera
        """
        with self._lock:
            self.camera_failures[camera_id] += 1
            
    def record_failure(self) -> None:
        """Record general cycle failure"""
        with self._lock:
            self.total_failures += 1
            
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics.
        
        Returns:
            Dictionary of aggregated metrics
        """
        with self._lock:
            total_cycles = len(self.decisions)
            successful = total_cycles
            
            if not total_cycles:
                return self._empty_summary()
                
            passes = self.decisions.count("PASS")
            fails = self.decisions.count("FAIL")
            
            summary = {
                "total_cycles": total_cycles,
                "successful_cycles": successful,
                "failed_cycles": self.total_failures,
                "pass_count": passes,
                "fail_count": fails,
                "pass_rate": (passes / total_cycles * 100) if total_cycles > 0 else 0,
                "avg_cycle_time": sum(self.cycle_times) / len(self.cycle_times) if self.cycle_times else 0,
                "min_cycle_time": min(self.cycle_times) if self.cycle_times else 0,
                "max_cycle_time": max(self.cycle_times) if self.cycle_times else 0,
                "avg_quality_score": sum(self.quality_scores) / len(self.quality_scores) if self.quality_scores else 0,
                "total_defects": sum(self.defect_counts),
                "avg_defects_per_cycle": sum(self.defect_counts) / len(self.defect_counts) if self.defect_counts else 0,
                "camera_failures": dict(self.camera_failures)
            }
            
            return summary
            
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary structure"""
        return {
            "total_cycles": 0,
            "successful_cycles": 0,
            "failed_cycles": 0,
            "pass_count": 0,
            "fail_count": 0,
            "pass_rate": 0.0,
            "avg_cycle_time": 0.0,
            "min_cycle_time": 0.0,
            "max_cycle_time": 0.0,
            "avg_quality_score": 0.0,
            "total_defects": 0,
            "avg_defects_per_cycle": 0.0,
            "camera_failures": {}
        }
        
    def reset(self) -> None:
        """Reset all metrics"""
        with self._lock:
            self.cycle_times.clear()
            self.decisions.clear()
            self.defect_counts.clear()
            self.quality_scores.clear()
            self.camera_failures.clear()
            self.total_failures = 0