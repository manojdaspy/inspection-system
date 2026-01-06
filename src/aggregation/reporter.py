"""
Inspection Reporter - Generates unified inspection reports
"""

from datetime import datetime
from typing import Dict, Any

from src.utils.logger import setup_logger


class InspectionReporter:
    """
    Generates structured inspection reports combining all results.
    """
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        
    def generate_report(self, 
                       cycle_id: int,
                       camera_results: Dict[str, Dict[str, Any]],
                       aggregated_result: Dict[str, Any],
                       total_time_ms: float) -> Dict[str, Any]:
        """
        Generate comprehensive inspection report.
        
        Args:
            cycle_id: Inspection cycle identifier
            camera_results: Raw results from each camera
            aggregated_result: Aggregated assessment
            total_time_ms: Total cycle execution time
            
        Returns:
            Complete inspection report
        """
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Build camera detail section
        camera_details = {}
        for camera_id, result in camera_results.items():
            camera_details[camera_id] = {
                "quality_score": result.get("quality_score", 0.0),
                "defects_found": len(result.get("detections", [])),
                "processing_time_ms": result.get("pipeline_time_ms", 0.0),
                "defect_details": [
                    {
                        "type": det["class"],
                        "severity": det["severity"],
                        "confidence": det["confidence"]
                    }
                    for det in result.get("detections", [])
                ]
            }
            
        report = {
            "cycle_id": cycle_id,
            "timestamp": timestamp,
            "cameras": camera_details,
            "aggregated_score": aggregated_result["aggregated_score"],
            "decision": aggregated_result["decision"],
            "defects_found": aggregated_result["total_defects"],
            "severity_breakdown": aggregated_result["severity_counts"],
            "total_time_ms": round(total_time_ms, 2),
            "cameras_used": aggregated_result["cameras_used"]
        }
        
        # Log report summary
        self.logger.info(
            f"Report #{cycle_id}: {report['decision']} | "
            f"Score: {report['aggregated_score']:.2f} | "
            f"Defects: {report['defects_found']} | "
            f"Time: {report['total_time_ms']:.0f}ms"
        )
        
        return report
        
    def format_report_text(self, report: Dict[str, Any]) -> str:
        """
        Format report as human-readable text.
        
        Args:
            report: Report dictionary
            
        Returns:
            Formatted text report
        """
        lines = [
            f"═══════════════════════════════════════════",
            f"  INSPECTION REPORT - Cycle #{report['cycle_id']}",
            f"═══════════════════════════════════════════",
            f"Timestamp:     {report['timestamp']}",
            f"Decision:      {report['decision']}",
            f"Score:         {report['aggregated_score']:.2f}",
            f"Total Time:    {report['total_time_ms']:.0f}ms",
            f"",
            f"Defects Found: {report['defects_found']}",
        ]
        
        if report['defects_found'] > 0:
            severity = report['severity_breakdown']
            lines.append(f"  - Critical:  {severity.get('critical', 0)}")
            lines.append(f"  - Major:     {severity.get('major', 0)}")
            lines.append(f"  - Minor:     {severity.get('minor', 0)}")
            
        lines.append(f"")
        lines.append(f"Camera Results:")
        
        for camera_id, details in report['cameras'].items():
            lines.append(f"  {camera_id}:")
            lines.append(f"    Score:   {details['quality_score']:.2f}")
            lines.append(f"    Defects: {details['defects_found']}")
            lines.append(f"    Time:    {details['processing_time_ms']:.0f}ms")
            
        lines.append(f"═══════════════════════════════════════════")
        
        return "\n".join(lines)