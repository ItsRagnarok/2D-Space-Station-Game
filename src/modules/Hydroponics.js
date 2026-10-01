import { S, GROW_MS, setEnergy } from '../game/state.js';
import { ui } from '../ui/ui.js';

const NAMES = { crystal: 'Cristale', rare: 'Cristale rare', flora: 'Floră extraterestră', mush: 'Ciuperci luminiscente' };
const BED_POS = [[112, 118], [182, 118], [252, 118], [112, 172], [182, 172], [252, 172]];
const INCUBATORS = [
  { x: 30, kind: 'plant', text: 'Incubator: răsad de floră, crește sub lumină artificială.' },
  { x: 62, kind: 'crystal', text: 'Incubator: un cristal viu, pulsează încet.' },
  { x: 94, kind: 'jelly', text: 'Incubator: o formă de viață necunoscută. Pare să te urmărească.' },
];
const GEN = { x: 336, y: 196 };

export default class Hydroponics {
  static SPECIALS = { '3,8': 'floor_vent', '14,6': 'floor_vent', '8,4': 'floor_grate', '20,9': 'floor_grate' };
  static EMERGENCY = [[8, 62], [150, 56], [20, 200], [364, 200]];
  constructor(c) { this.c = c; }

  build() {
    const c = this.c;
    INCUBATORS.forEach((inc) => {
      c.prop('incubator_plant_0', inc.x, 56, { w: 22, h: 12 }, `incubator_${inc.kind}`);
      c.interact({ x: inc.x, y: 62, r: 26, prompt: () => inc.text, use: () => ui.toast(inc.text), anim: false });
      c.light({ x: inc.x, y: 70, s: 0.9, a: 0.7, power: true, glow: inc.kind === 'jelly' ? 0xb46bff : inc.kind === 'crystal' ? 0x3a86ff : 0x3ed06a, ga: 0.28, gs: 0.7 });
    });
    c.prop('console_0', 160, 52, { w: 44, h: 10 }, 'console'); c.prop('console_1', 208, 52, { w: 44, h: 10 }, 'console');
    c.light({ x: 160, y: 40, s: 0.8, a: 0.5, power: true }); c.light({ x: 208, y: 40, s: 0.8, a: 0.5, power: true });
    c.prop('rack_0', 262, 52, { w: 18, h: 10 }); c.prop('rack_1', 284, 52, { w: 18, h: 10 });
    c.prop('pipes_v', 376, 118, { w: 10, h: 104 });
    c.prop('bench_0', 330, 100, { w: 40, h: 12 }); c.shade(330, 100, 44); c.light({ x: 330, y: 84, s: 0.7, a: 0.5, power: true, glow: 0x3ed06a, ga: 0.16 });
    c.prop('locker_0', 14, 100, { w: 14, h: 12 });
    c.prop('crate_steel', 36, 200, { w: 16, h: 10 }); c.prop('crate_orange', 54, 202, { w: 16, h: 10 });
    c.sprite(45, 190, 'crate_steel', { origin: [0.5, 1], z: c.Y(203) }); c.shade(45, 202, 40);

    this.gen = c.prop('biogen_0', GEN.x, GEN.y, { w: 48, h: 16 }, 'biogen'); c.shade(GEN.x, GEN.y, 56);
    c.light({ x: GEN.x, y: GEN.y - 24, s: 1.5, a: 0.95, glow: 0x9aff20, ga: 0.33, gs: 1.1 });
    c.interact({ x: GEN.x, y: GEN.y + 4, r: 44,
      prompt: () => (S.res.flora >= 2 || S.res.mush >= 1) ? '[E] Alimentează bio-generatorul (2 floră sau 1 ciupercă) → energie' : 'Bio-generator · ai nevoie de 2 floră sau 1 ciupercă',
      use: () => {
        if (S.res.flora >= 2) { S.res.flora -= 2; setEnergy(S.energy + 25); S.counters.feed++; ui.toast('+25% energie'); }
        else if (S.res.mush >= 1) { S.res.mush -= 1; setEnergy(S.energy + 15); S.counters.feed++; ui.toast('+15% energie'); }
        else ui.toast('Nu ai combustibil biologic');
        ui.setRes(S.res);
      } });

    this.drone = c.sprite(160, 80, 'drone_0', { z: 6000, anim: 'drone' });
    this.droneShadow = c.sprite(160, 110, 'shadow_20', { z: c.Y(1), scale: 0.6, alpha: 0.7 });

    this.beds = S.beds.map((data, i) => {
      const [x, y] = BED_POS[i];
      const bed = { data, x, y, plants: [] };
      c.sprite(x, y, 'bed_0', { origin: [0.5, 1], z: c.Y(y) }); c.shade(x, y, 62); c.solid(x, y - 8, 54, 20);
      [-12, 12].forEach((dx) => bed.plants.push(c.sprite(x + dx, y - 12, 'plant_crystal_1_0', { origin: [0.5, 0.91], z: c.Y(y) + 1 })));
      bed.spark = c.sprite(x, y - 36, 'sparkle_0', { z: c.Y(y) + 2, anim: 'sparkle' }).setVisible(false);
      const color = data.type === 'rare' ? 0xff9a2a : data.type === 'mush' ? 0xa45cff : data.type === 'flora' ? 0x3ed06a : 0x3a86ff;
      c.light({ x, y: y - 22, s: 0.9, a: 0.75, power: true, when: () => data.stage === 3, glow: color, ga: 0.3, gs: 0.8 });
      c.interact({ x, y: y + 6, r: 38,
        prompt: () => {
          if (data.stage === 3) return `[E] Recoltează · ${NAMES[data.type]}`;
          const pct = Math.round((data.stage - 1) * 50 + (data.t / GROW_MS[data.stage - 1]) * 50);
          return `${NAMES[data.type]} · crește ${pct}%` + (S.energy < 25 ? ' (oprit: fără energie)' : '');
        },
        use: () => {
          if (data.stage !== 3) return;
          S.res[data.type] += 1; S.counters.harvest++; data.stage = 1; data.t = 0;
          ui.setRes(S.res); ui.toast(`+1 ${NAMES[data.type]}`);
        } });
      return bed;
    });
    this.plantFrame = 0; this.shown = [];
    c.time(600, () => { this.plantFrame = 1 - this.plantFrame; this.refresh(true); });
    this.refresh(true);
    if (S.crew.farmer) c.npc({ outfit: 'yellow', x: 148, y: 146, name: 'Fermierul', lines: ['Plantele cresc mai repede când le vorbești. Sau așa zic eu.', 'Mai aduc semințe din depozit. Tu ai grijă de energie.', 'Floră pentru generator, cristale pentru reactor. Nu le încurca.'] });
  }

  refresh(force) {
    this.beds.forEach((b, i) => {
      if (!force && this.shown[i] === b.data.stage) return;
      this.shown[i] = b.data.stage;
      b.plants.forEach((p) => p.setTexture('o', `plant_${b.data.type}_${b.data.stage}_${this.plantFrame}`));
      b.spark.setVisible(b.data.stage === 3);
    });
  }

  update(time) {
    this.refresh(false);
    const c = this.c;
    this.drone.setPosition(c.X(200 + Math.sin(time / 1700) * 90), c.Y(84 + Math.sin(time / 520) * 3));
    this.droneShadow.setPosition(this.drone.x, c.Y(112));
  }
}
