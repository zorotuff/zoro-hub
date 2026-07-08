/* =========================================================
   NEXUS Game Hub — frontend behaviour only.
   No backend calls: all data is placeholder / in-memory,
   with theme + settings persisted to localStorage for a
   nicer repeat-visit experience (purely client-side).
   ========================================================= */

document.addEventListener('DOMContentLoaded', () => {
  initParticleField();
  initSearch();
  initFilterChips();
  initNavSync();
  initModals();
  initThemePicker();
  initSettingsPanel();
  initCardPlayButtons();
});

/* ---------------------------------------------------------
   Ambient particle field
   Lightweight canvas starfield drifting slowly upward.
   Colors are re-read from the active theme's CSS variables
   so particles match whichever theme is selected.
   Pauses when the tab is hidden or animations are off.
--------------------------------------------------------- */
function initParticleField() {
  const canvas = document.getElementById('particle-field');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let particles = [];
  let animationFrame;
  let width, height;
  let running = false;

  const PARTICLE_COUNT = 70;

  function getThemeColors() {
    const styles = getComputedStyle(document.documentElement);
    return [
      styles.getPropertyValue('--accent-violet').trim() || '#8b5cf6',
      styles.getPropertyValue('--accent-cyan').trim() || '#22d3ee',
      styles.getPropertyValue('--accent-pink').trim() || '#f472b6',
      styles.getPropertyValue('--accent-indigo').trim() || '#6366f1',
    ];
  }

  let colors = getThemeColors();

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }

  function createParticle() {
    return {
      x: Math.random() * width,
      y: Math.random() * height,
      radius: Math.random() * 1.6 + 0.4,
      speed: Math.random() * 0.35 + 0.05,
      drift: (Math.random() - 0.5) * 0.2,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: Math.random() * 0.5 + 0.15,
    };
  }

  function init() {
    resize();
    particles = Array.from({ length: PARTICLE_COUNT }, createParticle);
  }

  function tick() {
    ctx.clearRect(0, 0, width, height);
    for (const p of particles) {
      p.y -= p.speed;
      p.x += p.drift;

      if (p.y < -10) {
        p.y = height + 10;
        p.x = Math.random() * width;
        p.color = colors[Math.floor(Math.random() * colors.length)];
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (running) animationFrame = requestAnimationFrame(tick);
  }

  function start() {
    if (running) return;
    running = true;
    animationFrame = requestAnimationFrame(tick);
  }

  function stop() {
    running = false;
    cancelAnimationFrame(animationFrame);
  }

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stop();
    } else if (!document.documentElement.classList.contains('motion-off')) {
      start();
    }
  });

  window.addEventListener('resize', resize);

  // Re-color particles whenever the theme changes.
  window.addEventListener('nexus:theme-changed', () => {
    colors = getThemeColors();
  });

  // Respond to the manual "Animations" toggle in Settings.
  window.addEventListener('nexus:motion-changed', (e) => {
    if (e.detail.enabled) {
      start();
    } else {
      stop();
      ctx.clearRect(0, 0, width, height); // clear so a static frame doesn't linger oddly
    }
  });

  init();

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const motionForcedOff = document.documentElement.classList.contains('motion-off');
  if (!prefersReducedMotion && !motionForcedOff) {
    start();
  } else {
    running = true;
    tick(); // draw a single static frame
    running = false;
  }
}

/* ---------------------------------------------------------
   Search bar
   Filters visible game cards by title (case-insensitive).
--------------------------------------------------------- */
function initSearch() {
  const input = document.getElementById('search-input');
  const grid = document.getElementById('game-grid');
  const emptyState = document.getElementById('empty-state');
  if (!input || !grid) return;

  input.addEventListener('input', applyFilters);

  function applyFilters() {
    const query = input.value.trim().toLowerCase();
    const activeChip = document.querySelector('.chip.active');
    const statusFilter = activeChip ? activeChip.dataset.filter : 'all';

    const cards = Array.from(grid.querySelectorAll('.game-card'));
    let visibleCount = 0;

    cards.forEach((card) => {
      const title = (card.dataset.title || '').toLowerCase();
      const status = card.dataset.status;

      const matchesSearch = title.includes(query);
      const matchesStatus = statusFilter === 'all' || status === statusFilter;
      const isVisible = matchesSearch && matchesStatus;

      card.classList.toggle('hidden-by-filter', !isVisible);
      if (isVisible) visibleCount += 1;
    });

    if (emptyState) emptyState.hidden = visibleCount !== 0;
  }

  window.__nexusApplyFilters = applyFilters;
}

/* ---------------------------------------------------------
   Filter chips (All / Installed / Coming Soon)
--------------------------------------------------------- */
function initFilterChips() {
  const chips = document.querySelectorAll('.chip');
  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      chips.forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      if (typeof window.__nexusApplyFilters === 'function') {
        window.__nexusApplyFilters();
      }
    });
  });
}

/* ---------------------------------------------------------
   Sidebar + bottom nav
   Keeps both nav sets in sync (same data-nav id) and opens
   the matching modal for items flagged with data-modal.
--------------------------------------------------------- */
function initNavSync() {
  const allNavItems = document.querySelectorAll('.side-link, .nav-item');

  allNavItems.forEach((item) => {
    item.addEventListener('click', () => {
      const navId = item.dataset.nav;

      // Sync active state across sidebar + bottom nav.
      allNavItems.forEach((i) => {
        i.classList.toggle('active', i.dataset.nav === navId);
      });

      // Items like Themes/Settings also carry data-modal and
      // are handled by initModals(); no page routing exists yet
      // since this is a frontend-only shell.
    });
  });
}

