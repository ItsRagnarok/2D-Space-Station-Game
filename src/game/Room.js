import Phaser from 'phaser';
import { S, tick, save, setEnergy, ambient } from './state.js';
import { updateStory, objectivesView } from './story.js';
import { ui } from '../ui/ui.js';
import { controls } from '../ui/controls.js';

export const W = 384, H = 220, SPEED = 58;

// Base class for every station room: floor + wall, player, doors, interactions, NPCs, lights/darkness, camera.
export default class Room extends Phaser.Scene {
  init(data) { this.spawnName = (data && data.spawn) || 'default'; }

  create() {
    window.__orbital = this;
    this.solids = this.physics.add.staticGroup();
    this.interactables = []; this.lights = []; this.npcs = [];
    this.facing = 'down'; this.acting = 0; this.leaving = false; this.storyAcc = 0;
    this.flashlight = !!this.registry.get('flash');
    this.flashAuto = this.registry.get('flashAuto') || false;
    this.buildFloor();
    this.build();
    this.buildPlayer();
    this.buildLighting();
    this.setupCamera();
    this.cameras.main.fadeIn(250);
    this.scale.on('resize', this.setupCamera, this);
    this.events.once('shutdown', () => this.scale.off('resize', this.setupCamera, this));
    ui.debugFn = () => `inner ${innerWidth}x${innerHeight} · visual ${window.visualViewport ? Math.round(window.visualViewport.width) + 'x' + Math.round(window.visualViewport.height) : '-'} · dpr ${devicePixelRatio} · game ${this.scale.width}x${this.scale.height} · zoom ${this.cameras.main.zoom} · standalone ${navigator.standalone === true}`;
    S.room = this.scene.key; save();
    ui.setRes(S.res); ui.setObjectives(objectivesView()); this.syncEnergy();
    if (this.onEnter) this.onEnter();
  }

  // ---------- room shell ----------
  buildFloor() {
    const rt = this.add.renderTexture(0, 0, W, H).setOrigin(0).setDepth(0);
    const opts = { originX: 0, originY: 0 };
    const rnd = new Phaser.Math.RandomDataGenerator([this.scene.key]);
    const special = this.constructor.SPECIALS || {};
    for (let ty = 0; ty < 11; ty++) for (let tx = 0; tx < 24; tx++) rt.stamp('o', special[`${tx},${ty}`] || `floor_${rnd.between(0, 5)}`, tx * 16, 44 + ty * 16, opts);
    for (let x = 0; x < W; x += 120) rt.stamp('o', 'wall_120', x, 0, opts);
    this.solid(W / 2, 24, W, 52);
    this.physics.world.setBounds(0, 0, W, H);
  }

  solid(cx, cy, w, h) {
    const z = this.add.zone(cx, cy, w, h); this.physics.add.existing(z, true); this.solids.add(z);
  }
  shade(x, feet, w) { this.add.image(x, feet - 1, 'o', 'shadow_20').setScale(w / 20, 1).setDepth(feet - 0.5).setAlpha(0.9); }
  prop(frame, x, feet, solid = null, anim = null) {
    const s = this.add.sprite(x, feet, 'o', frame).setOrigin(0.5, 1).setDepth(feet);
    if (anim) s.play(anim);
    if (solid) this.solid(x + (solid.dx || 0), feet - solid.h / 2, solid.w, solid.h);
    return s;
  }
  addInteractable(it) { this.interactables.push(it); return it; }

  addDoor(x, target, spawn, label) {
    const s = this.add.sprite(x, 48, 'o', 'door_0').setOrigin(0.5, 1).setDepth(47);
    this.addLight({ x, y: 40, s: 0.55, a: 0.5, glow: 0xf2a93b, ga: 0.18 });
    this.addInteractable({ x, y: 60, r: 28, prompt: () => `[E] Ușă → ${label}`, use: () => {
      if (this.leaving) return;
      this.leaving = true; s.setFrame('door_1'); this.time.delayedCall(120, () => s.setFrame('door_2'));
      const slow = S.energy < 25 ? 700 : 0;
      if (slow) ui.toast('Ușa se deschide greu: energie scăzută');
      this.time.delayedCall(260 + slow, () => {
        this.registry.set('flash', this.flashlight); this.registry.set('flashAuto', this.flashAuto);
        this.cameras.main.fadeOut(250);
        this.cameras.main.once('camerafadeoutcomplete', () => this.scene.start(target, { spawn }));
      });
    } });
    return s;
  }

  addNpc({ outfit, x, y, name, lines }) {
    const s = this.add.sprite(x, y, 'o', `odysseus_${outfit}_down_idle_0`).setOrigin(0.5, 0.92).setDepth(y);
    s.play(`odysseus_${outfit}_down_idle`);
    this.shade(x, y, 16); this.solid(x, y - 3, 10, 6);
    let i = 0;
    this.addInteractable({ x, y: y + 2, r: 24, prompt: () => `[E] Vorbește cu ${name}`, use: () => { ui.dialog([{ who: name, text: lines[i++ % lines.length] }]); }, anim: false });
    return s;
  }

