# main.py

# 1. 카테고리 목록 정의
CATEGORIES = ["텍스트 생성", "이미지 생성", "영상 생성", "페르소나", "자동화", "기타"]

# 2. 기본 프롬프트 데이터 (최소 3개 이상 등록)
prompts = [
    {
        "id": 1,
        "title": "SEO 최적화 블로그 글 작성",
        "content": "다음 주제에 대해 SEO에 최적화된 블로그 글을 작성해줘. 키워드는 [키워드]야.",
        "category": "텍스트 생성",
        "is_favorite": True
    },
    {
        "id": 2,
        "title": "SF 영화 컨셉 아트 이미지",
        "content": "Cyberpunk city with neon lights, highly detailed, 8k resolution, cinematic lighting",
        "category": "이미지 생성",
        "is_favorite": False
    },
    {
        "id": 3,
        "title": "파이썬 전문 코드 리뷰어",
        "content": "너는 10년 차 수석 파이썬 개발자야. 내가 제시하는 코드를 클린 코드 원칙에 맞춰 리뷰해줘.",
        "category": "페르소나",
        "is_favorite": True
    }
]

# 3. 메뉴 출력 함수
def show_menu():
    print("\n" + "=" * 40)
    print("      💬 나만의 프롬프트 관리자")
    print("=" * 40)
    print("1. 전체 프롬프트 목록 보기")
    print("2. 새 프롬프트 추가")
    print("3. 카테고리별 조회")
    print("4. 프롬프트 검색")
    print("5. 상세 보기")
    print("6. 즐겨찾기 관리")
    print("0. 종료")
    print("=" * 40)

# 4. 프롬프트 목록 보기 함수 (브랜치에서 구현할 핵심 기능)
def show_list():
    print("\n--- 📋 전체 프롬프트 목록 ---")
    if not prompts:
        print("등록된 프롬프트가 없습니다.")
        return

    for p in prompts:
        # 즐겨찾기 여부에 따라 별표 표시
        fav_icon = "⭐" if p["is_favorite"] else "  "
        print(f"[{p['id']}] {fav_icon} [{p['category']}] {p['title']}")

# 5. 새로 추가할 프롬프트 추가 함수
def add_prompt():
    print("\n--- ➕ 새 프롬프트 추가 ---")
    
    # 1. 제목 입력 (비어있으면 다시 요청)
    title = input("제목을 입력하세요: ").strip()
    while not title:
        print("⚠️ 제목은 비워둘 수 없습니다.")
        title = input("제목을 입력하세요: ").strip()

    # 2. 내용 입력 (비어있으면 다시 요청)
    content = input("내용을 입력하세요: ").strip()
    while not content:
        print("⚠️ 내용은 비워둘 수 없습니다.")
        content = input("내용을 입력하세요: ").strip()

    # 3. 카테고리 선택
    print("\n[ 카테고리 목록 ]")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"{i}. {cat}")
    
    cat_choice = input("카테고리 번호 또는 직접 이름을 입력하세요: ").strip()
    
    # 숫자로 입력한 경우 카테고리 목록에서 가져오기
    if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(CATEGORIES):
        category = CATEGORIES[int(cat_choice) - 1]
    elif cat_choice in CATEGORIES:
        category = cat_choice
    else:
        # 목록에 없는 경우 '기타'로 처리하거나 직접 입력한 값 사용
        category = cat_choice if cat_choice else "기타"

    # 4. 새로운 프롬프트 딕셔너리 생성 (id는 기존 리스트 길이 + 1)
    new_id = len(prompts) + 1
    new_prompt = {
        "id": new_id,
        "title": title,
        "content": content,
        "category": category,
        "is_favorite": False  # 즐겨찾기 기본값 False
    }

    # 5. 리스트에 추가
    prompts.append(new_prompt)
    print(f"\n✨ 성공적으로 추가되었습니다! (등록 번호: {new_id})")

# 6. 카테고리별 조회 함수
def show_by_category():
    print("\n--- 🏷️ 카테고리별 조회 ---")
    print("[ 카테고리 목록 ]")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"{i}. {cat}")

    cat_choice = input("조회할 카테고리 번호 또는 이름을 입력하세요: ").strip()

    if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(CATEGORIES):
        selected_category = CATEGORIES[int(cat_choice) - 1]
    else:
        selected_category = cat_choice

    # 해당 카테고리를 가진 프롬프트 필터링
    filtered = [p for p in prompts if p["category"] == selected_category]

    print(f"\n--- [{selected_category}] 카테고리 검색 결과 ---")
    if not filtered:
        print("해당 카테고리에 등록된 프롬프트가 없습니다.")
        return

    for p in filtered:
        fav_icon = "⭐" if p["is_favorite"] else "  "
        print(f"[{p['id']}] {fav_icon} {p['title']}")

