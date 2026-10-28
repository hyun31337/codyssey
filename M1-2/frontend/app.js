const API_BASE_URL = "http://localhost:8000";
let currentMessages = [];
let currentConversationId = null; // 현재 선택되거나 진행 중인 대화 ID 관리

window.onload = () => {
    fetchSummary();
    fetchDataList();
    fetchConversations();
    initTabs();
    const dateInput = document.getElementById('inputDate');
    if (dateInput) dateInput.valueAsDate = new Date();
};

function initTabs() {
    const chatBtn = document.getElementById('chatTabBtn');
    const dataBtn = document.getElementById('dataTabBtn');
    const chatSec = document.getElementById('chatSection');
    const dataSec = document.getElementById('dataSection');

    chatBtn.onclick = () => {
        chatBtn.classList.add('active');
        dataBtn.classList.remove('active');
        chatSec.classList.add('active');
        dataSec.classList.remove('active');
    };

    dataBtn.onclick = () => {
        dataBtn.classList.add('active');
        chatBtn.classList.remove('active');
        dataSec.classList.add('active');
        chatSec.classList.remove('active');
    };
}

async function fetchSummary() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/data/summary`);
        const data = await res.json();
        document.getElementById('summaryContent').innerHTML = `
            <p><b>기간:</b> ${data.period}</p>
            <p><b>총 기록:</b> ${data.count}개</p>
            <p><b>평균:</b> ${data.metrics.average} | 최대: ${data.metrics.max}</p>
            <p><b>추세:</b> ${data.trend}</p>
        `;
    } catch (err) {
        document.getElementById('summaryContent').innerText = '요약 정보를 불러오지 못했습니다.';
    }
}

// 새 대화 시작 버튼 함수
function startNewConversation() {
    currentConversationId = null;
    currentMessages = [];
    const chatBox = document.getElementById('chatBox');
    chatBox.innerHTML = '<div class="message ai">새로운 대화가 시작되었습니다. 무엇을 도와드릴까요?</div>';
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const msg = input.value.trim();
    if (!msg) return;

    appendMessage(msg, 'user');
    currentMessages.push({ role: 'user', content: msg });
    input.value = '';

    const chatBox = document.getElementById('chatBox');
    
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai';
    loadingDiv.style.color = '#666';
    loadingDiv.style.fontStyle = 'italic';
    loadingDiv.innerText = 'AI 트레이너가 분석 중입니다...';
    chatBox.appendChild(loadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        const res = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        });

        const data = await res.json();
        loadingDiv.remove();

        if (!res.ok) {
            const errorMsg = data.detail || "알 수 없는 서버 오류가 발생했습니다.";
            appendMessage(`⚠️ [전송 실패] ${errorMsg}`, 'ai');
            return;
        }

        appendMessage(data.reply, 'ai');
        currentMessages.push({ role: 'ai', content: data.reply });

        // 대화 저장 또는 업데이트 실행
        await saveOrUpdateConversation(msg.substring(0, 15) + "...");
        fetchSummary();
    } catch (err) {
        loadingDiv.remove();
        appendMessage(`⚠️ [네트워크 오류] 백엔드 서버 상태를 확인하세요.`, 'ai');
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') sendMessage();
}

function appendMessage(text, sender) {
    const chatBox = document.getElementById('chatBox');
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.innerText = text;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function fetchDataList() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/data`);
        const list = await res.json();
        const tbody = document.getElementById('dataTableBody');
        tbody.innerHTML = '';
        list.forEach(item => {
            tbody.innerHTML += `
                <tr id="row-${item.id}">
                    <td><input type="date" id="date-${item.id}" value="${item.date}" disabled style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px; background:#f9f9f9;"></td>
                    <td><input type="text" id="type-${item.id}" value="${item.exercise_type}" disabled style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px; background:#f9f9f9;"></td>
                    <td><input type="number" step="0.1" id="val-${item.id}" value="${item.value}" disabled style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px; background:#f9f9f9;"></td>
                    <td><input type="text" id="memo-${item.id}" value="${item.memo || ''}" disabled style="width:100%; padding:6px; border:1px solid #ddd; border-radius:4px; background:#f9f9f9;"></td>
                    <td>
                        <button id="edit-btn-${item.id}" onclick="enableEdit('${item.id}')" style="background:#f39c12; color:white; border:none; padding:6px 10px; border-radius:4px; cursor:pointer; margin-right:4px;">수정</button>
                        <button class="delete-btn" onclick="deleteData('${item.id}')">삭제</button>
                    </td>
                </tr>
            `;
        });
    } catch (err) {
        console.error('데이터 조회 실패', err);
    }
}

