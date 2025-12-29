"""
Pipeline Service: Wrapper for the image analysis pipeline.
Handles image processing and returns structured JSON results.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Optional

# Add parent directory to path for importing image_pipeline
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from image_pipeline.image_pipeline import ImagePipeline


class PipelineService:
    """Service for running the image analysis pipeline."""
    
    def __init__(self, device: str = 'cpu'):
        self.device = device
        self._pipeline: Optional[ImagePipeline] = None
    
    @property
    def pipeline(self) -> ImagePipeline:
        """Lazy-load the pipeline (models are heavy)."""
        if self._pipeline is None:
            print("Initializing image pipeline (this may take a moment)...")
            self._pipeline = ImagePipeline(device=self.device)
        return self._pipeline
    
    def analyze_images(self, image_paths: List[str]) -> dict:
        """
        Analyze a list of images and return aggregated results.
        
        Args:
            image_paths: List of absolute paths to images
            
        Returns:
            Aggregated analysis result as a dictionary
        """
        # Initialize aggregated results
        aggregated = {
            "total_faces": 0,
            "gender": {"male": 0, "female": 0},
            "age_group": {"10s": 0, "20s": 0, "30s": 0, "40_plus": 0}
        }
        
        for img_path in image_paths:
            if not os.path.exists(img_path):
                print(f"Warning: Image not found: {img_path}")
                continue
            
            try:
                face_results = self.pipeline.process_image(img_path)
                
                for face in face_results:
                    aggregated["total_faces"] += 1
                    
                    # Count gender
                    gender = face["gender"].lower()
                    if gender in aggregated["gender"]:
                        aggregated["gender"][gender] += 1
                    
                    # Count age group
                    age_group = face["age_group"]
                    if age_group in aggregated["age_group"]:
                        aggregated["age_group"][age_group] += 1
                        
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        
        return aggregated
    
    def analyze_directory(self, directory_path: str) -> dict:
        """
        Analyze all images in a directory.
        
        Args:
            directory_path: Path to directory containing images
            
        Returns:
            Aggregated analysis result as a dictionary
        """
        return self.pipeline.process_directory(directory_path)


# Singleton instance
_pipeline_service: Optional[PipelineService] = None


def get_pipeline_service() -> PipelineService:
    """Get or create pipeline service instance."""
    global _pipeline_service
    if _pipeline_service is None:
        _pipeline_service = PipelineService(device='cpu')
    return _pipeline_service
