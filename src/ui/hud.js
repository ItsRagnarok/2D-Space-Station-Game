import '@fontsource/rajdhani/600.css';
import '@fontsource/rajdhani/700.css';
import './hud.css';

const RES = [['crystal', 'Cristale'], ['rare', 'Rare'], ['flora', 'Floră'], ['mush', 'Ciuperci']];

export function createHud() {
  const ui = document.getElementById('ui');
  const isTouch = matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
  if (isTouch) document.body.classList.add('touch');
  ui.innerHTML = `
    <div id="energy" class="panel"><div class="name"><span>Odysseus</span><span id="epct">100%</span></div>
      <div class="bar"><i id="ebar" style="width:100%"></i></div><div class="state" id="estate">Energie normală</div></div>
    <div id="res" class="panel">${RES.map(([k, n]) => `<div><img src="assets/icons/${k}.png" alt=""><span>${n}</span><b id="r-${k}">0</b></div>`).join('')}</div>
    <div id="help" class="panel">WASD / săgeți · E acțiune · F lanternă · 1–5 energie (test)</div>
    <div id="prompt" class="panel"></div><div id="toast" class="panel"></div>
    <div id="stick"><i></i></div>
    <div id="fl" class="btn">Lanternă</div><div id="act" class="btn">Acțiune</div>
    <div id="ios-tip" class="panel">Pentru ecran complet pe iPhone: Distribuie → <b>Adaugă pe ecranul principal</b>, apoi deschide jocul de acolo.<br><button>Am înțeles</button></div>
    <div id="rotate">Rotește telefonul în modul landscape ca să joci.</div>`;
  const $ = (id) => document.getElementById(id);
  // iPhone Safari can't hide its bars from code: suggest installing to the home screen (fullscreen PWA).
  const standalone = navigator.standalone === true || matchMedia('(display-mode: standalone)').matches || matchMedia('(display-mode: fullscreen)').matches;
  const iOS = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  let seen = false; try { seen = localStorage.getItem('oh-ios-tip') === '1'; } catch (e) { /* private mode */ }
  if (iOS && !standalone && !seen) {
    const tip = $('ios-tip'); tip.style.display = 'block';
    tip.querySelector('button').addEventListener('click', () => { tip.style.display = 'none'; try { localStorage.setItem('oh-ios-tip', '1'); } catch (e) { /* ignore */ } });
  }
  // Android / desktop: go fullscreen + landscape on the first tap (needs a user gesture).
  if (!standalone) {
    const goFull = () => {
      const el = document.documentElement;
      (el.requestFullscreen ? el.requestFullscreen({ navigationUI: 'hide' }) : Promise.reject()).then(() => screen.orientation && screen.orientation.lock && screen.orientation.lock('landscape').catch(() => {})).catch(() => {});
      window.removeEventListener('pointerdown', goFull);
    };
    if (isTouch) window.addEventListener('pointerdown', goFull, { once: true });
  }
  document.addEventListener('gesturestart', (e) => e.preventDefault());
  let toastTimer;
  return {
    isTouch,
    setEnergy(e, label, color) {
      $('epct').textContent = Math.round(e) + '%';
      const bar = $('ebar'); bar.style.width = e + '%'; bar.style.setProperty('--c', color);
      const st = $('estate'); st.textContent = label; st.style.setProperty('--c', color);
    },
    setRes(r) { RES.forEach(([k]) => { $('r-' + k).textContent = r[k]; }); },
    prompt(text) { const p = $('prompt'); if (text) { p.textContent = text; p.classList.add('show'); } else p.classList.remove('show'); },
    toast(msg) { const t = $('toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 1600); },
  };
}
