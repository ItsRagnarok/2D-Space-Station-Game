import Phaser from 'phaser';
import { S, tick, save, setEnergy, ambient } from './state.js';
import { updateStory, objectivesView, ACTS } from './story.js';
import { ui } from '../ui/ui.js';
import { controls } from '../ui/controls.js';
import { MODULES, CORRIDORS, RW, RH, WW, WH } from './layout.js';

const SPEED = 58, B = 10;
const ZOOMS = [0.4, 0.5, 0.65, 0.8, 1, 1.5, 2, 3, 4, 5, 6];

// Splits [from, to] into the ranges that are NOT inside `gaps` (used for hull strips and walls with openings).
function segments(from, to, gaps) {
  const out = []; let a = from;
  [...gaps].sort((p, q) => p[0] - q[0]).forEach(([g0, g1]) => { if (g0 > a) out.push([a, g0]); a = Math.max(a, g1); });
  if (a < to) out.push([a, to]);
  return out;
}

// Handed to each room module: local coordinates in, world coordinates out.
class Ctx {
  constructor(scene, def) { this.scene = scene; this.def = def; this.ox = def.ox; this.oy = def.oy; }
  X(x) { return this.ox + x; } Y(y) { return this.oy + y; }
  prop(frame, x, feet, solid, anim) { return this.scene.prop(frame, this.X(x), this.Y(feet), solid, anim); }
  solid(cx, cy, w, h) { this.scene.solid(this.X(cx), this.Y(cy), w, h); }
  shade(x, feet, w) { this.scene.shade(this.X(x), this.Y(feet), w); }
  sprite(x, y, frame, o = {}) {
    const s = this.scene.add.sprite(this.X(x), this.Y(y), 'o', frame);
    if (o.origin) s.setOrigin(o.origin[0], o.origin[1]);
    s.setDepth(o.z !== undefined ? o.z : this.Y(y));
    if (o.scale) s.setScale(o.scale); if (o.alpha !== undefined) s.setAlpha(o.alpha); if (o.anim) s.play(o.anim);
    return s;
  }
  light(cfg) { return this.scene.addLight({ ...cfg, x: this.X(cfg.x), y: this.Y(cfg.y) }); }
  interact(it) { return this.scene.addInteractable({ ...it, x: this.X(it.x), y: this.Y(it.y) }); }
  npc(cfg) { return this.scene.addNpc({ ...cfg, x: this.X(cfg.x), y: this.Y(cfg.y) }); }
  time(delay, fn) { this.scene.time.addEvent({ delay, loop: true, callback: fn }); }
}

// The whole station in one continuous world: rooms, corridors, doors, the player, light and camera.
export default class Station extends Phaser.Scene {
  constructor() { super('Station'); }

  create() {
    window.__orbital = this;
    this.solids = this.physics.add.staticGroup();
    this.interactables = []; this.lights = []; this.doors = []; this.zones = []; this.modules = [];
    this.facing = 'down'; this.acting = 0; this.storyAcc = 0; this.posAcc = 0; this.overview = false; this.cur = null;
    this.flashlight = false; this.flashAuto = false;
    this.physics.world.setBounds(0, 0, WW, WH);
    this.buildSpace();
    MODULES.forEach((def) => this.buildModule(def));
    CORRIDORS.forEach((c) => this.buildCorridor(c));
    this.buildLighting();
    this.buildPlayer();
    this.setupCamera();
    this.cameras.main.fadeIn(250);
    this.scale.on('resize', this.setupCamera, this);
    this.events.once('shutdown', () => this.scale.off('resize', this.setupCamera, this));
    ui.onZoom = () => this.onZoom();
    ui.onMap = () => this.toggleOverview();
    ui.debugFn = () => `inner ${innerWidth}x${innerHeight} · visual ${window.visualViewport ? Math.round(window.visualViewport.width) + 'x' + Math.round(window.visualViewport.height) : '-'} · dpr ${devicePixelRatio} · game ${this.scale.width}x${this.scale.height} · zoom ${this.cameras.main.zoom.toFixed(2)} · standalone ${navigator.standalone === true}`;
    this.input.on('pointermove', (p) => {
      if (!this.overview || !p.isDown) return;
      if (Math.hypot(p.x - p.downX, p.y - p.downY) > 6) this.dragged = true;
      if (this.dragged) { const c = this.cameras.main; c.scrollX -= (p.x - p.prevPosition.x) / c.zoom; c.scrollY -= (p.y - p.prevPosition.y) / c.zoom; }
    });
    this.input.on('pointerdown', () => { this.dragged = false; });
    this.input.on('pointerup', (p) => { if (this.overview && !this.dragged) this.pickModule(p.worldX, p.worldY); });
    this.input.keyboard.on('keydown-ENTER', () => { if (this.overview) this.goSelected(); });
    ui.setRes(S.res); ui.setObjectives(objectivesView()); setEnergy(S.energy);
    if (!S.introSeen) { S.introSeen = true; ui.banner('Actul 1', 'Trezirea'); ui.dialog(ACTS[0].intro); }
  }

