"""
Chat Router: Handles LLM-based Q&A about analysis results.
"""

import json
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..database import get_db, Analysis, ChatLog
from ..services.llm_service import get_llm_service
from ..schemas.models import ChatRequest, ChatResponse, ChatHistoryResponse, ChatHistoryItem

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about analysis results.
    The LLM answers based ONLY on the JSON data - no hallucination.
    """
    # Get analysis
    analysis = db.query(Analysis).filter(Analysis.analysis_id == request.analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed. Status: {analysis.status}"
        )
    
    # Parse JSON result
    try:
        json_data = json.loads(analysis.json_result)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid analysis result format")
    
    # Get LLM answer
    llm_service = get_llm_service()
    answer = llm_service.answer_question(json_data, request.question)
    
    # Log the chat
    chat_log = ChatLog(
        analysis_id=request.analysis_id,
        question=request.question,
        answer=answer
    )
    db.add(chat_log)
    db.commit()
    
    return ChatResponse(
        analysis_id=request.analysis_id,
        question=request.question,
        answer=answer,
        created_at=chat_log.created_at
    )


@router.get("/history/{analysis_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get chat history for an analysis."""
    # Verify analysis exists
    analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get chat logs
    logs = db.query(ChatLog).filter(
        ChatLog.analysis_id == analysis_id
    ).order_by(ChatLog.created_at.asc()).all()
    
    history = [
        ChatHistoryItem(
            question=log.question,
            answer=log.answer,
            created_at=log.created_at
        )
        for log in logs
    ]
    
    return ChatHistoryResponse(
        analysis_id=analysis_id,
        history=history
    )


@router.get("/summary/{analysis_id}")
async def get_summary(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get a natural language summary of the analysis results."""
    analysis = db.query(Analysis).filter(Analysis.analysis_id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != "completed":
        raise HTTPException(
            status_code=400,
            detail=f"Analysis not completed. Status: {analysis.status}"
        )
    
    json_data = json.loads(analysis.json_result)
    
    llm_service = get_llm_service()
    summary = llm_service.get_summary(json_data)
    
    return {
        "analysis_id": analysis_id,
        "summary": summary,
        "raw_data": json_data
    }
