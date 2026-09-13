from PIL import Image, ImageDraw
import numpy as np
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "grass_tile.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

# Generate a small 64x64 low-poly grass tile
W = H = 64
img = Image.new("RGBA", (W, H), (80, 160, 70, 255))
d = ImageDraw.Draw(img)
# draw a few darker/light blobs
rng = np.random.default_rng(42)
for i in range(8):
    x = int(rng.integers(0, W + 1))
    y = int(rng.integers(0, H + 1))
    r = int(rng.integers(6, 19))
    shade = int(rng.integers(-24, 25))
    col = (
        max(0, min(255, 80 + shade)),
        max(0, min(255, 160 + shade)),
        max(0, min(255, 70 + shade)),
        180,
    )
    d.ellipse((x - r, y - r, x + r, y + r), fill=col)
# subtle noise dots
for i in range(120):
    x = int(rng.integers(0, W))
    y = int(rng.integers(0, H))
    d.point((x, y), fill=(40, 90, 40, 200))

img.save(OUT)
print("Wrote grass tile to", OUT)
