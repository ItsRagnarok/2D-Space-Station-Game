import Hydroponics from '../modules/Hydroponics.js';
import Command from '../modules/Command.js';
import Reactor from '../modules/Reactor.js';
import Hangar from '../modules/Hangar.js';
import Lab from '../modules/Lab.js';

// The whole station is ONE world. Every room is a module placed at (ox, oy); rooms are 384x220 (wall on top).
// `gaps` = openings in the hull (local coordinates) where corridors connect; `topDoors` = doors in the back wall.
export const RW = 384, RH = 220;
export const WW = 1488, WH = 860;

export const MODULES = [
  { key: 'Hydroponics', accent: 0x3ed06a, label: 'Hidroponică', cls: Hydroponics, ox: 120, oy: 300, gaps: { right: [[130, 190]] }, spawn: [64, 150] },
  { key: 'Command', accent: 0x25d0cf, label: 'Centrul de comandă', cls: Command, ox: 552, oy: 300, gaps: { left: [[130, 190]], right: [[130, 190]], bottom: [[160, 224]] }, topDoors: [{ x: 192, locked: true, label: 'Laborator' }], spawn: [192, 150] },
  { key: 'Reactor', accent: 0xff9a2a, label: 'Reactor', cls: Reactor, ox: 984, oy: 300, gaps: { left: [[130, 190]] }, spawn: [192, 190] },
  { key: 'Hangar', accent: 0x58a4ff, label: 'Hangar', cls: Hangar, ox: 552, oy: 568, gaps: {}, topDoors: [{ x: 192 }], spawn: [192, 190] },
  { key: 'Lab', accent: 0xf2a93b, label: 'Laborator', cls: Lab, ox: 552, oy: 32, gaps: {}, locked: true, spawn: [192, 150] },
];

// Corridors (world coordinates). H = horizontal, V = vertical.
export const CORRIDORS = [
  { type: 'H', x0: 504, x1: 552, y0: 430, y1: 490 },
  { type: 'H', x0: 936, x1: 984, y0: 430, y1: 490 },
  { type: 'V', x0: 712, x1: 776, y0: 520, y1: 568 },
];
