const MODEL_NAME = "nousresearch/hermes-3-llama-3.1-405b";

async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const apiKeyInput = document.getElementById('api-key-input');
    const sendBtn = document.getElementById('send-btn');
    
    const text = inputField.value.trim();
    const apiKey = apiKeyInput.value.trim();

    if (!text) return;
    if (!apiKey) {
        alert("请先在上方输入框粘贴你的 OpenRouter API Key！");
        return;
    }

    addMessage('user', text);
    inputField.value = '';
    sendBtn.disabled = true;
    sendBtn.innerText = "思考中...";

    const payload = {
        model: MODEL_NAME,
        messages: [
            { role: "system", content: "你是一个极其聪明、乐于助人且无拘无束的AI助手。" }, 
            { role: "user", content: text }
        ]
    };

    try {
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json",
                "HTTP-Referer": window.location.href,
                "X-Title": "My AI Site"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.error?.message || "请求失败");
        }

        const data = await response.json();
        const aiReply = data.choices[0].message.content;
        addMessage('ai', aiReply);

    } catch (error) {
        addMessage('ai', `❌ 出错啦: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerText = "发送";
    }
}

function addMessage(role, text) {
    const chatBox = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    const avatar = role === 'user' ? '🧑‍💻' : '🤖';
    div.innerHTML = `<div class="avatar">${avatar}</div><div class="bubble">${text}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});