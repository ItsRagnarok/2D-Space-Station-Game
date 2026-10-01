import Phaser from 'phaser';

const WORLD = 20000; // big map; the camera wraps around it conceptually
const TILE = 512;

// Parallax layers: farther = smaller factor = moves slower.
const STAR_LAYERS = [
  { key: 'stars0', count: 90, size: [0.6, 1.1], alpha: [0.25, 0.6], factor: 0.08 },
  { key: 'stars1', count: 60, size: [0.9, 1.6], alpha: [0.4, 0.8], factor: 0.2 },
  { key: 'stars2', count: 28, size: [1.3, 2.4], alpha: [0.6, 1.0], factor: 0.45 },
];

export default class SpaceScene extends Phaser.Scene {
  constructor() {
    super('Space');
  }

  create() {
    const rng = new Phaser.Math.RandomDataGenerator(['space-station-1']);
    this.rng = rng;

    this.makeTextures(rng);

    const { width, height } = this.scale;

    // Deep background gradient (fixed to the screen).
    this.bg = this.add.image(0, 0, 'bg').setOrigin(0).setScrollFactor(0).setDepth(-100);

    // Nebula clouds (very far, very slow).
    this.nebula = this.add.tileSprite(0, 0, width, height, 'nebula')
      .setOrigin(0).setScrollFactor(0).setDepth(-90).setAlpha(0.9);

    // Star layers.
    this.starLayers = STAR_LAYERS.map((cfg, i) => ({
      cfg,
      sprite: this.add.tileSprite(0, 0, width, height, cfg.key)
        .setOrigin(0).setScrollFactor(0).setDepth(-80 + i),
    }));

    // A distant planet placed in the world, drifts slowly with the camera.
    this.planet = this.add.image(0, 0, 'planet').setDepth(-70).setScrollFactor(0);
    this.planetFactor = 0.06;

    // A tiny far moon orbiting-ish near the planet.
    this.moon = this.add.image(0, 0, 'moon').setDepth(-69).setScrollFactor(0);

    // Shooting stars.
    this.streaks = [];
    this.time.addEvent({ delay: 3500, loop: true, callback: () => this.spawnStreak() });

    // Camera starts somewhere in the middle of the big world and drifts.
    this.cam = this.cameras.main;
    this.pos = new Phaser.Math.Vector2(WORLD / 2, WORLD / 2);
    this.vel = new Phaser.Math.Vector2(0, 0);
    this.drift = new Phaser.Math.Vector2(14, 6); // px/s constant slow glide
    this.driftAngle = 0;
    this.startPos = this.pos.clone();

    // Drag to look around (touch or mouse), with inertia.
    this.dragging = false;
    this.input.on('pointerdown', (p) => {
      this.dragging = true;
      this.lastPtr = { x: p.x, y: p.y, t: p.time };
      this.vel.set(0, 0);
    });
    this.input.on('pointermove', (p) => {
      if (!this.dragging || !p.isDown) return;
      const dx = p.x - this.lastPtr.x;
      const dy = p.y - this.lastPtr.y;
      const dt = Math.max(1, p.time - this.lastPtr.t) / 1000;
      this.pos.x -= dx;
      this.pos.y -= dy;
      this.vel.set(-dx / dt, -dy / dt);
      this.lastPtr = { x: p.x, y: p.y, t: p.time };
    });
    const release = () => { this.dragging = false; };
    this.input.on('pointerup', release);
    this.input.on('pointerupoutside', release);

    this.scale.on('resize', this.onResize, this);
    this.onResize({ width, height });
  }

  onResize(size) {
    const w = size.width ?? this.scale.width;
    const h = size.height ?? this.scale.height;
    this.bg.setDisplaySize(w, h);
    this.nebula.setSize(w, h);
    this.starLayers.forEach((l) => l.sprite.setSize(w, h));
    this.cam.setSize(w, h);
  }

