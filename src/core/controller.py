"""
Inspection Controller - Orchestrates the inspection workflow
"""

import time
import threading
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.utils.logger import setup_logger


class InspectionController:
    """
    Main controller that orchestrates the inspection cycle.
    Coordinates parallel camera operations and sequential processing.
    """
    
    MAX_CYCLE_TIMEOUT = 5.0  # seconds
    
    def __init__(self, cameras, preprocessor, inference_engine, 
                 postprocessor, aggregator, reporter, metrics):
        self.cameras = cameras
        self.preprocessor = preprocessor
        self.inference_engine = inference_engine
        self.postprocessor = postprocessor
        self.aggregator = aggregator
        self.reporter = reporter
        self.metrics = metrics
        self.logger = setup_logger(__name__)
        
    def execute_cycle(self, cycle_id: int) -> Dict[str, Any]:
        """
        Execute a complete inspection cycle.
        
        Args:
            cycle_id: Unique identifier for this cycle
            
        Returns:
            Inspection report dictionary
        """
        start_time = time.time()
        
        try:
            # Step 1: Trigger and parallel capture
            self.logger.info(f"Cycle {cycle_id}: Triggering cameras")
            frames = self._parallel_capture()
            
            if not frames:
                raise Exception("No frames captured from any camera")
            
            # Step 2: Per-camera processing pipeline
            self.logger.info(f"Cycle {cycle_id}: Processing {len(frames)} camera frames")
            camera_results = self._process_frames(frames)
            
            # Step 3: Aggregate results
            self.logger.info(f"Cycle {cycle_id}: Aggregating results")
            aggregated = self.aggregator.aggregate(camera_results)
            
            # Step 4: Generate report
            elapsed_ms = (time.time() - start_time) * 1000
            report = self.reporter.generate_report(
                cycle_id=cycle_id,
                camera_results=camera_results,
                aggregated_result=aggregated,
                total_time_ms=elapsed_ms
            )
            
            # Record metrics
            self.metrics.record_cycle(report)
            
            self.logger.info(f"Cycle {cycle_id}: Complete - {report['decision']} "
                           f"(Score: {report['aggregated_score']:.2f})")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Cycle {cycle_id} failed: {str(e)}")
            self.metrics.record_failure()
            raise
            
    def _parallel_capture(self) -> Dict[str, Dict[str, Any]]:
        """
        Capture frames from all cameras in parallel.
        
        Returns:
            Dictionary mapping camera_id to frame data
        """
        frames = {}
        
        with ThreadPoolExecutor(max_workers=len(self.cameras)) as executor:
            # Submit capture tasks
            future_to_camera = {
                executor.submit(self._capture_with_retry, camera): camera
                for camera in self.cameras
            }
            
            # Collect results
            for future in as_completed(future_to_camera):
                camera = future_to_camera[future]
                try:
                    frame = future.result(timeout=self.MAX_CYCLE_TIMEOUT)
                    if frame:
                        frames[camera.camera_id] = frame
                        self.logger.debug(f"Captured frame from {camera.camera_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to capture from {camera.camera_id}: {str(e)}")
                    self.metrics.record_camera_failure(camera.camera_id)
                    
        return frames
        
    def _capture_with_retry(self, camera, max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """
        Attempt to capture frame with retry logic.
        
        Args:
            camera: Camera object
            max_retries: Maximum number of retry attempts
            
        Returns:
            Frame data or None if all retries failed
        """
        for attempt in range(max_retries):
            try:
                frame = camera.capture()
                return frame
            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.debug(f"{camera.camera_id}: Retry {attempt + 1}/{max_retries}")
                    time.sleep(0.05)  # Small delay between retries
                else:
                    self.logger.error(f"{camera.camera_id}: All retries failed")
                    return None
                    
    def _process_frames(self, frames: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Process each frame through the complete pipeline.
        
        Args:
            frames: Dictionary of camera_id to frame data
            
        Returns:
            Dictionary of camera_id to processing results
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=len(frames)) as executor:
            future_to_camera = {
                executor.submit(self._process_single_frame, camera_id, frame): camera_id
                for camera_id, frame in frames.items()
            }
            
            for future in as_completed(future_to_camera):
                camera_id = future_to_camera[future]
                try:
                    result = future.result()
                    results[camera_id] = result
                except Exception as e:
                    self.logger.error(f"Processing failed for {camera_id}: {str(e)}")
                    # Continue with other cameras
                    
        return results
        
    def _process_single_frame(self, camera_id: str, frame: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single frame through the complete pipeline.
        
        Args:
            camera_id: Camera identifier
            frame: Frame data
            
        Returns:
            Processing result
        """
        pipeline_start = time.time()
        
        # Preprocess
        preprocessed = self.preprocessor.process(frame)
        
        # Inference
        detections = self.inference_engine.infer(preprocessed, camera_id)
        
        # Post-process
        result = self.postprocessor.process(detections, camera_id)
        
        result['pipeline_time_ms'] = (time.time() - pipeline_start) * 1000
        
        return result