"""
Upload Router: Handles image upload and storage.
"""

import os
import json
import uuid
import shutil
from pathlib import Path
from typing import List
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db, Analysis
from ..config import UPLOAD_DIR
from ..schemas.models import UploadResponse, ErrorResponse

router = APIRouter(prefix="/api", tags=["upload"])

# Allowed image extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def validate_image(filename: str) -> bool:
    """Check if file has allowed image extension."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


@router.post("/upload", response_model=UploadResponse)
async def upload_images(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload multiple images for analysis.
    Creates a new analysis record and stores images.
    
    Returns:
        analysis_id to use for subsequent operations
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Validate files
    for file in files:
        if not validate_image(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {file.filename}. Allowed: {ALLOWED_EXTENSIONS}"
            )
    
    # Generate unique analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Create upload directory for this analysis
    upload_path = UPLOAD_DIR / analysis_id
    upload_path.mkdir(parents=True, exist_ok=True)
    
    saved_paths = []
    
    try:
        # Save each uploaded file
        for file in files:
            file_path = upload_path / file.filename
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            saved_paths.append(str(file_path))
        
        # Create analysis record in database
        analysis = Analysis(
            analysis_id=analysis_id,
            json_result="{}",  # Empty until analysis runs
            image_paths=json.dumps(saved_paths),
            status="pending"
        )
        db.add(analysis)
        db.commit()
        
        return UploadResponse(
            analysis_id=analysis_id,
            image_count=len(saved_paths),
            message=f"Successfully uploaded {len(saved_paths)} images. Use /api/analyze/{analysis_id} to start analysis."
        )
        
    except Exception as e:
        # Cleanup on error
        if upload_path.exists():
            shutil.rmtree(upload_path)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/uploads/{analysis_id}")
async def get_upload_info(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get information about uploaded images for an analysis."""
    analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    image_paths = json.loads(analysis.image_paths) if analysis.image_paths else []
    
    return {
        "analysis_id": analysis_id,
        "status": analysis.status,
        "image_count": len(image_paths),
        "image_paths": image_paths,
        "created_at": analysis.created_at
    }
