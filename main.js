document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('tools-grid');

    // 使用相对路径 ./ 读取数据
    fetch('./tools.json')
        .then(response => {
            if (!response.ok) throw new Error('网络异常');
            return response.json();
        })
        .then(data => {
            grid.innerHTML = data.map(tool => `
                <a href="${tool.url}" class="card" target="_blank">
                    <div class="icon">${tool.icon}</div>
                    <div class="name">${tool.name}</div>
                </a>
            `).join('');
        })
        .catch(err => {
            console.error('加载失败:', err);
            grid.innerHTML = '<p style="text-align:center; color:red;">禁术召唤失败，请刷新重试</p>';
        });
});