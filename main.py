"""
Manufacturing Inspection System - Main Entry Point
Runs 10 inspection cycles with multi-camera parallel processing
"""

import time
import signal
import sys
from typing import Dict, Any

from src.core.controller import InspectionController
from src.core.camera import CameraFactory
from src.processing.preprocessor import Preprocessor
from src.processing.inference_engine import InferenceEngine
from src.processing.postprocessor import Postprocessor
from src.aggregation.aggregator import ResultAggregator
from src.aggregation.reporter import InspectionReporter
from src.utils.logger import setup_logger
from src.utils.metrics import MetricsCollector


class InspectionSystem:
    """Main system orchestrator for the inspection workflow"""
    
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.metrics = MetricsCollector()
        self.running = True
        
        # Initialize components
        self.cameras = [
            CameraFactory.create_camera("CAM_01", resolution=(1920, 1080)),
            CameraFactory.create_camera("CAM_02", resolution=(1920, 1080))
        ]
        
        self.preprocessor = Preprocessor()
        self.inference_engine = InferenceEngine()
        self.postprocessor = Postprocessor()
        self.aggregator = ResultAggregator()
        self.reporter = InspectionReporter()
        
        self.controller = InspectionController(
            cameras=self.cameras,
            preprocessor=self.preprocessor,
            inference_engine=self.inference_engine,
            postprocessor=self.postprocessor,
            aggregator=self.aggregator,
            reporter=self.reporter,
            metrics=self.metrics
        )
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        self.logger.info("Shutting down inspection system...")
        self.running = False
        self._print_summary()
        sys.exit(0)
        
    def run_cycles(self, num_cycles: int = 10):
        """
        Run specified number of inspection cycles
        
        Args:
            num_cycles: Number of inspection cycles to execute
        """
        self.logger.info(f"Starting inspection system - {num_cycles} cycles")
        print(f"\n{'='*60}")
        print(f"  Manufacturing Inspection System - Starting {num_cycles} Cycles")
        print(f"{'='*60}\n")
        
        for cycle_id in range(1, num_cycles + 1):
            if not self.running:
                break
                
            try:
                print(f"[Cycle {cycle_id:02d}/{num_cycles:02d}] Starting inspection...")
                
                # Execute inspection cycle
                report = self.controller.execute_cycle(cycle_id)
                
                # Display cycle result
                decision = report['decision']
                symbol = "✓" if decision == "PASS" else "✗"
                color = "\033[92m" if decision == "PASS" else "\033[91m"
                reset = "\033[0m"
                
                print(f"{color}[Cycle {cycle_id:02d}/{num_cycles:02d}] {symbol} {decision}{reset} "
                      f"- Score: {report['aggregated_score']:.2f} "
                      f"- Defects: {report['defects_found']} "
                      f"- Time: {report['total_time_ms']:.0f}ms")
                
                # Simulate part movement between cycles
                if cycle_id < num_cycles:
                    time.sleep(0.5)
                    
            except Exception as e:
                self.logger.error(f"Cycle {cycle_id} failed: {str(e)}")
                print(f"\033[91m[Cycle {cycle_id:02d}/{num_cycles:02d}] ✗ ERROR\033[0m - {str(e)}")
                
        self._print_summary()
        
    def _print_summary(self):
        """Print final summary statistics"""
        stats = self.metrics.get_summary()
        
        print(f"\n{'='*60}")
        print(f"  INSPECTION SUMMARY")
        print(f"{'='*60}")
        print(f"Total Cycles:        {stats['total_cycles']}")
        print(f"Successful:          {stats['successful_cycles']}")
        print(f"Failed:              {stats['failed_cycles']}")
        print(f"Pass Rate:           {stats['pass_rate']:.1f}%")
        print(f"Average Cycle Time:  {stats['avg_cycle_time']:.0f}ms")
        print(f"Total Defects:       {stats['total_defects']}")
        print(f"Camera Failures:     {stats['camera_failures']}")
        print(f"{'='*60}\n")
        
        self.logger.info(f"Inspection system completed - {stats['successful_cycles']} successful cycles")


def main():
    """Main entry point"""
    system = InspectionSystem()
    system.run_cycles(num_cycles=10)


if __name__ == "__main__":
    main()