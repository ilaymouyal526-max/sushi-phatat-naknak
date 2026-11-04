from PIL import Image, ImageDraw, ImageFont
src=Image.open('/root/.claude/uploads/8da19ccc-f5ab-50f2-bd41-7c530964c845/5e5b1b3a-image.jpg').convert('RGB')
W,H=1200,1800  # 6x9 cm @ ~508dpi placeholder ratio 2:3
GOLD=(214,178,110); BG=(22,22,24)
im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)
F=lambda s,b=True: ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf'%('Bold' if b else 'Regular'),s)
# border
d.rounded_rectangle((20,20,W-20,H-20),40,outline=GOLD,width=6)
# logo
logo=src.crop((112,44,320,276)).resize((160,178)); im.paste(logo,(60,55))
d.text((235,85),"HOW TO ENJOY YOUR",font=F(56),fill=GOLD)
d.text((235,150),"SUSHI PUSH POP",font=F(84),fill=GOLD)
# 4 step thumbs in a row
boxes=[(72,318,568,822),(628,318,1124,822),(72,926,568,1430),(628,926,1124,1430)]
caps=["Remove sauce","Open lid","Add sauce","Push up"]
tw=255; y=290
for i,(b,c) in enumerate(zip(boxes,caps)):
    x=40+i*(tw+25)+10
    im.paste(src.crop(b).resize((tw,tw)),(x,y))
    d.rectangle((x,y,x+tw,y+tw),outline=GOLD,width=4)
    d.ellipse((x-12,y-14,x+48,y+46),fill=GOLD); d.text((x+18,y+16),str(i+1),font=F(40),fill=BG,anchor='mm')
    d.text((x+tw/2,y+tw+30),c,font=F(34,False),fill=(235,225,205),anchor='mm')
    if i<3: d.text((x+tw+12,y+tw/2),"›",font=F(60),fill=GOLD,anchor='mm')
# kid hero placeholder
kx0,ky0,kx1,ky1=60,640,W-60,1590
d.rounded_rectangle((kx0,ky0,kx1,ky1),36,outline=GOLD,width=6,fill=(34,32,30))
d.ellipse((kx0-14,ky0-24,kx0+76,ky0+66),fill=GOLD); d.text((kx0+31,ky0+21),"5",font=F(56),fill=BG,anchor='mm')

d.text((W/2,(ky0+ky1)/2-60),"ANIME KID BITING",font=F(70),fill=GOLD,anchor='mm')
d.text((W/2,(ky0+ky1)/2+20),"shocked & sparkly-eyed  —  WOW!",font=F(44,False),fill=(235,225,205),anchor='mm')
d.text((W/2,(ky0+ky1)/2+90),"[ placeholder – generated later ]",font=F(36,False),fill=(150,140,120),anchor='mm')
d.text((W/2,1680),"ENJOY!",font=F(96),fill=GOLD,anchor='mm')
im.save('sticker_mockup_v1.png')
