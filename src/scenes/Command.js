import Room from '../game/Room.js';
import { S, setEnergy } from '../game/state.js';
import { currentAct } from '../game/story.js';
import { ui } from '../ui/ui.js';

const CREW = {
  farmer: { name: 'Fermierul', cost: 'crystal', n: 2, label: '2 cristale', outfit: 'yellow', gain: 'plantele cresc cu 50% mai repede' },
  engineer: { name: 'Inginerul', cost: 'rare', n: 1, label: '1 cristal rar', outfit: 'green', gain: 'energia scade cu 30% mai încet' },
};

export default class Command extends Room {
  constructor() { super('Command'); this.spawns = { default: [192, 150], fromHydroponics: [48, 64], fromReactor: [192, 64], fromHangar: [336, 64] }; }
  static SPECIALS = { '11,4': 'floor_grate', '12,4': 'floor_grate', '3,8': 'floor_vent', '20,8': 'floor_vent' };

  build() {
    this.addDoor(48, 'Hydroponics', 'fromCommand', 'Hidroponică');
    this.addDoor(192, 'Reactor', 'fromCommand', 'Reactor');
    this.addDoor(336, 'Hangar', 'fromCommand', 'Hangar');
    [120, 264].forEach((x, i) => {
      const s = this.add.sprite(x, 46, 'o', `screen_map_${i}`).setOrigin(0.5, 1).setDepth(46); s.play('screen_map');
      this.addLight({ x, y: 36, s: 1.1, a: 0.55, power: true, glow: 0x22c4c4, ga: 0.16 });
    });

    // ORION terminal
    this.prop('orion_0', 58, 118, { w: 24, h: 10 }, 'orion'); this.shade(58, 118, 30);
    this.addLight({ x: 58, y: 98, s: 0.9, a: 0.7, glow: 0x22c4c4, ga: 0.3 });     // ORION never fully sleeps
    this.addInteractable({ x: 58, y: 124, r: 34, prompt: () => '[E] Vorbește cu ORION', use: () => {
      const a = currentAct();
      const todo = a.objectives.filter((o) => !S.objDone[o.id]).map((o) => o.text);
      ui.dialog([{ who: 'ORION', text: `Actul ${a.n}, ${a.title}. Rămas de făcut: ${todo.length ? todo.join('; ') : 'nimic'}.` }, { who: 'ORION', text: `Energie ${Math.round(S.energy)}%. Cât timp ai lanterna, nu ești singur în întuneric.` }]);
    } });

    // holo table (the research generator, reused) with a rotating globe
    this.prop('generator_0', 192, 168, { w: 60, h: 18 }, null);
    this.shade(192, 168, 70);
    this.globe = this.add.image(192, 104, 'o', 'globe_00').setDepth(169); this.globeI = 0;
    this.addLight({ x: 192, y: 112, s: 1.5, a: 0.9, power: true, glow: 0x3a86ff, ga: 0.3, gs: 1.2 });
    this.addInteractable({ x: 192, y: 176, r: 44,
      prompt: () => S.act >= 3 && !S.flags.signalScanned ? '[E] Decodează semnalul (1 cristal rar)' : '[E] Masa holografică',
      use: () => {
        if (S.act >= 3 && !S.flags.signalScanned) {
          if (S.res.rare < 1) { ui.toast('Ai nevoie de 1 cristal rar'); return; }
          S.res.rare -= 1; S.flags.signalScanned = true; ui.setRes(S.res);
          ui.dialog([{ who: 'ORION', text: 'Semnalul e decodat: coordonate. O planetă la două salturi de aici. Ceva ne cheamă.' }]);
        } else ui.dialog([{ who: 'ORION', text: S.flags.signalScanned ? 'Coordonatele sunt salvate. Nava Meridian așteaptă în hangar.' : 'Harta sectorului. Deocamdată, doar zgomot și stele.' }]);
      } });

    // cryo terminal
    this.prop('cryo_terminal_0', 330, 118, { w: 28, h: 10 }, 'cryo'); this.shade(330, 118, 34);
    this.addLight({ x: 330, y: 100, s: 0.8, a: 0.6, power: true, glow: 0xf2a93b, ga: 0.2 });
    const nextCrew = () => (!S.crew.farmer ? 'farmer' : !S.crew.engineer ? 'engineer' : null);
    this.addInteractable({ x: 330, y: 124, r: 36,
      prompt: () => { const k = nextCrew(); if (!k) return 'Terminal de criosomn · toți membrii sunt treji'; return `[E] Trezește ${CREW[k].name} (${CREW[k].label}, energie ≥ 40%)`; },
      use: () => {
        const k = nextCrew(); if (!k) { ui.toast('Toți membrii echipajului sunt treji'); return; }
        const c = CREW[k];
        if (S.energy < 40) { ui.toast('Prea puțină energie pentru criosomn (≥ 40%)'); return; }
        if (S.res[c.cost] < c.n) { ui.toast(`Îți trebuie ${c.label}`); return; }
        S.res[c.cost] -= c.n; S.crew[k] = true; setEnergy(S.energy - 5); ui.setRes(S.res);
        ui.dialog([{ who: 'ORION', text: `${c.name} se trezește din criosomn.` }, { who: c.name, text: `Unde… Odysseus? Bine. Am pierdut timp. Bonus: ${c.gain}.` }]);
      } });

    this.prop('console_0', 120, 196, { w: 44, h: 10 }, 'console'); this.prop('console_1', 264, 196, { w: 44, h: 10 }, 'console');
    this.addLight({ x: 120, y: 184, s: 0.7, a: 0.45, power: true }); this.addLight({ x: 264, y: 184, s: 0.7, a: 0.45, power: true });
  }

  roomUpdate(time) {
    const i = Math.floor(time / 130) % 12;
    if (i !== this.globeI) { this.globeI = i; this.globe.setFrame(`globe_${String(i).padStart(2, '0')}`); }
    this.globe.y = 104 + Math.sin(time / 600) * 1.5;
  }

  onEnter() { S.flags.visitedCommand = true; }
}
