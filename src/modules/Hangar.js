import { S, setEnergy } from '../game/state.js';
import { ui } from '../ui/ui.js';

export default class Hangar {
  static SPECIALS = { '2,6': 'floor_grate', '3,6': 'floor_grate', '21,7': 'floor_vent' };
  static EMERGENCY = [[24, 64], [360, 64], [24, 200], [360, 200]];
  constructor(c) { this.c = c; }

  build() {
    const c = this.c;
    c.sprite(300, 46, 'space_gate_0', { origin: [0.5, 1], z: c.Y(46), anim: 'space_gate' });
    c.light({ x: 300, y: 56, s: 2.2, a: 0.5, glow: 0x3a86ff, ga: 0.16, gs: 2 });
    c.interact({ x: 300, y: 62, r: 60, prompt: () => 'Fereastra spre spațiu', use: () => ui.dialog([{ who: 'ORION', text: 'Dedesubt e planeta sterpă pe care orbităm. Nimic nu a crescut acolo de mii de ani. Poate de asta stația e atât de importantă.' }]), anim: false });

    c.sprite(230, 196, 'pad', { origin: [0.5, 1], z: c.Y(1) });
    this.ship = c.prop('ship_0', 230, 176, { w: 44, h: 22 }, 'ship_idle'); c.shade(230, 176, 60);
    c.light({ x: 230, y: 168, s: 1.3, a: 0.6, glow: 0x58a4ff, ga: 0.2, gs: 1.1 });
    c.interact({ x: 230, y: 184, r: 52,
      prompt: () => {
        if (S.act >= 3 && !S.flags.shipReady) return S.flags.signalScanned ? '[E] Pregătește nava Meridian (10% energie)' : 'Meridian · decodează mai întâi semnalul în comandă';
        return S.flags.shipReady ? 'Meridian e pregătită pentru zbor' : '[E] Nava Meridian';
      },
      use: () => {
        if (S.act >= 3 && !S.flags.shipReady) {
          if (!S.flags.signalScanned) { ui.toast('Mai întâi decodează semnalul'); return; }
          if (S.energy < 40) { ui.toast('Energie prea mică pentru pregătire (≥ 40%)'); return; }
          setEnergy(S.energy - 10); S.flags.shipReady = true;
          ui.dialog([{ who: 'ORION', text: 'Rezervoarele sunt pline, motoarele calibrate. Meridian e gata.' }]);
        } else ui.dialog([{ who: 'ORION', text: 'Meridian. Navă de explorare ușoară. Rezervoarele erau goale când am adormit.' }]);
      } });

    c.prop('tank', 350, 120, { w: 22, h: 10 }); c.prop('tank', 328, 124, { w: 22, h: 10 });
    c.prop('crate_steel', 38, 196, { w: 16, h: 10 }); c.prop('crate_orange', 56, 198, { w: 16, h: 10 });
    c.sprite(47, 186, 'crate_steel', { origin: [0.5, 1], z: c.Y(199) }); c.shade(47, 198, 40);
    c.prop('console_0', 110, 52, { w: 44, h: 10 }, 'console'); c.light({ x: 110, y: 40, s: 0.8, a: 0.5, power: true });
    c.prop('rack_0', 30, 52, { w: 18, h: 10 });
  }
  onEnter() { S.flags.visitedHangar = true; }
}
