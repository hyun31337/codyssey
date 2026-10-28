import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import data, chat, conversations

load_dotenv()

app = FastAPI(
    title="AI Personal Trainer API",
    version="1.0.0",
    description="시계열 운동 데이터를 활용한 AI 개인 PT 비서 백엔드",
)

origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(data.router)
app.include_router(chat.router)
app.include_router(conversations.router)


@app.get("/")
def root():
    return {
        "message": "AI Personal Trainer API 서버가 정상적으로 동작 중입니다."
    }