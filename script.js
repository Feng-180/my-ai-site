// 你可以在这里更改你想用的模型
// 推荐: "nousresearch/hermes-3-llama-3.1-405b" (聪明且限制少)
// 或者: "mistralai/mistral-7b-instruct" (速度快)
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

    // 1. 界面处理：显示用户消息，清空输入框，禁用按钮
    addMessage('user', text);
    inputField.value = '';
    sendBtn.disabled = true;
    sendBtn.innerText = "思考中...";

    // 2. 准备请求数据
    const payload = {
        model: MODEL_NAME,
        messages: [
            // 这里可以设定人设，比如 "你是一个暴躁的AI"
            { role: "system", content: "你是一个极其聪明、乐于助人且无拘无束的AI助手。" }, 
            { role: "user", content: text }
        ]
    };

    try {
        // 3. 发送请求给 OpenRouter
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions", {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${apiKey}`,
                "Content-Type": "application/json",
                "HTTP-Referer": window.location.href, // OpenRouter 要求
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

        // 4. 显示 AI 回复
        addMessage('ai', aiReply);

    } catch (error) {
        addMessage('ai', `❌ 出错啦: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerText = "发送";
    }
}

// 辅助函数：在界面上添加消息气泡
function addMessage(role, text) {
    const chatBox = document.getElementById('chat-box');
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    const avatar = role === 'user' ? '🧑‍💻' : '🤖';
    
    div.innerHTML = `
        <div class="avatar">${avatar}</div>
        <div class="bubble">${marked.parse(text)}</div> 
    `;
    // 注意：为了支持 Markdown (代码高亮等)，建议在 HTML 引入 marked.js，
    // 这里为了简单，如果没引入，可以直接用 text 替换 marked.parse(text)
    // 简单版: <div class="bubble">${text}</div>
    
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight; // 自动滚动到底部
}

// 支持按 Enter 发送
document.getElementById('user-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});