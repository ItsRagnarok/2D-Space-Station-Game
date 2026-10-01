"""SDXL + pixel-art-xl LoRA, img2img from the forge scene (CPU, slow)."""
import torch, sys, os, time
from PIL import Image
from diffusers import StableDiffusionXLImg2ImgPipeline, EulerAncestralDiscreteScheduler
HERE = os.path.dirname(__file__); M = os.path.join(HERE, '..', 'models'); OUT = os.path.join(HERE, '..', 'out', 'hangar')
torch.set_num_threads(4)
pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(os.path.join(M, 'sdxl'), torch_dtype=torch.bfloat16, variant='fp16', use_safetensors=True)
pipe.load_lora_weights(os.path.join(M, 'pxl'), weight_name='pixel-art-xl.safetensors'); pipe.fuse_lora(lora_scale=1.0)
pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
strength = float(sys.argv[1]); steps = int(sys.argv[2])
init = Image.open(os.path.join(OUT, 'hangar_noship.png')).convert('RGB').resize((768, 576), Image.NEAREST)
prompt = ("pixel art, sci-fi spaceship hangar docking bay seen from above at a 3/4 angle, empty landing pad with orange and black hazard stripes, "
          "dense industrial machinery walls, glowing orange lights and conduits, dark steel floor panels, crates, pipes, cyan accents, highly detailed")
neg = "spaceship, vehicle, text, watermark, blurry, smooth, photo, 3d render, lowres"
t = time.time()
img = pipe(prompt, negative_prompt=neg, image=init, strength=strength, guidance_scale=7, num_inference_steps=steps, generator=torch.Generator().manual_seed(3)).images[0]
img.save(os.path.join(OUT, f'xl_s{int(strength*100)}.png')); print('done', time.time() - t)