  // ---------- world building ----------
  buildSpace() {
    this.add.tileSprite(WW / 2, WH / 2, 5000, 4000, 'stars_tile').setScrollFactor(0.5).setDepth(-30);
    this.add.image(WW - 90, WH + 20, 'planet_rock').setScrollFactor(0.85).setDepth(-29);
    const arm = (x, y, w, h) => this.add.rectangle(x + w / 2, y + h / 2, w, h, 0x4e5562).setStrokeStyle(1, 0x1a1d24).setDepth(4);
    const img = (frame, x, y, d = 3) => this.add.image(x, y, 'o', frame).setDepth(d);
    // solar arrays on struts above and below the hydroponics and reactor modules
    [[312, 252], [312, 568], [1176, 252], [1176, 568]].forEach(([x, y]) => { img('solar_array', x, y); arm(x - 3, y < 400 ? y + 17 : y - 28, 6, y < 400 ? 31 : 22); });
    [[1176, 568]].forEach(() => 0);
    this.engines = [[74, 380], [74, 450]].map(([x, y]) => this.add.sprite(x, y, 'o', 'engine_0').setDepth(3));
    [[1290, 288], [700, 288], [200, 288]].forEach(([x, y]) => img('antenna', x, y, 6));
    this.engineT = 0;
  }

