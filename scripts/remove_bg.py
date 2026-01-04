from PIL import Image
import os
from collections import Counter

root = os.path.dirname(__file__)
src = os.path.join(root, '..', 'NOVA_logo.png')
dst = os.path.join(root, '..', 'NOVA_logo_transparent.png')

if not os.path.exists(src):
    print('SOURCE_MISSING', src)
    raise SystemExit(1)

im = Image.open(src).convert('RGBA')
px = im.load()
W, H = im.size

# Sample small regions at corners and edges to find dominant background color
samples = []
for x in range(0, min(6, W)):
    for y in range(0, min(6, H)):
        samples.append(px[x, y][:3])
for x in range(max(0, W-6), W):
    for y in range(0, min(6, H)):
        samples.append(px[x, y][:3])
for x in range(0, min(6, W)):
    for y in range(max(0, H-6), H):
        samples.append(px[x, y][:3])
for x in range(max(0, W-6), W):
    for y in range(max(0, H-6), H):
        samples.append(px[x, y][:3])

# Determine the most common color among samples
most_common = Counter(samples).most_common(1)
if not most_common:
    print('NO_SAMPLES')
    raise SystemExit(1)
bg_color = most_common[0][0]
print('DETECTED_BG', bg_color)

# Threshold for near-match
thresh = 30

new = Image.new('RGBA', im.size)
for y in range(H):
    for x in range(W):
        r,g,b,a = px[x, y]
        dr = abs(r - bg_color[0])
        dg = abs(g - bg_color[1])
        db = abs(b - bg_color[2])
        if dr <= thresh and dg <= thresh and db <= thresh:
            new.putpixel((x,y), (r,g,b,0))
        else:
            new.putpixel((x,y), (r,g,b,a))

new.save(dst)
print('SAVED', dst)
