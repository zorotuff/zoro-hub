/* ============================================================
   ZORO HUB — TIC TAC TOE GAME LOGIC
   ============================================================ */

(function () {
  'use strict';

  // ---------------- Constants ----------------

  const WIN_PATTERNS = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], // rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], // columns
    [0, 4, 8], [2, 4, 6]             // diagonals
  ];

  const PLAYER_SYMBOL = 'X';
  const AI_SYMBOL = 'O';
  const AI_THINK_DELAY_MS = 550;

  // ---------------- DOM references ----------------

  const screens = {
    mode: document.getElementById('screen-mode'),
    difficulty: document.getElementById('screen-difficulty'),
    game: document.getElementById('screen-game')
  };

  const modeSingleplayerBtn = document.getElementById('modeSingleplayer');
  const modeMultiplayerBtn = document.getElementById('modeMultiplayer');

  const difficultyCards = Array.from(document.querySelectorAll('.ttt-difficulty-card'));
  const starterCards = Array.from(document.querySelectorAll('.ttt-starter-card'));
  const difficultyBackBtn = document.getElementById('difficultyBackBtn');
  const startGameBtn = document.getElementById('startGameBtn');

  const boardEl = document.getElementById('tttBoard');
  const cellEls = Array.from(document.querySelectorAll('.ttt-cell'));
  const winLineSvg = document.getElementById('winLineSvg');
  const winLineEl = document.getElementById('winLine');
  const turnIndicator = document.getElementById('turnIndicator');
  const turnIndicatorText = document.getElementById('turnIndicatorText');
  const metaDifficulty = document.getElementById('metaDifficulty');
  const gameBackBtn = document.getElementById('gameBackBtn');
  const restartBtn = document.getElementById('restartBtn');

  const resultModalOverlay = document.getElementById('resultModalOverlay');
  const resultIcon = document.getElementById('resultIcon');
  const resultTitle = document.getElementById('resultTitle');
  const resultMessage = document.getElementById('resultMessage');
  const rewardCoins = document.getElementById('rewardCoins');
  const rewardXp = document.getElementById('rewardXp');
  const modalBackBtn = document.getElementById('modalBackBtn');
  const modalPlayAgainBtn = document.getElementById('modalPlayAgainBtn');

  const statCoins = document.getElementById('statCoins');
  const statXp = document.getElementById('statXp');
  const toastEl = document.getElementById('tttToast');

  // ---------------- State ----------------

  const state = {
    difficulty: null,   // 'easy' | 'medium' | 'hard'
    starter: null,      // 'player' | 'ai'
    board: Array(9).fill(null),
    currentTurn: null,  // 'player' | 'ai'
    isGameOver: false,
    isProcessing: false
  };

  // ---------------- Screen switching ----------------

  function showScreen(name) {
    Object.entries(screens).forEach(([key, el]) => {
      if (!el) return;
      el.classList.toggle('is-active', key === name);
    });
  }

  // ---------------- Toast ----------------

  let toastTimer = null;
  function showToast(message) {
    if (!toastEl) return;
    toastEl.textContent = message;
    toastEl.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      toastEl.classList.remove('is-visible');
    }, 2400);
  }

  // ---------------- Ripple effect ----------------

  function attachRipple(el) {
    el.addEventListener('click', (e) => {
      if (el.disabled) return;
      const rect = el.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const ripple = document.createElement('span');
      ripple.className = 'ttt-ripple';
      ripple.style.width = ripple.style.height = size + 'px';
      ripple.style.left = (e.clientX - rect.left - size / 2) + 'px';
      ripple.style.top = (e.clientY - rect.top - size / 2) + 'px';
      el.appendChild(ripple);
      setTimeout(() => ripple.remove(), 650);
    });
  }

  document.querySelectorAll('.ripple-btn').forEach(attachRipple);

  // ---------------- Mode select ----------------

  modeSingleplayerBtn.addEventListener('click', () => {
    showScreen('difficulty');
  });

  modeMultiplayerBtn.addEventListener('click', () => {
    showToast('Multiplayer is coming soon!');
  });

  // ---------------- Difficulty / starter select ----------------

  difficultyCards.forEach((card) => {
    card.addEventListener('click', () => {
      difficultyCards.forEach((c) => c.classList.remove('is-selected'));
      card.classList.add('is-selected');
      state.difficulty = card.dataset.difficulty;
      refreshStartButton();
    });
  });

  starterCards.forEach((card) => {
    card.addEventListener('click', () => {
      starterCards.forEach((c) => c.classList.remove('is-selected'));
      card.classList.add('is-selected');
      state.starter = card.dataset.starter;
      refreshStartButton();
    });
  });

  function refreshStartButton() {
    startGameBtn.disabled = !(state.difficulty && state.starter);
  }

  difficultyBackBtn.addEventListener('click', () => {
    showScreen('mode');
  });

  startGameBtn.addEventListener('click', () => {
    startNewGame();
    showScreen('game');
  });

  // ---------------- Board rendering ----------------