  buildModule(def) {
    const { ox, oy } = def, cls = def.cls, gaps = def.gaps || {};
    const PAD = B + 4, acc = def.accent || 0x25d0cf;
    const rt = this.add.renderTexture(ox - PAD, oy - PAD, RW + 2 * PAD, RH + 2 * PAD).setOrigin(0).setDepth(0);
    const opts = { originX: 0, originY: 0 };
    const rnd = new Phaser.Math.RandomDataGenerator([def.key]);
    const special = cls.SPECIALS || {};
    for (let ty = 0; ty < 11; ty++) for (let tx = 0; tx < 24; tx++) rt.stamp('o', special[`${tx},${ty}`] || `floor_${rnd.between(0, 5)}`, PAD + tx * 16, PAD + 44 + ty * 16, opts);
    for (let x = 0; x < RW; x += 120) rt.stamp('o', 'wall_120', PAD + x, PAD, opts);
    const fr = (color, x, y, w, h, a = 1) => rt.fill(color, a, x - (ox - PAD), y - (oy - PAD), w, h);

    // floor detail: darker perimeter band with accent studs, orange light trails, recessed panels
    const rd = new Phaser.Math.RandomDataGenerator([def.key + 'd']);
    fr(0x12151a, ox, oy + 44, 6, RH - 44, 0.8); fr(0x12151a, ox + RW - 6, oy + 44, 6, RH - 44, 0.8); fr(0x12151a, ox, oy + RH - 6, RW, 6, 0.8);
    for (let i = 52; i < RH - 8; i += 16) { fr(acc, ox + 2, oy + i, 2, 2); fr(acc, ox + RW - 4, oy + i, 2, 2); }
    for (let i = 8; i < RW - 8; i += 16) fr(acc, ox + i, oy + RH - 4, 2, 2);
    for (let x = 24; x < RW - 24; x += 14) { fr(0xffc455, ox + x, oy + RH - 14, 8, 1); fr(0xb0580f, ox + x, oy + RH - 13, 8, 1); }
    for (let y = 60; y < RH - 20; y += 14) { fr(0xffc455, ox + 12, oy + y, 1, 8, 0.8); fr(0xffc455, ox + RW - 13, oy + y, 1, 8, 0.8); }
    for (let i = 0; i < 8; i++) {
      const x = rd.between(24, RW - 90), y = rd.between(62, RH - 44), w = rd.between(26, 60), h = rd.between(14, 30);
      fr(0x0e1014, ox + x, oy + y, w, h, 0.5); fr(0x4e5562, ox + x, oy + y, w, 1, 0.6); fr(0x4e5562, ox + x, oy + y, 1, h, 0.6);
      fr(acc, ox + x + 2, oy + y + 2, 2, 1, 0.9);
    }

    // hull ring with openings and a neon inner edge, painted once into the same texture
    const strip = (x, y, w, h, side) => {
      fr(0x1a1d24, x, y, w, h); fr(0x2e333d, x + 1, y + 1, w - 2, h - 2); fr(0x4e5562, x + 1, y + 1, w - 2, 1);
      if (side === 'l') fr(acc, x + w - 1, y, 1, h); else if (side === 'r') fr(acc, x, y, 1, h); else if (side === 'b') fr(acc, x, y, w, 1); else fr(acc, x, y + h - 1, w, 1);
      if (w > h) for (let i = x + 6; i < x + w - 6; i += 24) fr(acc, i, y + 4, 6, 2); else for (let i = y + 6; i < y + h - 6; i += 24) fr(acc, x + 4, i, 2, 6);
    };
    const glow = (x, y, w, h, side) => [0.34, 0.18, 0.08].forEach((al, k) => {
      if (side === 'l') fr(acc, x - 1 - k, y, 1, h, al); else if (side === 'r') fr(acc, x + w + k, y, 1, h, al); else if (side === 'b') fr(acc, x, y + h + k, w, 1, al); else fr(acc, x, y - 1 - k, w, 1, al);
    });
    segments(0, RH, gaps.left || []).forEach(([a, b]) => { strip(ox - B, oy + a, B, b - a, 'l'); glow(ox - B, oy + a, B, b - a, 'l'); this.solid(ox - B / 2, oy + (a + b) / 2, B, b - a); });
    segments(0, RH, gaps.right || []).forEach(([a, b]) => { strip(ox + RW, oy + a, B, b - a, 'r'); glow(ox + RW, oy + a, B, b - a, 'r'); this.solid(ox + RW + B / 2, oy + (a + b) / 2, B, b - a); });
    segments(-B, RW + B, gaps.bottom || []).forEach(([a, b]) => { strip(ox + a, oy + RH, b - a, B, 'b'); glow(ox + a, oy + RH, b - a, B, 'b'); this.solid(ox + (a + b) / 2, oy + RH + B / 2, b - a, B); });
    const doorRanges = (def.topDoors || []).map((d) => [d.x - 16, d.x + 16]);
    segments(-B, RW + B, doorRanges).forEach(([a, b]) => { strip(ox + a, oy - B, b - a, B, 't'); glow(ox + a, oy - B, b - a, B, 't'); });
    // back wall solids, with a gap for every door
    segments(0, RW, doorRanges).forEach(([a, b]) => this.solid(ox + (a + b) / 2, oy + 20, b - a, 60));
    (def.topDoors || []).forEach((d) => this.addDoor(ox + d.x, oy, d));

    // vignette on the room, then the room's contents
    this.add.image(ox, oy, 'vignette').setOrigin(0).setDepth(950);
    const dark = this.add.renderTexture(ox, oy, RW, RH).setOrigin(0).setDepth(900);
    this.zones.push({ rt: dark, x: ox, y: oy, w: RW, h: RH });
    const ctx = new Ctx(this, def);
    const inst = new cls(ctx);
    inst.build();
    (cls.EMERGENCY || []).forEach(([x, y]) => (this.emergency = this.emergency || []).push(this.add.image(ox + x, oy + y, 'o', 'light_radial_64').setScale(0.5).setTint(0xff2a3a).setAlpha(0.8).setBlendMode(Phaser.BlendModes.ADD).setDepth(925).setVisible(false)));
    this.modules.push({ def, inst, rect: new Phaser.Geom.Rectangle(ox, oy, RW, RH) });
  }

