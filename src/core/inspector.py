"""
Inspector - Pipeline manager for inspection workflow
"""

from typing import Dict, Any

from src.utils.logger import setup_logger


class InspectionPipeline:
    """
    Manages the complete inspection pipeline for a single camera.
    Coordinates preprocessing, inference, and post-processing steps.
    """
    
    def __init__(self, camera_id: str, preprocessor, inference_engine, postprocessor):
        self.camera_id = camera_id
        self.preprocessor = preprocessor
        self.inference_engine = inference_engine
        self.postprocessor = postprocessor
        self.logger = setup_logger(f"{__name__}.{camera_id}")
        
    def process(self, frame: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a frame through the complete pipeline.
        
        Args:
            frame: Raw frame data from camera
            
        Returns:
            Processing results including detections and quality score
        """
        self.logger.debug(f"Starting pipeline for frame {frame.get('frame_number')}")
        
        # Step 1: Preprocess
        preprocessed = self.preprocessor.process(frame)
        
        # Step 2: Run inference
        detections = self.inference_engine.infer(preprocessed, self.camera_id)
        
        # Step 3: Post-process
        result = self.postprocessor.process(detections, self.camera_id)
        
        self.logger.debug(f"Pipeline complete - Score: {result.get('quality_score', 0):.2f}")
        
        return result