"""Compose push-pop how-to sticker: boss layout, replace panel interiors, keep number badges on top.
usage: python3 compose.py out.png [p1.png] [p2.png] [p3.png] [p4.png]   ('-' = keep original panel)"""
import sys
from PIL import Image, ImageDraw
SRC='/root/.claude/uploads/8da19ccc-f5ab-50f2-bd41-7c530964c845/5e5b1b3a-image.jpg'
# inner areas inside the 3px gold frames (measured)
INNER=[(73,319,566,821),(628,319,1120,821),(73,928,566,1429),(628,928,1120,1429)]
# number badges (center, radius incl. soft edge), measured
BADGES=[(90,334),(645,334),(90,943),(645,943)]
R=50
orig=Image.open(SRC).convert('RGB'); out=orig.copy()
for i,p in enumerate(sys.argv[2:6]):
    if p=='-': continue
    x0,y0,x1,y1=INNER[i]
    out.paste(Image.open(p).convert('RGB').resize((x1-x0,y1-y0),Image.LANCZOS),(x0,y0))
mask=Image.new('L',orig.size,0); d=ImageDraw.Draw(mask)
for cx,cy in BADGES: d.ellipse((cx-R,cy-R,cx+R,cy+R),fill=255)
out.paste(orig,(0,0),mask)   # badges always on top
out.save(sys.argv[1])
