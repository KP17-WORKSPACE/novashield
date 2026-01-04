from PIL import Image
import os
src = os.path.join(os.path.dirname(__file__), '..', 'Nova_logo.jpeg')
dst = os.path.join(os.path.dirname(__file__), '..', 'Nova_logo.png')
print('SRC', src)
if not os.path.exists(src):
    print('SOURCE_MISSING')
    raise SystemExit(1)
im = Image.open(src).convert('RGBA')
datas = im.getdata()
newData = []
for item in datas:
    r, g, b, a = item
    if r > 245 and g > 245 and b > 245:
        newData.append((255,255,255,0))
    else:
        newData.append((r, g, b, a))
im.putdata(newData)
im.save(dst, 'PNG')
print('SAVED', dst)