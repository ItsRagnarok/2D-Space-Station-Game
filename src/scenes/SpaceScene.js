import Phaser from 'phaser';

const ART = 3; // one art pixel = 3 screen pixels (chunky look, smooth motion)
const TILE = 256; // texture tile size in art pixels
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5].map((v) => v / 16);

// Few stars, dim. Farther layers move slower.
const STAR_LAYERS = [
  { key: 'stars0', count: 12, colors: ['#2a3050', '#333a5e'], big: 0, factor: 0.08 },
  { key: 'stars1', count: 7, colors: ['#5a6492', '#6c76a6'], big: 0, factor: 0.2 },
  { key: 'stars2', count: 4, colors: ['#aab4e6', '#dfe6ff'], big: 0.5, factor: 0.45 },
];

export default class SpaceScene extends Phaser.Scene {
  constructor() {
    super('Space');
  }

  create() {
    this.rng = new Phaser.Math.RandomDataGenerator(['space-station-pixel-1']);
    this.makeStaticTextures();

    const { width, height } = this.scale;

    this.nebula = this.add.tileSprite(0, 0, width, height, 'nebula')
      .setOrigin(0).setScrollFactor(0).setDepth(-90).setTileScale(ART);

    this.starLayers = STAR_LAYERS.map((cfg, i) => ({
      cfg,
      sprite: this.add.tileSprite(0, 0, width, height, cfg.key)
        .setOrigin(0).setScrollFactor(0).setDepth(-80 + i).setTileScale(ART),
    }));

    this.planet = this.add.image(0, 0, '__DEFAULT').setDepth(-70).setScrollFactor(0).setScale(ART);
    this.planetR = 0;
    this.moon = this.add.image(0, 0, 'moon').setDepth(-69).setScrollFactor(0).setScale(ART);
    this.planetFactor = 0.1;

    this.streaks = [];
    this.time.addEvent({ delay: 5000, loop: true, callback: () => this.spawnStreak() });

    this.cam = this.cameras.main;
    this.pos = new Phaser.Math.Vector2(0, 0); // unbounded map, tiles repeat forever
    this.startPos = this.pos.clone();
    this.vel = new Phaser.Math.Vector2(0, 0);
    this.driftAngle = 0;

    // Drag to look around (touch or mouse) with inertia.
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
    this.nebula.setSize(w, h);
    this.starLayers.forEach((l) => l.sprite.setSize(w, h));
    this.cam.setSize(w, h);

    // Planet radius in art pixels: ~17% of the short screen side (medium, not huge).
    const R = Phaser.Math.Clamp(Math.round((Math.min(w, h) / ART) * 0.17), 16, 60);
    if (R !== this.planetR) {
      this.planetR = R;
      if (this.textures.exists('planet')) this.textures.remove('planet');
      this.makePlanetTexture(R);
      this.planet.setTexture('planet');
    }
  }

  update(time, delta) {
    const dt = Math.min(delta, 50) / 1000;

    // Slow, never perfectly straight glide.
    this.driftAngle += dt * 0.05;
    const dx = 12 + Math.cos(this.driftAngle) * 4;
    const dy = 5 + Math.sin(this.driftAngle * 0.7) * 4;

    if (!this.dragging) {
      this.vel.x += (dx - this.vel.x) * Math.min(1, dt * 1.5);
      this.vel.y += (dy - this.vel.y) * Math.min(1, dt * 1.5);
      this.pos.x += this.vel.x * dt;
      this.pos.y += this.vel.y * dt;
    }

    const { width, height } = this.scale;

    this.nebula.tilePositionX = (this.pos.x * 0.05) / ART;
    this.nebula.tilePositionY = (this.pos.y * 0.05) / ART;
    this.starLayers.forEach(({ cfg, sprite }, i) => {
      sprite.tilePositionX = (this.pos.x * cfg.factor) / ART;
      sprite.tilePositionY = (this.pos.y * cfg.factor) / ART;
      // Stepped twinkle (two brightness levels) to keep the pixel feel.
      sprite.alpha = Math.sin(time / (700 + i * 450) + i * 2) > 0.2 ? 1 : 0.65;
    });

    // Big planet, partly off the top-right edge, drifting very slowly.
    const px = width * 0.68 - (this.pos.x - this.startPos.x) * this.planetFactor;
    const py = height * 0.24 - (this.pos.y - this.startPos.y) * this.planetFactor;
    this.planet.setPosition(px, py);

    const ang = time * 0.00005;
    this.moon.setPosition(
      px + Math.cos(ang) * this.planetR * ART * 1.9,
      py + Math.sin(ang) * this.planetR * ART * 0.45 + this.planetR * ART * 0.3,
    );
    this.moon.setDepth(Math.sin(ang) > 0 ? -68 : -71);

    for (let i = this.streaks.length - 1; i >= 0; i--) {
      const s = this.streaks[i];
      s.life -= dt;
      s.obj.x += s.v * dt;
      s.obj.y += s.v * dt;
      s.obj.alpha = s.life > 0.2 ? 1 : Math.max(0, s.life / 0.2);
      if (s.life <= 0) {
        s.obj.destroy();
        this.streaks.splice(i, 1);
      }
    }
  }