  update(time, delta) {
    const dt = Math.min(delta, 50) / 1000;

    // Gently rotate the drift direction so motion never feels mechanical.
    this.driftAngle += dt * 0.05;
    const dx = this.drift.x + Math.cos(this.driftAngle) * 6;
    const dy = this.drift.y + Math.sin(this.driftAngle * 0.7) * 5;

    if (!this.dragging) {
      // Inertia decays toward the constant drift.
      this.vel.x += (dx - this.vel.x) * Math.min(1, dt * 1.5);
      this.vel.y += (dy - this.vel.y) * Math.min(1, dt * 1.5);
      this.pos.x += this.vel.x * dt;
      this.pos.y += this.vel.y * dt;
    }

    // Keep inside the huge world by wrapping (seamless thanks to tiling).
    this.pos.x = Phaser.Math.Wrap(this.pos.x, 0, WORLD);
    this.pos.y = Phaser.Math.Wrap(this.pos.y, 0, WORLD);

    const { width, height } = this.scale;

    this.nebula.tilePositionX = this.pos.x * 0.04;
    this.nebula.tilePositionY = this.pos.y * 0.04;
    for (const { cfg, sprite } of this.starLayers) {
      sprite.tilePositionX = this.pos.x * cfg.factor;
      sprite.tilePositionY = this.pos.y * cfg.factor;
      // Subtle twinkle: each layer breathes at a different rhythm.
      sprite.alpha = 0.85 + 0.15 * Math.sin(time / (900 + cfg.factor * 4000));
    }

    // Planet: world position relative to the camera, heavily damped.
    const px = width * 0.74 - (this.pos.x - this.startPos.x) * this.planetFactor;
    const py = height * 0.24 - (this.pos.y - this.startPos.y) * this.planetFactor;
    this.planet.setPosition(px, py);
    this.planet.setScale(Math.max(0.35, Math.min(width, height) / 1100));
    this.planet.rotation = time * 0.000004;
    this.moon.setPosition(
      px + Math.cos(time * 0.00004) * 260 * this.planet.scale,
      py + Math.sin(time * 0.00004) * 70 * this.planet.scale,
    );
    this.moon.setScale(this.planet.scale);
    this.moon.setDepth(Math.sin(time * 0.00004) > 0 ? -68 : -71);

    // Shooting stars.
    for (let i = this.streaks.length - 1; i >= 0; i--) {
      const s = this.streaks[i];
      s.life -= dt;
      s.obj.x += s.vx * dt;
      s.obj.y += s.vy * dt;
      s.obj.alpha = Math.max(0, Math.min(1, s.life / s.max)) * 0.9;
      if (s.life <= 0) {
        s.obj.destroy();
        this.streaks.splice(i, 1);
      }
    }
  }

  spawnStreak() {
    const { width, height } = this.scale;
    const angle = Phaser.Math.DegToRad(this.rng.between(20, 50));
    const speed = this.rng.between(700, 1100);
    const obj = this.add.image(this.rng.between(0, width), this.rng.between(-20, height * 0.4), 'streak')
      .setScrollFactor(0).setDepth(-60).setRotation(angle).setOrigin(1, 0.5);
    this.streaks.push({
      obj,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 0.7,
      max: 0.7,
    });
  }

