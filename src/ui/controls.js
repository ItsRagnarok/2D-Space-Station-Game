// Unified input (DOM-only, so it survives scene changes): keyboard, mouse (left = action, right = flashlight), touch joystick + buttons.
import { ui } from './ui.js';

export const controls = {
  x: 0, y: 0, _act: false, _flash: false,
  takeAction() { const a = this._act; this._act = false; return a; },
  takeFlash() { const a = this._flash; this._flash = false; return a; },
  debugEnergy: () => null,
};

export function initControls() {
  if (controls.ready) return controls;
  controls.ready = true;
  const down = new Set();
  const dev = {};
  window.addEventListener('keydown', (e) => {
    const k = e.key.toLowerCase();
    if (['arrowup', 'arrowdown', 'arrowleft', 'arrowright', ' '].includes(k)) e.preventDefault();
    if (e.repeat) return;
    down.add(k);
    if (k === 'e' || k === ' ' || k === 'enter') controls._act = true;
    if (k === 'f') controls._flash = true;
    if (k === 'escape') ui.toggleMenu();
    if (ui.dev && '12345'.includes(k)) dev.set = { 1: 100, 2: 60, 3: 35, 4: 15, 5: 0 }[k];
  });
  window.addEventListener('keyup', (e) => down.delete(e.key.toLowerCase()));
  window.addEventListener('blur', () => down.clear());
  controls.debugEnergy = () => { const v = dev.set; dev.set = undefined; return v === undefined ? null : v; };

  const game = document.getElementById('game');
  window.addEventListener('contextmenu', (e) => e.preventDefault());
  game.addEventListener('mousedown', (e) => {
    if (e.button === 2) controls._flash = true; else if (e.button === 0) controls._act = true;
  });

  const stick = document.getElementById('stick'), knob = stick.querySelector('i');
  let touchVec = { x: 0, y: 0 }, pid = null;
  const move = (e) => {
    const r = stick.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    let dx = (e.clientX - cx) / (r.width / 2), dy = (e.clientY - cy) / (r.height / 2);
    const m = Math.hypot(dx, dy); if (m > 1) { dx /= m; dy /= m; }
    touchVec = { x: Math.abs(dx) < .18 ? 0 : dx, y: Math.abs(dy) < .18 ? 0 : dy };
    knob.style.transform = `translate(${dx * 31}px, ${dy * 31}px)`;
  };
  const end = () => { pid = null; touchVec = { x: 0, y: 0 }; knob.style.transform = ''; };
  stick.addEventListener('pointerdown', (e) => { pid = e.pointerId; stick.setPointerCapture(pid); move(e); e.preventDefault(); });
  stick.addEventListener('pointermove', (e) => { if (e.pointerId === pid) move(e); });
  stick.addEventListener('pointerup', end); stick.addEventListener('pointercancel', end);
  const bind = (id, fn) => document.getElementById(id).addEventListener('pointerdown', (e) => { fn(); e.preventDefault(); });
  bind('act', () => { controls._act = true; }); bind('fl', () => { controls._flash = true; });

  controls.update = () => {
    let x = (down.has('d') || down.has('arrowright') ? 1 : 0) - (down.has('a') || down.has('arrowleft') ? 1 : 0);
    let y = (down.has('s') || down.has('arrowdown') ? 1 : 0) - (down.has('w') || down.has('arrowup') ? 1 : 0);
    if (!x && !y) { x = touchVec.x; y = touchVec.y; }
    controls.x = x; controls.y = y;
  };
  return controls;
}
