// public/js/main.js

// 1) Use `const` for values that never change,
//    `let` only if you plan to reassign later.
const SPEED = 150;  // pixels per second
const GAP   = 0.05; // seconds between strokes

window.addEventListener('DOMContentLoaded', () => {
  console.log('🔥 main.js loaded & DOM ready');

  // —— DRAW-ANIMATION SETUP —— //
  const outlines = document.querySelectorAll('#logo path:not(.inner)');
  outlines.forEach((path, i) => {
    const length = path.getTotalLength();
    path.style.setProperty('--len', length);
    path.style.strokeDasharray  = length;
    path.style.strokeDashoffset = length;
    path.style.animation = `
      draw ${length / SPEED}s
      linear ${GAP * i}s
      forwards
    `;
  });

  // —— LIVE HIGHLIGHTING —— //
const textarea   = document.querySelector('textarea');
const previewEl  = document.getElementById('preview');

textarea.addEventListener('input', () => {
  // Copy text over
  previewEl.textContent = textarea.value;
  // Re-run Prism on that <code>
  Prism.highlightElement(previewEl);
});

  // —— SIDEBAR TOGGLE —— //
  const sidebar   = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggle-sidebar');
  console.log({ sidebar, toggleBtn });

  if (!sidebar || !toggleBtn) {
    console.error('⚠️ Could not find #sidebar or #toggle-sidebar in the DOM');
    return;
  }

  toggleBtn.addEventListener('click', () => {
    console.log('📣 toggle button clicked');
    sidebar.classList.toggle('hidden');
  });
});

// ——— Simple “ping” check ———
fetch('ping.json')
  .then(res => res.json())
  .then(data => {
    console.log('⏱  pong →', data);
    // e.g. turn your status-dot green/red:
    const dot = document.querySelector('#status-dot');
    if (dot) {
      dot.style.backgroundColor = data.status === 'ok' ? 'limegreen' : 'crimson';
    }
  })
  .catch(err => console.error('❌ ping failed', err));