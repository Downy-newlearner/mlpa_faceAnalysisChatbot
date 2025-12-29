"""
LLM Service: GPT-4o-mini integration for answering questions about analysis results.
The LLM only uses the provided JSON data - no hallucination allowed.
"""

import json
from typing import Optional
from openai import OpenAI

from ..config import get_settings

# System prompt designed to prevent hallucination
SYSTEM_PROMPT = """당신은 이미지 분석 결과에 대해 질문에 답변하는 도우미입니다.
얼굴 인식 분석을 통해 생성된 JSON 데이터가 제공됩니다.

## 규칙 (반드시 준수)
1. 오직 제공된 JSON 데이터만 사용하여 답변하세요
2. JSON에 없는 정보는 절대 추측하거나 만들어내지 마세요
3. 질문이 JSON 데이터로 답할 수 없는 경우, 솔직하게 "제공된 데이터로는 답변할 수 없습니다"라고 하세요
4. 정확한 숫자와 비율을 사용하세요
5. 친절하고 전문적인 톤을 유지하세요
6. 한국어로 답변하세요

## JSON 데이터 구조
- total_faces: 감지된 총 얼굴 수
- gender: 성별 분포 (male, female)
- age_group: 연령대 분포 (10s, 20s, 30s, 40_plus)
"""


class LLMService:
    """Service for interacting with OpenAI GPT-4o-mini."""
    
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def answer_question(self, json_data: dict, question: str) -> str:
        """
        Answer a question based on the provided JSON data.
        
        Args:
            json_data: The analysis result JSON
            question: User's question in natural language
            
        Returns:
            Natural language answer based on the JSON data
        """
        # Format the JSON for the prompt
        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # Create the user message with JSON context
        user_message = f"""## 분석 결과 데이터
```json
{json_str}
```

## 사용자 질문
{question}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=0,  # Deterministic output for accuracy
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"죄송합니다. 답변을 생성하는 중 오류가 발생했습니다: {str(e)}"
    
    def get_summary(self, json_data: dict) -> str:
        """
        Generate a natural language summary of the analysis results.
        
        Args:
            json_data: The analysis result JSON
            
        Returns:
            Natural language summary
        """
        question = "이 분석 결과를 간단히 요약해주세요. 총 인원 수, 성별 비율, 연령대 분포를 포함해주세요."
        return self.answer_question(json_data, question)


# Singleton instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
