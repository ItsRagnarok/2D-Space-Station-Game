import { S, setEnergy } from '../game/state.js';
import { ui } from '../ui/ui.js';

export default class Reactor {
  static SPECIALS = { '10,7': 'floor_vent', '13,7': 'floor_vent', '4,5': 'floor_grate', '19,5': 'floor_grate' };
  static EMERGENCY = [[24, 64], [360, 64], [24, 200], [360, 200]];
  constructor(c) { this.c = c; }

  build() {
    const c = this.c;
    c.prop('pipes_v', 14, 124, { w: 10, h: 104 }); c.prop('pipes_v', 370, 150, { w: 10, h: 104 });
    c.prop('console_0', 80, 52, { w: 44, h: 10 }, 'console'); c.prop('console_1', 304, 52, { w: 44, h: 10 }, 'console');
    c.light({ x: 80, y: 40, s: 0.8, a: 0.5, power: true }); c.light({ x: 304, y: 40, s: 0.8, a: 0.5, power: true });
    c.prop('tank', 330, 120, { w: 22, h: 10 }); c.prop('tank', 354, 124, { w: 22, h: 10 });
    c.prop('locker_0', 36, 100, { w: 14, h: 12 }); c.prop('locker_1', 54, 100, { w: 14, h: 12 }); c.light({ x: 45, y: 80, s: 0.8, a: 0.5, glow: 0xe8902a, ga: 0.22 });
    c.prop('rack_1', 340, 196, { w: 18, h: 10 });
    c.prop('crate_orange', 40, 190, { w: 16, h: 10 }); c.prop('crate_steel', 58, 192, { w: 16, h: 10 });

    this.core = c.prop('reactor_off', 192, 150, { w: 44, h: 18 }); c.shade(192, 150, 62);
    this.coreOn = null;
    c.light({ x: 192, y: 112, s: 2.1, a: 1, when: () => this.isOn(), glow: 0xff9a2a, ga: 0.34, gs: 1.7 });
    c.interact({ x: 192, y: 160, r: 50,
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
    if (S.crew.engineer) c.npc({ outfit: 'green', x: 134, y: 146, name: 'Inginerul', lines: ['Reactorul respiră mai bine acum. Încă pierdem energie, dar mai încet.', 'Cristalele rare dau cel mai mult. Dar nu le irosi.', 'Dacă se întunecă, ține lanterna aprinsă și vino direct aici.'] });
  }

  isOn() { return S.energy >= 5; }
  update() {
    const on = this.isOn();
    if (on !== this.coreOn) {
      this.coreOn = on;
      if (on) this.core.play('reactor_on'); else { this.core.stop(); this.core.setTexture('o', 'reactor_off'); }
    }
  }
}
