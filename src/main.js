import Phaser from 'phaser';
import SpaceScene from './scenes/SpaceScene.js';

// The game renders at the real screen size so motion is sub-pixel smooth; the
// pixel-art look comes from scaling the art up (see ART in SpaceScene) with
// nearest-neighbour filtering.
const PIXEL = 1;
const logicalSize = () => ({
  width: Math.max(120, Math.ceil(window.innerWidth / PIXEL)),
  height: Math.max(120, Math.ceil(window.innerHeight / PIXEL)),
});

const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: '#04050b',
  ...logicalSize(),
  scale: { mode: Phaser.Scale.NONE },
  pixelArt: true,
  roundPixels: true,
  render: { antialias: false, powerPreference: 'low-power' },
  fps: { target: 60 },
  input: { activePointers: 2 },
  scene: [SpaceScene],
});

const onResize = () => {
  const { width, height } = logicalSize();
  game.scale.resize(width, height);
};
window.addEventListener('resize', onResize);
window.addEventListener('orientationchange', () => setTimeout(onResize, 150));
