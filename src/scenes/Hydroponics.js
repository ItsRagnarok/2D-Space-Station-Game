import Phaser from 'phaser';
import { createHud } from '../ui/hud.js';
import { createControls } from '../ui/controls.js';

const W = 384, H = 220;          // world size in art pixels
const SPEED = 58;
const GROW_MS = [7000, 9000];    // stage 1->2, 2->3 (demo pace)
const DECAY_MS = 3000;           // -1% energy every 3 s (demo pace; real pace is tuned later)

// Energy -> ambient light (1 = full light). Matches docs/REGULI.md.
export function ambient(e) {
  const p = [[0, 0.07], [25, 0.32], [50, 0.62], [75, 1.0]];
  if (e >= 75) return 1;
  for (let i = 0; i < p.length - 1; i++) {
    if (e <= p[i + 1][0]) return p[i][1] + (p[i + 1][1] - p[i][1]) * (e - p[i][0]) / (p[i + 1][0] - p[i][0]);
  }
  return 1;
}
function energyState(e) {
  if (e >= 75) return ['Energie normală', '#2fe58a'];
  if (e >= 50) return ['Economie de energie', '#c8e84a'];
  if (e >= 25) return ['AVARIE · lumini de urgență', '#f2a93b'];
  if (e > 0) return ['BLACKOUT · doar lanterna', '#ff5a6a'];
  return ['BLACKOUT TOTAL', '#ff3a4a'];
}

const NAMES = { crystal: 'Cristale', rare: 'Cristale rare', flora: 'Floră extraterestră', mush: 'Ciuperci luminiscente' };
const BEDS = [
  { x: 112, y: 118, type: 'crystal' }, { x: 182, y: 118, type: 'flora' }, { x: 252, y: 118, type: 'mush' },
  { x: 112, y: 172, type: 'rare' }, { x: 182, y: 172, type: 'crystal' }, { x: 252, y: 172, type: 'flora' },
];
const INCUBATORS = [
  { x: 30, kind: 'plant', text: 'Incubator: răsad de floră, crește sub lumină artificială.' },
  { x: 62, kind: 'crystal', text: 'Incubator: un cristal viu, pulsează încet.' },
  { x: 94, kind: 'jelly', text: 'Incubator: o formă de viață necunoscută. Pare să te urmărească.' },
  { x: 126, kind: 'plant', text: 'Incubator: spori în repaus.' },
];
const GEN = { x: 336, y: 196 };

export default class Hydroponics extends Phaser.Scene {
  constructor() { super('Hydroponics'); }

  create() {
    window.__orbital = this;
    this.hud = createHud();
    this.controls = createControls(this);
    this.energy = 100;
    this.res = { crystal: 0, rare: 0, flora: 0, mush: 0 };
    this.facing = 'down';
    this.acting = 0;
    this.flashlight = false;
    this.flashAuto = false;
    this.solids = this.physics.add.staticGroup();
    this.interactables = [];
    this.statics = [];

    this.buildRoom();
    this.buildProps();
    this.buildBeds();
    this.buildPlayer();
    this.buildLighting();
    this.setupCamera();

    this.time.addEvent({ delay: DECAY_MS, loop: true, callback: () => this.setEnergy(this.energy - 1) });
    this.time.addEvent({ delay: 600, loop: true, callback: () => { this.plantFrame = 1 - this.plantFrame; this.refreshPlants(); } });
    this.plantFrame = 0;
    this.hud.setRes(this.res);
    this.setEnergy(100);
    this.scale.on('resize', () => this.setupCamera());
  }

  // ---------- room ----------
  buildRoom() {
    const rt = this.add.renderTexture(0, 0, W, H).setOrigin(0).setDepth(0);
    const opts = { originX: 0, originY: 0 };
    const rnd = new Phaser.Math.RandomDataGenerator(['floor']);
    for (let ty = 0; ty < 11; ty++) {
      for (let tx = 0; tx < 24; tx++) {
        let f = `floor_${rnd.between(0, 5)}`;
        if ((tx === 3 && ty === 8) || (tx === 14 && ty === 6)) f = 'floor_vent';
        if ((tx === 8 && ty === 4) || (tx === 20 && ty === 9)) f = 'floor_grate';
        rt.stamp('o', f, tx * 16, 44 + ty * 16, opts);
      }
    }
    for (let x = 0; x < W; x += 120) rt.stamp('o', 'wall_120', x, 0, opts);
    this.solid(W / 2, 24, W, 52);                    // back wall
    this.physics.world.setBounds(0, 0, W, H);
  }

