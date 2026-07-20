// ==========================================
// PLAYER
// ==========================================

const playBtn =
document.getElementById("playBtn");

const startScreen =
document.getElementById("startScreen");

gameRunning = false;

const player = document.getElementById("player");

const obstacleContainer = document.getElementById("obstacles");

const obstacles = [];

const coins = [];

let coinCount = 0;

let speed = 7;

let distance = 0;

let gameRunning = true;

let rotation = 0;

let landingScale = 1;

let playerY = 0;
let velocity = 0;

const gravity = 0.9;
const jumpForce = -16;

let isGrounded = true;

const groundY = 0;

// ==========================================
// INPUT
// ==========================================

function jump(){

    if(!isGrounded) return;

    velocity = jumpForce;

    landingScale = 1.12;

    isGrounded = false;

}

document.addEventListener("keydown",(e)=>{

    if(e.code==="Space"){

        e.preventDefault();

        jump();

    }

});

document.addEventListener("mousedown",jump);

document.addEventListener("touchstart",jump);

// ==========================================
// CREATE SPIKE
// ==========================================

function spawnCoin(){

    const coin = document.createElement("div");

    coin.className = "coin";

    coin.style.left = window.innerWidth + "px";

    coin.style.bottom =
    (170 + Math.random()*130) + "px";

    coinContainer.appendChild(coin);

    coins.push(coin);

}

function spawnSpike(){

    const spike = document.createElement("div");

    spike.className = "spike";

    spike.style.left = window.innerWidth + "px";

    obstacleContainer.appendChild(spike);

    obstacles.push(spike);

}

// ==========================================
// GAME LOOP
// ==========================================

function update(){

    if(!gameRunning) return;

    velocity += gravity;

    playerY += velocity;

    if(playerY > groundY){

    if(!isGrounded){

        landingScale = 0.82;

    }

    playerY = groundY;

    velocity = 0;

    isGrounded = true;

}

coins.forEach((coin,index)=>{

    let x=parseFloat(coin.style.left);

    x-=speed;

    coin.style.left=x+"px";

    const coinRect = coin.getBoundingClientRect();

    if(

        playerRect.left < coinRect.right &&
        playerRect.right > coinRect.left &&
        playerRect.top < coinRect.bottom &&
        playerRect.bottom > coinRect.top

    ){

        coin.remove();

        coins.splice(index,1);

        coinCount++;

        document.getElementById("coins").innerText =
        coinCount;

    }

    if(x<-40){

        coin.remove();

        coins.splice(index,1);

    }

});

    // Rotate while in air

if(!isGrounded){

    rotation += 10;

}else{

    rotation *= 0.8;

}

// Landing squash

landingScale += (1 - landingScale) * 0.15;

player.style.transform =

`translateY(${playerY}px)

 rotate(${rotation}deg)

 scale(${landingScale})`;

    const playerRect = player.getBoundingClientRect();

    obstacles.forEach((spike,index)=>{

        let x=parseFloat(spike.style.left);

        x-=speed;

        spike.style.left=x+"px";

        const spikeRect = spike.getBoundingClientRect();

        // COLLISION

        if(

            playerRect.left < spikeRect.right &&
            playerRect.right > spikeRect.left &&
            playerRect.top < spikeRect.bottom &&
            playerRect.bottom > spikeRect.top

        ){

            endGame();

        }

        if(x<-60){

            spike.remove();

            obstacles.splice(index,1);

        }
        
        document.querySelector(".game").classList.add("shake");

    });

    distance += speed*0.02;

    const progress =

    Math.min(distance/1000*100,100);

    document.getElementById("progressFill").style.width =
    progress + "%";

    speed += 0.0004;

    document.getElementById("distance").innerText =
    Math.floor(distance);

    if(gameRunning){

    requestAnimationFrame(update);

}

}

setInterval(()=>{

    spawnSpike();

},1800);

const xpEarned =

Math.floor(distance/10)+coinCount*5;

console.log("XP Earned:",xpEarned);

playBtn.addEventListener("click",()=>{

startScreen.remove();

gameRunning=true;

update();

});

// ==========================================
// RESTART
// ==========================================

function restartGame(){

    location.reload();

}

setInterval(()=>{

    spawnCoin();

},2600);