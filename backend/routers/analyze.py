"""
Analyze Router: Handles image analysis pipeline execution.
"""

import json
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db, Analysis
from ..services.pipeline_service import get_pipeline_service
from ..schemas.models import AnalysisResponse, AnalysisResult

router = APIRouter(prefix="/api", tags=["analyze"])


def run_analysis_background(analysis_id: str, image_paths: list):
    """Background task to run the analysis pipeline."""
    from ..database import SessionLocal
    
    db = SessionLocal()
    try:
        # Update status to processing
        analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
        if not analysis:
            return
        
        analysis.status = "processing"
        db.commit()
        
        # Run the pipeline
        pipeline_service = get_pipeline_service()
        result = pipeline_service.analyze_images(image_paths)
        
        # Update with results
        analysis.json_result = json.dumps(result, ensure_ascii=False)
        analysis.status = "completed"
        analysis.updated_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        # Mark as failed
        analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
        if analysis:
            analysis.status = "failed"
            analysis.json_result = json.dumps({"error": str(e)})
            db.commit()
    finally:
        db.close()


@router.get("/analyses")
async def list_analyses(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all analyses, ordered by creation date (newest first)."""
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(limit).all()
    
    result = []
    for a in analyses:
        image_paths = json.loads(a.image_paths) if a.image_paths else []
        json_result = json.loads(a.json_result) if a.json_result and a.json_result != "{}" else None
        
        result.append({
            "analysis_id": a.analysis_id,
            "status": a.status,
            "image_count": len(image_paths),
            "total_faces": json_result.get("total_faces", 0) if json_result else 0,
            "created_at": a.created_at.isoformat()
        })
    
    return {"analyses": result}


@router.post("/analyze/{analysis_id}")
async def start_analysis(
    analysis_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start the image analysis pipeline for uploaded images.
    Analysis runs in background - poll /api/result/{analysis_id} for results.
    """
    analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found. Upload images first.")
    
    if analysis.status == "processing":
        raise HTTPException(status_code=400, detail="Analysis is already in progress")
    
    if analysis.status == "completed":
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "message": "Analysis already completed. Use /api/result/{analysis_id} to get results."
        }
    
    # Get image paths
    image_paths = json.loads(analysis.image_paths) if analysis.image_paths else []
    
    if not image_paths:
        raise HTTPException(status_code=400, detail="No images found for this analysis")
    
    # Start background analysis
    background_tasks.add_task(run_analysis_background, analysis_id, image_paths)
    
    return {
        "analysis_id": analysis_id,
        "status": "processing",
        "message": f"Analysis started for {len(image_paths)} images. Poll /api/result/{analysis_id} for results."
    }


@router.get("/result/{analysis_id}", response_model=AnalysisResponse)
async def get_result(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get the analysis result."""
    analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    result = None
    if analysis.status == "completed":
        try:
            result_dict = json.loads(analysis.json_result)
            result = AnalysisResult(
                total_faces=result_dict.get("total_faces", 0),
                gender=result_dict.get("gender", {}),
                age_group=result_dict.get("age_group", {})
            )
        except:
            result = None
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status=analysis.status,
        result=result,
        created_at=analysis.created_at,
        message=f"Status: {analysis.status}"
    )


@router.get("/result/{analysis_id}/raw")
async def get_raw_result(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get the raw JSON result."""
    analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail=f"Analysis not completed. Status: {analysis.status}")
    
    return json.loads(analysis.json_result)