  spawnStreak() {
    const { width, height } = this.scale;
    const obj = this.add.image(this.rng.between(0, width), this.rng.between(-10, height * 0.35), 'streak')
      .setScrollFactor(0).setDepth(-60).setOrigin(1, 1).setScale(ART);
    this.streaks.push({ obj, v: this.rng.between(360, 520), life: 0.9 });
  }

  // ---------- Procedural pixel art ----------
  canvasTex(key, w, h) {
    const tex = this.textures.createCanvas(key, w, h);
    const g = tex.getContext();
    g.imageSmoothingEnabled = false;
    return { tex, g };
  }

  makeStaticTextures() {
    const rng = this.rng;

    // Star tiles: 1px squares (a few small plus-shaped ones). Integer coords => seamless.
    for (const L of STAR_LAYERS) {
      const { tex, g } = this.canvasTex(L.key, TILE, TILE);
      for (let i = 0; i < L.count; i++) {
        const x = rng.between(2, TILE - 3);
        const y = rng.between(2, TILE - 3);
        g.fillStyle = rng.pick(L.colors);
        g.fillRect(x, y, 1, 1);
        if (rng.frac() < L.big) {
          g.fillStyle = L.colors[0];
          g.fillRect(x - 1, y, 1, 1); g.fillRect(x + 1, y, 1, 1);
          g.fillRect(x, y - 1, 1, 1); g.fillRect(x, y + 1, 1, 1);
        }
      }
      tex.refresh();
    }

    // Very dark dithered nebula, barely lighter than the void.
    {
      const { tex, g } = this.canvasTex('nebula', TILE, TILE);
      const blobs = [];
      for (let i = 0; i < 6; i++) {
        blobs.push({
          x: rng.between(0, TILE), y: rng.between(0, TILE),
          r: rng.between(50, 90), c: rng.pick(['#0b0a1e', '#0e0a20', '#071420']),
        });
      }
      for (let y = 0; y < TILE; y++) {
        for (let x = 0; x < TILE; x++) {
          let best = null; let bd = 0;
          for (const b of blobs) {
            const ddx = Math.min(Math.abs(x - b.x), TILE - Math.abs(x - b.x));
            const ddy = Math.min(Math.abs(y - b.y), TILE - Math.abs(y - b.y));
            const d = Math.max(0, 1 - Math.hypot(ddx, ddy) / b.r);
            if (d > bd) { bd = d; best = b; }
          }
          if (best && bd > BAYER[(y % 4) * 4 + (x % 4)] * 0.9) {
            g.fillStyle = best.c;
            g.fillRect(x, y, 1, 1);
          }
        }
      }
      tex.refresh();
    }

    // Small moon (3-tone pixel disc).
    {
      const R = 6; const S = R * 2 + 1;
      const { tex, g } = this.canvasTex('moon', S, S);
      const tones = ['#14141c', '#262735', '#4a4c63', '#7a7d99'];
      for (let y = 0; y < S; y++) {
        for (let x = 0; x < S; x++) {
          const nx = (x - R) / R; const ny = (y - R) / R;
          const d2 = nx * nx + ny * ny;
          if (d2 > 1) continue;
          const l = Math.max(0, -nx * 0.6 - ny * 0.5 + Math.sqrt(1 - d2) * 0.6);
          const idx = Phaser.Math.Clamp(Math.floor(l * 4 + (BAYER[(y % 4) * 4 + (x % 4)] - 0.5)), 0, 3);
          g.fillStyle = tones[idx];
          g.fillRect(x, y, 1, 1);
        }
      }
      tex.refresh();
    }

    // Shooting star: 45° pixel trail fading toward the tail.
    {
      const N = 14;
      const { tex, g } = this.canvasTex('streak', N, N);
      for (let i = 0; i < N; i++) {
        const a = i / (N - 1);
        g.fillStyle = `rgba(220,230,255,${(0.15 + a * 0.85).toFixed(2)})`;
        g.fillRect(i, i, 1, 1);
      }
      tex.refresh();
    }
  }

