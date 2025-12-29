"""
Image Pipeline: Face Detection + Gender + Age Classification
Processes images and outputs aggregated statistics in JSON format.
"""

import os
import sys
import json
import glob
from datetime import datetime
from PIL import Image
import torch
import cv2

from huggingface_hub import hf_hub_download
from ultralytics import YOLO
from transformers import ViTForImageClassification, ViTImageProcessor


class ImagePipeline:
    """Pipeline for face detection, gender classification, and age classification."""
    
    def __init__(self, device='cpu'):
        self.device = torch.device(device)
        print("Loading models...")
        self._load_models()
        print("All models loaded successfully!\n")
    
    def _load_models(self):
        """Load all required models."""
        # 1. YOLOv8 Face Detection
        print("  [1/3] Loading YOLOv8 Face Detection model...")
        yolo_model_path = hf_hub_download(
            repo_id="arnabdhar/YOLOv8-Face-Detection",
            filename="model.pt",
        )
        self.face_detector = YOLO(yolo_model_path)
        self.face_detector.to(self.device)
        
        # 2. Gender Classification
        print("  [2/3] Loading Gender Classification model...")
        gender_model_id = "rizvandwiki/gender-classification"
        self.gender_model = ViTForImageClassification.from_pretrained(gender_model_id)
        self.gender_processor = ViTImageProcessor.from_pretrained(gender_model_id)
        self.gender_model.to(self.device)
        self.gender_model.eval()
        
        # 3. Age Classification
        print("  [3/3] Loading Age Classification model...")
        age_model_id = "nateraw/vit-age-classifier"
        self.age_model = ViTForImageClassification.from_pretrained(age_model_id)
        self.age_processor = ViTImageProcessor.from_pretrained(age_model_id)
        self.age_model.to(self.device)
        self.age_model.eval()
    
    def _map_age_to_group(self, age_label: str) -> str:
        """Map model age label to output age group."""
        age_mapping = {
            "0-2": "10s",
            "3-9": "10s",
            "10-19": "10s",
            "20-29": "20s",
            "30-39": "30s",
            "40-49": "40_plus",
            "50-59": "40_plus",
            "60-69": "40_plus",
            "more than 70": "40_plus",
        }
        return age_mapping.get(age_label, "40_plus")
    
    def detect_faces(self, image_path: str):
        """Detect faces in an image and return bounding boxes."""
        results = self.face_detector(image_path, verbose=False)
        
        # Debug: Check raw detection count
        raw_count = len(results[0].boxes)
        print(f"    [DEBUG] Raw YOLO detections: {raw_count}")
        
        faces = []
        for box in results[0].boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = box.conf[0].item()
            faces.append({
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "confidence": conf
            })
        return faces
    
    def classify_gender(self, face_image: Image.Image) -> str:
        """Classify gender of a face image."""
        inputs = self.gender_processor(images=face_image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.gender_model(**inputs)
            predicted_idx = outputs.logits.argmax(-1).item()
        return self.gender_model.config.id2label[predicted_idx]
    
    def classify_age(self, face_image: Image.Image) -> str:
        """Classify age of a face image and return mapped age group."""
        inputs = self.age_processor(images=face_image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.age_model(**inputs)
            predicted_idx = outputs.logits.argmax(-1).item()
        age_label = self.age_model.config.id2label[predicted_idx]
        return self._map_age_to_group(age_label)
    
    def process_image(self, image_path: str) -> list:
        """Process a single image: detect faces and classify each."""
        # Detect faces
        faces = self.detect_faces(image_path)
        
        if not faces:
            return []
        
        # Load original image for cropping
        original_image = Image.open(image_path).convert('RGB')
        
        results = []
        skipped_small = 0
        for face in faces:
            x1, y1, x2, y2 = face["bbox"]
            
            # Crop face region
            face_crop = original_image.crop((x1, y1, x2, y2))
            
            # Skip very small faces (likely false positives or too small for classification)
            # Minimum size reduced to 10x10 to handle group photos with many small faces
            if face_crop.width < 10 or face_crop.height < 10:
                skipped_small += 1
                continue
            
            # Classify gender and age
            gender = self.classify_gender(face_crop)
            age_group = self.classify_age(face_crop)
            
            results.append({
                "bbox": face["bbox"],
                "confidence": face["confidence"],
                "gender": gender,
                "age_group": age_group
            })
        
        if skipped_small > 0:
            print(f"    [DEBUG] Skipped {skipped_small} faces (too small < 10x10)")
        
        return results
    
    def process_directory(self, input_dir: str) -> dict:
        """Process all images in a directory and aggregate results."""
        # Supported image extensions
        image_patterns = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]
        
        # Gather all image file paths
        image_paths = []
        for pattern in image_patterns:
            image_paths.extend(glob.glob(os.path.join(input_dir, pattern)))
        
        if not image_paths:
            print(f"No images found in {input_dir}")
            return None
        
        print(f"Found {len(image_paths)} images in {input_dir}")
        
        # Initialize counters
        total_faces = 0
        gender_counts = {"male": 0, "female": 0}
        age_group_counts = {"10s": 0, "20s": 0, "30s": 0, "40_plus": 0}
        
        # Process each image
        for i, img_path in enumerate(image_paths, 1):
            img_name = os.path.basename(img_path)
            print(f"  [{i}/{len(image_paths)}] Processing {img_name}...", end=" ")
            
            try:
                face_results = self.process_image(img_path)
                num_faces = len(face_results)
                total_faces += num_faces
                
                for face in face_results:
                    # Count gender
                    gender = face["gender"].lower()
                    if gender in gender_counts:
                        gender_counts[gender] += 1
                    
                    # Count age group
                    age_group = face["age_group"]
                    if age_group in age_group_counts:
                        age_group_counts[age_group] += 1
                
                print(f"{num_faces} faces detected")
                
            except Exception as e:
                print(f"Error: {e}")
        
        return {
            "total_faces": total_faces,
            "gender": gender_counts,
            "age_group": age_group_counts
        }
    
    def run(self, input_dirs: list, output_path: str) -> dict:
        """Run the pipeline on multiple directories and save JSON result."""
        # Initialize aggregated results
        aggregated = {
            "total_faces": 0,
            "gender": {"male": 0, "female": 0},
            "age_group": {"10s": 0, "20s": 0, "30s": 0, "40_plus": 0}
        }
        
        # Process each directory
        for input_dir in input_dirs:
            input_dir = os.path.expanduser(input_dir)
            if not os.path.isdir(input_dir):
                print(f"Directory not found: {input_dir}")
                continue
            
            print(f"\n{'='*60}")
            print(f"Processing directory: {input_dir}")
            print('='*60)
            
            result = self.process_directory(input_dir)
            
            if result:
                aggregated["total_faces"] += result["total_faces"]
                for gender, count in result["gender"].items():
                    aggregated["gender"][gender] += count
                for age_group, count in result["age_group"].items():
                    aggregated["age_group"][age_group] += count
        
        # Save results to JSON
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(aggregated, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print("Pipeline completed!")
        print(f"Results saved to: {output_path}")
        print('='*60)
        print(json.dumps(aggregated, indent=2))
        
        return aggregated


def main():
    # Define input directories
    input_dirs = [
        "~/MLPA_face_detection_chatbot/data/classroom",
    ]
    
    # Define output path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(script_dir, "results", "pipeline_result.json")
    
    # Create and run pipeline
    pipeline = ImagePipeline(device='cpu')
    result = pipeline.run(input_dirs, output_path)
    
    return result


if __name__ == "__main__":
    main()
