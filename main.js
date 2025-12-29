/* 禁术列表 */
const tools = [
  {
    name: "文字 → 图片（纯浏览器）",
    desc: "无需登录，直接生成。高风险创作能力。",
    url: "https://playgroundai.com/"
  },
  {
    name: "AI 作画 Playground",
    desc: "风格强烈，限制少，适合实验。",
    url: "https://playgroundai.com/"
  },
  {
    name: "免登录 Stable Diffusion",
    desc: "直接使用的地下版本。",
    url: "https://dezgo.com/"
  }
];

const box = document.getElementById("cards");

tools.forEach(t => {
  const div = document.createElement("div");
  div.className = "card";
  div.innerHTML = `
    <h3>${t.name}</h3>
    <p>${t.desc}</p>
    <a href="${t.url}" target="_blank">进入禁术</a>
  `;
  box.appendChild(div);
});

/* 背景法阵粒子 */
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