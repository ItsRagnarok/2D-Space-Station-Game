import Phaser from 'phaser';
import SpaceScene from './scenes/SpaceScene.js';

// Pixel-art look: the game renders at a small logical resolution and the canvas
// is stretched with nearest-neighbour filtering (see index.html CSS).
const PIXEL = 3; // one game pixel = 3 screen pixels
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
