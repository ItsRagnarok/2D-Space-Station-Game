import '@fontsource/rajdhani/600.css';
import '@fontsource/rajdhani/700.css';
import './hud.css';
import { resetAll } from '../game/state.js';

const RES = [['crystal', 'Cristale'], ['rare', 'Rare'], ['flora', 'Floră'], ['mush', 'Ciuperci']];
const DEV = new URLSearchParams(location.search).has('dev');

// One persistent DOM overlay shared by every room. Rooms only call the small API at the bottom.
export const ui = {
  isTouch: false, dev: DEV, dialogOpen: false, menuOpen: false, zoomOffset: 0, onZoom: null, onMap: null,
  get blocking() { return this.dialogOpen || this.menuOpen; },
};

export function initUi() {
  if (ui.ready) return ui;
  ui.ready = true;
  const root = document.getElementById('ui');
  ui.isTouch = matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
  if (ui.isTouch) document.body.classList.add('touch');
  root.innerHTML = `
    <div id="energy" class="panel"><div class="name"><span>Odysseus</span><span id="epct">100%</span></div>
      <div class="bar"><i id="ebar" style="width:100%"></i></div><div class="state" id="estate">Energie normală</div></div>
    <div id="obj" class="panel"><div class="name" id="otitle"></div><div id="olist"></div></div>
    <div id="res" class="panel">${RES.map(([k, n]) => `<div><img src="assets/icons/${k}.png" alt=""><span>${n}</span><b id="r-${k}">0</b></div>`).join('')}</div>
    <div id="menu-btn" class="panel">Meniu</div>
    <div id="tools" class="panel"><button id="t-map">Hartă</button><button id="t-zout" aria-label="Depărtează">−</button><button id="t-zin" aria-label="Apropie">+</button></div>
    <div id="mapinfo" class="panel"><div class="mt"></div><div class="ms"></div><div class="mb"><button id="map-go">Teleportare</button><button id="map-close">Închide harta</button></div></div>
    <div id="help" class="panel">WASD / săgeți · click stânga acțiune · click dreapta lanternă · rotiță = zoom · M hartă · Esc meniu${DEV ? ' · 1–5 energie (dev)' : ''}</div>
    <div id="prompt" class="panel"></div><div id="toast" class="panel"></div><div id="banner"><small></small><b></b></div>
    <div id="dialog" class="panel"><div class="who"></div><div class="txt"></div><div class="next">▶ acțiune</div></div>
    <div id="menu"><div class="box panel">
      <div class="mt">Meniu</div>
      <div id="m-main"><button id="m-cont">Continuă</button><button id="m-help">Controale</button><button id="m-reset" class="danger">Reset total</button></div>
      <div id="m-info" style="display:none"><p>PC: WASD / săgeți · <b>click stânga</b> acțiune · <b>click dreapta</b> lanternă · Esc meniu.</p><p>Telefon: joystick stânga, butoanele Acțiune și Lanternă.</p><button id="m-back">Înapoi</button></div>
      <div id="m-confirm" style="display:none"><p><b>Reset total</b> șterge tot progresul: actele, resursele, echipajul. Povestea reîncepe de la Actul 1. Nu se poate anula.</p><button id="m-no">Anulează</button><button id="m-yes" class="danger">Șterge tot</button></div>
    </div></div>
    <div id="stick"><i></i></div><div id="fl" class="btn">Lanternă</div><div id="act" class="btn">Acțiune</div>
    <div id="ios-tip" class="panel">Pentru ecran complet pe iPhone: Distribuie → <b>Adaugă pe ecranul principal</b>, apoi deschide jocul de acolo.<br><button>Am înțeles</button></div>
    <div id="dbg" class="panel"></div>
    <div id="rotate">Rotește telefonul în modul landscape ca să joci.</div>`;
  const $ = (id) => document.getElementById(id);

  // ---- platform niceties ----
  const standalone = navigator.standalone === true || matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches;
  const iOS = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  let seen = false; try { seen = localStorage.getItem('oh-ios-tip') === '1'; } catch (e) { /* private mode */ }
  if (iOS && !standalone && !seen) {
    const tip = $('ios-tip'); tip.style.display = 'block';
    tip.querySelector('button').addEventListener('click', () => { tip.style.display = 'none'; try { localStorage.setItem('oh-ios-tip', '1'); } catch (e) { /* ignore */ } });
  }
  if (!standalone && ui.isTouch) {
    const goFull = () => {
      const el = document.documentElement;
      (el.requestFullscreen ? el.requestFullscreen({ navigationUI: 'hide' }) : Promise.reject()).then(() => screen.orientation && screen.orientation.lock && screen.orientation.lock('landscape').catch(() => {})).catch(() => {});
      window.removeEventListener('pointerdown', goFull);
    };
    window.addEventListener('pointerdown', goFull, { once: true });
  }
  document.addEventListener('gesturestart', (e) => e.preventDefault());
  let taps = [], dbgOn = false;
  $('energy').addEventListener('pointerdown', () => {
    const n = Date.now(); taps = taps.filter((t) => n - t < 1500); taps.push(n);
    if (taps.length >= 3) { taps = []; dbgOn = !dbgOn; $('dbg').style.display = dbgOn ? 'block' : 'none'; }
  });
  setInterval(() => { if (dbgOn && ui.debugFn) $('dbg').textContent = ui.debugFn(); }, 400);

  // ---- HUD API ----
  let toastTimer, bannerTimer;
  ui.setEnergy = (e, label, color) => {
    $('epct').textContent = Math.round(e) + '%';
    const bar = $('ebar'); bar.style.width = e + '%'; bar.style.setProperty('--c', color);
    const st = $('estate'); st.textContent = label; st.style.setProperty('--c', color);
  };
  ui.setRes = (r) => RES.forEach(([k]) => { $('r-' + k).textContent = r[k]; });
  ui.setObjectives = ({ title, list }) => {
    $('otitle').textContent = title;
    $('olist').innerHTML = list.map((o) => `<div class="${o.done ? 'ok' : ''}${o.soon ? ' soon' : ''}"><b>${o.done ? '✓' : '○'}</b>${o.text}${o.progress ? ` <i>${o.progress}</i>` : ''}${o.soon ? ' <i>în curând</i>' : ''}</div>`).join('');
  };
  ui.prompt = (text) => { const p = $('prompt'); if (text && !ui.blocking) { p.textContent = text; p.classList.add('show'); } else p.classList.remove('show'); };
  ui.toast = (msg) => { const t = $('toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 1800); };
  ui.banner = (small, big) => { const b = $('banner'); b.querySelector('small').textContent = small; b.querySelector('b').textContent = big; b.classList.add('show'); clearTimeout(bannerTimer); bannerTimer = setTimeout(() => b.classList.remove('show'), 3200); };

  // ---- dialog (advance with Action / tap) ----
  let queue = [], doneCb = null;
  const showLine = () => { const l = queue[0]; $('dialog').querySelector('.who').textContent = l.who; $('dialog').querySelector('.txt').textContent = l.text; };
  ui.dialog = (lines, cb) => {
    if (!lines || !lines.length) { if (cb) cb(); return; }
    queue = lines.slice(); doneCb = cb || null; ui.dialogOpen = true; $('dialog').classList.add('show'); showLine();
  };
  ui.advance = () => {
    queue.shift();
    if (queue.length) { showLine(); return; }
    ui.dialogOpen = false; $('dialog').classList.remove('show');
    const cb = doneCb; doneCb = null; if (cb) cb();
  };
  $('dialog').addEventListener('pointerdown', (e) => { ui.advance(); e.preventDefault(); });

  // ---- zoom + station map ----
  ui.zoomBy = (d) => { const z = Math.max(-3, Math.min(3, ui.zoomOffset + d)); if (z === ui.zoomOffset) return; ui.zoomOffset = z; if (ui.onZoom) ui.onZoom(); };
  ui.openMap = () => { if (!ui.blocking && ui.onMap) ui.onMap(); };
  const tap = (id, fn) => $(id).addEventListener('pointerdown', (e) => { fn(); e.preventDefault(); });
  tap('t-zin', () => ui.zoomBy(1)); tap('t-zout', () => ui.zoomBy(-1)); tap('t-map', () => ui.openMap());
  let mapGo = null, mapClose = null;
  ui.mapMode = (on, go, close) => { mapGo = go; mapClose = close; $('mapinfo').classList.toggle('show', false); $('t-map').textContent = on ? 'Înapoi' : 'Hartă'; };
  ui.showMapInfo = ({ title, text, canGo }) => { const m = $('mapinfo'); m.querySelector('.mt').textContent = title; m.querySelector('.ms').textContent = text; $('map-go').style.display = canGo ? '' : 'none'; m.classList.add('show'); };
  $('map-go').addEventListener('click', () => mapGo && mapGo());
  $('map-close').addEventListener('click', () => mapClose && mapClose());

  // ---- menu ----
  const show = (id) => ['m-main', 'm-info', 'm-confirm'].forEach((m) => { $(m).style.display = m === id ? 'block' : 'none'; });
  ui.toggleMenu = (force) => {
    ui.menuOpen = force === undefined ? !ui.menuOpen : force;
    $('menu').classList.toggle('show', ui.menuOpen);
    if (ui.menuOpen) show('m-main');
  };
  $('menu-btn').addEventListener('pointerdown', (e) => { ui.toggleMenu(); e.preventDefault(); });
  $('m-cont').addEventListener('click', () => ui.toggleMenu(false));
  $('m-help').addEventListener('click', () => show('m-info'));
  $('m-back').addEventListener('click', () => show('m-main'));
  $('m-reset').addEventListener('click', () => show('m-confirm'));
  $('m-no').addEventListener('click', () => show('m-main'));
  $('m-yes').addEventListener('click', () => { resetAll(); location.reload(); });
  return ui;
}
