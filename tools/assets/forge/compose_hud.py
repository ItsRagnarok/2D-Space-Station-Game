"""Compose the final preview: pixel scene (x3, nearest) + HUD panels (real font) -> HTML -> PNG via Chromium."""
import base64, subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, '..', 'out')
def b64(p): return base64.b64encode(open(os.path.join(out, p), 'rb').read()).decode()
scene = b64('scene_native.png')
icons = {k: b64(f'icons/{k}.png') for k in ('gear', 'crystal', 'chip', 'coin', 'ship_blueprint')}
html = f'''<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;background:#000}}
.stage{{position:relative;width:960px;height:540px;overflow:hidden;font-family:'Rajdhani','DejaVu Sans Condensed',sans-serif;font-weight:600;color:#d8fff0}}
img{{image-rendering:pixelated;position:absolute}}
.p{{position:absolute;box-sizing:border-box;background:rgba(3,22,20,.9);border:3px solid #2fe58a;border-radius:8px;box-shadow:0 0 14px rgba(47,229,138,.35),inset 0 0 18px rgba(47,229,138,.08);padding:12px 16px}}
.h{{display:flex;align-items:center;gap:10px;color:#2fe58a;font-size:20px;letter-spacing:1.5px;text-transform:uppercase;font-weight:700}}
.bar{{height:14px;background:#04231c;border:2px solid #1f8a5c;margin:8px 0 12px;position:relative}}
.bar i{{position:absolute;left:0;top:0;bottom:0;width:42%;background:repeating-linear-gradient(90deg,#2fe58a 0 6px,#25c474 6px 8px)}}
.obj{{display:flex;align-items:center;gap:10px;font-size:17px;margin:6px 0;white-space:nowrap}}
.obj b{{flex:none;width:12px;height:12px;border:2px solid #e8c02a;border-radius:50%}}
.row{{display:flex;align-items:center;justify-content:space-between;font-size:18px;margin:9px 0;white-space:nowrap}}
.row>span{{display:flex;align-items:center;gap:10px}}
.dim{{color:#8fb7aa;font-size:14px;white-space:nowrap;letter-spacing:1px;text-transform:uppercase}}
</style></head><body><div class="stage">
<img src="data:image/png;base64,{scene}" style="left:0;top:0;width:960px;height:540px">
<div class="p" style="left:24px;top:22px;width:350px;height:150px">
  <div class="h"><img src="data:image/png;base64,{icons['gear']}" style="position:static;width:32px;height:28px">Cercetare<span style="margin-left:auto;color:#d8fff0">42%</span></div>
  <div class="bar"><i></i></div>
  <div class="obj"><b></b>Deblochează culturi noi</div>
  <div class="obj"><b></b>Îmbunătățește motoarele</div>
  <div class="obj"><b></b>Construiește un depozit mai mare</div>
</div>
<div class="p" style="left:692px;top:22px;width:244px;height:326px">
  <div style="display:flex;justify-content:center;margin-bottom:6px"><img src="data:image/png;base64,{icons['ship_blueprint']}" style="position:static;width:140px;height:66px"></div>
  <div class="dim">Următorul upgrade</div>
  <div style="font-size:20px;font-weight:700;margin:2px 0 6px">Motor avansat</div>
  <div class="row"><span><img src="data:image/png;base64,{icons['crystal']}" style="position:static;width:28px;height:24px">Titan</span><b>15<span style="color:#8fb7aa">/20</span></b></div>
  <div class="row"><span><img src="data:image/png;base64,{icons['chip']}" style="position:static;width:26px;height:26px">Circuite</span><b>8<span style="color:#8fb7aa">/10</span></b></div>
  <div class="row"><span><img src="data:image/png;base64,{icons['coin']}" style="position:static;width:28px;height:24px">Credite</span><b>2,5k</b></div>
  <div style="margin-top:16px;border:3px solid #2fe58a;background:#2fe58a;color:#02150e;text-align:center;font-size:18px;font-weight:700;letter-spacing:1.5px;padding:6px 0;border-radius:6px">CERCETEAZĂ</div>
</div>
</div></body></html>'''
open(os.path.join(out, 'research_hud.html'), 'w').write(html)
shot = f"""const {{ chromium }} = require('/opt/node-tools/node_modules/playwright');
(async () => {{
  const b = await chromium.launch({{ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] }});
  const p = await b.newPage({{ viewport: {{ width: 960, height: 540 }} }});
  await p.goto('file://{os.path.join(out, "research_hud.html")}'); await p.waitForTimeout(1500);
  await p.screenshot({{ path: '{os.path.join(out, "research_final.png")}' }});
  await b.close();
}})();
"""
open(os.path.join(out, 'shot.cjs'), 'w').write(shot)
print(subprocess.run(['node', os.path.join(out, 'shot.cjs')], capture_output=True, text=True))
