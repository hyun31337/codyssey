document.getElementById('submit-btn').addEventListener('click', async () => {
    const date = document.getElementById('travel-date').value;
    const location = document.getElementById('travel-location').value;
    const interest = document.getElementById('travel-interest').value;
    const resultArea = document.getElementById('result-area');

    if (!date) {
        alert('여행 날짜를 선택해 주세요!');
        return;
    }

    resultArea.innerText = 'AI가 실시간 축제 정보를 분석 중입니다... 잠시만 기다려주세요!';

    try {
        const response = await fetch('/api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ date, location, interest })
        });

        const data = await response.json();
        
        if (response.ok) {
            resultArea.innerText = data.recommendation;
        } else {
            resultArea.innerText = '오류 발생: ' + (data.recommendation || '알 수 없는 에러');
        }
    } catch (error) {
        console.error('API 통신 에러:', error);
        resultArea.innerText = '서버 통신 중 오류가 발생했습니다.';
    }
});