/* ---------------------------------------------------------
   Modals (Themes, Settings)
   Generic open/close wiring driven by data-modal / data-close-modal.
--------------------------------------------------------- */
function initModals() {
  const openTriggers = document.querySelectorAll('[data-modal]');
  const closeTriggers = document.querySelectorAll('[data-close-modal]');
  const overlays = document.querySelectorAll('.modal-overlay');

  function openModal(id) {
    const overlay = document.getElementById(id);
    if (overlay) overlay.hidden = false;
  }

  function closeModal(overlay) {
    overlay.hidden = true;
  }

  openTriggers.forEach((trigger) => {
    trigger.addEventListener('click', () => {
      openModal(trigger.dataset.modal);
    });
  });

  closeTriggers.forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const overlay = trigger.closest('.modal-overlay');
      if (overlay) closeModal(overlay);
    });
  });

  overlays.forEach((overlay) => {
    // Click on the dark backdrop (outside the modal box) closes it.
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal(overlay);
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      overlays.forEach((overlay) => {
        if (!overlay.hidden) closeModal(overlay);
      });
    }
  });
}

/* ---------------------------------------------------------
   Theme picker
   Sets <html data-theme="..."> which drives every color
   variable in hub.css. Persisted to localStorage so the
   choice survives a reload (frontend-only, no backend call).
--------------------------------------------------------- */
function initThemePicker() {
  const swatches = document.querySelectorAll('.theme-swatch');
  const html = document.documentElement;

  const savedTheme = safeStorageGet('nexus-theme') || 'obsidian';
  applyTheme(savedTheme);

  swatches.forEach((swatch) => {
    swatch.addEventListener('click', () => {
      applyTheme(swatch.dataset.theme);
      safeStorageSet('nexus-theme', swatch.dataset.theme);
    });
  });

  function applyTheme(themeName) {
    html.setAttribute('data-theme', themeName);
    swatches.forEach((s) => s.classList.toggle('active', s.dataset.theme === themeName));
    window.dispatchEvent(new CustomEvent('nexus:theme-changed', { detail: { theme: themeName } }));
  }
}

/* ---------------------------------------------------------
   Settings panel
   Music/SFX volume sliders + animations toggle.
   Frontend-only: values are stored locally, no audio engine
   or backend wired up yet. Animations toggle actually disables
   CSS transitions/animations and pauses the particle field.
--------------------------------------------------------- */
function initSettingsPanel() {
  const musicSlider = document.getElementById('music-volume');
  const musicValue = document.getElementById('music-volume-value');
  const sfxSlider = document.getElementById('sfx-volume');
  const sfxValue = document.getElementById('sfx-volume-value');
  const animationsToggle = document.getElementById('animations-toggle');
  const html = document.documentElement;

  // Restore saved values, falling back to sensible defaults.
  const savedMusic = safeStorageGet('nexus-music-volume');
  const savedSfx = safeStorageGet('nexus-sfx-volume');
  const savedAnimations = safeStorageGet('nexus-animations');

  if (musicSlider && savedMusic !== null) {
    musicSlider.value = savedMusic;
  }
  if (sfxSlider && savedSfx !== null) {
    sfxSlider.value = savedSfx;
  }
  if (animationsToggle) {
    animationsToggle.checked = savedAnimations === null ? true : savedAnimations === 'true';
    setMotion(animationsToggle.checked, false);
  }

  updateLabel(musicValue, musicSlider);
  updateLabel(sfxValue, sfxSlider);

  if (musicSlider) {
    musicSlider.addEventListener('input', () => {
      updateLabel(musicValue, musicSlider);
      safeStorageSet('nexus-music-volume', musicSlider.value);
      // Hook point: wire this value into a real <audio> element's
      // .volume property once music tracks are added.
    });
  }

  if (sfxSlider) {
    sfxSlider.addEventListener('input', () => {
      updateLabel(sfxValue, sfxSlider);
      safeStorageSet('nexus-sfx-volume', sfxSlider.value);
      // Hook point: wire this value into sound-effect playback volume.
    });
  }

  if (animationsToggle) {
    animationsToggle.addEventListener('change', () => {
      setMotion(animationsToggle.checked, true);
      safeStorageSet('nexus-animations', String(animationsToggle.checked));
    });
  }

  function updateLabel(labelEl, sliderEl) {
    if (labelEl && sliderEl) labelEl.textContent = `${sliderEl.value}%`;
  }

  function setMotion(enabled, notify) {
    html.classList.toggle('motion-off', !enabled);
    if (notify) {
      window.dispatchEvent(new CustomEvent('nexus:motion-changed', { detail: { enabled } }));
    }
  }
}

/* ---------------------------------------------------------
   Card play buttons
   The Guess The Number card/hero button are real <a href="/menu">
   links (no JS needed). Disabled "Notify Me" buttons on
   Coming Soon games just get lightweight click feedback.
--------------------------------------------------------- */
function initCardPlayButtons() {
  const notifyButtons = document.querySelectorAll('.card-play[disabled]');
  notifyButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      // Buttons are disabled, so this is a no-op safeguard only;
      // kept as a hook point for a future "notify me" backend call.
    });
  });
}

/* ---------------------------------------------------------
   localStorage helpers
   Wrapped in try/catch so the hub still works if storage is
   unavailable (e.g. private browsing with storage disabled).
--------------------------------------------------------- */
function safeStorageGet(key) {
  try {
    return window.localStorage.getItem(key);
  } catch (e) {
    return null;
  }
}

function safeStorageSet(key, value) {
  try {
    window.localStorage.setItem(key, value);
  } catch (e) {
    /* ignore */
  }
}