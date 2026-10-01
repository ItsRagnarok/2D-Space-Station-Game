"""Export every research-module sprite as its own PNG (+ animation frames) and render a preview GIF."""
import os, subprocess, shutil
from core import *
import objects as o
import scene

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out', 'research')
os.makedirs(os.path.join(OUT, 'sprites'), exist_ok=True)
S = os.path.join(OUT, 'sprites')
count = 0
def save(name, im):
    global count
    im.save(os.path.join(S, name + '.png')); count += 1

for i in range(3): save(f'generator_{i}', o.generator(i / 3))
for i in range(12): save(f'globe_{i:02d}', o.globe(i * math.pi * 2 / 12))
for i in range(3): save(f'pedestal_{i}', o.pedestal(i / 3))
for sch in ('white', 'yellow', 'green'):
    for pose in ('idle', 'work', 'point'):
        for fr in (0, 1):
            if pose == 'point' and fr: continue
            save(f'astronaut_{sch}_{pose}_{fr}', o.astronaut(sch, pose, fr))
for i in range(4): save(f'console_{i}', o.console(i))
for i in range(2):
    save(f'bench_{i}', o.bench(i)); save(f'rack_{i}', o.rack(i)); save(f'locker_{i}', o.locker(i)); save(f'plant_jar_{i}', o.plant_jar(i)); save(f'drone_{i}', o.drone(i))
save('crate_steel', o.crate('steel')); save('crate_orange', o.crate('o')); save('pipes_v', o.pipes_v(104))
for t in range(3): save(f'floor_plain_{t}', __import__('scene_base').floor_tile(t * 131))
save('floor_vent', __import__('scene_base').floor_tile(5, 'vent')); save('floor_grate', __import__('scene_base').floor_tile(9, 'grate'))
print('sprites exported:', count)

# preview GIF: 6.3 s @10 fps, scene only, x2 nearest
frames = os.path.join(OUT, 'frames'); shutil.rmtree(frames, ignore_errors=True); os.makedirs(frames)
N = 63
for i in range(N):
    upscale(scene.render(i / 10.0), 2).convert('RGB').save(os.path.join(frames, f'f{i:03d}.png'))
pal = os.path.join(OUT, 'pal.png')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', os.path.join(frames, 'f%03d.png'), '-vf', 'palettegen=max_colors=96:stats_mode=diff', pal], check=True)
gif = os.path.join(OUT, 'research_preview.gif')
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', os.path.join(frames, 'f%03d.png'), '-i', pal, '-lavfi', 'paletteuse=dither=none', '-loop', '0', gif], check=True)
print('gif', os.path.getsize(gif) // 1024, 'KB')
