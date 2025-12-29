"""
FastAPI Backend Server for Face Detection Chatbot.
Main entry point for the API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings, UPLOAD_DIR
from .database import init_db
from .routers import upload, analyze, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    print("🚀 Starting Face Detection Chatbot API...")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Face Detection Chatbot API",
    description="""
    이미지 분석 파이프라인과 LLM 챗봇을 결합한 API입니다.
    
    ## 기능
    - 📷 이미지 업로드
    - 🔍 얼굴 감지 + 성별/나이 분류
    - 💬 분석 결과에 대한 자연어 질의응답
    
    ## 워크플로우
    1. POST /api/upload - 이미지 업로드
    2. POST /api/analyze/{analysis_id} - 분석 시작
    3. GET /api/result/{analysis_id} - 결과 조회
    4. POST /api/chat - 질문하기
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(chat.router)

# Serve uploaded files (optional, for debugging)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Face Detection Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/upload",
            "analyze": "POST /api/analyze/{analysis_id}",
            "result": "GET /api/result/{analysis_id}",
            "chat": "POST /api/chat",
            "history": "GET /api/history/{analysis_id}"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
