"""Wrap-around label v1 (Option 2: Yoko Ono front + how-to back). Local layout, no credits.
Placeholder size: tube Ø60mm x label height 120mm -> 200mm wide (188.5 circumference + overlap)."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
PX=12                                   # px per mm (~305 dpi)
W,H=200*PX,120*PX
mm=lambda v:int(v*PX)
SRC=Image.open('boss_base.jpg').convert('RGB')
BG=(26,26,28); GOLD=(214,178,110); GOLD_D=(120,98,60); CREAM=(235,225,205); RED=(178,34,34)
F=lambda s,b=True:ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf'%('Bold' if b else 'Regular'),s)
JP=lambda s:ImageFont.truetype('/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf',s)

im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im)

def seigaiha(box,r,col,width=2):
    x0,y0,x1,y1=box; layer=Image.new('RGBA',(x1-x0,y1-y0),(0,0,0,0)); ld=ImageDraw.Draw(layer)
    row=0; y=0
    while y<y1-y0+r:
        off=0 if row%2==0 else r
        x=-r+off
        while x<x1-x0+r:
            for k in (1.0,0.72,0.44):
                rr=int(r*k); ld.arc((x-rr,y-rr,x+rr,y+rr),180,360,fill=col,width=width)
            x+=2*r
        y+=r//2; row+=1
    im.paste(layer,(x0,y0),layer)

def paste_gold(img,pos,lo=60,hi=120):
    L=img.convert('L').point(lambda v:0 if v<lo else 255 if v>hi else int((v-lo)*255/(hi-lo)))
    im.paste(img,pos,L)

def paste_feather(img,pos,feather=10):
    m=Image.new('L',img.size,0); ImageDraw.Draw(m).rectangle((feather,feather,img.size[0]-feather,img.size[1]-feather),fill=255)
    im.paste(img,pos,m.filter(ImageFilter.GaussianBlur(feather/2)))

# ---- background pattern zones: seams + transition
seigaiha((0,0,mm(8),H),mm(4),GOLD_D+(140,))
seigaiha((mm(192),0,W,H),mm(4),GOLD_D+(140,))
seigaiha((mm(80),0,mm(98),H),mm(4),GOLD_D+(170,))
# top & bottom gold rules
for y in (mm(3),H-mm(3)): d.line((0,y,W,y),fill=GOLD,width=4)

# ---- FRONT (x 8..80): Yoko Ono hero
fx0,fx1=mm(8),mm(80); fcx=(fx0+fx1)//2
# sakura branch (from boss artwork) top-right of front
br=SRC.crop((1045,0,1194,300)).resize((mm(24),mm(48)))
paste_gold(br,(fx1-mm(25),mm(5)))
logo=SRC.crop((76,40,312,280)); lw=mm(44); logo=logo.resize((lw,int(lw*logo.size[1]/logo.size[0])),Image.LANCZOS)
paste_gold(logo,(fcx-lw//2,mm(14)))
ly=mm(14)+logo.size[1]
# "SUSHI / PUSH POP" in the same gold brush lettering as the how-to title (cropped from the boss artwork)
k=mm(56)/(1042-619)
w1=SRC.crop((346,136,592,232)); w1=w1.resize((int(w1.width*k),int(w1.height*k)),Image.LANCZOS)
w2=SRC.crop((619,136,1042,232)); w2=w2.resize((int(w2.width*k),int(w2.height*k)),Image.LANCZOS)
paste_gold(w1,(fcx-w1.width//2,ly+mm(4)),95,150)
paste_gold(w2,(fcx-w2.width//2,ly+mm(4)+w1.height+mm(1)),95,150)
# vertical katakana ヨーコ・オノ on the left edge of front
kx=fx0+mm(7)
for i,ch in enumerate("ヨーコ・オノ"):
    t=Image.new('RGBA',(mm(7),mm(7)),(0,0,0,0)); ImageDraw.Draw(t).text((mm(3.5),mm(3.5)),ch,font=JP(mm(5.5)),fill=GOLD,anchor='mm')
    if ch=='ー': t=t.rotate(90)
    im.paste(t,(kx-mm(3.5),mm(22)+i*mm(7)),t)
# hanko stamp
hx,hy,hr=fx1-mm(12),H-mm(16),mm(6)
d.rounded_rectangle((hx-hr,hy-hr,hx+hr,hy+hr),mm(1.5),fill=RED)
d.text((hx,hy),"YO",font=F(mm(5.5)),fill=(250,235,220),anchor='mm')
# PUSH arrow at bottom of front
d.text((fcx-mm(6),H-mm(10)),"PUSH ↑",font=F(mm(4.2)),fill=CREAM,anchor='mm')

# ---- transition band (80..98): soy-sauce clip zone note
d.text((mm(89),H//2),"",font=F(20),fill=GOLD)

# ---- BACK (x 100..192): how-to
bx0,bx1=mm(100),mm(192); bcx=(bx0+bx1)//2
title=SRC.crop((345,60,1045,235)); tw=mm(70); title=title.resize((tw,int(tw*title.size[1]/title.size[0])),Image.LANCZOS)
paste_gold(title,(bcx-title.size[0]//2,mm(6)))
ty=mm(6)+title.size[1]
fs=mm(32); gap=mm(5); gx0=bcx-fs-gap//2
caps=[(120,838,520,882),(750,838,1000,882),(180,1448,460,1492),(720,1448,1030,1492)]
badges=[(90,334),(645,334),(90,943),(645,943)]
for i in range(4):
    cx=gx0+(i%2)*(fs+gap); cy=ty+mm(4)+(i//2)*(fs+mm(10))
    fr=Image.open(f'frames/step{i+1}.png').convert('RGB').resize((fs,fs),Image.LANCZOS)
    im.paste(fr,(cx,cy)); d.rectangle((cx,cy,cx+fs,cy+fs),outline=GOLD,width=4)
    # badge from boss artwork, circular
    bxc,byc=badges[i]; b=SRC.crop((bxc-47,byc-47,bxc+47,byc+47)).resize((mm(9),mm(9)),Image.LANCZOS)
    m=Image.new('L',b.size,0); ImageDraw.Draw(m).ellipse((1,1,b.size[0]-2,b.size[1]-2),fill=255)
    im.paste(b,(cx-mm(3),cy-mm(3)),m)
    c=SRC.crop(caps[i]); ch=mm(4.2); c=c.resize((int(c.size[0]*ch/c.size[1]),ch),Image.LANCZOS)
    paste_gold(c,(cx+fs//2-c.size[0]//2,cy+fs+mm(1.5)),70,140)

im.save('wrap_v1_flat.png')

# ---- guides overlay (for review only)
g=im.copy(); gd=ImageDraw.Draw(g)
for x,lab in [(mm(8),'seam/overlap'),(mm(80),'front | side'),(mm(98),'side | back'),(mm(192),'seam/overlap')]:
    for y in range(0,H,30): gd.line((x,y,x,y+15),fill=(0,200,255),width=3)
    gd.text((x+8,H-mm(8)),lab,font=F(28),fill=(0,200,255))
gd.text((mm(81),mm(50)),"soy\nclip\nzone",font=F(30),fill=(0,200,255))
g.save('wrap_v1_guides.png')

# ---- cylinder mockups (front & back views)
R=60/2*PX; circ=2*math.pi*R
def cyl(center_mm,out):
    ow=int(2*R)+40; o=Image.new('RGB',(ow+200,H+200),(232,228,220))
    src=im.load(); px=o.load()
    for X in range(int(-R)+1,int(R)):
        th=math.asin(X/R); u=int((center_mm*PX+th*R)%W)
        shade=0.55+0.45*math.cos(th)
        for y in range(H):
            r,gg,b=src[u,y]; px[100+20+int(X+R),100+y]=(int(r*shade),int(gg*shade),int(b*shade))
    od=ImageDraw.Draw(o)
    od.ellipse((120,100-mm(5),120+int(2*R),100+mm(5)),fill=(20,20,22))
    o.save(out)
cyl(44,'wrap_v1_mock_front.png'); cyl(146,'wrap_v1_mock_back.png')
a=Image.open('wrap_v1_mock_front.png'); b=Image.open('wrap_v1_mock_back.png')
s=Image.new('RGB',(a.width*2+40,a.height),(232,228,220)); s.paste(a,(0,0)); s.paste(b,(a.width+40,0)); s.save('wrap_v1_mock.png')
