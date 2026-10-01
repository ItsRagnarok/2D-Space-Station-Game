import { defineConfig } from 'vite';

// base './' so the build works from file:// inside Capacitor's WebView.
export default defineConfig({
  base: './',
  build: { chunkSizeWarningLimit: 2000 },
});
