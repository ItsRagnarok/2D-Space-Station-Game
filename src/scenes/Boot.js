import Phaser from 'phaser';
import { initUi, ui } from '../ui/ui.js';
import { initControls } from '../ui/controls.js';
import { S, on, energyState } from '../game/state.js';

export default class Boot extends Phaser.Scene {
  constructor() { super('Boot'); }

  preload() {
    this.load.atlas('o', 'assets/orbital.png', 'assets/orbital.json');
    this.load.image('vignette', 'assets/vignette.png');
    this.load.image('stars_tile', 'assets/stars_tile.png');
    this.load.image('planet_rock', 'assets/planet_rock.png');
  }

  create() {
    initUi(); initControls();
    on('energy', (e) => { const [l, c] = energyState(e); ui.setEnergy(e, l, c); });
    const A = this.anims;
    const seq = (name, n) => Array.from({ length: n }, (_, i) => ({ key: 'o', frame: `${name}_${i}` }));
    for (const outfit of ['station', 'eva', 'yellow', 'green']) {
      for (const dir of ['down', 'up', 'right']) {
        const base = `odysseus_${outfit}_${dir}`;
        A.create({ key: `${base}_idle`, frames: seq(`${base}_idle`, 2), frameRate: 2, repeat: -1 });
        A.create({ key: `${base}_walk`, frames: seq(`${base}_walk`, 4), frameRate: 8, repeat: -1 });
        A.create({ key: `${base}_act`, frames: seq(`${base}_act`, 2), frameRate: 6, repeat: 2 });
      }
    }
    A.create({ key: 'biogen', frames: seq('biogen', 4), frameRate: 5, repeat: -1 });
    for (const k of ['plant', 'crystal', 'jelly']) A.create({ key: `incubator_${k}`, frames: seq(`incubator_${k}`, 4), frameRate: 4, repeat: -1 });
    A.create({ key: 'console', frames: seq('console', 4), frameRate: 3, repeat: -1 });
    A.create({ key: 'drone', frames: seq('drone', 2), frameRate: 12, repeat: -1 });
    A.create({ key: 'sparkle', frames: seq('sparkle', 2), frameRate: 4, repeat: -1 });
    A.create({ key: 'reactor_on', frames: seq('reactor_on', 4), frameRate: 6, repeat: -1 });
    A.create({ key: 'ship_idle', frames: seq('ship', 3), frameRate: 6, repeat: -1 });
    A.create({ key: 'space_gate', frames: seq('space_gate', 2), frameRate: 1, repeat: -1 });
    A.create({ key: 'screen_map', frames: seq('screen_map', 4), frameRate: 3, repeat: -1 });
    A.create({ key: 'orion', frames: seq('orion', 4), frameRate: 3, repeat: -1 });
    A.create({ key: 'cryo', frames: seq('cryo_terminal', 2), frameRate: 2, repeat: -1 });
    this.scene.start('Station');
  }
}