  solid(cx, cy, w, h) {
    const z = this.add.zone(cx, cy, w, h);
    this.physics.add.existing(z, true);
    this.solids.add(z);
  }

  shade(x, feet, w) {
    this.add.image(x, feet - 1, 'o', 'shadow_20').setScale(w / 20, 1).setDepth(feet - 0.5).setAlpha(0.9);
  }

  prop(frame, x, feet, solid = null, anim = null) {
    const s = this.add.sprite(x, feet, 'o', frame).setOrigin(0.5, 1).setDepth(feet);
    if (anim) s.play(anim);
    if (solid) this.solid(x + (solid.dx || 0), feet - solid.h / 2, solid.w, solid.h);
    this.statics.push(s);
    return s;
  }

  buildProps() {
    INCUBATORS.forEach((inc) => {
      const s = this.prop('incubator_plant_0', inc.x, 56, { w: 22, h: 12 });
      s.play(`incubator_${inc.kind}`);
      inc.sprite = s;
      this.interactables.push({ kind: 'incubator', x: inc.x, y: 60, r: 26, data: inc });
    });
    this.prop('console_0', 190, 52, { w: 44, h: 10 }, 'console');
    this.prop('console_1', 238, 52, { w: 44, h: 10 }, 'console');
    this.prop('rack_0', 284, 52, { w: 18, h: 10 });
    this.prop('pipes_v', 376, 150, { w: 10, h: 104 });
    this.prop('crate_steel', 36, 200, { w: 16, h: 10 }); this.prop('crate_orange', 54, 202, { w: 16, h: 10 });
    this.prop('crate_steel', 45, 190, null).setDepth(203);
    this.shade(45, 202, 40);
    this.gen = this.prop('biogen_0', GEN.x, GEN.y, { w: 48, h: 16 }, 'biogen');
    this.shade(GEN.x, GEN.y, 56);
    this.interactables.push({ kind: 'gen', x: GEN.x, y: GEN.y + 4, r: 44 });
    this.drone = this.add.sprite(160, 80, 'o', 'drone_0').setDepth(600).play('drone');
    this.droneShadow = this.add.image(160, 110, 'o', 'shadow_20').setDepth(1).setScale(0.6).setAlpha(0.7);
  }

  buildBeds() {
    this.beds = BEDS.map((b, i) => {
      const bed = { ...b, stage: 1 + (i % 3), t: 0, plants: [] };
      this.add.sprite(b.x, b.y, 'o', 'bed_0').setOrigin(0.5, 1).setDepth(b.y);
      this.shade(b.x, b.y, 62);
      this.solid(b.x, b.y - 8, 54, 20);
      [-12, 12].forEach((dx) => bed.plants.push(this.add.image(b.x + dx, b.y - 12, 'o', 'plant_crystal_1_0').setOrigin(0.5, 0.91).setDepth(b.y + 1)));
      bed.spark = this.add.sprite(b.x, b.y - 36, 'o', 'sparkle_0').setDepth(b.y + 2).play('sparkle').setVisible(false);
      this.interactables.push({ kind: 'bed', x: b.x, y: b.y + 6, r: 38, data: bed });
      return bed;
    });
    this.refreshPlants();
  }

  refreshPlants() {
    this.beds.forEach((b) => {
      b.plants.forEach((p) => p.setTexture('o', `plant_${b.type}_${b.stage}_${this.plantFrame}`));
      b.spark.setVisible(b.stage === 3);
    });
  }

  // ---------- player ----------
  buildPlayer() {
    this.player = this.physics.add.sprite(64, 150, 'o', 'odysseus_station_down_idle_0').setOrigin(0.5, 0.92);
    this.player.body.setSize(8, 6).setOffset(4, 17);
    this.player.setCollideWorldBounds(true);
    this.physics.add.collider(this.player, this.solids);
    this.playerShadow = this.add.image(0, 0, 'o', 'shadow_20').setScale(0.8, 1);
    this.player.play('odysseus_station_down_idle');
  }

