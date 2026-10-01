import Room from '../game/Room.js';
import { S, GROW_MS, setEnergy } from '../game/state.js';
import { ACTS } from '../game/story.js';
import { ui } from '../ui/ui.js';

const NAMES = { crystal: 'Cristale', rare: 'Cristale rare', flora: 'Floră extraterestră', mush: 'Ciuperci luminiscente' };
const BED_POS = [[112, 118], [182, 118], [252, 118], [112, 172], [182, 172], [252, 172]];
const INCUBATORS = [
  { x: 30, kind: 'plant', text: 'Incubator: răsad de floră, crește sub lumină artificială.' },
  { x: 62, kind: 'crystal', text: 'Incubator: un cristal viu, pulsează încet.' },
  { x: 94, kind: 'jelly', text: 'Incubator: o formă de viață necunoscută. Pare să te urmărească.' },
];
const GEN = { x: 336, y: 196 };

export default class Hydroponics extends Room {
  constructor() { super('Hydroponics'); this.spawns = { default: [64, 150], fromCommand: [160, 64] }; }
  static SPECIALS = { '3,8': 'floor_vent', '14,6': 'floor_vent', '8,4': 'floor_grate', '20,9': 'floor_grate' };

  build() {
    INCUBATORS.forEach((inc) => {
      this.prop('incubator_plant_0', inc.x, 56, { w: 22, h: 12 }, `incubator_${inc.kind}`);
      this.addInteractable({ x: inc.x, y: 62, r: 26, prompt: () => inc.text, use: () => ui.toast(inc.text), anim: false });
      this.addLight({ x: inc.x, y: 70, s: 0.9, a: 0.7, power: true, glow: inc.kind === 'jelly' ? 0xb46bff : inc.kind === 'crystal' ? 0x3a86ff : 0x3ed06a, ga: 0.28, gs: 0.7 });
    });
    this.addDoor(160, 'Command', 'fromHydroponics', 'Centrul de comandă');
    this.prop('console_0', 214, 52, { w: 44, h: 10 }, 'console'); this.prop('console_1', 262, 52, { w: 44, h: 10 }, 'console');
    this.addLight({ x: 214, y: 40, s: 0.8, a: 0.5, power: true }); this.addLight({ x: 262, y: 40, s: 0.8, a: 0.5, power: true });
    this.prop('rack_0', 306, 52, { w: 18, h: 10 });
    this.prop('pipes_v', 376, 150, { w: 10, h: 104 });
    this.prop('crate_steel', 36, 200, { w: 16, h: 10 }); this.prop('crate_orange', 54, 202, { w: 16, h: 10 });
    this.prop('crate_steel', 45, 190).setDepth(203); this.shade(45, 202, 40);

    this.gen = this.prop('biogen_0', GEN.x, GEN.y, { w: 48, h: 16 }, 'biogen'); this.shade(GEN.x, GEN.y, 56);
    this.addLight({ x: GEN.x, y: GEN.y - 24, s: 1.5, a: 0.95, glow: 0x9aff20, ga: 0.33, gs: 1.1 });
    this.addInteractable({ x: GEN.x, y: GEN.y + 4, r: 44,
      prompt: () => (S.res.flora >= 2 || S.res.mush >= 1) ? '[E] Alimentează bio-generatorul (2 floră sau 1 ciupercă) → energie' : 'Bio-generator · ai nevoie de 2 floră sau 1 ciupercă',
      use: () => {
        if (S.res.flora >= 2) { S.res.flora -= 2; setEnergy(S.energy + 25); S.counters.feed++; ui.toast('+25% energie'); }
        else if (S.res.mush >= 1) { S.res.mush -= 1; setEnergy(S.energy + 15); S.counters.feed++; ui.toast('+15% energie'); }
        else ui.toast('Nu ai combustibil biologic');
        ui.setRes(S.res);
      } });

    this.drone = this.add.sprite(160, 80, 'o', 'drone_0').setDepth(600).play('drone');
    this.droneShadow = this.add.image(160, 110, 'o', 'shadow_20').setDepth(1).setScale(0.6).setAlpha(0.7);

    this.beds = S.beds.map((data, i) => {
      const [x, y] = BED_POS[i];
      const bed = { data, x, y, plants: [] };
      this.add.sprite(x, y, 'o', 'bed_0').setOrigin(0.5, 1).setDepth(y); this.shade(x, y, 62); this.solid(x, y - 8, 54, 20);
      [-12, 12].forEach((dx) => bed.plants.push(this.add.image(x + dx, y - 12, 'o', 'plant_crystal_1_0').setOrigin(0.5, 0.91).setDepth(y + 1)));
      bed.spark = this.add.sprite(x, y - 36, 'o', 'sparkle_0').setDepth(y + 2).play('sparkle').setVisible(false);
      const color = data.type === 'rare' ? 0xff9a2a : data.type === 'mush' ? 0xa45cff : data.type === 'flora' ? 0x3ed06a : 0x3a86ff;
      this.addLight({ x, y: y - 22, s: 0.9, a: 0.75, power: true, when: () => data.stage === 3, glow: color, ga: 0.3, gs: 0.8 });
      this.addInteractable({ x, y: y + 6, r: 38,
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
    this.time.addEvent({ delay: 600, loop: true, callback: () => { this.plantFrame = 1 - this.plantFrame; this.refreshPlants(true); } });
    this.refreshPlants(true);
    if (S.crew.farmer) this.addNpc({ outfit: 'yellow', x: 148, y: 146, name: 'Fermierul', lines: ['Plantele cresc mai repede când le vorbești. Sau așa zic eu.', 'Mai aduc semințe din depozit. Tu ai grijă de energie.', 'Floră pentru generator, cristale pentru reactor. Nu le încurca.'] });
  }

  refreshPlants(force) {
    this.beds.forEach((b, i) => {
      if (!force && this.shown[i] === b.data.stage) return;
      this.shown[i] = b.data.stage;
      b.plants.forEach((p) => p.setTexture('o', `plant_${b.data.type}_${b.data.stage}_${this.plantFrame}`));
      b.spark.setVisible(b.data.stage === 3);
    });
  }

  roomUpdate(time) {
    this.refreshPlants(false);
    this.drone.x = 200 + Math.sin(time / 1700) * 90; this.drone.y = 84 + Math.sin(time / 520) * 3;
    this.droneShadow.setPosition(this.drone.x, 112);
  }

  onEnter() {
    if (!S.introSeen) {
      S.introSeen = true; ui.banner('Actul 1', 'Trezirea'); ui.dialog(ACTS[0].intro);
    }
  }
}
