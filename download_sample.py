import numpy as np
from PIL import Image, ImageDraw
import os

os.makedirs("sample_data", exist_ok=True)

# Create a mock X-ray image (grayscale)
width, height = 512, 512
img_array = np.zeros((height, width), dtype=np.uint8)

# Add some gradient background
for y in range(height):
    img_array[y, :] = min(255, int(y * 0.1) + 20)
    
img = Image.fromarray(img_array).convert("L")
draw = ImageDraw.Draw(img)

# Draw rib cage like structures
for i in range(5):
    y = 100 + i * 50
    draw.ellipse((100, y, 250, y+40), fill=150, outline=200)
    draw.ellipse((260, y, 410, y+40), fill=150, outline=200)

# Add some noise
noise = np.random.normal(0, 15, (height, width))
img_array = np.clip(np.array(img) + noise, 0, 255).astype(np.uint8)
img = Image.fromarray(img_array)

filename = "sample_data/sample_xray.png"
img.save(filename)
print(f"Generated synthetic mock X-ray at {filename}")
