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
    this.ship = c.prop('ship_0', 230, 176, { w: 44, h: 22 }, 'ship_idle'); this.ship.setVisible(false); c.shade(230, 176, 90);
    this.shipImg = c.scene.add.image(c.X(230), c.Y(182), 'ship_hero').setOrigin(0.5, 1).setDepth(c.Y(177)); this.padPos = { x: c.X(230), y: c.Y(182) };
    c.scene.hangarPad = this.padPos; c.scene.hangarShip = this.shipImg;
    c.light({ x: 230, y: 168, s: 1.3, a: 0.6, glow: 0x58a4ff, ga: 0.2, gs: 1.1 });
    c.interact({ x: 230, y: 186, r: 62,
      prompt: () => {
        if (c.scene.piloting) return null;
        if (S.act >= 3 && !S.flags.shipReady) return S.flags.signalScanned ? '[E] Pregătește nava Meridian (10% energie)' : 'Meridian · decodează mai întâi semnalul în comandă';
        return '[E] Pilotează Meridian';
      },
      use: () => {
        if (c.scene.piloting) return;
        if (S.act >= 3 && !S.flags.shipReady) {
          if (!S.flags.signalScanned) { ui.toast('Mai întâi decodează semnalul'); return; }
          if (S.energy < 40) { ui.toast('Energie prea mică pentru pregătire (≥ 40%)'); return; }
          setEnergy(S.energy - 10); S.flags.shipReady = true;
          ui.dialog([{ who: 'ORION', text: 'Rezervoarele sunt pline, motoarele calibrate. Meridian e gata.' }]);
        } else c.scene.startFlight();
      } });

    c.prop('tank', 350, 120, { w: 22, h: 10 }); c.prop('tank', 328, 124, { w: 22, h: 10 });
    c.prop('crate_steel', 38, 196, { w: 16, h: 10 }); c.prop('crate_orange', 56, 198, { w: 16, h: 10 });
    c.sprite(47, 186, 'crate_steel', { origin: [0.5, 1], z: c.Y(199) }); c.shade(47, 198, 40);
    c.prop('console_0', 110, 52, { w: 44, h: 10 }, 'console'); c.light({ x: 110, y: 40, s: 0.8, a: 0.5, power: true });
    c.prop('rack_0', 30, 52, { w: 18, h: 10 });
    c.prop('bench_1', 336, 196, { w: 40, h: 12 }); c.shade(336, 196, 44); c.prop('locker_0', 366, 190, { w: 14, h: 12 });
    [[168, 120], [292, 120], [168, 200], [292, 200]].forEach(([x, y]) => c.light({ x, y, s: 0.45, a: 0.4, glow: 0xff9a2a, ga: 0.28 }));
  }
  onEnter() { S.flags.visitedHangar = true; }
}
