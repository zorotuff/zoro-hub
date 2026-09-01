"use strict";

/* ===========================================
   ZORO HUB - TIC TAC TOE
   PART 1
   CORE + SCREEN SYSTEM
=========================================== */

console.log("TTT Part 1 Loaded");

/* ---------- Screens ---------- */

const screens = {
    mode: document.getElementById("screen-mode"),
    difficulty: document.getElementById("screen-difficulty"),
    game: document.getElementById("screen-game")
};

/* ---------- Buttons ---------- */

const modeSingleplayer = document.getElementById("modeSingleplayer");
const modeMultiplayer = document.getElementById("modeMultiplayer");

const difficultyBackBtn = document.getElementById("difficultyBackBtn");
const gameBackBtn = document.getElementById("gameBackBtn");

const startGameBtn = document.getElementById("startGameBtn");

const resultOverlay =
document.getElementById("resultModalOverlay");

const modalPlayAgainBtn =
document.getElementById("modalPlayAgainBtn");

const modalBackBtn =
document.getElementById("modalBackBtn");

/* ---------- Show Screen ---------- */

function showScreen(target){

    Object.values(screens).forEach(screen=>{

        screen.classList.remove("is-active");

    });

    target.classList.add("is-active");

}

/* ---------- Initial Screen ---------- */

showScreen(screens.mode);

/* ---------- Mode ---------- */

modeSingleplayer.addEventListener("click",()=>{

    console.log("Singleplayer");

    showScreen(screens.difficulty);

});

modeMultiplayer.addEventListener("click",()=>{

    alert("Coming Soon 👀");

});

/* ---------- Back Buttons ---------- */

difficultyBackBtn.addEventListener("click",()=>{

    showScreen(screens.mode);

});

gameBackBtn.addEventListener("click",()=>{

    showScreen(screens.mode);

});

/* ===========================================
   PART 2
   GAME SETUP
=========================================== */

let gameSettings = {

    difficulty: null,

    starter: null

};

/* ---------- Cards ---------- */

const difficultyCards =
document.querySelectorAll(".ttt-difficulty-card");

const starterCards =
document.querySelectorAll(".ttt-starter-card");

/* ---------- Update Button ---------- */

function updateStartButton(){

    startGameBtn.disabled = !(

        gameSettings.difficulty &&

        gameSettings.starter

    );

}

/* ---------- Difficulty ---------- */

difficultyCards.forEach(card=>{

    card.addEventListener("click",()=>{

        difficultyCards.forEach(c=>{

            c.classList.remove("selected");

        });

        card.classList.add("selected");

        gameSettings.difficulty =
        card.dataset.difficulty;

        console.log(
            "Difficulty:",
            gameSettings.difficulty
        );

        updateStartButton();

    });

});

/* ---------- Starter ---------- */

starterCards.forEach(card=>{

    card.addEventListener("click",()=>{

        starterCards.forEach(c=>{

            c.classList.remove("selected");

        });

        card.classList.add("selected");

        gameSettings.starter =
        card.dataset.starter;

        console.log(
            "Starter:",
            gameSettings.starter
        );

        updateStartButton();

    });

});

/* ===========================================
   PART 3
   BOARD + GAME STATE
=========================================== */

const cells = document.querySelectorAll(".ttt-cell");

const turnIndicatorText =
document.getElementById("turnIndicatorText");

const metaDifficulty =
document.getElementById("metaDifficulty");

const gameState = {

    board: Array(9).fill(""),

    currentPlayer: "X",

    gameOver: false,

    aiThinking: false

};

/* ---------- Reset ---------- */

function resetBoard(){

    gameState.board = Array(9).fill("");

    gameState.gameOver = false;

    gameState.aiThinking = false;

    gameState.currentPlayer =
        gameSettings.starter === "player"
        ? "X"
        : "O";

    cells.forEach(cell=>{

        cell.textContent = "";

        cell.className = "ttt-cell ripple-btn";

    });

    updateTurnUI();

    if(gameSettings.starter==="ai"){

        gameState.aiThinking = true;

        setTimeout(aiMove,500);

    }

}

/* ---------- Turn UI ---------- */

function updateTurnUI(){

    if(gameState.currentPlayer==="X"){

        turnIndicatorText.textContent =
        "Your Turn";

    }else{

        turnIndicatorText.textContent =
        "AI Thinking...";

    }

}

/* ---------- Start Match ---------- */

startGameBtn.addEventListener("click",()=>{

    zoroStartSession("tic_tac_toe");

    resetBoard();

    metaDifficulty.textContent =
    gameSettings.difficulty.toUpperCase();

    updateTurnUI();

    showScreen(screens.game);

});

/* ---------- Place Symbol ---------- */

cells.forEach(cell=>{

    cell.addEventListener("click",()=>{

        if(gameState.gameOver) return;

        if(gameState.aiThinking) return;

        if(gameState.currentPlayer!=="X") return;

        const index = Number(cell.dataset.index);

        if(gameState.board[index]!="") return;

        gameState.board[index]="X";

        cell.textContent="X";

        if(checkWinner("X")){

            finishGame("win");

            return;

            }

        if(isBoardFull()){

            finishGame("draw");

            return;

            }

        cell.classList.add("x");

        gameState.currentPlayer="O";

        gameState.aiThinking=true;

        updateTurnUI();

        setTimeout(()=>{

            aiMove();

        },500);

    });

});

/* ---------- Restart ---------- */

restartBtn.onclick = ()=>{

    resetBoard();

};

/* ---------- AI ---------- */

