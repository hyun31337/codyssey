import argparse, requests, json, os, re, sys, time
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# ==========================================
# 0. 환경 변수 및 API 클라이언트 설정
# ==========================================
# .env 파일에서 API 키들을 불러옵니다.
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

# OpenAI API 키가 없으면 프로그램 종료
if not OPENAI_API_KEY:
    print("오류: OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    sys.exit(1)

# OpenAI 클라이언트 생성
client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url="https://copa.codyssey.kr/v1"
)

# 사용할 LLM 모델 이름 정의
MODEL_NAME = "gemini-3-flash"


# ==========================================
# 1. 보조 함수들 (날짜 검증 및 HTML 제거)
# ==========================================
def validate_date(date_str):
    """사용자가 입력한 날짜가 YYYY-MM-DD 형식이 맞는지 검증합니다."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def clean_html(raw_text):
    """네이버 검색 결과에 포함된 쓸데없는 HTML 태그(<b> 등)를 제거합니다."""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_text)


# ==========================================
# 2. 핵심 기능 함수 1: LLM 1차 추천 받기
# ==========================================
def get_llm_recommendation(date_str):
    """여행 날짜를 받아 LLM에게 추천 도시, 날씨, 행사 정보를 JSON 형태로 요청합니다."""
    prompt = f"""
    사용자가 입력한 여행 날짜: {date_str}
    이 시기에 국내 여행하기 좋은 도시 1곳을 추천하고, 해당 시기의 일반적인 날씨, 주요 행사/축제 후보(1~3개), 추천 근거를 작성해주세요.
    반드시 아래 JSON 형식으로만 응답하세요. 마크다운 코드블록(```json ... ```)을 쓰지 말고 순수 JSON 문자열만 출력하세요.
    
    {{
        "recommended_city": "도시이름",
        "weather": "날씨 요약",
        "events": ["행사1", "행사2"],
        "reason": "추천 근거 2~4문장"
    }}
    """
    
    errors = []
    content = ""
    
    # JSON 파싱 실패 시 최대 1번 더 재시도합니다.
    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            return json.loads(content), errors  # 성공 시 딕셔너리와 에러 리스트 반환
        except Exception as e:
            if attempt == 0:
                # 첫 번째 실패 시, 유효한 JSON으로 다시 달라고 프롬프트를 수정해서 재시도
                prompt = "이전 출력이 JSON 파싱에 실패했습니다. 유효한 JSON 형식으로만 다시 출력해주세요:\n" + content
                errors.append({"step": "llm_recommendation", "type": "PARSE_ERROR", "message": str(e)})
            else:
                errors.append({"step": "llm_recommendation", "type": "FATAL_ERROR", "message": str(e)})
                raise e


# ==========================================
# 3. 핵심 기능 함수 2: 네이버 맛집 검색하기
# ==========================================
def search_restaurants(city):
    """추천받은 도시 이름을 바탕으로 네이버 지역 API를 통해 맛집 5곳을 검색합니다."""
    errors = []
    restaurants = []
    
    # 네이버 API 키가 없으면 에러 기록 후 빈 리스트 반환 (프로그램 중단 안 함)
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        errors.append({"step": "place_search", "type": "AUTH_ERROR", "message": "NAVER_CLIENT_ID or NAVER_CLIENT_SECRET is missing"})
        return restaurants, errors

    url = f"https://openapi.naver.com/v1/search/local.json?query={city} 맛집&display=5"
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    
    try:
        res = requests.get(url, headers=headers)
        
        # 인증 오류 발생 시
        if res.status_code in [401, 403]:
            errors.append({"step": "place_search", "type": "AUTH_ERROR", "message": f"HTTP {res.status_code}"})
            return restaurants, errors
        
        data = res.json()
        items = data.get("items", [])
        
        # 검색 결과가 0건일 때
        if not items:
            errors.append({"step": "place_search", "type": "EMPTY_RESULT", "message": f"0 results for query={city} 맛집"})
            return restaurants, errors

        # 검색된 맛집 정보를 깔끔하게 정리
        for item in items:
            restaurants.append({
                "name": clean_html(item.get("title")),
                "address": item.get("roadAddress") or item.get("address"),
                "category": item.get("category"),
                "url": item.get("link"),
                "x": item.get("mapx"),
                "y": item.get("mapy")
            })
    except Exception as e:
        errors.append({"step": "place_search", "type": "NETWORK_ERROR", "message": str(e)})
        
    return restaurants, errors


# ==========================================
# 4. 핵심 기능 함수 3: 최종 리포트 마크다운 생성
# ==========================================
def generate_final_report(date_str, rec_data, restaurants):
    """1차 추천 정보와 맛집 목록을 종합하여 최종 Markdown 리포트를 작성합니다."""
    prompt = f"""
    아래 데이터를 바탕으로 국내 여행 추천 리포트를 Markdown 형식으로 작성해주세요.
    
    [입력 데이터]
    - 여행 날짜: {date_str}
    - 추천 정보: {json.dumps(rec_data, ensure_ascii=False)}
    - 맛집 목록: {json.dumps(restaurants, ensure_ascii=False)}
    
    [포함해야 할 목차]
    # {date_str} 국내 여행 추천 리포트
    ## 추천 지역
    ## 추천 이유
    ## 날씨 요약
    ## 행사/축제
    ## 맛집 추천 (맛집이 없으면 "데이터 없음 (장소 검색 결과 0건)"으로 표기)
    ## 1일 일정 제안 (오전/오후/저녁 수준으로 간단히)
    """
    
    # 서버 불안정(502 등)에 대비해 최대 3회까지 재시도
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == 2:
                raise e
            print(f"  - 일시적 서버 오류 발생, 2초 후 재시도합니다... ({attempt + 1}/3)")
            time.sleep(2)


# ==========================================
# 5. 메인 실행 흐름 (Main)
# ==========================================
def main():
    # CLI 인자 설정 (--date "YYYY-MM-DD" 입력받기)
    parser = argparse.ArgumentParser(description="국내 여행 추천 프로그램")
    parser.add_argument("--date", "-date", required=True, help="여행 날짜 (YYYY-MM-DD)")
    args = parser.parse_args()

    date_str = args.date
    
    # 날짜 형식 검증
    if not validate_date(date_str):
        print(f"오류: 잘못된 날짜 형식입니다 ('{date_str}'). YYYY-MM-DD 형식으로 입력해주세요.")
        sys.exit(1)

    all_errors = []  # 프로그램 실행 중 발생하는 모든 오류를 담을 리스트

    # [1단계] LLM을 이용한 1차 추천 도시/날씨/행사 생성
    print(f"[1/3] 1차 추천 생성 중(LLM)...")
    try:
        rec_data, llm_errors = get_llm_recommendation(date_str)
        all_errors.extend(llm_errors)
        city = rec_data.get("recommended_city", "제주")
        print(f"  - recommended_city: \"{city}\"")
    except Exception as e:
        print(f"  - 오류 발생: LLM 1차 추천 실패 ({e})")
        sys.exit(1)

    # [2단계] 네이버 API를 이용한 맛집 검색
    print(f"[2/3] 맛집 검색 중(네이버 지역 API)...")
    restaurants, place_errors = search_restaurants(city)
    all_errors.extend(place_errors)
    if place_errors:
        print(f"  - 경고/오류 발생: 맛집 검색 결과 없음 또는 인증 실패. 계속 진행합니다.")
    else:
        print(f"  - 맛집 {len(restaurants)}곳 검색 완료")

    # [3단계] 수집된 모든 데이터를 종합해 최종 리포트(Markdown) 생성
    print(f"[3/3] 최종 리포트 생성 중(LLM)...")
    try:
        report_md = generate_final_report(date_str, rec_data, restaurants)
    except Exception as e:
        print(f"  - 오류 발생: 최종 리포트 생성 실패 ({e})")
        sys.exit(1)

# ==========================================
# 6. 결과 파일 저장 (JSON & Markdown)
# ==========================================
    os.makedirs("results", exist_ok=True)
    
    # 원본 데이터 구조화
    raw_data = {
        "date": date_str,
        "recommendation": rec_data,
        "restaurants": restaurants,
        "errors": all_errors
    }
    
    json_filename = f"results/{date_str}_travel_data.json"
    md_filename = f"results/{date_str}_travel_plan.md"

    # JSON 파일로 저장
    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)

    # 마크다운 리포트 하단에 오류 요약 섹션 추가
    report_md += f"\n\n## 오류 요약(errors)\n```json\n{json.dumps(all_errors, ensure_ascii=False, indent=4)}\n```"

    # Markdown 파일로 저장
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n완료! {md_filename} 및 원본 데이터가 저장되었습니다.")

if __name__ == "__main__":
    main()