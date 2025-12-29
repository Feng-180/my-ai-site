document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('tools-grid');
    // 使用相对路径读取 json
    fetch('./tools.json')
        .then(res => res.json())
        .then(data => {
            grid.innerHTML = data.map(item => `
                <a href="${item.url}" class="card" target="_blank">
                    <div class="icon">${item.icon}</div>
                    <div class="name">${item.name}</div>
                </a>
            `).join('');
        });
});