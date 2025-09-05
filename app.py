from flask import Flask, render_template, request, send_from_directory
from config import STYLE_MAP
import replicate
import requests
import os
import datetime

app = Flask(__name__)

REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None

    if request.method == "POST":
        prompt = request.form["prompt"]
        style = request.form["style"]
        style_modifier = STYLE_MAP.get(style, "")
        full_prompt = f"{style_modifier}, {prompt}"

        print("Sending to Replicate:", {"prompt": full_prompt})

        output = replicate.run(
            "prunaai/flux.1-dev:b0306d92aa025bb747dc74162f3c27d6ed83798e08e5f8977adf3d859d0536a3",
            input={
                "prompt": full_prompt,
                # "width": 1024,
                # "height": 1024,
                # "inference_steps": 2,
                # "intermediate_timesteps": 1.3,
                # "guidance_scale": 4.5,
                # "seed": -1,
                # "output_format": "jpg",
                # "output_quality": 80
            }
        )

        print("Replicate output:", output)

        if output and isinstance(output, str):
            image_url = output
        else:
            print("No image URL returned")
            return "Image generation failed", 500

        # Save image locally
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sketch_{style}_{timestamp}.jpg"
        filepath = os.path.join("static", "sketches", filename)
        os.makedirs("static/sketches", exist_ok=True)
        response = requests.get(image_url)
        with open(filepath, "wb") as f:
            f.write(response.content)

        return render_template("index.html", image_path=filepath)

    # GET request fallback
    return render_template("index.html", image_path=None)

from flask import redirect, url_for

@app.route("/clear", methods=["POST"])
def clear():
    sketches_dir = os.path.join("static", "sketches")
    try:
        files = sorted(
            [f for f in os.listdir(sketches_dir) if f.endswith(".png")],
            key=lambda x: os.path.getmtime(os.path.join(sketches_dir, x)),
            reverse=True
        )
        if files:
            os.remove(os.path.join(sketches_dir, files[0]))
    except Exception as e:
        print("Error clearing sketch:", e)

    return redirect(url_for("index"))

# Optional: Enable debug mode explicitly if needed
app.config["DEBUG"] = False  # or True for testing



