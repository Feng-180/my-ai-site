/* 禁术列表自动渲染逻辑 */
const box = document.getElementById("cards");

// 1. 自动从 tools.json 读取所有数据
fetch('tools.json')
  .then(response => response.json())
  .then(data => {
    // 清空旧的三个写死的内容
    box.innerHTML = ""; 
    
    // 2. 循环遍历 JSON 里的每一项 (此时会循环 25 次)
    data.forEach(t => {
      const div = document.createElement("div");
      div.className = "card";
      
      // 这里的 t.title, t.danger 对应你 JSON 里的字段名
      div.innerHTML = `
        <div class="card-tag">${t.danger || 'S'} 级禁术</div>
        <h3>${t.title}</h3>
        <p>危险系数：${t.danger || '未知'}</p>
        <a href="${t.url}" target="_blank">点击解析禁术</a>
      `;
      box.appendChild(div);
    });
  })
  .catch(err => {
    console.error("禁书目录读取失败:", err);
    box.innerHTML = "<p style='color:orange;'>正在重新解析禁术目录...</p>";
  });

/* 背景法阵粒子 - 保持你的原有视觉效果 */
const c = document.getElementById("bg");
const ctx = c.getContext("2d");
let w, h;
function resize() {
  w = c.width = window.innerWidth;
  h = c.height = window.innerHeight;
}
resize();
window.addEventListener("resize", resize);

const dots = Array.from({ length: 90 }, () => ({
  x: Math.random()*w,
  y: Math.random()*h,
  r: Math.random()*2+0.5,
  s: Math.random()*0.3+0.1
}));

function draw() {
  ctx.clearRect(0,0,w,h);
  dots.forEach(d=>{
    d.y -= d.s;
    if(d.y<0) d.y=h;
    ctx.beginPath();
    ctx.arc(d.x,d.y,d.r,0,Math.PI*2);
    ctx.fillStyle="rgba(255,140,60,.45)";
    ctx.fill();
  });
  requestAnimationFrame(draw);
}
draw();