  buildCorridor(c) {
    const H = c.type === 'H', pad = 6;
    const x = c.x0 - (H ? 0 : pad), y = c.y0 - (H ? pad : 0), w = c.x1 - c.x0 + (H ? 0 : 2 * pad), h = c.y1 - c.y0 + (H ? 2 * pad : 0);
    const rt = this.add.renderTexture(x, y, w, h).setOrigin(0).setDepth(0);
    const rnd = new Phaser.Math.RandomDataGenerator(['cor' + c.x0 + c.y0]);
    const opts = { originX: 0, originY: 0 };
    for (let yy = c.y0; yy < c.y1; yy += 16) for (let xx = c.x0; xx < c.x1; xx += 16) rt.stamp('o', `floor_${rnd.between(0, 5)}`, xx - x, yy - y, opts);
    const rail = (rx, ry, rw, rh) => {
      rt.fill(0x1a1d24, 1, rx - x, ry - y, rw, rh); rt.fill(0x2e333d, 1, rx - x + 1, ry - y + 1, rw - 2, rh - 2); rt.fill(0xe8902a, 1, rx - x + 1, ry - y + 1, rw - 2, 1);
      this.solid(rx + rw / 2, ry + rh / 2, rw, rh);
    };
    const mx = (c.x0 + c.x1) / 2, my = (c.y0 + c.y1) / 2;
    if (H) for (let xx = c.x0 + 4; xx < c.x1 - 4; xx += 12) { rt.fill(0xffc455, 1, xx - x, my - y, 7, 1); rt.fill(0xb0580f, 1, xx - x, my - y + 1, 7, 1); }
    else for (let yy = c.y0 + 4; yy < c.y1 - 4; yy += 12) { rt.fill(0xffc455, 1, mx - x, yy - y, 1, 7); rt.fill(0xb0580f, 1, mx - x + 1, yy - y, 1, 7); }
    if (H) { rail(c.x0 + B, c.y0 - pad, c.x1 - c.x0 - 2 * B, pad); rail(c.x0 + B, c.y1, c.x1 - c.x0 - 2 * B, pad); }
    else { rail(c.x0 - pad, c.y0 + B, pad, c.y1 - c.y0 - 2 * B); rail(c.x1, c.y0 + B, pad, c.y1 - c.y0 - 2 * B); }
    const dark = this.add.renderTexture(c.x0, c.y0, c.x1 - c.x0, c.y1 - c.y0).setOrigin(0).setDepth(900);
    this.zones.push({ rt: dark, x: c.x0, y: c.y0, w: c.x1 - c.x0, h: c.y1 - c.y0 });
    this.addLight({ x: (c.x0 + c.x1) / 2, y: (c.y0 + c.y1) / 2, s: 0.8, a: 0.45, power: true, glow: 0x22c4c4, ga: 0.1 });
  }

  addDoor(cx, oy, d) {
    const s = this.add.sprite(cx, oy + 48, 'o', 'door_0').setOrigin(0.5, 1).setDepth(oy + 47);
    const zone = this.add.zone(cx, oy + 20, 32, 60); this.physics.add.existing(zone, true); this.solids.add(zone);
    this.doors.push({ s, zone, x: cx, y0: oy - 10, y1: oy + 50, locked: !!d.locked, open: false });
    this.addLight({ x: cx, y: oy + 40, s: 0.55, a: 0.5, glow: 0xf2a93b, ga: 0.18 });
    if (d.locked) this.addInteractable({ x: cx, y: oy + 62, r: 30, prompt: () => `Ușă blocată · ${d.label}: în construcție`, use: () => ui.toast(`${d.label}: în construcție. Se deschide mai târziu în poveste.`), anim: false });
  }

