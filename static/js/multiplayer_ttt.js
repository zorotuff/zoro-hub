const MY_USERNAME = window.ZORO_USERNAME;

let currentRoom = null;
let pollTimer = null;

const lobby = document.getElementById("lobby");
const waiting = document.getElementById("waiting");
const gameArea = document.getElementById("gameArea");
const resultArea = document.getElementById("resultArea");

function showOnly(el) {
    [lobby, waiting, gameArea, resultArea].forEach(p => p.classList.add("hidden"));
    el.classList.remove("hidden");
}

async function api(path, opts) {
    const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || data.error || `HTTP ${res.status}`);
    return data;
}

document.getElementById("createBtn").addEventListener("click", async () => {
    try {
        const data = await api("/api/multiplayer/create", {
            method: "POST", body: JSON.stringify({ game_id: "tic_tac_toe_mp" })
        });
        enterRoom(data.room_code);
    } catch (e) { alert(e.message); }
});

document.getElementById("joinBtn").addEventListener("click", async () => {
    const code = document.getElementById("joinCode").value.trim().toUpperCase();
    if (!code) return;
    try {
        await api("/api/multiplayer/join", { method: "POST", body: JSON.stringify({ room_code: code }) });
        enterRoom(code);
    } catch (e) { alert(e.message); }
});

function enterRoom(code) {
    currentRoom = code;
    showOnly(waiting);
    document.getElementById("waitingCode").textContent = code;
    startPolling();
}

document.getElementById("readyBtn").addEventListener("click", async () => {
    try {
        await api("/api/multiplayer/ready", {
            method: "POST", body: JSON.stringify({ room_code: currentRoom, ready: true })
        });
    } catch (e) { alert(e.message); }
});

async function leaveRoom() {
    if (currentRoom) {
        try { await api("/api/multiplayer/leave", { method: "POST", body: JSON.stringify({ room_code: currentRoom }) }); }
        catch (e) {}
    }
    stopPolling();
    currentRoom = null;
    showOnly(lobby);
}
document.getElementById("leaveBtnWaiting").addEventListener("click", leaveRoom);
document.getElementById("leaveBtnGame").addEventListener("click", leaveRoom);
document.getElementById("rematchBtn").addEventListener("click", () => { showOnly(lobby); });

function startPolling() {
    stopPolling();
    poll();
    pollTimer = setInterval(poll, 1200);
}
function stopPolling() {
    if (pollTimer) clearInterval(pollTimer);
    pollTimer = null;
}

async function poll() {
    if (!currentRoom) return;
    try {
        const data = await api(`/api/multiplayer/room/${currentRoom}`);
        render(data);
    } catch (e) {
        stopPolling();
        showOnly(lobby);
    }
}

function render(room) {
    if (room.status === "waiting") {
        showOnly(waiting);
        document.getElementById("waitingPlayers").innerHTML = room.players.map(p => `
            <div class="mp-player-row">
                <span>${escapeHtml(p.username)}${p.username === MY_USERNAME ? " (you)" : ""}</span>
                <span class="${p.ready ? 'mp-player-ready' : 'mp-player-waiting'}">${p.ready ? "READY" : "waiting"}</span>
            </div>
        `).join("");
    } else if (room.status === "active") {
        showOnly(gameArea);
        renderBoard(room);
    } else if (room.status === "finished") {
        showOnly(resultArea);
        renderResult(room);
        stopPolling();
    }
}

function renderBoard(room) {
    const state = room.state;
    const board = document.getElementById("board");
    const turnBanner = document.getElementById("turnBanner");
    const isMyTurn = state.turn === MY_USERNAME;

    turnBanner.textContent = isMyTurn ? "Your Turn" : `Waiting for ${state.turn}`;

    board.innerHTML = state.board.map((cell, i) => `
        <button class="mp-cell ${cell ? 'filled' : ''}" data-pos="${i}" ${cell || !isMyTurn ? "disabled" : ""}>${cell || ""}</button>
    `).join("");

    if (isMyTurn) {
        board.querySelectorAll(".mp-cell:not(.filled)").forEach(btn => {
            btn.addEventListener("click", async () => {
                try {
                    await api("/api/multiplayer/move", {
                        method: "POST",
                        body: JSON.stringify({ room_code: currentRoom, move: { position: parseInt(btn.dataset.pos, 10) } })
                    });
                    poll();
                } catch (e) {
                    alert(e.message);
                }
            });
        });
    }
}

function renderResult(room) {
    const state = room.state;
    const title = document.getElementById("resultTitle");
    const reward = document.getElementById("resultReward");
    if (!state.winner) {
        title.textContent = "Draw!";
    } else if (state.winner === MY_USERNAME) {
        title.textContent = "You Win!";
    } else {
        title.textContent = `${state.winner} Wins!`;
    }
    reward.textContent = "Coins and XP have been credited to your account.";
}

function escapeHtml(v) {
    return String(v ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}