  // ---------- light ----------
  buildLighting() {
    this.dark = this.add.renderTexture(0, 0, W, H).setOrigin(0).setDepth(900);
    this.add.image(0, 0, 'vignette').setOrigin(0).setDepth(950);
    const mk = (frame) => this.make.image({ key: 'o', frame, add: false });
    this.lightR = mk('light_radial_64'); this.lightC = mk('light_cone');
    this.glow = (x, y, s, color, a, depth = 920) => this.add.image(x, y, 'o', 'light_radial_64').setScale(s).setTint(color).setAlpha(a).setBlendMode(Phaser.BlendModes.ADD).setDepth(depth);
    this.glowGen = this.glow(GEN.x, GEN.y - 24, 1.1, 0x9aff20, 0.35);
    this.glowInc = INCUBATORS.map((i) => this.glow(i.x, 70, 0.7, i.kind === 'jelly' ? 0xb46bff : i.kind === 'crystal' ? 0x3a86ff : 0x3ed06a, 0.28));
    this.glowBeds = this.beds.map((b) => this.glow(b.x, b.y - 22, 0.8, b.type === 'rare' ? 0xff9a2a : b.type === 'mush' ? 0xa45cff : b.type === 'flora' ? 0x3ed06a : 0x3a86ff, 0.3));
    this.emergency = [[8, 62], [376, 62], [150, 56], [300, 60], [20, 200]].map(([x, y]) => this.glow(x, y, 0.5, 0xff2a3a, 0.8, 925).setVisible(false));
  }

  drawDarkness(time) {
    const a = ambient(this.energy);
    this.dark.setVisible(a < 0.999);
    const on = this.energy >= 25;
    this.glowInc.forEach((g) => g.setVisible(on)); this.glowGen.setAlpha(0.3 + 0.07 * Math.sin(time / 300));
    this.beds.forEach((b, i) => this.glowBeds[i].setVisible(b.stage === 3 && on));
    const blink = Math.floor(time / 600) % 2 === 0;
    this.emergency.forEach((g) => g.setVisible(this.energy < 50 && blink));
    if (a >= 0.999) return;
    const rt = this.dark;
    rt.clear(); rt.fill(0x02040a, 1 - a);
    const er = (img, x, y, s, alpha, rot = 0) => { img.setPosition(x, y).setScale(s).setAlpha(alpha).setRotation(rot); rt.erase(img, x, y); };
    const px = this.player.x, py = this.player.y - 8;
    er(this.lightR, px, py, 0.62, 0.85);
    er(this.lightR, GEN.x, GEN.y - 24, 1.5, 0.95);
    if (on) {
      INCUBATORS.forEach((i) => er(this.lightR, i.x, 70, 0.9, 0.7));
      this.beds.forEach((b) => { if (b.stage === 3) er(this.lightR, b.x, b.y - 22, 0.9, 0.75); });
      er(this.lightR, 190, 40, 0.8, 0.5); er(this.lightR, 238, 40, 0.8, 0.5);
    }
    if (this.flashlight) {
      const rot = { right: 0, down: Math.PI / 2, left: Math.PI, up: -Math.PI / 2 }[this.facing];
      this.lightC.setOrigin(0, 0.5);
      er(this.lightC, px, py, 1, 1, rot);
    }
  }

  // ---------- camera ----------
  setupCamera() {
    const cam = this.cameras.main;
    const z = Math.max(2, Math.round(this.scale.height / 170));
    cam.setZoom(z);
    const vw = cam.width / z, vh = cam.height / z;
    const bx = vw > W ? -(vw - W) / 2 : 0, by = vh > H ? -(vh - H) / 2 : 0;
    cam.setBounds(bx, by, Math.max(W, vw), Math.max(H, vh));
    cam.startFollow(this.player, true, 0.12, 0.12);
    cam.roundPixels = true;
  }