  // Big gas giant with a ring, shaded per-pixel into a few dithered tones.
  makePlanetTexture(R) {
    const rng = new Phaser.Math.RandomDataGenerator(['planet-1']);
    const ringOut = R * 1.85;
    const S = Math.ceil(ringOut) * 2 + 2;
    const c = S / 2;
    const { tex, g } = this.canvasTex('planet', S, S);
    const img = g.createImageData(S, S);
    const put = (x, y, hex) => {
      const n = parseInt(hex.slice(1), 16);
      const i = (y * S + x) * 4;
      img.data[i] = n >> 16; img.data[i + 1] = (n >> 8) & 255; img.data[i + 2] = n & 255; img.data[i + 3] = 255;
    };

    const body = ['#0a0716', '#150f30', '#231a52', '#352878', '#4b3b9a'];
    const ringTones = ['#1b1638', '#2a2352', '#3b3270'];
    const L = (() => { const v = [-0.6, -0.5, 0.62]; const m = Math.hypot(...v); return v.map((a) => a / m); })();
    const tilt = -0.28;
    const squash = 0.3;

    const ringAt = (x, y) => {
      const u = x - c;
      const v = (y - c) - tilt * u;
      const r = Math.hypot(u, v / squash);
      let tone = -1;
      if (r >= R * 1.42 && r <= R * 1.6) tone = 1;
      else if (r >= R * 1.68 && r <= ringOut) tone = 2;
      else if (r >= R * 1.6 && r < R * 1.68) tone = -1;
      if (tone < 0) return null;
      const dither = BAYER[(y % 4) * 4 + (x % 4)] > 0.55 ? tone - 1 : tone;
      return { color: ringTones[Math.max(0, dither)], front: v >= 0 };
    };
    const bodyAt = (x, y) => {
      const nx = (x - c) / R; const ny = (y - c) / R;
      const d2 = nx * nx + ny * ny;
      if (d2 > 1) return null;
      const nz = Math.sqrt(1 - d2);
      let t = Math.max(0, nx * L[0] + ny * L[1] + nz * L[2]);
      t = t * 0.9 + Math.sin(ny * 8 + Math.sin(nx * 3) * 0.7) * 0.07;
      const idx = Phaser.Math.Clamp(Math.floor(t * 5 + (BAYER[(y % 4) * 4 + (x % 4)] - 0.5) * 0.9), 0, 4);
      return body[idx];
    };

    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
      const r = ringAt(x, y);
      if (r && !r.front) put(x, y, r.color); // ring behind the planet
    }
    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
      const b = bodyAt(x, y);
      if (b) put(x, y, b);
    }
    for (let y = 0; y < S; y++) for (let x = 0; x < S; x++) {
      const r = ringAt(x, y);
      if (r && r.front) put(x, y, r.color); // ring in front
    }
    // A few crater/storm pixels for character.
    for (let i = 0; i < 6; i++) {
      const x = Math.round(c + rng.realInRange(-0.6, 0.2) * R);
      const y = Math.round(c + rng.realInRange(-0.5, 0.5) * R);
      if (bodyAt(x, y)) { put(x, y, body[3]); put(x + 1, y, body[3]); }
    }

    g.putImageData(img, 0, 0);
    tex.refresh();
  }
}
