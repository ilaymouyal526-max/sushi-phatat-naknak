# v2: boss's exact layout (2x2 equal panels); panel 4 = "Push up & enjoy" with kid placeholder
from PIL import Image, ImageDraw, ImageFont
src=Image.open('/root/.claude/uploads/8da19ccc-f5ab-50f2-bd41-7c530964c845/5e5b1b3a-image.jpg').convert('RGB')
d=ImageDraw.Draw(src); GOLD=(214,178,110)
F=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',s)
x0,y0,x1,y1=632,930,1120,1428   # inner area of panel 4
p=src.crop((x0,y0,x1,y1)).convert('RGBA'); ov=Image.new('RGBA',p.size,(20,20,22,170)); p=Image.alpha_composite(p,ov)
src.paste(p.convert('RGB'),(x0,y0))
cx=(x0+x1)//2
d.text((cx,y0+210),"ANIME KID",font=F(44),fill=GOLD,anchor='mm')
d.text((cx,y0+265),"pushes up & bites — WOW!",font=F(28),fill=(235,225,205),anchor='mm')
d.text((cx,y0+310),"[placeholder]",font=F(22),fill=(160,150,130),anchor='mm')
src.save('sticker_mockup_v2.png')
