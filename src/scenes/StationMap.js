import Phaser from 'phaser';
import { S, ambient } from '../game/state.js';
import { ui } from '../ui/ui.js';
import { controls } from '../ui/controls.js';

// The whole station seen from space. Tap/click a module to select it, then "Teleportare".
// Hull modules are placed in station coordinates (centre ~ 280,170).
const MODULES = [
  { key: 'Hydroponics', label: 'Hidroponică', frame: 'hull_hydro', x: 120, y: 170, w: 128, h: 92 },
  { key: 'Command', label: 'Centrul de comandă', frame: 'hull_command', x: 280, y: 170, w: 96, h: 84 },
  { key: 'Reactor', label: 'Reactor', frame: 'hull_reactor', x: 440, y: 170, w: 104, h: 92 },
  { key: 'Hangar', label: 'Hangar', frame: 'hull_hangar', x: 280, y: 274, w: 140, h: 84 },
  { key: 'Lab', label: 'Laborator', frame: 'hull_lab', x: 280, y: 74, w: 96, h: 70, locked: true },
];

export default class StationMap extends Phaser.Scene {
  constructor() { super('StationMap'); }

  create() {
    window.__orbital = this;
    document.body.classList.add('inmap');
    const cam = this.cameras.main; cam.setBackgroundColor('#02040a'); cam.fadeIn(250);
    this.stars = this.add.tileSprite(280, 170, 3600, 2400, 'stars_tile').setDepth(-20);
    this.add.image(560, 320, 'planet_rock').setDepth(-19);

    const img = (frame, x, y, d = 1) => this.add.image(x, y, 'o', frame).setDepth(d);
    this.parts = [];
    // connectors, solar arrays, antennas, engines
    [[200, 170], [360, 170]].forEach(([x, y]) => this.parts.push(img('conn_h', x, y)));
    [[280, 118], [280, 224]].forEach(([x, y]) => this.parts.push(img('conn_v', x, y)));
    [[120, 100], [120, 240]].forEach(([x, y]) => this.parts.push(img('solar_array', x, y)));
    [[440, 100], [440, 240]].forEach(([x, y]) => this.parts.push(img('solar_array', x, y)));
    [[440, 128], [232, 128]].forEach(([x, y]) => this.parts.push(img('antenna', x, y, 2)));
    this.engines = [[22, 150], [22, 190]].map(([x, y]) => this.add.sprite(x, y, 'o', 'engine_0').setDepth(1));
    this.flameT = 0;

    this.mods = MODULES.map((m) => {
      const spr = this.add.image(m.x, m.y, 'o', m.frame).setDepth(3);
      const zone = this.add.zone(m.x, m.y, m.w, m.h).setInteractive();
      zone.on('pointerup', (p) => { if (!this.dragged) this.select(m); });
      this.parts.push(spr);
      this.add.text(m.x, m.y + m.h / 2 - 5, m.label, { fontFamily: 'Rajdhani, sans-serif', fontSize: '9px', fontStyle: '700', color: m.locked ? '#a8a4d8' : '#d8fff0', backgroundColor: '#02040acc', padding: { x: 3, y: 1 } }).setOrigin(0.5, 1).setDepth(6).setResolution(2);
      return { ...m, spr };
    });
    this.sel = null;
    this.gfx = this.add.graphics().setDepth(8);

    // pan by dragging (mouse or touch); wheel/pinch/buttons zoom through ui.zoomBy
    this.dragged = false;
    this.input.on('pointermove', (p) => {
      if (!p.isDown) return;
      const d = Math.hypot(p.x - p.downX, p.y - p.downY);
      if (d > 6) this.dragged = true;
      if (this.dragged) { cam.scrollX -= (p.x - p.prevPosition.x) / cam.zoom; cam.scrollY -= (p.y - p.prevPosition.y) / cam.zoom; }
    });
    this.input.on('pointerdown', () => { this.dragged = false; });
    this.input.keyboard.on('keydown-ENTER', () => this.go());
    ui.onZoom = () => this.fit(true);
    ui.onMap = () => this.close();
    ui.mapMode(true, () => this.go(), () => this.close());
    this.scale.on('resize', () => this.fit(false), this);
    this.events.once('shutdown', () => { document.body.classList.remove('inmap'); ui.mapMode(false); ui.onZoom = null; ui.onMap = null; });
    this.fit(false);
    const here = this.mods.find((m) => m.key === S.room); if (here) this.select(here, true);
  }