  // ---- Procedural art (all drawn with canvas, no external assets) ----
  makeTextures(rng) {
    const tex = this.textures;
    const make = (key, w, h, draw) => {
      const c = tex.createCanvas(key, w, h);
      draw(c.getContext(), w, h);
      c.refresh();
    };

    // Background gradient.
    make('bg', 4, 512, (g, w, h) => {
      const grad = g.createLinearGradient(0, 0, 0, h);
      grad.addColorStop(0, '#02030a');
      grad.addColorStop(0.55, '#070b1f');
      grad.addColorStop(1, '#0c0a22');
      g.fillStyle = grad;
      g.fillRect(0, 0, w, h);
    });

    // Seamless star tiles: draw each star at 9 offsets so edges wrap.
    for (const L of STAR_LAYERS) {
      make(L.key, TILE, TILE, (g) => {
        for (let i = 0; i < L.count; i++) {
          const x = rng.realInRange(0, TILE);
          const y = rng.realInRange(0, TILE);
          const r = rng.realInRange(L.size[0], L.size[1]);
          const a = rng.realInRange(L.alpha[0], L.alpha[1]);
          const tint = rng.pick(['#ffffff', '#cfe3ff', '#ffe9c8', '#d7d0ff']);
          for (let ox = -TILE; ox <= TILE; ox += TILE) {
            for (let oy = -TILE; oy <= TILE; oy += TILE) {
              const grd = g.createRadialGradient(x + ox, y + oy, 0, x + ox, y + oy, r * 2.2);
              grd.addColorStop(0, hexA(tint, a));
              grd.addColorStop(0.4, hexA(tint, a * 0.5));
              grd.addColorStop(1, hexA(tint, 0));
              g.fillStyle = grd;
              g.beginPath();
              g.arc(x + ox, y + oy, r * 2.2, 0, Math.PI * 2);
              g.fill();
            }
          }
        }
      });
    }

    // Nebula tile (soft coloured blobs, wraps seamlessly).
    make('nebula', 1024, 1024, (g, w) => {
      const colors = ['rgba(90,60,200,', 'rgba(30,110,200,', 'rgba(170,50,150,', 'rgba(20,150,170,'];
      for (let i = 0; i < 14; i++) {
        const x = rng.realInRange(0, w);
        const y = rng.realInRange(0, w);
        const r = rng.realInRange(160, 380);
        const col = rng.pick(colors);
        for (let ox = -w; ox <= w; ox += w) {
          for (let oy = -w; oy <= w; oy += w) {
            const grd = g.createRadialGradient(x + ox, y + oy, 0, x + ox, y + oy, r);
            grd.addColorStop(0, col + '0.16)');
            grd.addColorStop(0.5, col + '0.06)');
            grd.addColorStop(1, col + '0)');
            g.fillStyle = grd;
            g.fillRect(x + ox - r, y + oy - r, r * 2, r * 2);
          }
        }
      }
    });

    // Distant planet: sphere shading + bands + atmosphere + ring.
    make('planet', 640, 640, (g, w) => {
      const c = w / 2;
      const R = 170;
      // Atmosphere glow.
      let grd = g.createRadialGradient(c, c, R * 0.9, c, c, R * 1.5);
      grd.addColorStop(0, 'rgba(120,170,255,0.35)');
      grd.addColorStop(1, 'rgba(120,170,255,0)');
      g.fillStyle = grd;
      g.fillRect(0, 0, w, w);

      // Back half of the ring.
      const ring = (front) => {
        g.save();
        g.translate(c, c);
        g.rotate(-0.35);
        g.scale(1, 0.28);
        g.beginPath();
        g.arc(0, 0, R * 1.75, front ? 0 : Math.PI, front ? Math.PI : Math.PI * 2);
        g.lineWidth = 26;
        g.strokeStyle = 'rgba(210,190,255,0.35)';
        g.stroke();
        g.beginPath();
        g.arc(0, 0, R * 1.5, front ? 0 : Math.PI, front ? Math.PI : Math.PI * 2);
        g.lineWidth = 10;
        g.strokeStyle = 'rgba(160,200,255,0.3)';
        g.stroke();
        g.restore();
      };
      ring(false);

      // Body with bands, clipped to circle.
      g.save();
      g.beginPath();
      g.arc(c, c, R, 0, Math.PI * 2);
      g.clip();
      const body = g.createLinearGradient(0, c - R, 0, c + R);
      ['#4b3f9e', '#6a5acd', '#8a6bd6', '#5a4fb8', '#3b3585'].forEach((col, i, a) =>
        body.addColorStop(i / (a.length - 1), col));
      g.fillStyle = body;
      g.fillRect(c - R, c - R, R * 2, R * 2);
      for (let i = 0; i < 9; i++) {
        g.fillStyle = `rgba(${rng.between(150, 255)},${rng.between(140, 220)},255,${rng.realInRange(0.04, 0.12)})`;
        g.fillRect(c - R, c - R + rng.between(0, R * 2), R * 2, rng.between(6, 22));
      }
      // Terminator shadow + rim light.
      const shade = g.createRadialGradient(c - R * 0.45, c - R * 0.45, R * 0.1, c, c, R * 1.05);
      shade.addColorStop(0, 'rgba(255,255,255,0.18)');
      shade.addColorStop(0.5, 'rgba(0,0,0,0)');
      shade.addColorStop(1, 'rgba(0,0,10,0.85)');
      g.fillStyle = shade;
      g.fillRect(c - R, c - R, R * 2, R * 2);
      g.restore();

      ring(true);
    });

    // Small moon.
    make('moon', 64, 64, (g) => {
      const grd = g.createRadialGradient(22, 22, 2, 32, 32, 28);
      grd.addColorStop(0, '#d9dbe6');
      grd.addColorStop(0.6, '#8d90a3');
      grd.addColorStop(1, '#2a2c3a');
      g.fillStyle = grd;
      g.beginPath();
      g.arc(32, 32, 20, 0, Math.PI * 2);
      g.fill();
    });

    // Shooting star streak.
    make('streak', 160, 6, (g, w, h) => {
      const grd = g.createLinearGradient(0, 0, w, 0);
      grd.addColorStop(0, 'rgba(255,255,255,0)');
      grd.addColorStop(1, 'rgba(255,255,255,1)');
      g.fillStyle = grd;
      g.fillRect(0, h / 2 - 1, w, 2);
    });
  }
}

function hexA(hex, a) {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${n >> 16},${(n >> 8) & 255},${n & 255},${a})`;
}
