const cards=document.querySelectorAll(".game-card");

const left=document.querySelector(".launcher-arrow.left");

const right=document.querySelector(".launcher-arrow.right");

const currentGame=document.getElementById("currentGame");

const totalGames=document.getElementById("totalGames");

let current=0;

totalGames.textContent=cards.length;

function render(){

cards.forEach(card=>{

card.className="game-card hidden";

});

cards[current].className="game-card active";

if(current>0){

cards[current-1].className="game-card left";

}

if(current<cards.length-1){

cards[current+1].className="game-card right";

}

currentGame.textContent=current+1;

}

left.onclick=()=>{

if(current>0){

current--;

render();

}

};

right.onclick=()=>{

if(current<cards.length-1){

current++;

render();

}

};

render();

cards.forEach(card=>{

card.addEventListener("mousemove",(e)=>{

const rect=card.getBoundingClientRect();

const x=e.clientX-rect.left;

const y=e.clientY-rect.top;

card.style.setProperty("--mx",`${x}px`);

card.style.setProperty("--my",`${y}px`);

const rotateY=(x-rect.width/2)/18;

const rotateX=-(y-rect.height/2)/18;

if(card.classList.contains("active")){

card.style.transform=

`translate(-50%,-50%) scale(1) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;

}

});

card.addEventListener("mouseleave",()=>{

card.style.transform="";

});

});

cards.forEach(card=>{

const btn=card.querySelector("button");

if(!btn)return;

btn.addEventListener("click",(e)=>{

e.stopPropagation();

const url=card.dataset.url;

if(!url||url=="#")return;

window.location.href=url;

});

});

const switchBtn = document.getElementById("switchToV5");

if(switchBtn){

switchBtn.addEventListener("click", async ()=>{

const response = await fetch("/api/change_hub",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({
version:"v5"
})

});

const data = await response.json();

if(data.success){

window.location.href="/hub";

}else{

alert("Couldn't switch hub.");

}

});

}