  // ---------- rules ----------
  setEnergy(e) {
    this.energy = Phaser.Math.Clamp(e, 0, 100);
    const [label, color] = energyState(this.energy);
    this.hud.setEnergy(this.energy, label, color);
    if (this.energy < 50 && !this.flashAuto) { this.flashAuto = true; this.flashlight = true; }
    if (this.energy >= 50) this.flashAuto = false;
  }

  toast(msg) { this.hud.toast(msg); }

  nearest() {
    let best = null, bd = 1e9;
    const px = this.player.x, py = this.player.y;
    this.interactables.forEach((it) => {
      const d = Math.hypot(px - it.x, py - it.y);
      if (d < it.r && d < bd) { best = it; bd = d; }
    });
    return best;
  }

  promptFor(it) {
    if (!it) return null;
    if (it.kind === 'bed') {
      const b = it.data;
      if (b.stage === 3) return `[E] Recoltează · ${NAMES[b.type]}`;
      const pct = Math.round(((b.stage - 1) * 50 + (b.t / GROW_MS[b.stage - 1]) * 50));
      return `${NAMES[b.type]} · crește ${pct}%` + (this.energy < 25 ? ' (oprit: fără energie)' : '');
    }
    if (it.kind === 'gen') {
      const can = this.res.flora >= 2 || this.res.mush >= 1;
      return can ? '[E] Alimentează bio-generatorul (2 floră sau 1 ciupercă) → energie' : 'Bio-generator · ai nevoie de 2 floră sau 1 ciupercă';
    }
    return it.data.text;
  }

  act(it) {
    if (!it) return;
    this.acting = 0.7;
    if (it.kind === 'bed' && it.data.stage === 3) {
      const b = it.data;
      this.res[b.type] += 1; b.stage = 1; b.t = 0; this.refreshPlants();
      this.hud.setRes(this.res); this.toast(`+1 ${NAMES[b.type]}`);
    } else if (it.kind === 'gen') {
      if (this.res.flora >= 2) { this.res.flora -= 2; this.setEnergy(this.energy + 25); this.toast('+25% energie'); }
      else if (this.res.mush >= 1) { this.res.mush -= 1; this.setEnergy(this.energy + 15); this.toast('+15% energie'); }
      else this.toast('Nu ai combustibil biologic');
      this.hud.setRes(this.res);
    } else if (it.kind === 'incubator') this.toast(it.data.text);
  }

  // ---------- loop ----------
  update(time, delta) {
    const c = this.controls; c.update();
    const dbg = c.debugEnergy(); if (dbg !== null && dbg !== this._dbg) this.setEnergy(dbg); this._dbg = dbg;
    if (c.takeFlash()) { this.flashlight = !this.flashlight; this.flashAuto = true; }

    const p = this.player;
    let vx = c.x, vy = c.y;
    if (this.acting > 0) { this.acting -= delta / 1000; vx = vy = 0; }
    const len = Math.hypot(vx, vy);
    if (len > 0) { vx /= len; vy /= len; }
    p.setVelocity(vx * SPEED, vy * SPEED);
    if (len > 0) this.facing = Math.abs(vx) > Math.abs(vy) ? (vx > 0 ? 'right' : 'left') : (vy > 0 ? 'down' : 'up');
    const d = this.facing === 'left' ? 'right' : this.facing;
    p.setFlipX(this.facing === 'left');
    const anim = this.acting > 0 ? 'act' : len > 0 ? 'walk' : 'idle';
    const key = `odysseus_station_${d}_${anim}`;
    if (p.anims.currentAnim?.key !== key) p.play(key);
    p.setDepth(p.y);
    this.playerShadow.setPosition(p.x, p.y - 1).setDepth(p.y - 0.5);

    if (c.takeAction()) this.act(this.nearest());
    this.hud.prompt(this.promptFor(this.nearest()));

    if (this.energy >= 25) {
      this.beds.forEach((b) => {
        if (b.stage < 3) { b.t += delta; if (b.t >= GROW_MS[b.stage - 1]) { b.stage += 1; b.t = 0; this.refreshPlants(); } }
      });
    }
    this.drone.x = 200 + Math.sin(time / 1700) * 90; this.drone.y = 84 + Math.sin(time / 520) * 3;
    this.droneShadow.setPosition(this.drone.x, 112 + Math.sin(time / 520) * 1);
    this.drawDarkness(time);
  }
}