  solid(cx, cy, w, h) { const z = this.add.zone(cx, cy, w, h); this.physics.add.existing(z, true); this.solids.add(z); }
  shade(x, feet, w) { this.add.image(x, feet - 1, 'o', 'shadow_20').setScale(w / 20, 1).setDepth(feet - 0.5).setAlpha(0.9); }
  prop(frame, x, feet, solid = null, anim = null) {
    const s = this.add.sprite(x, feet, 'o', frame).setOrigin(0.5, 1).setDepth(feet);
    if (anim) s.play(anim);
    if (solid) this.solid(x + (solid.dx || 0), feet - solid.h / 2, solid.w, solid.h);
    return s;
  }
  addInteractable(it) { this.interactables.push(it); return it; }
  addNpc({ outfit, x, y, name, lines }) {
    const s = this.add.sprite(x, y, 'o', `odysseus_${outfit}_down_idle_0`).setOrigin(0.5, 0.92).setDepth(y);
    s.play(`odysseus_${outfit}_down_idle`); this.shade(x, y, 16); this.solid(x, y - 3, 10, 6);
    let i = 0;
    this.addInteractable({ x, y: y + 2, r: 24, prompt: () => `[E] Vorbește cu ${name}`, use: () => ui.dialog([{ who: name, text: lines[i++ % lines.length] }]), anim: false });
    return s;
  }
  addLight({ x, y, s = 1, a = 0.9, power = false, when = null, glow = null, ga = 0.3, gs = null }) {
    const l = { x, y, s, a, power, when, glow: null };
    if (glow !== null) l.glow = this.add.image(x, y, 'o', 'light_radial_64').setScale(gs || s * 1.2).setTint(glow).setAlpha(ga).setBlendMode(Phaser.BlendModes.ADD).setDepth(920);
    this.lights.push(l); return l;
  }

  // ---------- player ----------
  buildPlayer() {
    const home = MODULES.find((m) => m.key === S.room) || MODULES[0];
    let [x, y] = [home.ox + home.spawn[0], home.oy + home.spawn[1]];
    if (S.pos && S.pos.x > 0 && S.pos.x < WW && S.pos.y > 0 && S.pos.y < WH) [x, y] = [S.pos.x, S.pos.y];
    this.player = this.physics.add.sprite(x, y, 'o', 'odysseus_station_down_idle_0').setOrigin(0.5, 0.92);
    this.player.body.setSize(8, 6).setOffset(4, 17);
    this.player.setCollideWorldBounds(true);
    this.physics.add.collider(this.player, this.solids);
    this.playerShadow = this.add.image(0, 0, 'o', 'shadow_20').setScale(0.8, 1);
    this.player.play('odysseus_station_down_idle');
  }

  // ---------- light ----------
  buildLighting() {
    this.lightR = this.make.image({ key: 'o', frame: 'light_radial_64', add: false });
    this.lightC = this.make.image({ key: 'o', frame: 'light_cone', add: false });
  }

