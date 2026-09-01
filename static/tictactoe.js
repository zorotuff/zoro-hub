/* ==========================
   PARTICLE BACKGROUND
   (same visual language as game.js)
========================== */

const canvas = document.getElementById("bgCanvas");
const ctx = canvas.getContext("2d");
let particles = [];

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener("resize", resizeCanvas);

class Particle {
    constructor() { this.reset(); }
    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.radius = Math.random() * 2 + 1;
        this.speedX = (Math.random() - 0.5) * 0.4;
        this.speedY = (Math.random() - 0.5) * 0.4;
        this.alpha = Math.random() * 0.6 + 0.2;
    }
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
            this.reset();
        }
    }
    draw() {
        ctx.beginPath();
        ctx.fillStyle = `rgba(0,180,255,${this.alpha})`;
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fill();
    }
}

for (let i = 0; i < 100; i++) particles.push(new Particle());

function connectParticles() {
    for (let a = 0; a < particles.length; a++) {
        for (let b = a + 1; b < particles.length; b++) {
            const dx = particles[a].x - particles[b].x;
            const dy = particles[a].y - particles[b].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < 120) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0,180,255,${0.15 - distance / 900})`;
                ctx.lineWidth = 1;
                ctx.moveTo(particles[a].x, particles[a].y);
                ctx.lineTo(particles[b].x, particles[b].y);
                ctx.stroke();
            }
        }
    }
}

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach((p) => { p.update(); p.draw(); });
    connectParticles();
    requestAnimationFrame(animate);
}
animate();

window.addEventListener("load", () => {
    document.body.animate([{ opacity: 0 }, { opacity: 1 }], { duration: 600, easing: "ease" });
});

/* ==========================
   STATE
========================== */

const state = {
    difficulty: "hard",
    first: "player",
    board: Array(9).fill(" "),
    humanSymbol: "X",
    aiSymbol: "O",
    active: false,
};

/* ==========================
   DOM REFS
========================== */

const modeSelect = document.getElementById("modeSelect");
const setupScreen = document.getElementById("setupScreen");
const gameScreen = document.getElementById("gameScreen");
const headerSubtitle = document.getElementById("headerSubtitle");

const singleplayerCard = document.getElementById("singleplayerCard");
const multiplayerCard = document.getElementById("multiplayerCard");
const backToModeBtn = document.getElementById("backToModeBtn");
const startGameBtn = document.getElementById("startGameBtn");

const difficultyOptions = document.getElementById("difficultyOptions");
const firstOptions = document.getElementById("firstOptions");

const tttBoard = document.getElementById("tttBoard");
const cells = Array.from(document.querySelectorAll(".cell"));
const gameStatus = document.getElementById("gameStatus");
const difficultyBadge = document.getElementById("difficultyBadge");
const winLine = document.getElementById("winLine");
const winLineEl = document.getElementById("winLineEl");

const playAgainBtn = document.getElementById("playAgainBtn");
const changeSetupBtn = document.getElementById("changeSetupBtn");

const statWins = document.getElementById("statWins");
const statDraws = document.getElementById("statDraws");
const statLosses = document.getElementById("statLosses");

const resultOverlay = document.getElementById("resultOverlay");
const resultEmoji = document.getElementById("resultEmoji");
const resultTitle = document.getElementById("resultTitle");
const resultSub = document.getElementById("resultSub");
const overlayPlayAgain = document.getElementById("overlayPlayAgain");
const overlayChangeSetup = document.getElementById("overlayChangeSetup");

/* ==========================
   SCREEN NAVIGATION
========================== */

function showScreen(screen) {
    [modeSelect, setupScreen, gameScreen].forEach((s) => s.classList.remove("active"));
    screen.classList.add("active");
}

singleplayerCard.addEventListener("click", () => {
    headerSubtitle.textContent = "Configure your match";
    showScreen(setupScreen);
});

multiplayerCard.addEventListener("click", () => {
    multiplayerCard.animate(
        [{ transform: "scale(1)" }, { transform: "scale(.96)" }, { transform: "scale(1)" }],
        { duration: 200 }
    );
});

backToModeBtn.addEventListener("click", () => {
    headerSubtitle.textContent = "Choose how you want to play";
    showScreen(modeSelect);
});

/* ==========================
   SETUP OPTIONS
========================== */

function wireOptionGroup(container, onSelect) {
    container.querySelectorAll(".setup-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            container.querySelectorAll(".setup-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            onSelect(btn.dataset.value);
        });
    });
}

wireOptionGroup(difficultyOptions, (value) => { state.difficulty = value; });
wireOptionGroup(firstOptions, (value) => { state.first = value; });

/* ==========================
   API HELPERS
========================== */

async function postJSON(url, body) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body || {}),
    });
    return res.json();
}

/* ==========================
   BOARD RENDERING
========================== */

function renderBoard(board) {
    board.forEach((val, i) => {
        const cell = cells[i];
        cell.classList.remove("win-cell", "pop");
        if (val === " ") {
            cell.innerHTML = "";
            cell.classList.remove("filled", "x-mark", "o-mark");
        } else {
            cell.classList.add("filled");
            cell.classList.toggle("x-mark", val === "X");
            cell.classList.toggle("o-mark", val === "O");
        }
    });
    winLine.classList.remove("show");
}

function placeMark(index, symbol) {
    const cell = cells[index];
    cell.classList.add("filled", "pop");
    cell.classList.toggle("x-mark", symbol === "X");
    cell.classList.toggle("o-mark", symbol === "O");
    cell.innerHTML = `<span class="mark-inner">${symbol === "X" ? "✕" : "○"}</span>`;
}

function drawWinLine(line) {
    if (!line) return;
    const [a, , c] = line;
    const centerOf = (idx) => {
        const row = Math.floor(idx / 3);
        const col = idx % 3;
        return { x: col + 0.5, y: row + 0.5 };
    };
    const p1 = centerOf(a);
    const p2 = centerOf(c);
    winLineEl.setAttribute("x1", p1.x);
    winLineEl.setAttribute("y1", p1.y);
    winLineEl.setAttribute("x2", p2.x);
    winLineEl.setAttribute("y2", p2.y);

    cells.forEach((c2, i) => {
        if (line.includes(i)) c2.classList.add("win-cell");
    });

    requestAnimationFrame(() => winLine.classList.add("show"));
}

function updateStats(stats) {
    statWins.textContent = stats.wins;
    statDraws.textContent = stats.draws;
    statLosses.textContent = stats.losses;
}

/* ==========================
   GAME FLOW
========================== */

async function startGame() {
    startGameBtn.disabled = true;
    startGameBtn.textContent = "Starting...";

    const data = await postJSON("/api/tictactoe/start", {
        difficulty: state.difficulty,
        first: state.first,
    });

    startGameBtn.disabled = false;
    startGameBtn.textContent = "Start Game";

    if (data.error) {
        alert(data.error);
        return;
    }

    state.board = data.board;
    state.humanSymbol = data.human_symbol;
    state.aiSymbol = data.ai_symbol;
    state.active = data.status === "ongoing";

    difficultyBadge.textContent = data.difficulty_label;
    updateStats(data.stats);
    renderBoard(state.board);

    if (data.status === "ongoing") {
        gameStatus.textContent = "Your Turn";
    } else {
        handleGameEnd(data.status, data.line, data.stats);
    }

    headerSubtitle.textContent = "Good luck!";
    showScreen(gameScreen);
}

async function handleCellClick(index) {
    if (!state.active) return;
    if (state.board[index] !== " ") return;

    // optimistic UI update for the human move
    placeMark(index, state.humanSymbol);
    state.board[index] = state.humanSymbol;
    gameStatus.textContent = "AI Thinking...";

    const data = await postJSON("/api/tictactoe/move", { cell: index });

    if (data.error) {
        // revert optimistic update
        state.board[index] = " ";
        renderBoard(state.board);
        gameStatus.textContent = "Your Turn";
        return;
    }

    state.board = data.board;

    if (data.ai_move !== null && data.ai_move !== undefined) {
        placeMark(data.ai_move, state.aiSymbol);
    }

    updateStats(data.stats);

    if (data.status === "ongoing") {
        state.active = true;
        gameStatus.textContent = "Your Turn";
    } else {
        state.active = false;
        handleGameEnd(data.status, data.line, data.stats);
    }
}

function handleGameEnd(status, line, stats) {
    if (line) drawWinLine(line);

    let emoji, title, sub;

    if (status === state.humanSymbol) {
        emoji = "🏆";
        title = "You Win!";
        sub = "You outplayed the AI. Well done!";
        gameStatus.textContent = "You Won!";
    } else if (status === state.aiSymbol) {
        emoji = "🤖";
        title = "AI Wins";
        sub = "The AI got you this time. Try again!";
        gameStatus.textContent = "AI Won";
    } else {
        emoji = "🤝";
        title = "Draw";
        sub = "A perfectly balanced game.";
        gameStatus.textContent = "Draw";
    }

    resultEmoji.textContent = emoji;
    resultTitle.textContent = title;
    resultSub.textContent = sub;
    updateStats(stats);

    setTimeout(() => resultOverlay.classList.add("show"), 500);
}

/* ==========================
   EVENT WIRING
========================== */

startGameBtn.addEventListener("click", startGame);

cells.forEach((cell) => {
    cell.addEventListener("click", () => handleCellClick(Number(cell.dataset.index)));
});

async function restart() {
    resultOverlay.classList.remove("show");
    await postJSON("/api/tictactoe/reset", {});
    startGame();
}

playAgainBtn.addEventListener("click", restart);
overlayPlayAgain.addEventListener("click", restart);

async function goToSetup() {
    resultOverlay.classList.remove("show");
    await postJSON("/api/tictactoe/reset", {});
    headerSubtitle.textContent = "Configure your match";
    showScreen(setupScreen);
}

changeSetupBtn.addEventListener("click", goToSetup);
overlayChangeSetup.addEventListener("click", goToSetup);