/* ============================================================
   ZORO HUB — TIC TAC TOE BACKGROUND CANVAS
   ============================================================
   Pure canvas, no libraries. Draws:
     - drifting glowing particles
     - thin connecting lines between nearby particles (neural net look)
     - a soft glow that follows the mouse
     - a subtle parallax shift of the whole particle field based on
       mouse position
   Performance:
     - particle count scales with viewport area, capped
     - the loop pauses entirely when the tab is hidden
     - connections are only checked within a limited radius
   ============================================================ */

(function () {
  'use strict';

  const canvas = document.getElementById('tttBackgroundCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = 0;
  let height = 0;
  let dpr = Math.min(window.devicePixelRatio || 1, 2);

  const mouse = { x: null, y: null, active: false };
  const parallax = { x: 0, y: 0 };

  let particles = [];
  let animationFrameId = null;

  const CONNECT_RADIUS = 130;
  const MAX_PARTICLES = 110;

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2);

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    buildParticles();
  }

  function buildParticles() {
    const area = width * height;
    const count = Math.min(MAX_PARTICLES, Math.round(area / 14000));

    particles = new Array(count).fill(null).map(() => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.25,
      vy: (Math.random() - 0.5) * 0.25,
      radius: Math.random() * 1.6 + 0.6,
      hue: Math.random() > 0.5 ? 'blue' : 'purple',
      twinkleOffset: Math.random() * Math.PI * 2
    }));
  }

  function colorFor(hue, alpha) {
    return hue === 'blue'
      ? `rgba(77, 171, 247, ${alpha})`
      : `rgba(168, 85, 247, ${alpha})`;
  }

  function step(timestamp) {
    ctx.clearRect(0, 0, width, height);

    // gentle parallax easing toward mouse position
    if (mouse.active) {
      const targetX = ((mouse.x / width) - 0.5) * 18;
      const targetY = ((mouse.y / height) - 0.5) * 18;
      parallax.x += (targetX - parallax.x) * 0.04;
      parallax.y += (targetY - parallax.y) * 0.04;
    } else {
      parallax.x += (0 - parallax.x) * 0.04;
      parallax.y += (0 - parallax.y) * 0.04;
    }

    // mouse glow
    if (mouse.active) {
      const glow = ctx.createRadialGradient(mouse.x, mouse.y, 0, mouse.x, mouse.y, 220);
      glow.addColorStop(0, 'rgba(120, 130, 250, 0.10)');
      glow.addColorStop(1, 'rgba(120, 130, 250, 0)');
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, width, height);
    }

    // update + draw particles
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < -20) p.x = width + 20;
      if (p.x > width + 20) p.x = -20;
      if (p.y < -20) p.y = height + 20;
      if (p.y > height + 20) p.y = -20;

      const twinkle = 0.55 + Math.sin(timestamp * 0.0015 + p.twinkleOffset) * 0.35;
      const drawX = p.x + parallax.x;
      const drawY = p.y + parallax.y;

      ctx.beginPath();
      ctx.arc(drawX, drawY, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = colorFor(p.hue, twinkle);
      ctx.shadowColor = colorFor(p.hue, 0.8);
      ctx.shadowBlur = 6;
      ctx.fill();
    }
    ctx.shadowBlur = 0;

    // neural network connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const a = particles[i];
        const b = particles[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < CONNECT_RADIUS) {
          const alpha = (1 - dist / CONNECT_RADIUS) * 0.16;
          ctx.beginPath();
          ctx.moveTo(a.x + parallax.x, a.y + parallax.y);
          ctx.lineTo(b.x + parallax.x, b.y + parallax.y);
          ctx.strokeStyle = `rgba(150, 160, 255, ${alpha})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }

    animationFrameId = requestAnimationFrame(step);
  }

  function start() {
    if (animationFrameId === null) {
      animationFrameId = requestAnimationFrame(step);
    }
  }

  function stop() {
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  }

  window.addEventListener('resize', resize);

  window.addEventListener('mousemove', (e) => {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
    mouse.active = true;
  });

  window.addEventListener('mouseleave', () => {
    mouse.active = false;
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      stop();
    } else {
      start();
    }
  });

  resize();
  start();
})();