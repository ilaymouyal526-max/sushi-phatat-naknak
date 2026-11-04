# Boss layout with generated kid in panel 4 (inner area 632..1120 x 930..1428)
from PIL import Image
import sys
src='/root/.claude/uploads/8da19ccc-f5ab-50f2-bd41-7c530964c845/5e5b1b3a-image.jpg'
for k in 'ABC':
    im=Image.open(src).convert('RGB')
    kid=Image.open(f'kid/kid_{k}.png').convert('RGB').resize((488,498))
    im.paste(kid,(632,930))
    im.save(f'sticker_v3_{k}.png')
row=[Image.open(f'sticker_v3_{k}.png').resize((597,800)) for k in 'ABC']
g=Image.new('RGB',(597*3+40,800),(20,20,22))
for i,r in enumerate(row): g.paste(r,(i*(597+20),0))
g.save('sticker_v3_compare.jpg',quality=88)
