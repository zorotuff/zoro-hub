/* ==========================================
        ZORO HUB V5 PARTICLE ENGINE
========================================== */

const canvas = document.getElementById("bgCanvas");

if(canvas){

const ctx = canvas.getContext("2d");

function resize(){

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

}

resize();

window.addEventListener("resize", resize);

const particles = [];

const mouse={

x:window.innerWidth/2,
y:window.innerHeight/2

};

window.addEventListener("mousemove",(e)=>{

mouse.x=e.clientX;
mouse.y=e.clientY;

});

const PARTICLE_COUNT = 90;

class Particle{

constructor(){

this.reset();

}

reset(){

this.x = Math.random()*canvas.width;
this.y = Math.random()*canvas.height;

this.radius = Math.random()*2+1;

this.vx = (Math.random()-0.5)*0.35;
this.vy = (Math.random()-0.5)*0.35;

this.alpha = Math.random()*0.6+0.2;

}

update(){

const dx=this.x-mouse.x;
const dy=this.y-mouse.y;

const dist=Math.sqrt(dx*dx+dy*dy);

if(dist<140){

const force=(140-dist)/140;

this.x+=(dx/dist)*force*1.8;
this.y+=(dy/dist)*force*1.8;

}

this.x+=this.vx;
this.y+=this.vy;

if(this.x<0)this.x=canvas.width;
if(this.x>canvas.width)this.x=0;

if(this.y<0)this.y=canvas.height;
if(this.y>canvas.height)this.y=0;

}

draw(){

ctx.beginPath();

ctx.arc(
this.x,
this.y,
this.radius,
0,
Math.PI*2
);

ctx.fillStyle=`rgba(110,170,255,${this.alpha})`;

ctx.fill();

}

}

for(let i=0;i<PARTICLE_COUNT;i++){

particles.push(new Particle());

}

function connect(){

for(let i=0;i<particles.length;i++){

for(let j=i+1;j<particles.length;j++){

const dx=particles[i].x-particles[j].x;
const dy=particles[i].y-particles[j].y;

const dist=Math.sqrt(dx*dx+dy*dy);

if(dist<140){

ctx.beginPath();

ctx.moveTo(
particles[i].x,
particles[i].y
);

ctx.lineTo(
particles[j].x,
particles[j].y
);

ctx.strokeStyle=
`rgba(110,170,255,${0.18-(dist/900)})`;

ctx.lineWidth=1;

ctx.stroke();

}

}

}

}

function animate(){

ctx.clearRect(
0,
0,
canvas.width,
canvas.height
);

particles.forEach(p=>{

p.update();

p.draw();

});

connect();

requestAnimationFrame(animate);

}

animate();

}

/* ==========================================
            MOUSE GLOW
========================================== */

const glow=document.getElementById("mouseGlow");

let mx=window.innerWidth/2;
let my=window.innerHeight/2;

let gx=mx;
let gy=my;

window.addEventListener("mousemove",(e)=>{

mx=e.clientX;
my=e.clientY;

});

function animateGlow(){

gx+=(mx-gx)*0.08;
gy+=(my-gy)*0.08;

if(glow){

glow.style.left=gx+"px";
glow.style.top=gy+"px";

}

requestAnimationFrame(animateGlow);

}

animateGlow();

/* ==========================================
          SHOOTING STARS
========================================== */

const stars=document.getElementById("shootingStars");

function createStar(){

if(!stars)return;

const star=document.createElement("div");

star.className="shooting-star";

star.style.left=Math.random()*window.innerWidth+"px";

star.style.top=Math.random()*250+"px";

star.style.animationDuration=

(1.2+Math.random()*1.3)+"s";

stars.appendChild(star);

setTimeout(()=>{

star.remove();

},2600);

}

setInterval(()=>{

createStar();

},2500);