  // lights: erase a hole in the darkness (+ optional coloured additive glow). `power` lights die below 25% energy; `when` is an extra condition.
  addLight({ x, y, s = 1, a = 0.9, power = false, when = null, glow = null, ga = 0.3, gs = null }) {
    const l = { x, y, s, a, power, when, glow: null, ga };
    if (glow !== null) l.glow = this.add.image(x, y, 'o', 'light_radial_64').setScale(gs || s * 1.2).setTint(glow).setAlpha(ga).setBlendMode(Phaser.BlendModes.ADD).setDepth(920);
    this.lights.push(l); return l;
  }

  // ---------- player ----------
  buildPlayer() {
    const sp = (this.spawns || {})[this.spawnName] || (this.spawns || {}).default || [64, 150];
    this.player = this.physics.add.sprite(sp[0], sp[1], 'o', 'odysseus_station_down_idle_0').setOrigin(0.5, 0.92);
    this.player.body.setSize(8, 6).setOffset(4, 17);
    this.player.setCollideWorldBounds(true);
    this.physics.add.collider(this.player, this.solids);
    this.playerShadow = this.add.image(0, 0, 'o', 'shadow_20').setScale(0.8, 1);
    this.player.play('odysseus_station_down_idle');
  }

  // ---------- lighting ----------
  buildLighting() {
    this.dark = this.add.renderTexture(0, 0, W, H).setOrigin(0).setDepth(900);
    this.add.image(0, 0, 'vignette').setOrigin(0).setDepth(950);
    this.lightR = this.make.image({ key: 'o', frame: 'light_radial_64', add: false });
    this.lightC = this.make.image({ key: 'o', frame: 'light_cone', add: false });
    this.emergency = (this.emergencyPoints || [[8, 62], [376, 62], [20, 200], [364, 200]]).map(([x, y]) =>
      this.add.image(x, y, 'o', 'light_radial_64').setScale(0.5).setTint(0xff2a3a).setAlpha(0.8).setBlendMode(Phaser.BlendModes.ADD).setDepth(925).setVisible(false));
  }

  drawDarkness(time) {
    const e = S.energy, a = ambient(e), on = e >= 25;
    const lit = (l) => (!l.power || on) && (!l.when || l.when());
    this.lights.forEach((l) => { if (l.glow) l.glow.setVisible(lit(l)); });
    const blink = Math.floor(time / 600) % 2 === 0;
    this.emergency.forEach((g) => g.setVisible(e < 50 && blink));
    this.dark.setVisible(a < 0.999);
    if (a >= 0.999) return;
    const rt = this.dark; rt.clear(); rt.fill(0x02040a, 1 - a);
    const er = (img, x, y, s, alpha, rot = 0) => { img.setPosition(x, y).setScale(s).setAlpha(alpha).setRotation(rot); rt.erase(img, x, y); };
    const px = this.player.x, py = this.player.y - 8;
    er(this.lightR, px, py, 0.62, 0.85);
    this.lights.forEach((l) => { if (lit(l)) er(this.lightR, l.x, l.y, l.s, l.a); });
    if (this.flashlight) {
      this.lightC.setOrigin(0, 0.5);
      er(this.lightC, px, py, 1, 1, { right: 0, down: Math.PI / 2, left: Math.PI, up: -Math.PI / 2 }[this.facing]);
    }
  }

  // ---------- camera ----------
  setupCamera() {
    const cam = this.cameras.main, vv = window.visualViewport;
    const cssH = Math.min(this.scale.height, window.innerHeight, vv ? vv.height : Infinity);   // iOS can report stale/bigger values
    const z = Phaser.Math.Clamp(Math.round(cssH / 190), 2, 5);
    cam.setZoom(z);
    const vw = cam.width / z, vh = cam.height / z;
    cam.setBounds(vw > W ? -(vw - W) / 2 : 0, vh > H ? -(vh - H) / 2 : 0, Math.max(W, vw), Math.max(H, vh));
    cam.startFollow(this.player, true, 0.12, 0.12);
    cam.roundPixels = true;
  }

  // ---------- helpers ----------
  syncEnergy() { setEnergy(S.energy); }
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
    if (ui.blocking) {
      p.setVelocity(0); p.anims.pause && 0;
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

    const near = this.nearest();
    if (controls.takeAction() && near) { if (near.anim !== false) this.acting = 0.5; near.use(); save(); }
    ui.prompt(near ? near.prompt() : null);

    this.storyAcc += delta; if (this.storyAcc > 500) { this.storyAcc = 0; updateStory(ui); }
    if (this.roomUpdate) this.roomUpdate(time, delta);
    this.drawDarkness(time);
  }
}