function aiMove(){

    if(gameState.gameOver) return;

    let move = null;

    switch(gameSettings.difficulty){

        case "easy":
            move = getRandomMove();
            break;

        case "medium":
            move = getMediumMove();
            break;

        case "hard":

            move = getBestMove();

            break;

        default:
            move = getRandomMove();

    }

    if(move===null){

        gameState.aiThinking=false;
        return;

    }

    gameState.board[move]="O";

    cells[move].textContent="O";

    cells[move].classList.add("o");

    if(checkWinner("O")){

        finishGame("lose");

        return;

        }

    if(isBoardFull()){

        finishGame("draw");

        return;

    }

    gameState.currentPlayer="X";

    gameState.aiThinking=false;

    updateTurnUI();

}

function getRandomMove(){

    const empty=[];

    for(let i=0;i<9;i++){

        if(gameState.board[i]==""){

            empty.push(i);

        }

    }

    if(empty.length===0){

        return null;

    }

    return empty[
        Math.floor(Math.random()*empty.length)
    ];

}

function getMediumMove(){

    // 50% chance to play randomly
    if(Math.random() < 0.5){

        return getRandomMove();

    }

    // 1. Win if possible
    for(let i=0;i<9;i++){

        if(gameState.board[i]!="") continue;

        gameState.board[i]="O";

        if(checkWinner("O")){

            gameState.board[i]="";

            return i;

        }

        gameState.board[i]="";

    }

    // 2. Block player
    for(let i=0;i<9;i++){

        if(gameState.board[i]!="") continue;

        gameState.board[i]="X";

        if(checkWinner("X")){

            gameState.board[i]="";

            return i;

        }

        gameState.board[i]="";

    }

    // 3. Take center
    if(gameState.board[4]==""){

        return 4;

    }

    // 4. Take random corner
    const corners=[0,2,6,8];

    let freeCorners=[];

    corners.forEach(c=>{

        if(gameState.board[c]==""){

            freeCorners.push(c);

        }

    });

    if(freeCorners.length){

        return freeCorners[
            Math.floor(Math.random()*freeCorners.length)
        ];

    }

    // 5. Random
    return getRandomMove();

}

function getBestMove(){

    let bestScore = -Infinity;

    let move = null;

    for(let i=0;i<9;i++){

        if(gameState.board[i]!="") continue;

        gameState.board[i]="O";

        let score = minimax(gameState.board,false);

        gameState.board[i]="";

        if(score>bestScore){

            bestScore = score;

            move = i;

        }

    }

    return move;

}

function minimax(board,isMaximizing){

    if(checkWinner("O")) return 10;

    if(checkWinner("X")) return -10;

    if(board.every(c=>c!="")) return 0;

    if(isMaximizing){

        let best=-Infinity;

        for(let i=0;i<9;i++){

            if(board[i]!="") continue;

            board[i]="O";

            let score=minimax(board,false);

            board[i]="";

            best=Math.max(score,best);

        }

        return best;

    }

    else{

        let best=Infinity;

        for(let i=0;i<9;i++){

            if(board[i]!="") continue;

            board[i]="X";

            let score=minimax(board,true);

            board[i]="";

            best=Math.min(score,best);

        }

        return best;

    }

}

function checkWinner(symbol){

    const wins = [

        [0,1,2],
        [3,4,5],
        [6,7,8],

        [0,3,6],
        [1,4,7],
        [2,5,8],

        [0,4,8],
        [2,4,6]

    ];

    for(const combo of wins){

        if(

            gameState.board[combo[0]]===symbol &&
            gameState.board[combo[1]]===symbol &&
            gameState.board[combo[2]]===symbol

        ){

            return true;

        }

    }

    return false;

}

function isBoardFull(){

    return gameState.board.every(cell=>cell!="");

}

function finishGame(result){

    gameState.gameOver=true;

    gameState.aiThinking=false;

    const overlay=document.getElementById("resultModalOverlay");

    const title=document.getElementById("resultTitle");

    const msg=document.getElementById("resultMessage");

    const icon=document.getElementById("resultIcon");

    if(result==="win"){

        icon.textContent="🏆";
        title.textContent="YOU WIN!";
        msg.textContent="The AI has been defeated!";

        const tierByDifficulty = {easy:"participation", medium:"good", hard:"top"};
        const tier = tierByDifficulty[gameSettings.difficulty] || "participation";
        zoroReportResult("tic_tac_toe", tier).then(reward=>{
            if(reward){
                msg.textContent = `The AI has been defeated! +${reward.coins_awarded} Coins, +${reward.xp_awarded} XP`;
            }
        });

    }

    else if(result==="lose"){

        icon.textContent="💀";
        title.textContent="YOU LOST";
        msg.textContent="The AI outplayed you.";

    }

    else{

        icon.textContent="🤝";
        title.textContent="DRAW";
        msg.textContent="Nobody wins this round.";

    }

    console.log("SHOW MODAL");

    overlay.classList.add("show");

}

modalPlayAgainBtn.onclick = () => {

    resultOverlay.classList.remove("show");

    resetBoard();

};

modalBackBtn.onclick = () => {

    resultOverlay.classList.remove("show");

    resetBoard();

    showScreen(screens.mode);

};

modalPlayAgainBtn.addEventListener("click",()=>{

    resultOverlay.classList.remove("show");

    resetBoard();

});

modalBackBtn.addEventListener("click",()=>{

    resultOverlay.classList.remove("show");

    resetBoard();

    showScreen(screens.mode);

});