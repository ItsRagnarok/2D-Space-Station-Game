"""img2img: enrich the forge hangar scene with a pixel-art diffusion model (CPU)."""
import torch, sys, os
from PIL import Image
from diffusers import StableDiffusionImg2ImgPipeline, DPMSolverMultistepScheduler
HERE = os.path.dirname(__file__); OUT = os.path.join(HERE, '..', 'out', 'hangar')
torch.set_num_threads(4)
pipe = StableDiffusionImg2ImgPipeline.from_pretrained(os.path.join(HERE, '..', 'models', 'pixelsd'), torch_dtype=torch.float32, safety_checker=None)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
init = Image.open(os.path.join(OUT, 'hangar_noship.png')).convert('RGB').resize((512, 384), Image.NEAREST)
strength = float(sys.argv[1]) if len(sys.argv) > 1 else 0.55
prompt = "pixelartstyle, empty sci-fi hangar landing pad, top-down 3/4 view, orange hazard stripes, glowing orange lights, dark industrial machinery walls, crates, pipes, detailed pixel art"
neg = "spaceship, ship, vehicle, blurry, text, watermark, ui, people faces, photo, smooth"
g = torch.Generator().manual_seed(5)
img = pipe(prompt, negative_prompt=neg, image=init, strength=strength, guidance_scale=7.5, num_inference_steps=24, generator=g).images[0]
img.save(os.path.join(OUT, f'ai_s{int(strength*100)}.png')); print('done')
