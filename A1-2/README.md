# 국내 여행 추천 프로그램 (Travel Planner)

사용자가 입력한 날짜(`-date`)를 바탕으로 LLM(OpenAI)이 시기별 맞춤형 여행지를 추천하고, **네이버 지역 검색 API**를 통해 해당 지역의 맛집 정보를 연동하여 최종 여행 리포트와 원본 데이터를 자동으로 생성해주는 CLI 프로그램입니다.

---

## 1. 주요 기능
- **CLI 인터페이스**: `argparse`를 활용하여 명령어 기반으로 간편하게 실행
- **LLM 1차 추천**: 입력된 날짜를 분석하여 추천 도시, 날씨 요약, 주요 행사/축제, 추천 근거를 구조화된 JSON 형태로 생성
- **네이버 지역 검색 연동**: 추천된 도시의 맛집 정보를 검색하여 상위 5곳의 상세 정보(이름, 주소, 카테고리, 링크 등) 확보 (검색 결과가 없거나 오류 발생 시에도 프로그램 중단 없이 '데이터 없음' 처리 후 정상 진행)
- **최종 리포트 생성**: 1차 추천 정보와 맛집 목록을 종합하여 깔끔한 Markdown(`- .md`) 리포트 자동 생성
- **보안 및 에러 관리**: `.env` 파일을 통한 API 키 관리 및 `errors` 섹션을 통한 예외/오류 이력 추적

---

## 2. 프로젝트 구조
travel-planner/
│
├── travel_planner.py      # 메인 실행 프로그램 코드
├── .env                   # API 키 환경변수 파일 (git 관리 제외)
└── results/               # 실행 결과 파일 저장 폴더
    ├── YYYY-MM-DD_travel_data.json  # 원본 데이터 및 에러 요약
    └── YYYY-MM-DD_travel_plan.md    # 최종 여행 추천 리포트

---

## 3. 설치 및 환경 설정 (Installation & Setup)

### 가상환경 생성 및 활성화
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS / Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows PowerShell)
.\venv\Scripts\Activate

### 필수 패키지 설치
pip install openai requests python-dotenv

---

## 4. API 키 설정 (보안 주의)

API 키가 코드에 직접 노출되지 않도록 **반드시** 프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 설정해야 합니다.

1. 프로젝트 루트 폴더에 `.env` 파일을 만듭니다.
2. 아래와 같이 OpenAI 및 네이버 Open API 키를 입력합니다.

OPENAI_API_KEY="Open API Key"
NAVER_CLIENT_ID="발급받은_네이버_Client_ID"
NAVER_CLIENT_SECRET="발급받은_네이버_Client_Secret"

> **⚠️ 보안 주의 사항**
> - API 키를 코드나 Git 저장소(README, 소스코드 등)에 직접 하드코딩하지 마세요.
> - `.env` 파일은 `.gitignore`에 등록하여 외부에 유출되지 않도록 관리해야 합니다.

---

## 5. 실행 방법 (Usage)

터미널에서 `--date` 옵션과 함께 여행 희망 날짜(`YYYY-MM-DD` 형식)를 입력하여 실행합니다.

python travel_planner.py --date "2026-05-15"

### 실행 예시 로그
[1/3] 1차 추천 생성 중(LLM)...
  - recommended_city: "제주"
[2/3] 맛집 검색 중(네이버 지역 API)...
  - 맛집 5곳 검색 완료
[3/3] 최종 리포트 생성 중(LLM)...

완료! results/2026-05-15_travel_plan.md 및 원본 데이터가 저장되었습니다.

---

## 6. 결과물 확인 방법

프로그램 실행이 성공하면 `results/` 폴더 내에 아래의 두 파일이 생성됩니다.

1. **원본 데이터 JSON (`results/YYYY-MM-DD_travel_data.json`)**
   - 1차 LLM 추천 결과 (도시, 날씨, 행사, 추천 근거)
   - 네이버 지역 검색을 통해 수집된 맛집 리스트
   - 프로그램 실행 중 발생한 오류/경고 이력 (`errors` 섹션)
2. **최종 여행 리포트 (`results/YYYY-MM-DD_travel_plan.md`)**
   - 추천 지역, 이유, 날씨, 행사/축제 정보
   - 맛집 리스트 추천 목록 (데이터 없을 시 "데이터 없음" 표기)
   - 1일 추천 일정 (오전/오후/저녁)
   - 오류 요약 섹션