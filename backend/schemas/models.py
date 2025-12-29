"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ==================== Analysis Schemas ====================

class GenderStats(BaseModel):
    """Gender statistics."""
    male: int = 0
    female: int = 0


class AgeGroupStats(BaseModel):
    """Age group statistics."""
    tens: int = Field(0, alias="10s")
    twenties: int = Field(0, alias="20s")
    thirties: int = Field(0, alias="30s")
    forty_plus: int = Field(0, alias="40_plus")
    
    class Config:
        populate_by_name = True


class AnalysisResult(BaseModel):
    """Complete analysis result."""
    total_faces: int = 0
    gender: GenderStats = GenderStats()
    age_group: AgeGroupStats = AgeGroupStats()


class AnalysisResponse(BaseModel):
    """Response for analysis endpoints."""
    analysis_id: str
    status: str
    result: Optional[AnalysisResult] = None
    created_at: datetime
    message: Optional[str] = None


class UploadResponse(BaseModel):
    """Response for upload endpoint."""
    analysis_id: str
    image_count: int
    message: str


# ==================== Chat Schemas ====================

class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    analysis_id: str
    question: str


class ChatResponse(BaseModel):
    """Response for chat endpoint."""
    analysis_id: str
    question: str
    answer: str
    created_at: datetime


class ChatHistoryItem(BaseModel):
    """Single chat history item."""
    question: str
    answer: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    """Response for chat history endpoint."""
    analysis_id: str
    history: List[ChatHistoryItem]


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
