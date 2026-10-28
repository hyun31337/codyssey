# AI 개인 PT 비서 (AI Personal Trainer Web App)

시계열 운동 데이터를 기반으로 개인 맞춤형 피드백과 조언을 제공하는 Full-Stack AI PT 비서 웹 애플리케이션입니다.

## 기술 스택 (Tech Stack)
- Backend: FastAPI, Python, Uvicorn
- Database & BaaS: Firebase Firestore
- AI Integration: OpenAI-compatible Proxy (gpt-5.4-mini)
- Frontend: Vanilla JavaScript, HTML5, CSS3
- Deployment: Backend(Render) / Frontend(Vercel)

## 프로젝트 구조 (Project Structure)
```
M1-2/
├── backend/
│   ├── routers/
│   │   ├── chat.py           # AI 챗봇 및 컨텍스트 주입 로직
│   │   ├── conversations.py  # 대화 기록 관리 (CRUD)
│   │   └── data.py           # 운동 기록 CRUD 및 요약/더미 데이터 생성
│   ├── firebase_config.py    # Firebase Firestore 연동 설정 (환경 변수 지원)
│   ├── main.py               # FastAPI 앱 메인 진입점 및 CORS 설정
│   └── requirements.txt      # 백엔드 라이브러리 의존성 목록
├── frontend/
│   ├── index.html            # 메인 웹 UI (챗봇, 데이터 관리 탭)
│   ├── style.css             # 스타일시트 (사이드바 확장 및 반응형 레이아웃)
│   └── app.js                # 프론트엔드 API 통신 및 동적 UI 제어
├── README.md
└── .gitignore                # 깃허브 제외 파일 설정 (.env, venv, service_account.json)
```

## 주요 기능 (Core Features)
1. AI 챗봇 및 문맥 주입 (Context Injection)
   - 운동 시계열 데이터 요약(평균, 최대, 트렌드 등)을 실시간 프롬프트에 주입하여 맞춤형 PT 피드백 제공
   - 상태 관리 가능한 대화 기록(저장, 불러오기, 이어서 대화하기, 새 대화 시작) 지원
2. 운동 데이터 관리 (Full CRUD)
   - 운동 기록 추가, 조회, 인라인 수정(PUT), 삭제 기능
   - 한 달치 무작위 운동 기록을 한 번에 생성하는 [더미 기록 (+10개)] 버튼 탑재
3. 데이터 통계 및 요약
   - 전체 운동 기간, 총 기록 수, 주요 지표(평균/최대/최소), 운동 추세 분석 자동 계산

## 환경 변수 설정 (Environment Variables)
- OPENAI_API_KEY: OpenAI 또는 프록시 서버 API 키
- ALLOWED_ORIGINS: CORS 허용 주소 (* 또는 Vercel 배포 URL)
- FIREBASE_CREDENTIALS: Render 배포 시 service_account.json 전체 텍스트 내용

## 로컬 실행 방법 (Local Installation)
1. 저장소 클론 및 백엔드 이동: cd M1-2/backend
2. 가상환경 생성 및 활성화: python -m venv venv 후 source venv/bin/activate
3. 패키지 설치: pip install -r requirements.txt
4. 백엔드 서버 실행: uvicorn main:app --reload --port 8000
5. 프론트엔드 실행: frontend/index.html 파일을 브라우저로 오픈

## 배포 정보 (Deployment URLs)
- 프론트엔드 배포 (Vercel): https://codyssey-frontend.vercel.app
- 백엔드 API 배포 (Render): https://codyssey-q520.onrender.com
- Swagger API 문서: https://codyssey-q520.onrender.com/docs