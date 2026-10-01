import Phaser from 'phaser';
import Boot from './scenes/Boot.js';
import Hydroponics from './scenes/Hydroponics.js';

const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: 'game',
  backgroundColor: '#000000',
  scale: { mode: Phaser.Scale.RESIZE, width: window.innerWidth, height: window.innerHeight },
  pixelArt: true,
  roundPixels: true,
  render: { antialias: false, powerPreference: 'low-power' },
  fps: { target: 60 },
  physics: { default: 'arcade', arcade: { gravity: { y: 0 } } },
  input: { activePointers: 3 },
  scene: [Boot, Hydroponics],
});

// iOS reports the new size late after launch/rotation: ask Phaser to re-measure a few times.
const remeasure = () => [60, 250, 700].forEach((t) => setTimeout(() => game.scale.refresh(), t));
window.addEventListener('orientationchange', remeasure);
window.addEventListener('resize', remeasure);
if (window.visualViewport) window.visualViewport.addEventListener('resize', remeasure);
remeasure();
