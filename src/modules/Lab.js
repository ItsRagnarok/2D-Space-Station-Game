// Under construction: visible from the Command room, not reachable until a later act.
export default class Lab {
  static SPECIALS = {};
  constructor(c) { this.c = c; }
  build() {
    const c = this.c, st = c.scene;
    const R = (x, y, w, h, col, a = 1, z = c.Y(60)) => st.add.rectangle(c.X(x) + w / 2, c.Y(y) + h / 2, w, h, col, a).setDepth(z);
    R(0, 0, 384, 220, 0x000000, 0.55, c.Y(300));                          // dim the whole room: nobody works here yet
    for (let x = 24; x < 384; x += 48) { R(x, 52, 3, 150, 0xb0580f); R(x, 52, 1, 150, 0xe8902a, 1, c.Y(61)); }
    for (const y of [70, 120, 170]) { R(8, y, 368, 3, 0xb0580f); R(8, y, 368, 1, 0xe8902a, 1, c.Y(61)); }
    const t = c.scene.add.text(c.X(192), c.Y(120), 'LABORATOR · ÎN CONSTRUCȚIE', { fontFamily: 'Rajdhani, sans-serif', fontSize: '12px', fontStyle: '700', color: '#f2b84b', backgroundColor: '#02040acc', padding: { x: 6, y: 3 } }).setOrigin(0.5).setDepth(c.Y(61)).setResolution(2);
    c.prop('crate_orange', 60, 190); c.prop('crate_steel', 80, 192); c.prop('crate_orange', 320, 188);
  }
}