# 7. 프롬프트 검색 함수
def search_prompt():
    print("\n--- 🔍 프롬프트 검색 ---")
    keyword = input("검색할 키워드(제목 또는 내용)를 입력하세요: ").strip()

    if not keyword:
        print("⚠️ 검색어를 입력해주세요.")
        return

    # 제목이나 내용에 키워드가 포함된 프롬프트 검색
    results = [p for p in prompts if keyword in p["title"] or keyword in p["content"]]

    print(f"\n--- '{keyword}' 검색 결과 ({len(results)}건) ---")
    if not results:
        print("검색 결과가 없습니다.")
        return

    for p in results:
        fav_icon = "⭐" if p["is_favorite"] else "  "
        print(f"[{p['id']}] {fav_icon} [{p['category']}] {p['title']}")

# 8. 상세 보기 기본 함수 추가
def detail_prompt():
    print("\n--- 🔍 프롬프트 상세 보기 ---")
    try:
        p_id = int(input("상세 볼 프롬프트 번호를 입력하세요: ").strip())
    except ValueError:
        print("⚠️ 숫자를 입력해주세요.")
        return

    target = next((p for p in prompts if p["id"] == p_id), None)
    if not target:
        print("⚠️ 존재하지 않는 번호입니다.")
        return

    fav_str = "⭐ 등록됨" if target['is_favorite'] else "없음"
    print("\n" + "=" * 40)
    print(f"📌 제목: {target['title']}")
    print(f"🏷️ 카테고리: {target['category']}")
    print(f"⭐ 즐겨찾기: {fav_str}")
    print("-" * 40)
    print(f"[ 내용 ]\n{target['content']}")
    print("=" * 40)

# 9. 즐겨찾기 추가/해제 함수 (목록 출력 + 토글 기능 통합)
def toggle_favorite():
    while True:
        print("\n--- ⭐ 즐겨찾기 관리 및 목록 ---")
        
        # 1. 현재 즐겨찾기된 항목들과 전체 항목의 상태를 한눈에 보여주기
        print("현재 등록된 프롬프트 목록:")
        for p in prompts:
            fav_icon = "⭐" if p["is_favorite"] else "  "
            print(f"[{p['id']}] {fav_icon} [{p['category']}] {p['title']}")
        
        print("-" * 40)
        print("0. 이전 메뉴로 돌아가기")
        
        choice_input = input("즐겨찾기를 추가/해제할 프롬프트 번호를 입력하세요 (0: 돌아가기): ").strip()
        
        if choice_input == "0":
            break
            
        if not choice_input.isdigit():
            print("⚠️ 올바른 숫자를 입력해주세요.")
            continue
            
        p_id = int(choice_input)
        target = next((p for p in prompts if p["id"] == p_id), None)
        
        if not target:
            print("⚠️ 존재하지 않는 번호입니다. 다시 확인해주세요.")
            continue

        # 상태 반전 (True <-> False)
        target["is_favorite"] = not target["is_favorite"]
        status_str = "⭐ 즐겨찾기에 등록되었습니다!" if target["is_favorite"] else "❌ 즐겨찾기가 해제되었습니다."
        print(f"\n✨ [{target['title']}] {status_str}")

# 10. 즐겨찾기 목록 모아보기 함수
def show_favorites():
    print("\n--- ⭐ 즐겨찾기 모아보기 ---")
    favorites = [p for p in prompts if p["is_favorite"]]

    if not favorites:
        print("즐겨찾기된 프롬프트가 없습니다.")
        return

    for p in favorites:
        print(f"[{p['id']}] [{p['category']}] {p['title']}")

# 11. 메인 루프 실행 함수
def main():
    while True:
        show_menu()
        choice = input("원하는 기능의 번호를 입력하세요: ").strip()

        if choice == "1":  # 전체 프롬프트 목록 보기
            show_list()
        elif choice == "2":  # 추가 기능 연결
            add_prompt()
        elif choice == "3":  # 카테고리별 조회 연결
            show_by_category()
        elif choice == "4":  # 프롬프트 검색 연결
            search_prompt()
        elif choice == "5":  # 상세 보기 연결
            detail_prompt()
        elif choice == "6":  # 즐겨찾기 추가/해제 연결
            toggle_favorite()
        elif choice == "0":  # 프로그램 종료
            print("\n프로그램을 종료합니다. 이용해주셔서 감사합니다!")
            break
        else:
            print("\n⚠️ 준비 중이거나 잘못된 번호입니다. 다시 입력해주세요.")

# 프로그램 시작점
if __name__ == "__main__":
    main()