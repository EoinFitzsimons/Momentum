from PIL import Image, ImageDraw
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets', 'props')
os.makedirs(OUT_DIR, exist_ok=True)

# simple top-down tree
def make_tree(path, color=(34,139,34,255)):
    img = Image.new('RGBA', (128,128), (0,0,0,0))
    d = ImageDraw.Draw(img)
    # canopy
    d.ellipse((16,8,112,88), fill=color)
    d.ellipse((24,32,104,112), fill=(int(color[0]*0.9),int(color[1]*0.9),int(color[2]*0.9),230))
    # trunk
    d.rectangle((56,88,72,120), fill=(100,60,30,255))
    img.save(path)

# bush
def make_bush(path):
    img = Image.new('RGBA', (96,96), (0,0,0,0))
    d = ImageDraw.Draw(img)
    d.ellipse((8,24,88,72), fill=(44,112,40,230))
    d.ellipse((24,8,72,64), fill=(30,90,30,200))
    img.save(path)

# rock
def make_rock(path):
    img = Image.new('RGBA', (80,60), (0,0,0,0))
    d = ImageDraw.Draw(img)
    d.polygon([(10,40),(30,10),(60,8),(70,28),(50,48),(20,48)], fill=(120,120,120,255))
    d.polygon([(18,36),(36,18),(56,16),(64,30),(48,42),(26,42)], fill=(100,100,100,255))
    img.save(path)

files = [
    ('tree_oak.png', (34,139,34,255)),
    ('tree_pine.png', (20,120,20,255)),
    ('tree_birch.png', (180,220,120,255)),
    ('bush_1.png', None),
    ('rock_1.png', None),
]

for name, col in files:
    path = os.path.join(OUT_DIR, name)
    if col:
        make_tree(path, color=col)
    elif 'bush' in name:
        make_bush(path)
    else:
        make_rock(path)

print('Generated placeholder sprites in', OUT_DIR)
