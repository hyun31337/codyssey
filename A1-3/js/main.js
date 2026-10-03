async function getFestivalRecommendations() {
    const dateInput = document.getElementById('trip-date').value;
    const locationInput = document.getElementById('trip-location').value;
    const interestInput = document.getElementById('trip-interest').value;
    
    const resultContainer = document.getElementById('result-container');
    const resultContent = document.getElementById('result-content');

    // 1. 실패 처리: 빈 입력 검사 (필수값 누락)
    if (!dateInput) {
        alert("여행 날짜는 필수 입력 항목입니다. 날짜를 선택해주세요.");
        return;
    }

    // UI 초기화 및 로딩 표시 (지연/타임아웃 대비 안내)
    resultContainer.classList.remove('hidden');
    resultContent.innerHTML = "⏳ AI가 해당 주간의 멋진 축제 정보를 분석 중입니다. 잠시만 기다려주세요...";

    try {
        // 백엔드(Vercel Serverless Function)로 요청 전송
        const response = await fetch('/api/index', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                date: dateInput,
                location: locationInput,
                interest: interestInput
            })
        });

        // 2. 실패 처리: API 서버 오류 (4xx / 5xx)
        if (!response.ok) {
            throw new Error(`서버 응답 오류 (상태 코드: ${response.status})`);
        }

        const data = await response.json();
        
        // 성공 시 결과 렌더링
        resultContent.innerHTML = `<p style="white-space: pre-line;">${data.recommendation}</p>`;

    } catch (error) {
        console.error("Error:", error);
        // 3. 실패 처리: 통신 오류 또는 예외 발생 시 안내 메시지
        resultContent.innerHTML = "❌ 현재 축제 정보를 불러오는 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.";
    }
}