const gold = document.querySelector(".blob-gold");

const cyan = document.querySelector(".blob-cyan");

document.addEventListener("mousemove",(e)=>{

const x=(e.clientX/window.innerWidth)-0.5;

const y=(e.clientY/window.innerHeight)-0.5;

gold.style.transform=
`translate(${x*40}px,${y*40}px)`;

cyan.style.transform=
`translate(${-x*40}px,${-y*40}px)`;

});