from flask import Flask, render_template, request, send_from_directory
from config import STYLE_MAP
from dotenv import load_dotenv
import replicate
import requests
import os
import datetime

app = Flask(__name__)

load_dotenv()
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    if request.method == "POST":
        prompt = request.form["prompt"]
        style = request.form["style"]
        style_modifier = STYLE_MAP.get(style, "")
        full_prompt = f"{style_modifier}, {prompt}"

        output = replicate.run("black-forest-labs/flux-schnell", input={"prompt": full_prompt})
        image_url = output[0]

        # Save image locally
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sketch_{style}_{timestamp}.png"
        filepath = os.path.join("static", "sketches", filename)
        response = requests.get(image_url)
        with open(filepath, "wb") as f:
            f.write(response.content)

        return render_template("index.html", image_path=filepath)

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



