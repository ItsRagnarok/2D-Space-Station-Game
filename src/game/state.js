// Single source of truth for the save: energy, resources, plants, crew, story progress.
// Acts only move forward. The only way back is the menu's "Reset total".
const KEY = 'orbital-harvest-save-v1';
export const DECAY_MS = 3000;          // -1% energy every 3 s (demo pace; real pace is tuned later)
export const GROW_MS = [7000, 9000];   // plant stage 1->2, 2->3 (demo pace)
const BED_TYPES = ['crystal', 'flora', 'mush', 'rare', 'crystal', 'flora'];

const fresh = () => ({
  v: 1, act: 1, started: false, introSeen: false, advancing: false,
  objDone: {}, flags: {}, counters: { harvest: 0, feed: 0, reactorFed: 0 },
  energy: 100, res: { crystal: 0, rare: 0, flora: 0, mush: 0 },
  beds: BED_TYPES.map((type, i) => ({ type, stage: 1 + (i % 3), t: 0 })),
  crew: { farmer: false, engineer: false },
  room: 'Hydroponics', pos: null,
});

function load() {
  try { const raw = localStorage.getItem(KEY); if (raw) { const d = JSON.parse(raw); if (d && d.v === 1) return { ...fresh(), ...d, advancing: false }; } } catch (e) { /* private mode / bad json */ }
  return fresh();
}

export const S = load();
const listeners = {};
export const on = (evt, fn) => { (listeners[evt] = listeners[evt] || []).push(fn); };
export const emit = (evt, arg) => (listeners[evt] || []).forEach((fn) => fn(arg));

let lastSave = 0;
export function save(force = true) {
  const n = Date.now();
  if (!force && n - lastSave < 4000) return;
  lastSave = n;
  try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) { /* ignore */ }
}

export function resetAll() {
  try { localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
  Object.keys(S).forEach((k) => delete S[k]);
  Object.assign(S, fresh());
}

export function setEnergy(e) {
  const v = Math.max(0, Math.min(100, e));
  if (v === S.energy) return;
  S.energy = v; emit('energy', v);
}

// Light level per energy (1 = full). Matches docs/REGULI.md.
export function ambient(e) {
  const p = [[0, 0.07], [25, 0.32], [50, 0.62], [75, 1.0]];
  if (e >= 75) return 1;
  for (let i = 0; i < p.length - 1; i++) if (e <= p[i + 1][0]) return p[i][1] + (p[i + 1][1] - p[i][1]) * (e - p[i][0]) / (p[i + 1][0] - p[i][0]);
  return 1;
}
export function energyState(e) {
  if (e >= 75) return ['Energie normală', '#2fe58a'];
  if (e >= 50) return ['Economie de energie', '#c8e84a'];
  if (e >= 25) return ['AVARIE · lumini de urgență', '#f2a93b'];
  if (e > 0) return ['BLACKOUT · doar lanterna', '#ff5a6a'];
  return ['BLACKOUT TOTAL', '#ff3a4a'];
}

let decayAcc = 0;
// Called every frame by whichever room is active, so plants keep growing and energy keeps draining between rooms.
export function tick(delta) {
  decayAcc += delta / DECAY_MS * (S.crew.engineer ? 0.7 : 1);
  while (decayAcc >= 1) { decayAcc -= 1; setEnergy(S.energy - 1); }
  if (S.energy >= 25) {
    const k = S.crew.farmer ? 1.5 : 1;
    S.beds.forEach((b) => {
      if (b.stage < 3) {
        b.t += delta * k;
        if (b.t >= GROW_MS[b.stage - 1]) { b.stage += 1; b.t = 0; emit('beds'); }
      }
    });
  }
  save(false);
}
if (typeof window !== 'undefined') window.__S = S;   // handy for debugging/tests