  drawDarkness(time) {
    const e = S.energy, a = ambient(e), on = e >= 25;
    const lit = (l) => (!l.power || on) && (!l.when || l.when());
    this.lights.forEach((l) => { if (l.glow) l.glow.setVisible(lit(l)); });
    const blink = Math.floor(time / 600) % 2 === 0;
    (this.emergency || []).forEach((g) => g.setVisible(e < 50 && blink));
    const px = this.player.x, py = this.player.y - 8;
    this.zones.forEach((z) => {
      z.rt.setVisible(a < 0.999);
      if (a >= 0.999) return;
      const rt = z.rt; rt.clear(); rt.fill(0x02040a, 1 - a);
      const near = (x, y, r) => x + r > z.x && x - r < z.x + z.w && y + r > z.y && y - r < z.y + z.h;
      const er = (img, x, y, s, alpha, rot = 0) => { img.setPosition(x - z.x, y - z.y).setScale(s).setAlpha(alpha).setRotation(rot); rt.erase(img, x - z.x, y - z.y); };
      if (near(px, py, 20)) er(this.lightR, px, py, 0.62, 0.85);
      this.lights.forEach((l) => { if (lit(l) && near(l.x, l.y, 32 * l.s)) er(this.lightR, l.x, l.y, l.s, l.a); });
      if (this.flashlight && near(px, py, 110)) {
        this.lightC.setOrigin(0, 0.5);
        er(this.lightC, px, py, 1, 1, { right: 0, down: Math.PI / 2, left: Math.PI, up: -Math.PI / 2 }[this.facing]);
      }
    });
  }

  // ---------- camera ----------
  zoomFor() {
    const vv = window.visualViewport;
    const cssH = Math.min(this.scale.height, window.innerHeight, vv ? vv.height : Infinity);   // iOS can report stale/bigger values
    const base = Phaser.Math.Clamp(Math.round(cssH / 190), 2, 5);
    const idx = Phaser.Math.Clamp(ZOOMS.indexOf(base) + ui.zoomOffset, 0, ZOOMS.length - 1);
    return ZOOMS[idx];
  }
  setupCamera() {
    const cam = this.cameras.main;
    cam.setBounds(-300, -300, WW + 600, WH + 600);
    if (this.overview) return this.fitOverview();
    cam.setZoom(this.zoomFor()); cam.startFollow(this.player, true, 0.12, 0.12); cam.roundPixels = true;
  }
  onZoom() {
    const cam = this.cameras.main;
    if (this.overview) { const z = Phaser.Math.Clamp(this.overviewZoom * (1.25 ** ui.zoomOffset), 0.2, 3); cam.setZoom(z); return; }
    cam.setZoom(this.zoomFor());
  }
  fitOverview() {
    const cam = this.cameras.main;
    this.overviewZoom = Math.min(cam.width / (WW + 80), cam.height / (WH + 100));
    cam.stopFollow(); cam.setZoom(this.overviewZoom * (1.25 ** ui.zoomOffset)); cam.centerOn(WW / 2, WH / 2);
  }
  toggleOverview() {
    this.overview = !this.overview;
    document.body.classList.toggle('inmap', this.overview);
    if (this.overview) {
      ui.zoomOffset = 0; this.fitOverview();
      ui.mapMode(true, () => this.goSelected(), () => this.toggleOverview());
      this.sel = null; const here = this.cur; if (here) this.pickModule(here.rect.centerX, here.rect.centerY);
    } else {
      ui.mapMode(false); ui.zoomOffset = 0;
      const cam = this.cameras.main; cam.setZoom(this.zoomFor()); cam.startFollow(this.player, true, 0.12, 0.12);
    }
  }
  pickModule(x, y) {
    const m = this.modules.find((mm) => Phaser.Geom.Rectangle.Contains(mm.rect, x, y));
    if (!m) return;
    this.sel = m;
    const d = m.def;
    const info = {
      Hydroponics: () => `${S.beds.filter((b) => b.stage === 3).length} din ${S.beds.length} paturi gata de recoltat.`,
      Command: () => 'Terminal ORION, masă holografică, criosomn.',
      Reactor: () => (S.energy >= 5 ? 'Reactorul funcționează.' : 'Reactorul e rece. Are nevoie de combustibil.'),
      Hangar: () => (S.flags.shipReady ? 'Nava Meridian e pregătită pentru zbor.' : 'Nava Meridian așteaptă pe pistă.'),
      Lab: () => 'În construcție. Se deschide mai târziu în poveste.',
    }[d.key]();
    ui.showMapInfo({ title: d.label + (this.cur && this.cur.def.key === d.key ? ' · ești aici' : ''), text: info, canGo: !d.locked });
  }
  goSelected() {
    const m = this.sel; if (!m || m.def.locked) return;
    this.cameras.main.fadeOut(200);
    this.cameras.main.once('camerafadeoutcomplete', () => {
      this.player.setPosition(m.def.ox + m.def.spawn[0], m.def.oy + m.def.spawn[1]); this.player.setVelocity(0);
      this.toggleOverview(); this.cameras.main.centerOn(this.player.x, this.player.y); this.cameras.main.fadeIn(250);
    });
  }

