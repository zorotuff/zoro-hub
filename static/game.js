"use strict";

/* ==============================
   ZORO HUB - GAME.JS
   Part 1
   Core + Animated Background
============================== */
document.body.classList.add("page-show");

document.addEventListener("DOMContentLoaded", () => {

    initParticles();
    initMouseGlow();
});




/* ==============================
      PARTICLE BACKGROUND
============================== */

const canvas = document.getElementById("bgCanvas");

if(canvas){

const ctx = canvas.getContext("2d");

let particles = [];
const PARTICLE_COUNT = 90;

function resizeCanvas(){

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

}

resizeCanvas();

window.addEventListener("resize", resizeCanvas);



class Particle{

    constructor(){

        this.reset();

    }

    reset(){

        this.x = Math.random()*canvas.width;
        this.y = Math.random()*canvas.height;

        this.radius = Math.random()*2.5+1;

        this.speedX = (Math.random()-0.5)*0.5;
        this.speedY = (Math.random()-0.5)*0.5;

        this.alpha = Math.random()*0.5+0.2;

    }

    update(){

        this.x += this.speedX;
        this.y += this.speedY;

        if(this.x<0) this.x=canvas.width;
        if(this.x>canvas.width) this.x=0;

        if(this.y<0) this.y=canvas.height;
        if(this.y>canvas.height) this.y=0;

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

        ctx.fillStyle=`rgba(120,180,255,${this.alpha})`;

        ctx.fill();

    }

}



function initParticles(){

    particles=[];

    for(let i=0;i<PARTICLE_COUNT;i++){

        particles.push(new Particle());

    }

    animateParticles();

}



function animateParticles(){

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

    connectParticles();

    requestAnimationFrame(
        animateParticles
    );

}



/* ==============================
     PARTICLE CONNECTIONS
============================== */

function connectParticles(){

    for(let a=0;a<particles.length;a++){

        for(let b=a+1;b<particles.length;b++){

            const dx=particles[a].x-particles[b].x;
            const dy=particles[a].y-particles[b].y;

            const dist=Math.sqrt(dx*dx+dy*dy);

            if(dist<130){

                ctx.beginPath();

                ctx.moveTo(
                    particles[a].x,
                    particles[a].y
                );

                ctx.lineTo(
                    particles[b].x,
                    particles[b].y
                );

                ctx.strokeStyle=`rgba(120,180,255,${
                    (130-dist)/500
                })`;

                ctx.lineWidth=1;

                ctx.stroke();

            }

        }

    }

}



/* ==============================
      MOUSE GLOW
============================== */

const mouse={

    x:0,
    y:0

};

window.addEventListener("mousemove",(e)=>{

    mouse.x=e.clientX;
    mouse.y=e.clientY;

});



function initMouseGlow(){

    function glow(){

        ctx.beginPath();

        ctx.arc(
            mouse.x,
            mouse.y,
            120,
            0,
            Math.PI*2
        );

        const gradient=ctx.createRadialGradient(

            mouse.x,
            mouse.y,
            0,

            mouse.x,
            mouse.y,
            120

        );

        gradient.addColorStop(
            0,
            "rgba(0,180,255,.12)"
        );

        gradient.addColorStop(
            1,
            "rgba(0,180,255,0)"
        );

        ctx.fillStyle=gradient;

        ctx.fill();

        requestAnimationFrame(glow);

    }

    glow();

}

/* ==============================
   ZORO HUB - GAME.JS
   Part 2
   UI Animations
============================== */

document.addEventListener("DOMContentLoaded",()=>{

    initPlayButton();

    initHistoryCards();

    initHearts();

    initHintButton();

});

/* ==============================
        PLAY BUTTON
============================== */

function initPlayButton(){

    const form=document.getElementById("guessForm");
    const btn=document.getElementById("guessButton");

    if(!form||!btn)return;

    form.addEventListener("submit",(e)=>{

        e.preventDefault();

        btn.disabled=true;

        btn.classList.add("clicked");

        btn.innerHTML="🎯 Guessing...";

        btn.animate([

            {
                transform:"scale(1)"
            },

            {
                transform:"scale(.92)"
            },

            {
                transform:"scale(1.08)"
            },

            {
                transform:"scale(1)"
            }

        ],{

            duration:450,

            easing:"ease"

        });

        setTimeout(()=>{

            form.submit();

        },450);

    });

}



/* ==============================
      HISTORY CARDS
============================== */

function initHistoryCards(){

    const cards=document.querySelectorAll(".history-card");

    cards.forEach((card,index)=>{

        card.style.opacity="0";

        card.style.transform="translateY(40px)";

        setTimeout(()=>{

            card.style.transition=".5s ease";

            card.style.opacity="1";

            card.style.transform="translateY(0px)";

        },index*90);

    });

}



/* ==============================
        HEARTS
============================== */

function initHearts(){

    const hearts=document.querySelectorAll(".heart");

    hearts.forEach((heart,index)=>{

        heart.animate([

            {

                transform:"scale(1)"

            },

            {

                transform:"scale(1.3)"

            },

            {

                transform:"scale(1)"

            }

        ],{

            duration:800,

            delay:index*120,

            iterations:1

        });

    });

}



/* ==============================
       HINT BUTTON
============================== */

function initHintButton(){

    const hint=document.querySelector(

        'button[value="hint"]'

    );

    if(!hint)return;

    hint.addEventListener("mouseenter",()=>{

        hint.animate([

            {

                transform:"rotate(-2deg)"

            },

            {

                transform:"rotate(2deg)"

            },

            {

                transform:"rotate(0deg)"

            }

        ],{

            duration:400

        });

    });

}



/* ==============================
      BUTTON HOVER GLOW
============================== */

document.querySelectorAll("button").forEach(btn=>{

    btn.addEventListener("mousemove",(e)=>{

        const rect=btn.getBoundingClientRect();

        btn.style.setProperty(

            "--x",

            `${e.clientX-rect.left}px`

        );

        btn.style.setProperty(

            "--y",

            `${e.clientY-rect.top}px`

        );

    });

});



/* ==============================
      SMOOTH SCROLL
============================== */

window.scrollTo({

    top:0,

    behavior:"smooth"

});

/* ===================================
        PART 3
=================================== */

document.addEventListener("DOMContentLoaded",()=>{

    createCursorTrail();

    buttonRipples();

    wrongGuessShake();

    floatingParticles();

});



/* =========================
    CURSOR TRAIL
========================= */

function createCursorTrail(){

    document.addEventListener("mousemove",(e)=>{

        const dot=document.createElement("div");

        dot.className="cursor-particle";

        dot.style.left=e.clientX+"px";

        dot.style.top=e.clientY+"px";

        document.body.appendChild(dot);

        setTimeout(()=>{

            dot.remove();

        },600);

    });

}



/* =========================
      BUTTON RIPPLE
========================= */

function buttonRipples(){

    document.querySelectorAll("button").forEach(btn=>{

        btn.addEventListener("click",(e)=>{

            const ripple=document.createElement("span");

            ripple.className="ripple";

            ripple.style.left=e.offsetX+"px";

            ripple.style.top=e.offsetY+"px";

            btn.appendChild(ripple);

            setTimeout(()=>{

                ripple.remove();

            },700);

        });

    });

}



/* =========================
    WRONG GUESS SHAKE
========================= */

function wrongGuessShake(){

    const msg=document.querySelector(".message");

    if(!msg)return;

    if(

        msg.innerText.includes("Higher") ||

        msg.innerText.includes("Lower")

    ){

        document.querySelector(".hero-card")?.animate([

            {transform:"translateX(0px)"},

            {transform:"translateX(-12px)"},

            {transform:"translateX(12px)"},

            {transform:"translateX(-8px)"},

            {transform:"translateX(8px)"},

            {transform:"translateX(0px)"}

        ],{

            duration:450

        });

    }

}



/* =========================
 FLOATING PARTICLES
========================= */

function floatingParticles(){

    for(let i=0;i<15;i++){

        const p=document.createElement("div");

        p.className="bg-particle";

        p.style.left=Math.random()*100+"vw";

        p.style.animationDelay=Math.random()*8+"s";

        p.style.animationDuration=(6+Math.random()*6)+"s";

        document.body.appendChild(p);

    }

}

/* =====================================
        PART 4
===================================== */

document.addEventListener("DOMContentLoaded",()=>{

    electricTitle();

    animateXP();

    heartExplosion();

    pageFlash();

});



/* ==========================
   TITLE ELECTRIC EFFECT
========================== */

function electricTitle(){

    const title=document.querySelector("h1");

    if(!title) return;

    title.animate(

        [

            {
                textShadow:"0 0 10px #4ea8ff"
            },

            {
                textShadow:"0 0 35px #9d4edd"
            },

            {
                textShadow:"0 0 10px #4ea8ff"
            }

        ],

        {

            duration:2500,

            iterations:Infinity

        }

    );

}






/* ==========================
 HEART LOSS EXPLOSION
========================== */

function heartExplosion(){

    const hearts=document.querySelectorAll(".heart");

    hearts.forEach(heart=>{

        heart.addEventListener("animationend",()=>{

            heart.animate([

                {

                    transform:"scale(1)"

                },

                {

                    transform:"scale(1.6) rotate(20deg)"

                },

                {

                    transform:"scale(.8)"

                },

                {

                    transform:"scale(1)"

                }

            ],{

                duration:900,

            });

        });

    });

}



/* ==========================
 PAGE FLASH
========================== */

function pageFlash(){

    const msg=document.body.innerText;

    if(msg.includes("Congratulations")){

        flash("#00ff88");

        confetti();

    }

    if(msg.includes("Game Over")){

        flash("#ff0033");

    }

}



function flash(color){

    const div=document.createElement("div");

    div.style.position="fixed";

    div.style.inset="0";

    div.style.background=color;

    div.style.opacity=".3";

    div.style.pointerEvents="none";

    div.style.zIndex="999999";

    document.body.appendChild(div);

    div.animate([

        {opacity:.35},

        {opacity:0}

    ],{

        duration:1200,

    });

    setTimeout(()=>{

        div.remove();

    },700);

}



/* ==========================
 CONFETTI
========================== */

function confetti(){

    for(let i=0;i<120;i++){

        const c=document.createElement("div");

        c.className="confetti";

        c.style.left=Math.random()*100+"vw";

        c.style.background=

        `hsl(${Math.random()*360},100%,60%)`;

        c.style.animationDelay=Math.random()+"s";

        document.body.appendChild(c);

        setTimeout(()=>{

            c.remove();

        },3000);

    }

}

/* ===================================
        PART 5
=================================== */

document.addEventListener("DOMContentLoaded",()=>{

    parallaxBackground();

    magneticButtons();

    pageTransition();

});



/* ======================
    3D PARALLAX
====================== */

function parallaxBackground(){

    document.addEventListener("mousemove",(e)=>{

        const x=(e.clientX/window.innerWidth-.5)*20;

        const y=(e.clientY/window.innerHeight-.5)*20;

        const wrapper=document.querySelector(".game-wrapper");

        if(wrapper){

            wrapper.style.transform=
            `rotateY(${x*.15}deg)
             rotateX(${-y*.15}deg)`;

        }

    });

}



/* ======================
MAGNETIC BUTTON
====================== */

function magneticButtons(){

    document.querySelectorAll("button").forEach(btn=>{

        btn.addEventListener("mousemove",(e)=>{

            const rect=btn.getBoundingClientRect();

            const x=e.clientX-rect.left-rect.width/2;

            const y=e.clientY-rect.top-rect.height/2;

            btn.style.transform=
            `translate(${x*.12}px,${y*.12}px) scale(1.05)`;

        });

        btn.addEventListener("mouseleave",()=>{

            btn.style.transform="translate(0,0) scale(1)";

        });

    });

}



/* ======================
PAGE FADE
====================== */

function pageTransition(){

    document.body.classList.add("page-show");

    document.querySelectorAll("a").forEach(link=>{

        link.addEventListener("click",(e)=>{

            if(link.target=="_blank") return;

            e.preventDefault();

            document.body.classList.add("page-hide");

            setTimeout(()=>{

                window.location=link.href;

            },350);

        });

    });

}

function showLevelUp(level){

    const popup=document.createElement("div");

    popup.className="level-popup";

    popup.innerHTML=`🏆 LEVEL ${level}`;

    document.body.appendChild(popup);

    setTimeout(()=>{

        popup.remove();

    },2500);

}}