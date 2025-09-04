import replicate
import os
import requests
import datetime
from config import STYLE_MAP
from dotenv import load_dotenv

load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

def generate_sketch(prompt, style):
    
    style_modifier = STYLE_MAP.get(style, "")
    full_prompt = f"{style_modifier}, {prompt}"

    output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": full_prompt})
    image_url = output[0]

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sketch_{style}_{timestamp}.png"

    response = requests.get(image_url)
    with open(filename, "wb") as f:
        f.write(response.content)
