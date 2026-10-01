import Phaser from 'phaser';
import SpaceScene from './scenes/SpaceScene.js';

new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: '#02030a',
  scale: {
    mode: Phaser.Scale.RESIZE, // fills any phone screen / orientation
    width: window.innerWidth,
    height: window.innerHeight,
  },
  render: { antialias: true, powerPreference: 'low-power' },
  fps: { target: 60 },
  input: { activePointers: 2 },
  scene: [SpaceScene],
});
