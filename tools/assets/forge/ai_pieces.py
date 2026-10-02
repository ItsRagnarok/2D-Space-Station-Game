"""SDXL + pixel-art-xl: small standalone pieces (txt2img, CPU). Output raw 512px; later snapped to game pixel grid."""
import torch, os, time
from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler
HERE = os.path.dirname(__file__); M = os.path.join(HERE, '..', 'models'); OUT = os.path.join(HERE, '..', 'out', 'hangar', 'pieces'); os.makedirs(OUT, exist_ok=True)
torch.set_num_threads(4)
pipe = StableDiffusionXLPipeline.from_pretrained(os.path.join(M, 'sdxl'), torch_dtype=torch.bfloat16, variant='fp16', use_safetensors=True)
pipe.load_lora_weights(os.path.join(M, 'pxl'), weight_name='pixel-art-xl.safetensors'); pipe.fuse_lora(lora_scale=1.0)
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
BASE = "pixel art, 3/4 top-down view, sci-fi industrial, dark steel with glowing orange lights and yellow hazard accents, highly detailed, plain solid dark background"
PIECES = {
 'wall_machinery': "tall control cabinet machinery wall unit with panels, vents, small screens and orange lit indicator lights",
 'floor_pad': "square steel floor panel tile with rivets, orange hazard stripe corner brackets, seamless flat top-down texture",
 'crates': "stack of metal cargo crates, orange and steel, with yellow warning stripes, single object",
}
NEG = "text, watermark, blurry, smooth, photo, 3d render, lowres, people, multiple objects"
for name, p in PIECES.items():
    t = time.time()
    img = pipe(f"{BASE}, {p}", negative_prompt=NEG, width=512, height=512, guidance_scale=7, num_inference_steps=16, generator=torch.Generator().manual_seed(21)).images[0]
    img.save(os.path.join(OUT, f'{name}.png')); print('done', name, round(time.time() - t), flush=True)
