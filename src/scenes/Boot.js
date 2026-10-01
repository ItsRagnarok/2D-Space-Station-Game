import Phaser from 'phaser';

export default class Boot extends Phaser.Scene {
  constructor() { super('Boot'); }

  preload() {
    this.load.atlas('o', 'assets/orbital.png', 'assets/orbital.json');
    this.load.image('vignette', 'assets/vignette.png');
  }

  create() {
    const A = this.anims;
    const seq = (name, n) => Array.from({ length: n }, (_, i) => ({ key: 'o', frame: `${name}_${i}` }));
    for (const outfit of ['station', 'eva']) {
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
    this.scene.start('Hydroponics');
  }
}
