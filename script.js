const API_BASE = '/api';
let currentNumberUrl = null;
let refreshInterval = null;

document.addEventListener('DOMContentLoaded', () => {
    loadNumbers();

    document.getElementById('refresh-numbers').addEventListener('click', loadNumbers);
    document.getElementById('close-messages').addEventListener('click', hideMessages);
    document.getElementById('auto-refresh').addEventListener('change', toggleAutoRefresh);
});

async function loadNumbers() {
    const grid = document.getElementById('numbers-grid');
    grid.innerHTML = '<div class="loading">...جاري جلب أحدث الأرقام</div>';
    
    try {
        const response = await fetch(`${API_BASE}/numbers`);
        const numbers = await response.json();
        
        grid.innerHTML = '';
        numbers.forEach(num => {
            const card = document.createElement('div');
            card.className = 'card';
            card.innerHTML = `
                <div class="number">${num.number}</div>
                <div class="country">
                    <span class="badge">${num.country}</span>
                    <span>انقر للعرض</span>
                </div>
            `;
            card.onclick = () => showMessages(num);
            grid.appendChild(card);
        });
    } catch (err) {
        grid.innerHTML = `<div class="error">خطأ في الاتصال بالخادم. تأكد من تشغيل server.py</div>`;
        console.error(err);
    }
}

async function showMessages(num) {
    currentNumberUrl = num.link;
    document.getElementById('current-number').innerText = num.number;
    document.getElementById('messages-section').classList.remove('hidden');
    
    // Copy to clipboard automatically
    navigator.clipboard.writeText(num.number);
    
    loadMessages();
    toggleAutoRefresh(); // Start interval if checked
}

function hideMessages() {
    document.getElementById('messages-section').classList.add('hidden');
    currentNumberUrl = null;
    if (refreshInterval) clearInterval(refreshInterval);
}

async function loadMessages() {
    if (!currentNumberUrl) return;
    
    const list = document.getElementById('messages-list');
    const autoRefresh = document.getElementById('auto-refresh').checked;
    
    if (!autoRefresh) list.innerHTML = '<div class="loading">...جاري التحديث</div>';

    try {
        const response = await fetch(`${API_BASE}/messages?url=${encodeURIComponent(currentNumberUrl)}`);
        const messages = await response.json();
        
        if (messages.length === 0) {
            list.innerHTML = '<div class="empty-state">لا يوجد رسائل بعد. انتظر قليلاً...</div>';
            return;
        }

        list.innerHTML = '';
        messages.forEach(msg => {
            const item = document.createElement('div');
            item.className = 'message-item';
            item.innerHTML = `
                <div class="message-header">
                    <span class="sender">${msg.sender}</span>
                    <span class="time">${msg.time}</span>
                </div>
                <div class="text">${msg.text}</div>
            `;
            list.appendChild(item);
        });
    } catch (err) {
        console.error(err);
    }
}

function toggleAutoRefresh() {
    const isChecked = document.getElementById('auto-refresh').checked;
    if (refreshInterval) clearInterval(refreshInterval);
    
    if (isChecked && currentNumberUrl) {
        refreshInterval = setInterval(loadMessages, 5000); // Poll every 5s
    }
}
