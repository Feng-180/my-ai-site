// AI工具数据示例
const tools = [
  { name: "AI工具1", url: "#", danger: "S" },
  { name: "AI工具2", url: "#", danger: "A" },
  { name: "AI工具3", url: "#", danger: "B" },
  { name: "AI工具4", url: "#", danger: "C" },
  { name: "AI工具5", url: "#", danger: "D" },
  { name: "AI工具6", url: "#", danger: "S" },
  { name: "AI工具7", url: "#", danger: "A" },
  { name: "AI工具8", url: "#", danger: "B" },
  { name: "AI工具9", url: "#", danger: "C" },
  { name: "AI工具10", url: "#", danger: "D" },
  { name: "AI工具11", url: "#", danger: "S" },
  { name: "AI工具12", url: "#", danger: "A" },
  { name: "AI工具13", url: "#", danger: "B" },
  { name: "AI工具14", url: "#", danger: "C" },
  { name: "AI工具15", url: "#", danger: "D" },
  { name: "AI工具16", url: "#", danger: "S" },
  { name: "AI工具17", url: "#", danger: "A" },
  { name: "AI工具18", url: "#", danger: "B" },
  { name: "AI工具19", url: "#", danger: "C" },
  { name: "AI工具20", url: "#", danger: "D" },
  { name: "AI工具21", url: "#", danger: "S" },
  { name: "AI工具22", url: "#", danger: "A" },
  { name: "AI工具23", url: "#", danger: "B" },
  { name: "AI工具24", url: "#", danger: "C" }
];

// 动态生成卡片
const cardsContainer = document.getElementById('cardsContainer');

tools.forEach(tool => {
  const card = document.createElement('div');
  card.className = 'card';
  if(tool.danger) card.classList.add(`danger-${tool.danger}`);
  card.innerHTML = `
    <div class="tool-name">${tool.name}</div>
    <a href="${tool.url}" target="_blank">打开工具</a>
  `;
  cardsContainer.appendChild(card);
});

// 背景粒子效果
const canvas = document.getElementById('bgCanvas');
const ctx = canvas.getContext('2d');
let w = canvas.width = window.innerWidth;
let h = canvas.height = window.innerHeight;

window.addEventListener('resize', () => {
  w = canvas.width = window.innerWidth;
  h = canvas.height = window.innerHeight;
});

const particles = [];
for(let i=0;i<80;i++){
  particles.push({
    x: Math.random()*w,
    y: Math.random()*h,
    r: Math.random()*2+1,
    dx: (Math.random()-0.5)*0.5,
    dy: (Math.random()-0.5)*0.5
  });
}

function draw(){
  ctx.clearRect(0,0,w,h);
  particles.forEach(p=>{
    ctx.beginPath();
    ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle='rgba(255,255,255,0.6)';
    ctx.fill();
    p.x += p.dx;
    p.y += p.dy;
    if(p.x<0||p.x>w) p.dx*=-1;
    if(p.y<0||p.y>h) p.dy*=-1;
  });
  requestAnimationFrame(draw);
}
draw();

// 光圈跟随鼠标/手指
document.addEventListener('mousemove', e=>{
  const circle = document.createElement('div');
  circle.style.position='fixed';
  circle.style.width='20px';
  circle.style.height='20px';
  circle.style.border='2px solid #ff66cc';
  circle.style.borderRadius='50%';
  circle.style.left=`${e.clientX-10}px`;
  circle.style.top=`${e.clientY-10}px`;
  circle.style.pointerEvents='none';
  circle.style.zIndex='0';
  document.body.appendChild(circle);
  setTimeout(()=>{circle.remove();},500);
});

document.addEventListener('touchmove', e=>{
  const touch = e.touches[0];
  const circle = document.createElement('div');
  circle.style.position='fixed';
  circle.style.width='20px';
  circle.style.height='20px';
  circle.style.border='2px solid #ff66cc';
  circle.style.borderRadius='50%';
  circle.style.left=`${touch.clientX-10}px`;
  circle.style.top=`${touch.clientY-10}px`;
  circle.style.pointerEvents='none';
  circle.style.zIndex='0';
  document.body.appendChild(circle);
  setTimeout(()=>{circle.remove();},500);
});