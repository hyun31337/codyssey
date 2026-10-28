# 🎉 FestaPick - AI 축제 추천 서비스

> 사용자가 선택한 날짜, 선호 지역, 관심 테마에 맞춰 최신 실시간 검색 정보 기반의 맞춤형 대한민국 지역 축제를 AI가 추천해주는 서비스입니다.

---

## 🛠 기술 스택

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Backend**: Python 3 (`http.server` Serverless Function)
- **AI Engine**: OpenAI API (`gpt-5.4-mini`)
- **External API**: Naver Search API (블로그 검색)
- **Deployment & Hosting**: Vercel

---

## 🔗 배포 URL

- **서비스 URL**: https://festapick.vercel.app

---

## 🔑 환경 변수 (Environment Variables) 설정

서버리스 함수 실행에 필요한 환경 변수는 다음과 같습니다.

| 변수명 | 필수 여부 | 설명 |
| :--- | :---: | :--- |
| `OPENAI_API_KEY` | **필수** | OpenAI API 인증 키 |
| `OPENAI_BASE_URL` | 선택 | 기본값: `https://copa.codyssey.kr/v1` |
| `NAVER_CLIENT_ID` | 선택 | 네이버 검색 API Client ID |
| `NAVER_CLIENT_SECRET` | 선택 | 네이버 검색 API Client Secret |

### `.env` 파일 설정 (로컬 개발 환경)
프로젝트 최상위 루트 디렉토리에 `.env` 파일을 생성하고 아래와 같이 설정합니다.

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://copa.codyssey.kr/v1
NAVER_CLIENT_ID=your_naver_client_id_here
NAVER_CLIENT_SECRET=your_naver_client_secret_here
```

### Vercel 환경 변수 설정 방법
1. Vercel Dashboard에 접속하여 프로젝트 선택

2. Settings -> Environment Variables 메뉴로 이동

3. Key와 Value에 위 변수명을 입력 후 Save 실행

4. 변경 사항 적용을 위해 재배포(Redeploy) 진행

## 🚀 로컬 실행 및 배포 방법
1. 로컬 개발 환경 실행 (Vercel CLI 활용)
```
Bash
# Vercel CLI 설치 (최초 1회)
npm install -g vercel

# 프로젝트 디렉토리 이동 및 로컬 서버 실행
vercel dev
```

2. Vercel 배포 방법
```
Bash
# Vercel 프로덕션 배포
vercel --prod
```