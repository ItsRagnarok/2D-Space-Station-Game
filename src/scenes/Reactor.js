import Room from '../game/Room.js';
import { S, setEnergy } from '../game/state.js';
import { ui } from '../ui/ui.js';

export default class Reactor extends Room {
  constructor() { super('Reactor'); this.spawns = { default: [192, 190], fromCommand: [192, 64] }; this.emergencyPoints = [[24, 64], [360, 64], [24, 200], [360, 200]]; }
  static SPECIALS = { '10,7': 'floor_vent', '13,7': 'floor_vent', '4,5': 'floor_grate', '19,5': 'floor_grate' };

  build() {
    this.addDoor(192, 'Command', 'fromReactor', 'Centrul de comandă');
    this.prop('pipes_v', 14, 150, { w: 10, h: 104 }); this.prop('pipes_v', 370, 150, { w: 10, h: 104 });
    this.prop('console_0', 80, 52, { w: 44, h: 10 }, 'console'); this.prop('console_1', 304, 52, { w: 44, h: 10 }, 'console');
    this.addLight({ x: 80, y: 40, s: 0.8, a: 0.5, power: true }); this.addLight({ x: 304, y: 40, s: 0.8, a: 0.5, power: true });
    this.prop('tank', 330, 120, { w: 22, h: 10 }); this.prop('tank', 354, 124, { w: 22, h: 10 });
    this.prop('crate_orange', 40, 190, { w: 16, h: 10 }); this.prop('crate_steel', 58, 192, { w: 16, h: 10 });

    this.core = this.prop('reactor_off', 192, 150, { w: 44, h: 18 }); this.shade(192, 150, 62);
    this.coreOn = null;
    this.addLight({ x: 192, y: 112, s: 2.1, a: 1, when: () => this.isOn(), glow: 0xff9a2a, ga: 0.34, gs: 1.7 });
    this.addInteractable({ x: 192, y: 160, r: 50,
      prompt: () => {
        if (S.res.crystal >= 2) return `[E] Alimentează reactorul (2 cristale → +20% energie)${this.isOn() ? '' : ' · repornește-l'}`;
        if (S.res.rare >= 1) return '[E] Alimentează reactorul (1 cristal rar → +30% energie)';
        return this.isOn() ? 'Reactorul funcționează. Combustibil: 2 cristale sau 1 cristal rar.' : 'Reactorul e rece. Ai nevoie de 2 cristale.';
      },
      use: () => {
        if (S.res.crystal >= 2) { S.res.crystal -= 2; setEnergy(S.energy + 20); S.counters.reactorFed++; ui.toast('+20% energie · reactor alimentat'); }
        else if (S.res.rare >= 1) { S.res.rare -= 1; setEnergy(S.energy + 30); S.counters.reactorFed++; ui.toast('+30% energie · reactor alimentat'); }
        else ui.toast('Nu ai combustibil pentru reactor');
        ui.setRes(S.res);
      } });
    if (S.crew.engineer) this.addNpc({ outfit: 'green', x: 134, y: 146, name: 'Inginerul', lines: ['Reactorul respiră mai bine acum. Încă pierdem energie, dar mai încet.', 'Cristalele rare dau cel mai mult. Dar nu le irosi.', 'Dacă se întunecă, ține lanterna aprinsă și vino direct aici.'] });
  }

  isOn() { return S.energy >= 5; }

  roomUpdate() {
    const on = this.isOn();
    if (on !== this.coreOn) {
      this.coreOn = on;
      if (on) this.core.play('reactor_on'); else { this.core.stop(); this.core.setTexture('o', 'reactor_off'); }
    }
  }
}