  // ---------- helpers ----------
  nearest() {
    let best = null, bd = 1e9;
    const px = this.player.x, py = this.player.y;
    this.interactables.forEach((it) => {
      if (it.when && !it.when()) return;
      const d = Math.hypot(px - it.x, py - it.y);
      if (d < it.r && d < bd) { best = it; bd = d; }
    });
    return best;
  }

  // ---------- loop ----------
  update(time, delta) {
    controls.update();
    const p = this.player;
    this.engineT += delta; const f = Math.floor(this.engineT / 120) % 3;
    this.engines.forEach((e) => e.setFrame(`engine_${f}`));
    this.modules.forEach((m) => m.inst.update && m.inst.update(time, delta));
    if (ui.blocking || this.overview) {
      p.setVelocity(0);
      if (controls.takeAction() && ui.dialogOpen) ui.advance();
      controls.takeFlash(); controls.debugEnergy();
      this.drawDarkness(time); return;
    }
    const dbg = controls.debugEnergy(); if (dbg !== null) setEnergy(dbg);
    tick(delta);
    if (S.energy < 50 && !this.flashAuto) { this.flashAuto = true; this.flashlight = true; }
    if (S.energy >= 50) this.flashAuto = false;
    if (controls.takeFlash()) { this.flashlight = !this.flashlight; this.flashAuto = true; if (this.flashlight) S.flags.flashUsed = true; }

    let vx = controls.x, vy = controls.y;
    if (this.acting > 0) { this.acting -= delta / 1000; vx = vy = 0; }
    const len = Math.hypot(vx, vy);
    if (len > 0) { vx /= len; vy /= len; }
    p.setVelocity(vx * SPEED, vy * SPEED);
    if (len > 0) this.facing = Math.abs(vx) > Math.abs(vy) ? (vx > 0 ? 'right' : 'left') : (vy > 0 ? 'down' : 'up');
    const d = this.facing === 'left' ? 'right' : this.facing;
    p.setFlipX(this.facing === 'left');
    const key = `odysseus_station_${d}_${this.acting > 0 ? 'act' : len > 0 ? 'walk' : 'idle'}`;
    if (p.anims.currentAnim?.key !== key) p.play(key);
    p.setDepth(p.y); this.playerShadow.setPosition(p.x, p.y - 1).setDepth(p.y - 0.5);

    // doors open when you come close
    this.doors.forEach((dr) => {
      // distance to the door opening itself (a 32 x 60 rectangle), so it opens from either side
      const near = !dr.locked && Math.hypot(Math.max(Math.abs(p.x - dr.x) - 16, 0), Math.max(dr.y0 - p.y, p.y - dr.y1, 0)) < 30;
      if (near !== dr.open) { dr.open = near; dr.s.setFrame(near ? 'door_2' : 'door_0'); dr.zone.body.enable = !near; }
    });
    // which room are we in?
    const cur = this.modules.find((m) => m.rect.contains(p.x, p.y)) || null;
    if (cur !== this.cur) { this.cur = cur; if (cur) { S.room = cur.def.key; if (cur.inst.onEnter) cur.inst.onEnter(); save(); } }

    const near = this.nearest();
    if (controls.takeAction() && near) { if (near.anim !== false) this.acting = 0.5; near.use(); save(); }
    ui.prompt(near ? near.prompt() : null);

    this.storyAcc += delta; if (this.storyAcc > 500) { this.storyAcc = 0; updateStory(ui); }
    S.pos = { x: Math.round(p.x), y: Math.round(p.y) };       // always current, so any save restores you exactly where you stand
    this.drawDarkness(time);
  }
}