function enableEdit(id) {
    document.getElementById(`date-${id}`).disabled = false;
    document.getElementById(`type-${id}`).disabled = false;
    document.getElementById(`val-${id}`).disabled = false;
    document.getElementById(`memo-${id}`).disabled = false;

    document.getElementById(`date-${id}`).style.background = "#fff";
    document.getElementById(`type-${id}`).style.background = "#fff";
    document.getElementById(`val-${id}`).style.background = "#fff";
    document.getElementById(`memo-${id}`).style.background = "#fff";

    const btn = document.getElementById(`edit-btn-${id}`);
    btn.innerText = "저장";
    btn.style.background = "#27ae60";
    btn.onclick = () => saveEdit(id);
}

async function saveEdit(id) {
    const payload = {
        date: document.getElementById(`date-${id}`).value,
        exercise_type: document.getElementById(`type-${id}`).value,
        value: parseFloat(document.getElementById(`val-${id}`).value),
        memo: document.getElementById(`memo-${id}`).value
    };

    const res = await fetch(`${API_BASE_URL}/api/data/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        alert("성공적으로 수정되었습니다!");
        fetchDataList();
        fetchSummary();
    } else {
        alert("수정에 실패했습니다.");
    }
}

async function addExerciseData(e) {
    e.preventDefault();
    const payload = {
        date: document.getElementById('inputDate').value,
        exercise_type: document.getElementById('inputExercise').value,
        value: parseFloat(document.getElementById('inputVal').value),
        memo: document.getElementById('inputMemo').value
    };

    const res = await fetch(`${API_BASE_URL}/api/data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        document.getElementById('dataForm').reset();
        document.getElementById('inputDate').valueAsDate = new Date();
        fetchDataList();
        fetchSummary();
    }
}

async function generateDummyData() {
    const res = await fetch(`${API_BASE_URL}/api/data/generate-dummy`, { method: 'POST' });
    const data = await res.json();
    if (res.ok) {
        alert(data.message);
        fetchDataList();
        fetchSummary();
    } else {
        alert("더미 생성 실패");
    }
}

async function deleteData(id) {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    const res = await fetch(`${API_BASE_URL}/api/data/${id}`, { method: 'DELETE' });
    if (res.ok) {
        fetchDataList();
        fetchSummary();
    }
}

// 대화 저장 및 업데이트 함수 (기존 대화면 이어서 누적 저장)
async function saveOrUpdateConversation(title) {
    if (currentMessages.length === 0) return;

    if (currentConversationId) {
        // 💡 이미 존재하는 대화라면 PUT 요청으로 해당 대화 문서 업데이트
        await fetch(`${API_BASE_URL}/api/conversations/${currentConversationId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, messages: currentMessages })
        });
    } else {
        // 💡 처음 시작한 대화라면 POST로 새 대화 생성
        const res = await fetch(`${API_BASE_URL}/api/conversations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title, messages: currentMessages })
        });
        const data = await res.json();
        if (res.ok && data.id) {
            currentConversationId = data.id; // 생성된 ID를 저장하여 다음부터는 이어서 수정함
        }
    }
    fetchConversations();
}

async function fetchConversations() {
    try {
        const res = await fetch(`${API_BASE_URL}/api/conversations`);
        const list = await res.json();
        const ul = document.getElementById('convList');
        ul.innerHTML = '';
        list.forEach(conv => {
            ul.innerHTML += `<li onclick="loadConversation('${conv.id}')">${conv.title}</li>`;
        });
    } catch (err) {
        console.error('대화 목록 조회 실패', err);
    }
}

async function loadConversation(id) {
    try {
        const res = await fetch(`${API_BASE_URL}/api/conversations/${id}`);
        const data = await res.json();
        const chatBox = document.getElementById('chatBox');
        chatBox.innerHTML = '';
        currentConversationId = data.id; // 선택한 대화 ID 지정 (이어서 대화하기 위함)
        currentMessages = data.messages || [];
        currentMessages.forEach(m => appendMessage(m.content, m.role));
    } catch (err) {
        console.error('대화 불러오기 실패', err);
    }
}