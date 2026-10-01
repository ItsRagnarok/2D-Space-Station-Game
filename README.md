# 2D Space Station Game

HTML5 + Phaser 3 (Vite), mobile-first. Packaged for Android later with Capacitor.

```bash
npm install
npm run dev      # dev server (reachable from your phone on the LAN)
npm run build    # outputs dist/ (base './' so it works inside Capacitor)
```

Current scene: procedural animated space (parallax stars, nebula, distant ringed planet + moon,
shooting stars) on a 20000x20000 wrapping world. Drag to look around; it glides on its own when idle.
