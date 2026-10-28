import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from routers.data import get_data_summary

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

@router.post("")
def chat_with_ai(req: ChatRequest):
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY가 설정되지 않았습니다.")
        
        client = OpenAI(
            api_key=api_key,
            base_url="https://copa.codyssey.kr/v1"
        )
        
        summary = get_data_summary()

        system_instruction = f"""
당신은 전문적이고 친절한 AI 개인 PT(Personal Trainer) 비서입니다.
사용자의 운동 시계열 데이터를 바탕으로 맞춤형 피드백과 조언을 제공하세요.

[사용자 운동 데이터 요약]
- 기록 기간: {summary.get('period')}
- 총 운동 기록 수: {summary.get('count')}개
- 주요 지표(수치): 평균 {summary.get('metrics', {}).get('average')}, 최대 {summary.get('metrics', {}).get('max')}, 최소 {summary.get('metrics', {}).get('min')}
- 최근 트렌드: {summary.get('trend')}

위 데이터를 기반으로 사용자의 질문에 전문 PT 트레이너 말투로 맞춤 답변을 해주세요.
"""

        response = client.chat.completions.create(
            model="gpt-5.4-mini",  # 연동할 모델명
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": req.message}
            ],
            temperature=0.7,
        )

        reply = response.choices[0].message.content if response.choices else "답변을 생성하지 못했습니다."
        return {"reply": reply, "summary_used": summary}

    except Exception as e:
        print(f"🔥 [OpenAI Proxy Error]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 서버 오류: {str(e)}")