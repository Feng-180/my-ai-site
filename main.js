document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('tools-grid');

    // 加上随机数后缀打破缓存，确保它读取你最新的 JSON
    fetch('./tools.json?v=' + Date.now())
        .then(response => response.json())
        .then(data => {
            grid.innerHTML = data.map(tool => `
                <a href="${tool.url}" class="card" target="_blank">
                    <div class="icon">${tool.danger === 'S' ? '🔥' : '🔮'}</div>
                    <div class="name">${tool.title}</div>
                </a>
            `).join('');
        })
        .catch(err => {
            console.error('加载失败:', err);
            grid.innerHTML = '<p style="color:white;text-align:center;">禁术目录加载中，请稍后...</p>';
        });
});