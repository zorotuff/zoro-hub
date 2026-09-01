"use strict";

/* ==========================================
        ZORO HUB - Guess The Number V2
                PART 1
========================================== */

document.addEventListener("DOMContentLoaded", () => {

    initBackground();

    initMouseGlow();

    initCursorTrail();

    initButtons();

});

/* ==========================================
            PARTICLE BACKGROUND
========================================== */

function initBackground(){

    const bg = document.querySelector(".background");

    if(!bg) return;

    for(let i=0;i<45;i++){

        const p = document.createElement("div");

        p.className = "bgParticle";

        p.style.left = Math.random()*100 + "vw";

        p.style.top = Math.random()*100 + "vh";

        p.style.animationDuration =
            (8 + Math.random()*12) + "s";

        p.style.animationDelay =
            Math.random()*5 + "s";

        p.style.opacity =
            0.15 + Math.random()*0.35;

        p.style.transform =
            `scale(${0.5+Math.random()*1.8})`;

        bg.appendChild(p);

    }

}

/* ==========================================
                MOUSE GLOW
========================================== */

function initMouseGlow(){

    const glow = document.createElement("div");

    glow.className = "mouseGlow";

    document.body.appendChild(glow);

    document.addEventListener("mousemove",(e)=>{

        glow.style.left = e.clientX + "px";

        glow.style.top = e.clientY + "px";

    });

}

/* ==========================================
                CURSOR TRAIL
========================================== */

function initCursorTrail(){

    document.addEventListener("mousemove",(e)=>{

        const dot = document.createElement("div");

        dot.className = "cursorDot";

        dot.style.left = e.clientX + "px";

        dot.style.top = e.clientY + "px";

        document.body.appendChild(dot);

        setTimeout(()=>{

            dot.remove();

        },500);

    });

}

/* ==========================================
                BUTTON EFFECTS
========================================== */

function initButtons(){

    document.querySelectorAll("button").forEach(btn=>{

        btn.addEventListener("mousemove",(e)=>{

            const rect = btn.getBoundingClientRect();

            btn.style.setProperty(
                "--mx",
                `${e.clientX-rect.left}px`
            );

            btn.style.setProperty(
                "--my",
                `${e.clientY-rect.top}px`
            );

        });

    });

}

/* ==========================================
                PART 2
========================================== */

document.addEventListener("DOMContentLoaded",()=>{

    animateGuessButton();

    animateHintButton();

    animateHearts();

    revealHistory();

});

/* ==========================================
            GUESS BUTTON
========================================== */

function animateGuessButton(){

    const form=document.querySelector(".guessForm");

    const btn=form?.querySelector("button");

    if(!form||!btn) return;

    form.addEventListener("submit",()=>{

        btn.disabled=true;

        btn.innerHTML="⏳ Guessing...";

        btn.animate([

            {transform:"scale(1)"},

            {transform:"scale(.92)"},

            {transform:"scale(1.08)"},

            {transform:"scale(1)"}

        ],{

            duration:450,

            easing:"ease"

        });

    });

}

/* ==========================================
            HINT BUTTON
========================================== */

function animateHintButton(){

    const hint=document.querySelector(".hintBtn");

    if(!hint) return;

    hint.addEventListener("mouseenter",()=>{

        hint.animate([

            {transform:"rotate(-2deg)"},

            {transform:"rotate(2deg)"},

            {transform:"rotate(0deg)"}

        ],{

            duration:350

        });

    });

}

/* ==========================================
            HEARTS
========================================== */

function animateHearts(){

    const hearts=document.querySelectorAll(".hearts span");

    hearts.forEach((heart,index)=>{

        if(heart.classList.contains("dead")) return;

        setTimeout(()=>{

            heart.animate([

                {transform:"scale(1)"},

                {transform:"scale(1.22)"},

                {transform:"scale(1)"}

            ],{

                duration:800,

                iterations:Infinity

            });

        },index*120);

    });

}

/* ==========================================
        HISTORY REVEAL
========================================== */

function revealHistory(){

    const cards=document.querySelectorAll(".historyItem");

    cards.forEach((card,index)=>{

        card.style.opacity="0";

        card.style.transform="translateY(30px)";

        setTimeout(()=>{

            card.style.transition=".45s ease";

            card.style.opacity="1";

            card.style.transform="translateY(0px)";

        },index*80);

    });

}

/* ==========================================
        RIPPLE EFFECT
========================================== */

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

/* ==========================================
                PART 3
========================================== */

document.addEventListener("DOMContentLoaded",()=>{

    resultAnimation();

    pageIntro();

    keyboardShortcut();

});

/* ==========================================
        RESULT POPUP
========================================== */

function resultAnimation(){

    const popup=document.querySelector(".resultCard");

    if(!popup) return;

    popup.animate([

        {

            opacity:0,

            transform:"scale(.7) rotate(-5deg)"

        },

        {

            opacity:1,

            transform:"scale(1.05) rotate(2deg)"

        },

        {

            opacity:1,

            transform:"scale(1)"

        }

    ],{

        duration:550,

        easing:"ease-out"

    });

}

/* ==========================================
            PAGE INTRO
========================================== */

function pageIntro(){

    const page=document.querySelector(".page");

    if(!page) return;

    page.animate([

        {

            opacity:0,

            transform:"translateY(40px)"

        },

        {

            opacity:1,

            transform:"translateY(0)"

        }

    ],{

        duration:600,

        easing:"ease"

    });

}

/* ==========================================
        ENTER TO SUBMIT
========================================== */

function keyboardShortcut(){

    const input=document.querySelector("input[name='guess']");

    const form=document.querySelector(".guessForm");

    if(!input||!form) return;

    input.addEventListener("keydown",(e)=>{

        if(e.key==="Enter"){

            form.submit();

        }

    });

}

/* ==========================================
        FLOATING NUMBER EFFECT
========================================== */

document.querySelectorAll(".historyGuess").forEach(el=>{

    el.addEventListener("mouseenter",()=>{

        el.animate([

            {transform:"translateY(0px)"},

            {transform:"translateY(-8px)"},

            {transform:"translateY(0px)"}

        ],{

            duration:350

        });

    });

});

/* ==========================================
        MAGNET BUTTON EFFECT
========================================== */

document.querySelectorAll("button").forEach(btn=>{

    btn.addEventListener("mousemove",(e)=>{

        const rect=btn.getBoundingClientRect();

        const x=e.clientX-rect.left-rect.width/2;

        const y=e.clientY-rect.top-rect.height/2;

        btn.style.transform=
            `translate(${x*0.06}px,${y*0.06}px)`;

    });

    btn.addEventListener("mouseleave",()=>{

        btn.style.transform="translate(0,0)";

    });

});

/* ==========================================
        HEART SPARKLES
========================================== */

setInterval(()=>{

    document.querySelectorAll(".hearts span:not(.dead)").forEach(h=>{

        h.animate([

            {filter:"drop-shadow(0 0 0px red)"},

            {filter:"drop-shadow(0 0 12px red)"},

            {filter:"drop-shadow(0 0 0px red)"}

        ],{

            duration:900

        });

    });

},1800);

/* ==========================================
        CONSOLE
========================================== */

console.log(
"%c🎯 Guess The Number V2 Loaded",
"color:#2EDBFF;font-size:18px;font-weight:bold;"
);