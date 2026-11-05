"""Ukiyo-e style Mount Fuji, rendered locally (supersampled). make_fuji(w,h) -> RGBA"""
import math, random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
GOLD=(214,178,110)

def make_fuji(w, h, seed=11):
    S=3; W,H=w*S,h*S; rnd=random.Random(seed)
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    base=int(H*0.84); peak=int(H*0.22)
    cx=W//2; half=int(W*0.48); top=int(W*0.05)
    K=3.0
    def flank(t): return (1-math.exp(-K*t))/(1-math.exp(-K))
    def x_at(y,side):
        f=min(max((y-peak)/(base-peak),0),1)
        t=-math.log(1-f*(1-math.exp(-K)))/K
        return cx+side*(top+(half-top)*t)
    N=120
    L=[(x_at(peak+(base-peak)*i/N,-1), peak+(base-peak)*i/N) for i in range(N+1)]
    R=[(x_at(peak+(base-peak)*i/N, 1), peak+(base-peak)*i/N) for i in range(N+1)]
    rim=[(cx-top,peak),(cx-top*0.55,peak+S*3),(cx-top*0.15,peak+S*1),(cx+top*0.3,peak+S*4),(cx+top*0.7,peak+S*1),(cx+top,peak)]
    poly=[(int(x),int(y)) for x,y in L[::-1]+rim+R]
    mask=Image.new('L',(W,H),0); ImageDraw.Draw(mask).polygon(poly,fill=255)

    # rising sun, behind the right shoulder
    sd=ImageDraw.Draw(img); sr=int(H*0.20); sx,sy=cx+int(W*0.17),int(H*0.24)
    sd.ellipse((sx-sr,sy-sr,sx+sr,sy+sr),fill=(196,48,38,255))
    sd.ellipse((sx-sr,sy-sr,sx+sr,sy+sr),outline=GOLD+(255,),width=S*2)

    # body: prussian-blue gradient, lit left / shaded right with soft diagonal terminator
    body=Image.new('RGBA',(W,H)); bp=body.load()
    for y in range(peak,base+1):
        f=(y-peak)/(base-peak)
        lit=(52+int(40*f),92+int(46*f),150+int(30*f)); shd=(22+int(16*f),40+int(24*f),84+int(26*f))
        term=cx+top*0.2+(y-peak)*0.12
        xl,xr=int(x_at(y,-1))-2,int(x_at(y,1))+2
        for x in range(max(0,xl),min(W,xr+1)):
            m=min(1,max(0,(x-term)/(W*0.025)))
            bp[x,y]=tuple(int(lit[i]*(1-m)+shd[i]*m) for i in range(3))+(255,)
    body.putalpha(mask); img.alpha_composite(body)

    # snow: long irregular fingers reaching down the slopes
    cap=peak+(base-peak)*0.26
    xl,xr=x_at(cap,-1),x_at(cap,1); n=10
    cuts=[0]+[ (i+rnd.uniform(-0.25,0.25))/n for i in range(1,n)]+[1]
    edge=[]; tips=[]
    for a,b in zip(cuts[:-1],cuts[1:]):
        xa=xl+(xr-xl)*a; xb=xl+(xr-xl)*b; xm=(xa+xb)/2
        depth=rnd.uniform(0.08,0.34)*(1-0.5*abs((a+b)/2-0.5)*2)
        yt=cap+(base-peak)*depth; xt=xm+(xm-cx)*depth*0.3
        wv=(xb-xa)*0.22
        y0=cap-(base-peak)*rnd.uniform(0,0.03)
        edge+= [(xa,y0),(xm-wv,(y0+yt)/2),(xt-wv*0.35,yt-(base-peak)*0.012),(xt,yt),(xt+wv*0.35,yt-(base-peak)*0.012),(xm+wv,(y0+yt)/2)]
        tips.append((xt,yt))
    edge.append((xr,cap))
    capL=[(x_at(y,-1),y) for y in [cap-(cap-peak)*k/30 for k in range(31)]]
    capR=[(x_at(y, 1),y) for y in [peak+(cap-peak)*k/30 for k in range(31)]]
    snowP=[(int(x),int(y)) for x,y in rim+capR+edge[::-1]+capL]
    smask=Image.new('L',(W,H),0); ImageDraw.Draw(smask).polygon(snowP,fill=255)
    smask=ImageChops.multiply(smask,mask)
    snow=Image.new('RGBA',(W,H)); sp=snow.load()
    for y in range(peak,int(base)):
        term=cx+top*0.2+(y-peak)*0.12
        for x in range(int(x_at(y,-1))-2,int(x_at(y,1))+3):
            if 0<=x<W:
                m=min(1,max(0,(x-term)/(W*0.02)))
                a=(246,243,234); b=(178,194,216)
                sp[x,y]=tuple(int(a[i]*(1-m)+b[i]*m) for i in range(3))+(255,)
    snow.putalpha(smask); img.alpha_composite(snow)
    # thin ridge lines in the snow
    ld=ImageDraw.Draw(img)
    rl=Image.new('RGBA',(W,H),(0,0,0,0)); rd=ImageDraw.Draw(rl)
    for x,y in tips:
        rd.line((int(x),int(y)-S*6,int(cx+(x-cx)*0.3),int(peak+(y-peak)*0.3)),fill=(196,208,226,200),width=S)
    rl.putalpha(ImageChops.multiply(rl.getchannel('A'),smask)); img.alpha_composite(rl)

    # gold outlines
    ld.line(poly,fill=GOLD+(255,),width=S*2,joint='curve')
    ld.line([(int(x),int(y)) for x,y in edge],fill=GOLD+(170,),width=S)

    # scalloped ukiyo-e clouds at the foot
    def cloud(x0,x1,y,r):
        c=Image.new('RGBA',(W,H),(0,0,0,0)); cd=ImageDraw.Draw(c)
        xs=[]; k=0; x=x0
        while x<=x1:
            xs.append((x,int(r*(1.0 if k%2==0 else 0.72)))); x+=int(r*1.15); k+=1
        for x,rr in xs:
            cd.ellipse((x-rr,y-rr,x+rr,y+rr),fill=(242,234,216,255),outline=GOLD+(255,),width=S*2)
        for x,rr in xs:   # erase inner outline overlap
            cd.ellipse((x-rr+S*3,y-rr+S*3,x+rr-S*3,y+rr-S*3),fill=(242,234,216,255))
        bot=y+int(r*0.45)
        cd.rectangle((xs[0][0]-xs[0][1],y,xs[-1][0]+xs[-1][1],bot),fill=(242,234,216,255))
        cd.rectangle((0,bot,W,H),fill=(0,0,0,0))
        cd.line((xs[0][0]-xs[0][1],bot,xs[-1][0]+xs[-1][1],bot),fill=GOLD+(255,),width=S*2)
        cd.line((xs[0][0]-xs[0][1],y,xs[0][0]-xs[0][1],bot),fill=GOLD+(255,),width=S*2)
        cd.line((xs[-1][0]+xs[-1][1],y,xs[-1][0]+xs[-1][1],bot),fill=GOLD+(255,),width=S*2)
        img.alpha_composite(c)
    cloud(int(W*0.06),int(W*0.36),int(H*0.86),int(H*0.06))
    cloud(int(W*0.62),int(W*0.94),int(H*0.90),int(H*0.055))
    return img.resize((w,h),Image.LANCZOS)

if __name__=='__main__':
    bg=Image.new('RGBA',(1600,900),(26,26,28,255)); bg.alpha_composite(make_fuji(1600,900)); bg.save('fuji_test.png')
