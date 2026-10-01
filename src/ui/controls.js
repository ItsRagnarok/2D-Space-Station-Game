// Unified input: keyboard (WASD/arrows) + touch joystick. The game only reads { x, y } and edge-triggered actions.
export function createControls(scene) {
  const c = { x: 0, y: 0, _act: false, _flash: false };
  const k = scene.input.keyboard.addKeys('W,A,S,D,UP,DOWN,LEFT,RIGHT,E,SPACE,F,ONE,TWO,THREE,FOUR,FIVE', false);
  scene.input.keyboard.on('keydown-E', () => { c._act = true; });
  scene.input.keyboard.on('keydown-SPACE', () => { c._act = true; });
  scene.input.keyboard.on('keydown-F', () => { c._flash = true; });
  scene.input.mouse.disableContextMenu();
  scene.input.on('pointerdown', (ptr) => {
    if (ptr.wasTouch || (ptr.event && ptr.event.pointerType && ptr.event.pointerType !== 'mouse')) return;
    if (ptr.rightButtonDown()) c._flash = true; else if (ptr.leftButtonDown()) c._act = true;
  });
  const stick = document.getElementById('stick'), knob = stick && stick.querySelector('i');
  let touchVec = { x: 0, y: 0 }, pid = null;
  const move = (e) => {
    const r = stick.getBoundingClientRect(), cx = r.left + r.width / 2, cy = r.top + r.height / 2;
    let dx = (e.clientX - cx) / (r.width / 2), dy = (e.clientY - cy) / (r.height / 2);
    const m = Math.hypot(dx, dy); if (m > 1) { dx /= m; dy /= m; }
    touchVec = { x: Math.abs(dx) < .18 ? 0 : dx, y: Math.abs(dy) < .18 ? 0 : dy };
    knob.style.transform = `translate(${dx * 36}px, ${dy * 36}px)`;
  };
  const end = () => { pid = null; touchVec = { x: 0, y: 0 }; if (knob) knob.style.transform = ''; };
  if (stick) {
    stick.addEventListener('pointerdown', (e) => { pid = e.pointerId; stick.setPointerCapture(pid); move(e); e.preventDefault(); });
    stick.addEventListener('pointermove', (e) => { if (e.pointerId === pid) move(e); });
    stick.addEventListener('pointerup', end); stick.addEventListener('pointercancel', end);
  }
  const bind = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener('pointerdown', (e) => { fn(); e.preventDefault(); }); };
  bind('act', () => { c._act = true; }); bind('fl', () => { c._flash = true; });
  c.update = () => {
    let x = (k.D.isDown || k.RIGHT.isDown ? 1 : 0) - (k.A.isDown || k.LEFT.isDown ? 1 : 0);
    let y = (k.S.isDown || k.DOWN.isDown ? 1 : 0) - (k.W.isDown || k.UP.isDown ? 1 : 0);
    if (!x && !y) { x = touchVec.x; y = touchVec.y; }
    c.x = x; c.y = y;
  };
  c.takeAction = () => { const a = c._act; c._act = false; return a; };
  c.takeFlash = () => { const a = c._flash; c._flash = false; return a; };
  c.debugEnergy = () => (k.ONE.isDown ? 100 : k.TWO.isDown ? 60 : k.THREE.isDown ? 35 : k.FOUR.isDown ? 15 : k.FIVE.isDown ? 0 : null);
  return c;
}