function xMarkSvg() {
    return (
        '<svg viewBox="0 0 100 100" class="ttt-mark mark-x">' +
        '<path d="M20 20 L80 80" fill="none" stroke="#4FC3F7" stroke-width="10" stroke-linecap="round"/>' +
        '<path d="M80 20 L20 80" fill="none" stroke="#4FC3F7" stroke-width="10" stroke-linecap="round"/>' +
        '</svg>'
    );
}

function oMarkSvg() {
    return (
        '<svg viewBox="0 0 100 100" class="ttt-mark mark-o">' +
        '<circle cx="50" cy="50" r="35" fill="none" stroke="#FF5E7E" stroke-width="10"/>' +
        '</svg>'
    );
}

  function renderMark(index, symbol) {
    const cell = cellEls[index];
    const markHolder = cell.querySelector('.ttt-mark');
    markHolder.className = 'ttt-mark ' + (symbol === PLAYER_SYMBOL ? 'mark-x' : 'mark-o');
    markHolder.innerHTML = symbol === PLAYER_SYMBOL ? xMarkSvg() : oMarkSvg();
    cell.classList.add('is-filled');
  }

  function clearBoardUI() {
    cellEls.forEach((cell) => {
      cell.classList.remove('is-filled', 'is-win-cell');
      const markHolder = cell.querySelector('.ttt-mark');
      markHolder.className = 'ttt-mark';
      markHolder.innerHTML = '';
    });
    winLineEl.style.opacity = '0';
    winLineSvg.classList.remove('is-drawn');
  }

  function updateTurnIndicator() {
    if (state.isGameOver) return;
    const isAiTurn = state.currentTurn === 'ai';
    turnIndicator.classList.toggle('is-ai-turn', isAiTurn);
    turnIndicatorText.textContent = isAiTurn ? 'AI is thinking...' : 'Your Turn';
  }

  // ---------------- Game flow ----------------

  function startNewGame() {
    state.board = Array(9).fill(null);
    state.isGameOver = false;
    state.isProcessing = false;
    state.currentTurn = state.starter === 'ai' ? 'ai' : 'player';

    clearBoardUI();
    metaDifficulty.textContent = capitalize(state.difficulty);
    updateTurnIndicator();

    if (state.currentTurn === 'ai') {
      state.isProcessing = true;
      setTimeout(runAiTurn, AI_THINK_DELAY_MS);
    }
  }

  function capitalize(str) {
    return str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
  }

  cellEls.forEach((cell) => {
    cell.addEventListener('click', () => {
      const index = parseInt(cell.dataset.index, 10);
      handlePlayerMove(index);
    });
  });

  function handlePlayerMove(index) {
    if (state.isGameOver || state.isProcessing) return;
    if (state.currentTurn !== 'player') return;
    if (state.board[index] !== null) return;

    placeMark(index, PLAYER_SYMBOL);

    const outcome = evaluateBoard(state.board);
    if (outcome) {
      finishGame(outcome);
      return;
    }

    state.currentTurn = 'ai';
    state.isProcessing = true;
    updateTurnIndicator();
    setTimeout(runAiTurn, AI_THINK_DELAY_MS);
  }

  function runAiTurn() {
    if (state.isGameOver) {
      state.isProcessing = false;
      return;
    }

    const index = chooseAiMove(state.board, state.difficulty);
    placeMark(index, AI_SYMBOL);

    const outcome = evaluateBoard(state.board);
    if (outcome) {
      finishGame(outcome);
      return;
    }

    state.currentTurn = 'player';
    state.isProcessing = false;
    updateTurnIndicator();
  }

  function placeMark(index, symbol) {
    state.board[index] = symbol;
    renderMark(index, symbol);
  }

  // ---------------- Win detection ----------------

  function evaluateBoard(board) {
    for (const pattern of WIN_PATTERNS) {
      const [a, b, c] = pattern;
      if (board[a] && board[a] === board[b] && board[a] === board[c]) {
        return { winner: board[a], pattern };
      }
    }
    if (board.every((cell) => cell !== null)) {
      return { winner: null, pattern: null }; // draw
    }
    return null; // game continues
  }

  // ---------------- AI ----------------

  function chooseAiMove(board, difficulty) {
    if (difficulty === 'easy') return randomMove(board);
    if (difficulty === 'medium') return mediumMove(board);
    return bestMinimaxMove(board);
  }

  function emptyIndices(board) {
    const result = [];
    for (let i = 0; i < board.length; i++) {
      if (board[i] === null) result.push(i);
    }
    return result;
  }

  function randomMove(board) {
    const options = emptyIndices(board);
    return options[Math.floor(Math.random() * options.length)];
  }

  function findWinningMove(board, symbol) {
    for (const index of emptyIndices(board)) {
      const copy = board.slice();
      copy[index] = symbol;
      const outcome = evaluateBoard(copy);
      if (outcome && outcome.winner === symbol) {
        return index;
      }
    }
    return null;
  }

  function mediumMove(board) {
    const winMove = findWinningMove(board, AI_SYMBOL);
    if (winMove !== null) return winMove;

    const blockMove = findWinningMove(board, PLAYER_SYMBOL);
    if (blockMove !== null) return blockMove;

    return randomMove(board);
  }

  function bestMinimaxMove(board) {
    let bestScore = -Infinity;
    let bestIndex = null;

    for (const index of emptyIndices(board)) {
      const copy = board.slice();
      copy[index] = AI_SYMBOL;
      const score = minimax(copy, 0, false);
      if (score > bestScore) {
        bestScore = score;
        bestIndex = index;
      }
    }

    return bestIndex;
  }

  function minimax(board, depth, isMaximizing) {
    const outcome = evaluateBoard(board);
    if (outcome) {
      if (outcome.winner === AI_SYMBOL) return 10 - depth;
      if (outcome.winner === PLAYER_SYMBOL) return depth - 10;
      return 0; // draw
    }

    if (isMaximizing) {
      let best = -Infinity;
      for (const index of emptyIndices(board)) {
        const copy = board.slice();
        copy[index] = AI_SYMBOL;
        best = Math.max(best, minimax(copy, depth + 1, false));
      }
      return best;
    } else {
      let best = Infinity;
      for (const index of emptyIndices(board)) {
        const copy = board.slice();
        copy[index] = PLAYER_SYMBOL;
        best = Math.min(best, minimax(copy, depth + 1, true));
      }
      return best;
    }
  }

  // ---------------- Winning line ----------------

  function cellCenter(index) {
    const row = Math.floor(index / 3);
    const col = index % 3;
    return { x: col * 100 + 50, y: row * 100 + 50 };
  }

  function drawWinningLine(pattern) {
    const start = cellCenter(pattern[0]);
    const end = cellCenter(pattern[2]);
    const length = Math.hypot(end.x - start.x, end.y - start.y);

    winLineEl.setAttribute('x1', start.x);
    winLineEl.setAttribute('y1', start.y);
    winLineEl.setAttribute('x2', end.x);
    winLineEl.setAttribute('y2', end.y);
    winLineEl.style.setProperty('--winline-length', length);
    winLineEl.style.strokeDasharray = String(length);
    winLineEl.style.strokeDashoffset = String(length);
    winLineEl.style.opacity = '1';

    // restart the CSS animation
    winLineSvg.classList.remove('is-drawn');
    void winLineSvg.offsetWidth; // force reflow
    winLineSvg.classList.add('is-drawn');
  }

  function highlightWinningCells(pattern) {
    pattern.forEach((index) => {
      cellEls[index].classList.add('is-win-cell');
    });
  }

  // ---------------- Game end / result flow ----------------

  function finishGame(outcome) {
    state.isGameOver = true;
    state.isProcessing = false;

    let result;

    if (outcome.pattern) {
      highlightWinningCells(outcome.pattern);
      drawWinningLine(outcome.pattern);
      result = outcome.winner === PLAYER_SYMBOL ? 'win' : 'loss';
    } else {
      result = 'draw';
    }

    turnIndicatorText.textContent =
      result === 'win' ? 'You Won!' : result === 'loss' ? 'AI Won' : 'Draw';
    turnIndicator.classList.remove('is-ai-turn');

    if (result === 'win') {
      launchConfetti();
    }

    sendResultToServer(result);
  }

  function sendResultToServer(result) {
    fetch('/ttt/result', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ result })
    })
      .then((response) => response.json())
      .then((data) => {
        if (data && data.success) {
          updateTopbarStats(data.profile);
          showResultModal(result, data.rewards);
        } else {
          showResultModal(result, { coins: 0, xp: 0 });
        }
      })
      .catch(() => {
        showResultModal(result, { coins: 0, xp: 0 });
      });
  }

  function updateTopbarStats(profile) {
    if (!profile) return;
    if (statCoins) statCoins.textContent = profile.coins;
    if (statXp) statXp.textContent = profile.xp;
  }

  // ---------------- Result modal ----------------

  const RESULT_CONTENT = {
    win: {
      icon: '🏆',
      title: 'You Win!',
      message: 'Victory secured. The board bends to your will.'
    },
    loss: {
      icon: '💀',
      title: 'You Lose',
      message: 'The AI outplayed you this time. Run it back.'
    },
    draw: {
      icon: '🤝',
      title: 'Draw',
      message: 'Neither side could break through. Evenly matched.'
    }
  };

  function showResultModal(result, rewards) {
    const content = RESULT_CONTENT[result];
    resultIcon.textContent = content.icon;
    resultTitle.textContent = content.title;
    resultMessage.textContent = content.message;
    const COIN_REWARDS = {
    easy: "10  or  25",
    medium: "20 or 50",
    hard: "50 or 100"
};

  rewardCoins.textContent = "+" + COIN_REWARDS[state.difficulty];
    
    requestAnimationFrame(() => {
      resultModalOverlay.classList.add('is-visible');
    });
  }

  function hideResultModal() {
    resultModalOverlay.classList.remove('is-visible');
  }

  modalPlayAgainBtn.addEventListener('click', () => {
    hideResultModal();
    startNewGame();
  });

  modalBackBtn.addEventListener('click', () => {
    hideResultModal();
    showScreen('mode');
  });

  // ---------------- Back / restart controls ----------------

  gameBackBtn.addEventListener('click', () => {
    showScreen('mode');
  });

  restartBtn.addEventListener('click', () => {
    startNewGame();
  });

  // ---------------- Confetti ----------------

  const confettiCanvas = document.getElementById('confettiCanvas');
  const confettiCtx = confettiCanvas ? confettiCanvas.getContext('2d') : null;
  let confettiPieces = [];
  let confettiFrameId = null;

  function resizeConfettiCanvas() {
    if (!confettiCanvas) return;
    confettiCanvas.width = window.innerWidth;
    confettiCanvas.height = window.innerHeight;
  }

  window.addEventListener('resize', resizeConfettiCanvas);
  resizeConfettiCanvas();

  const CONFETTI_COLORS = ['#4dabf7', '#a855f7', '#22c55e', '#eab308', '#f1f2f8'];

  function launchConfetti() {
    if (!confettiCtx) return;

    confettiPieces = new Array(140).fill(null).map(() => ({
      x: Math.random() * confettiCanvas.width,
      y: -20 - Math.random() * confettiCanvas.height * 0.4,
      size: Math.random() * 7 + 4,
      color: CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
      vx: (Math.random() - 0.5) * 3,
      vy: Math.random() * 2.5 + 2.5,
      rotation: Math.random() * Math.PI * 2,
      rotationSpeed: (Math.random() - 0.5) * 0.25,
      life: 0,
      maxLife: 180 + Math.random() * 60
    }));

    if (confettiFrameId === null) {
      confettiFrameId = requestAnimationFrame(stepConfetti);
    }
  }

  function stepConfetti() {
    confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);

    let alive = false;

    confettiPieces.forEach((p) => {
      if (p.life >= p.maxLife) return;
      alive = true;

      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.03;
      p.rotation += p.rotationSpeed;
      p.life += 1;

      const fade = 1 - Math.max(0, p.life - p.maxLife * 0.75) / (p.maxLife * 0.25);

      confettiCtx.save();
      confettiCtx.translate(p.x, p.y);
      confettiCtx.rotate(p.rotation);
      confettiCtx.globalAlpha = Math.max(0, Math.min(1, fade));
      confettiCtx.fillStyle = p.color;
      confettiCtx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      confettiCtx.restore();
    });

    if (alive) {
      confettiFrameId = requestAnimationFrame(stepConfetti);
    } else {
      confettiCtx.clearRect(0, 0, confettiCanvas.width, confettiCanvas.height);
      confettiFrameId = null;
    }
  }

  // ---------------- Initial profile load ----------------

  function loadInitialProfile() {
    fetch('/api/profile')
      .then((response) => response.json())
      .then((data) => {
        if (data && data.success) {
          updateTopbarStats(data.profile);
        }
      })
      .catch(() => {
        /* topbar stats simply stay at their placeholder values */
      });
  }

  loadInitialProfile();
})();