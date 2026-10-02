"""Series of AI sprite sheets for the hangar kit (resumable). Each sheet: several separate objects on flat background."""
import torch, os, time
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
HERE = os.path.dirname(__file__); M = os.path.join(HERE, '..', 'models'); OUT = os.path.join(HERE, '..', 'out', 'hangar', 'series'); os.makedirs(OUT, exist_ok=True)
torch.set_num_threads(4)
pipe = StableDiffusionXLPipeline.from_pretrained(os.path.join(M, 'sdxl'), torch_dtype=torch.bfloat16, variant='fp16', use_safetensors=True)
pipe.load_lora_weights(os.path.join(M, 'pxl'), weight_name='pixel-art-xl.safetensors'); pipe.fuse_lora(lora_scale=1.0)
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
BASE = "pixel art sprite sheet, four separate objects with wide gaps between them, 3/4 top-down view, sci-fi industrial hangar, dark steel with glowing orange lights and yellow hazard accents, highly detailed, plain flat grey background"
SHEETS = [
 ('cabinets_a', "tall machinery cabinets with panels, vents, small screens and orange indicator lights", 31),
 ('cabinets_b', "server racks and generator units with cyan and orange lit indicators", 32),
 ('consoles', "control consoles and computer terminals with glowing screens", 33),
 ('tanks', "fuel tanks, gas cylinders and barrels with hazard stripes", 34),
 ('pipes', "short pipe junctions, valves and orange conduit segments with brackets", 35),
 ('lockers', "storage lockers, tool benches and small workbenches", 36),
 ('crates_b', "cargo containers and stacked crates, orange and steel, separate with gaps", 37),
 ('lights', "wall lamps, warning beacons, floor light fixtures glowing orange", 38),
]
NEG = "text, watermark, blurry, smooth, photo, 3d render, lowres, people, overlapping, touching"
for name, p, seed in SHEETS:
    f = os.path.join(OUT, name + '.png')
    if os.path.exists(f): continue
    t = time.time()
    img = pipe(f"{BASE}, {p}", negative_prompt=NEG, width=512, height=512, guidance_scale=7, num_inference_steps=16, generator=torch.Generator().manual_seed(seed)).images[0]
    img.save(f); print('done', name, round(time.time() - t), flush=True)
