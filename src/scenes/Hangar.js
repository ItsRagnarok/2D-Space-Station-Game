import Room from '../game/Room.js';
import { S, setEnergy } from '../game/state.js';
import { ui } from '../ui/ui.js';

export default class Hangar extends Room {
  constructor() { super('Hangar'); this.spawns = { default: [192, 190], fromCommand: [48, 64] }; }
  static SPECIALS = { '2,6': 'floor_grate', '3,6': 'floor_grate', '21,7': 'floor_vent' };

  build() {
    this.addDoor(48, 'Command', 'fromHangar', 'Centrul de comandă');
    // wide window to space
    const gate = this.add.sprite(230, 46, 'o', 'space_gate_0').setOrigin(0.5, 1).setDepth(46); gate.play('space_gate');
    this.addLight({ x: 230, y: 56, s: 2.2, a: 0.5, glow: 0x3a86ff, ga: 0.16, gs: 2 });
    this.addInteractable({ x: 230, y: 62, r: 60, prompt: () => 'Fereastra spre spațiu', use: () => ui.dialog([{ who: 'ORION', text: 'Dedesubt e planeta sterpă pe care orbităm. Nimic nu a crescut acolo de mii de ani. Poate de asta stația e atât de importantă.' }]), anim: false });

    // landing pad + ship
    this.add.image(230, 196, 'o', 'pad').setOrigin(0.5, 1).setDepth(1);
    this.ship = this.prop('ship_0', 230, 176, { w: 44, h: 22 }, 'ship_idle'); this.shade(230, 176, 60);
    this.addLight({ x: 230, y: 168, s: 1.3, a: 0.6, glow: 0x58a4ff, ga: 0.2, gs: 1.1 });
    this.addInteractable({ x: 230, y: 184, r: 52,
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

    this.prop('tank', 340, 120, { w: 22, h: 10 }); this.prop('tank', 318, 124, { w: 22, h: 10 });
    this.prop('crate_steel', 38, 196, { w: 16, h: 10 }); this.prop('crate_orange', 56, 198, { w: 16, h: 10 }); this.prop('crate_steel', 47, 186).setDepth(199); this.shade(47, 198, 40);
    this.prop('console_0', 120, 52, { w: 44, h: 10 }, 'console'); this.addLight({ x: 120, y: 40, s: 0.8, a: 0.5, power: true });
    this.prop('rack_0', 356, 52, { w: 18, h: 10 });
  }

  onEnter() { S.flags.visitedHangar = true; }
}
