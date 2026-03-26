from PIL import Image
import sys
from collections import Counter

path = sys.argv[1] if len(sys.argv)>1 else 'debug_infield_render.png'
try:
    img = Image.open(path).convert('RGBA')
except Exception as e:
    print('ERROR opening image:', e)
    sys.exit(2)

w,h = img.size
print(f'Image: {path} size={w}x{h}')
px = img.load()
if px is None:
    print('ERROR loading pixel buffer')
    sys.exit(3)
# sample center pixel and area
cx,cy = w//2, h//2
print('Center pixel RGBA:', px[cx,cy])
# compute percentage of pixels where green is dominant and bright
count=0
total=0
for y in range(h):
    for x in range(w):
        r,g,b,a = px[x,y]
        if a<10:
            continue
        total+=1
        if g>r+30 and g>b+30 and g>100:
            count+=1

if total==0:
    print('No opaque pixels found')
else:
    pct = (count/total)*100
    print(f'Pixels green-dominant (>100 and >others+30): {count}/{total} ({pct:.1f}%)')

# report top 5 colors
cnt = Counter()
for y in range(0,h,4):
    for x in range(0,w,4):
        cnt[px[x,y]]+=1

print('Top colors (sampled):')
for col,n in cnt.most_common(8):
    print(col, n)

# locate pure bright-green pixels (exact 0,255,0)
green_coords = []
minx=miny=99999
maxx=maxy=0
for y in range(h):
    for x in range(w):
        r,g,b,a = px[x,y]
        if a>10 and r==0 and g==255 and b==0:
            green_coords.append((x,y))
            if x<minx: minx=x
            if y<miny: miny=y
            if x>maxx: maxx=x
            if y>maxy: maxy=y

if green_coords:
    print('Pure-green pixel count (exact 0,255,0):', len(green_coords))
    print('Pure-green bbox:', (minx,miny,maxx,maxy))
    print('Sample coords:', green_coords[::max(1,len(green_coords)//10)][:10])
else:
    print('No exact pure-green pixels found')