  fit(keepCenter) {
    const cam = this.cameras.main;
    const base = Phaser.Math.Clamp(Math.floor(Math.min(cam.width / 580, cam.height / 350)), 1, 5);
    const z = Phaser.Math.Clamp(base + ui.zoomOffset, 1, 7);
    const cx = keepCenter ? cam.scrollX + cam.width / 2 / cam.zoom : 280, cy = keepCenter ? cam.scrollY + cam.height / 2 / cam.zoom : 170;
    cam.setZoom(z); cam.centerOn(cx, cy); cam.roundPixels = true;
  }

  status(m) {
    if (m.locked) return 'În construcție. Se deschide în Actul 3, odată cu laboratorul.';
    if (m.key === 'Hydroponics') return `${S.beds.filter((b) => b.stage === 3).length} din ${S.beds.length} paturi gata de recoltat.`;
    if (m.key === 'Command') return 'Terminal ORION, masă holografică, criosomn.';
    if (m.key === 'Reactor') return S.energy >= 5 ? 'Reactorul funcționează.' : 'Reactorul e rece. Are nevoie de combustibil.';
    return S.flags.shipReady ? 'Nava Meridian e pregătită pentru zbor.' : 'Nava Meridian așteaptă pe pistă.';
  }

  select(m, quiet) {
    this.sel = m;
    ui.showMapInfo({ title: m.label + (m.key === S.room ? ' · ești aici' : ''), text: this.status(m), canGo: !m.locked });
  }

  go() {
    const m = this.sel; if (!m || m.locked) return;
    this.cameras.main.fadeOut(250);
    this.cameras.main.once('camerafadeoutcomplete', () => this.scene.start(m.key, { spawn: m.key === S.room ? 'resume' : 'default' }));
  }
  close() {
    this.cameras.main.fadeOut(200);
    this.cameras.main.once('camerafadeoutcomplete', () => this.scene.start(S.room, { spawn: 'resume' }));
  }

  update(time, delta) {
    controls.update();
    controls.takeAction(); controls.takeFlash();      // mouse clicks only select; Enter teleports
    this.stars.tilePositionX += delta * 0.006;                       // the station drifts: stars slide by
    this.flameT += delta;
    const f = Math.floor(this.flameT / 120) % 3;
    this.engines.forEach((e) => e.setFrame(`engine_${f}`));
    const a = ambient(S.energy), t = Phaser.Display.Color.GetColor(70 + 185 * a, 78 + 177 * a, 100 + 155 * a);
    this.mods.forEach((m) => m.spr.setTint(m.key === 'Reactor' && S.energy >= 5 ? 0xffffff : t));
    this.parts.forEach((p) => { if (!this.mods.some((m) => m.spr === p)) p.setTint(t); });
    const g = this.gfx; g.clear();
    const here = this.mods.find((m) => m.key === S.room);
    if (here) { const r = 3 + (Math.floor(time / 300) % 3); g.lineStyle(1, 0xf2a93b, 1); g.strokeRect(here.x - here.w / 2 - r, here.y - here.h / 2 - r, here.w + r * 2, here.h + r * 2); }
    if (this.sel) { g.lineStyle(1, 0x2fe58a, 1); g.strokeRect(this.sel.x - this.sel.w / 2 - 2, this.sel.y - this.sel.h / 2 - 2, this.sel.w + 4, this.sel.h + 4); }
  }
}
