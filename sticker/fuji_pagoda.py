"""Fuji + Chureito-style pagoda scene, drawn from scratch in the ad's black/gold palette
(composition inspired by the user's reference photo; nothing traced or copied from it)."""
import math, random
from PIL import Image, ImageDraw, ImageChops, ImageFilter
GOLD=(214,178,110); GOLD_HI=(246,222,160); GOLD_LO=(120,90,46); CREAM=(246,238,220); SNOW_SH=(196,190,176)
RED=(200,52,36); RED_D=(140,30,24); ROOF=(44,46,44)

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def fuji(img,cx,base,half,peak_h,S,rnd):
    W,H=img.size; peak=base-peak_h; top=int(half*0.10); K=2.6
    def x_at(y,side):
        f=min(max((y-peak)/(base-peak),0),1); t=-math.log(1-f*(1-math.exp(-K)))/K
        return cx+side*(top+(half-top)*t)
    ys=[peak+(base-peak)*i/100 for i in range(101)]
    # rounded summit like the photo
    cap=[(cx-top,peak),(cx-top*0.4,peak-S*2),(cx+top*0.3,peak-S*1),(cx+top,peak)]
    poly=[(x_at(y,-1),y) for y in ys[::-1]]+cap+[(x_at(y,1),y) for y in ys]
    poly=[(int(x),int(y)) for x,y in poly]
    m=Image.new('L',(W,H),0); ImageDraw.Draw(m).polygon(poly,fill=255)
    body=Image.new('RGBA',(W,H)); bp=body.load()
    for y in range(int(peak-top),base+1):
        f=max(0,(y-peak)/(base-peak)); term=cx+(y-peak)*0.18
        for x in range(max(0,int(x_at(y,-1))-2),min(W,int(x_at(y,1))+3)):
            lit=lerp(GOLD_HI,GOLD_LO,f); sh=lerp((170,132,72),(70,52,28),f)
            k=min(1,max(0,(x-term)/(W*0.02))); bp[x,y]=lerp(lit,sh,k)+(255,)
    body.putalpha(m); img.alpha_composite(body)
    # big snow cap with ragged ridges (like the photo: snow covers the upper ~45%)
    capy=peak+(base-peak)*0.42; xl,xr=x_at(capy,-1),x_at(capy,1); n=16
    edge=[]
    for i in range(n+1):
        x=xl+(xr-xl)*i/n; d=rnd.uniform(0.0,0.16) if i%2 else rnd.uniform(-0.06,0.0)
        edge.append((x,capy+(base-peak)*d))
    sp=[(x_at(y,-1),y) for y in [capy-(capy-peak)*k/30 for k in range(31)]]+cap+[(x_at(y,1),y) for y in [peak+(capy-peak)*k/30 for k in range(31)]]+edge[::-1]
    sm=Image.new('L',(W,H),0); ImageDraw.Draw(sm).polygon([(int(x),int(y)) for x,y in sp],fill=255); sm=ImageChops.multiply(sm,m)
    snow=Image.new('RGBA',(W,H)); spx=snow.load()
    for y in range(int(peak-top),int(capy+(base-peak)*0.2)):
        term=cx+(y-peak)*0.18
        for x in range(max(0,int(x_at(y,-1))-2),min(W,int(x_at(y,1))+3)):
            k=min(1,max(0,(x-term)/(W*0.015))); spx[x,y]=lerp(CREAM,SNOW_SH,k)+(255,)
    snow.putalpha(sm); img.alpha_composite(snow)
    # ridge lines
    rl=Image.new('RGBA',(W,H),(0,0,0,0)); rd=ImageDraw.Draw(rl)
    for i in range(1,n,2):
        x,y=edge[i]; rd.line((int(x),int(y),int(cx+(x-cx)*0.2),int(peak+(y-peak)*0.2)),fill=GOLD_LO+(150,),width=S)
    rl.putalpha(ImageChops.multiply(rl.getchannel('A'),sm)); img.alpha_composite(rl)
    ImageDraw.Draw(img).line(poly,fill=GOLD+(255,),width=S*2,joint='curve')

def roof(d,cx,y,half,h,S,snow=True):
    """curved pagoda roof with upturned eaves; y = eave line"""
    tip=int(h*0.9); pts=[]
    for i in range(41):
        t=i/40; x=cx-half+2*half*t
        sag=math.sin(math.pi*t)*h*0.10            # eave sags slightly in the middle
        up=(abs(t-0.5)*2)**4*tip                  # corners flick up
        pts.append((x,y+sag-up))
    top_l=(cx-half*0.30,y-h*1.6); top_r=(cx+half*0.30,y-h*1.6)
    poly=[top_l]+pts+[top_r]
    d.polygon([(int(x),int(yy)) for x,yy in poly],fill=ROOF)
    # red underside band
    under=[(x,yy) for x,yy in pts]+[(x,yy+h*0.22) for x,yy in pts[::-1]]
    d.polygon([(int(x),int(yy)) for x,yy in under],fill=RED_D)
    if snow:
        mid=[(top_l[0]+(x-top_l[0])*0.0+ (x-cx)*0.0, yy) for x,yy in []]
        sn=[(cx+(x-cx)*0.55, top_l[1]+(yy-top_l[1])*0.45) for x,yy in pts]
        d.polygon([(int(x),int(yy)) for x,yy in [top_l]+sn+[top_r]],fill=CREAM)
    d.line([(int(x),int(yy)) for x,yy in pts],fill=GOLD,width=S*2)
    d.line([(int(top_l[0]),int(top_l[1])),(int(top_r[0]),int(top_r[1]))],fill=GOLD,width=S)
    # tiny bells at the corners
    for x,yy in (pts[0],pts[-1]):
        d.line((int(x),int(yy),int(x),int(yy+h*0.35)),fill=GOLD,width=S); d.ellipse((int(x-S*3),int(yy+h*0.35),int(x+S*3),int(yy+h*0.35+S*6)),fill=GOLD)

def pagoda(img,cx,base,width,height,S):
    d=ImageDraw.Draw(img)
    tiers=5; th=height*0.78/tiers
    y=base
    for i in range(tiers):
        bw=width*(0.40-0.035*i); rh=th*0.42; wall_h=th-rh*0.55
        # walls: cream with red pillars + railing
        d.rectangle((int(cx-bw/2),int(y-wall_h),int(cx+bw/2),int(y)),fill=CREAM)
        for k in range(5):
            px=cx-bw/2+bw*k/4; d.rectangle((int(px-S*2),int(y-wall_h),int(px+S*2),int(y)),fill=RED)
        d.rectangle((int(cx-bw*0.18),int(y-wall_h*0.75),int(cx+bw*0.18),int(y)),fill=RED)   # door
        d.rectangle((int(cx-bw/2-S*4),int(y-S*5),int(cx+bw/2+S*4),int(y)),fill=RED)          # railing
        for k in range(9):
            px=cx-bw/2+bw*k/8; d.line((int(px),int(y-S*10),int(px),int(y-S*5)),fill=RED,width=S)
        d.line((int(cx-bw/2-S*4),int(y-S*10),int(cx+bw/2+S*4),int(y-S*10)),fill=RED,width=S*2)
        y-=wall_h
        roof(d,cx,y,width*(0.50-0.05*i),rh*1.1,S)
        y-=rh*1.25
    # sorin spire with rings
    sp_h=height*0.12; d.rectangle((int(cx-S*2),int(y-sp_h),int(cx+S*2),int(y)),fill=GOLD)
    for k in range(7):
        ry=y-sp_h*0.15-k*sp_h*0.11; rw=S*7-k*S*0.4
        d.ellipse((int(cx-rw),int(ry-S*2),int(cx+rw),int(ry+S*2)),fill=GOLD_LO,outline=GOLD,width=S)
    d.ellipse((int(cx-S*4),int(y-sp_h-S*6),int(cx+S*4),int(y-sp_h+S*2)),fill=GOLD)

def branches(img,S,rnd,origin,length,angle,depth=0):
    d=ImageDraw.Draw(img)
    x,y=origin; x2=x+length*math.cos(angle); y2=y-length*math.sin(angle)
    d.line((int(x),int(y),int(x2),int(y2)),fill=(70,56,40),width=max(S*2,int(S*(9-depth*2))))
    # snow lump on top of the branch
    for t in (0.2,0.45,0.7,0.95):
        sx,sy=x+(x2-x)*t,y+(y2-y)*t; r=S*(14-depth*3)*rnd.uniform(0.8,1.3)
        d.ellipse((int(sx-r*1.3),int(sy-r*1.1),int(sx+r*1.3),int(sy+r*0.3)),fill=CREAM)
    if depth<3:
        for da in (rnd.uniform(0.3,0.7),-rnd.uniform(0.2,0.6)):
            branches(img,S,rnd,(x2,y2),length*rnd.uniform(0.55,0.75),angle+da,depth+1)

def make_scene(w,h,seed=5):
    S=3; W,H=w*S,h*S; rnd=random.Random(seed)
    img=Image.new('RGBA',(W,H),(0,0,0,0))
    # faint gold wispy clouds (like the photo's sky streaks)
    cl=ImageDraw.Draw(img)
    for (x0,y0,x1,y1) in [(0.0,0.46,0.22,0.475)]:
        cl.rounded_rectangle((int(W*x0),int(H*y0),int(W*x1),int(H*y1)),int(H*0.015),fill=GOLD+(45,))
    fuji(img,int(W*0.36),int(H*0.80),int(W*0.38),int(H*0.50),S,rnd)
    # snowy town / plain at the foot
    ImageDraw.Draw(img).rectangle((0,int(H*0.80),W,H),fill=(36,34,32,255))
    for i in range(160):
        x=rnd.uniform(0,W*0.75); y=rnd.uniform(H*0.81,H*0.97); r=S*rnd.uniform(1,2.4)
        ImageDraw.Draw(img).ellipse((int(x-r),int(y-r),int(x+r),int(y+r)),fill=GOLD+(rnd.randint(60,140),))
    pagoda(img,int(W*0.84),int(H*1.0),int(W*0.36),int(H*0.86),S)
    
    
    ImageDraw.Draw(img).line((0,int(H*0.80),int(W*0.70),int(H*0.80)),fill=GOLD+(255,),width=S*2)
    return img.resize((w,h),Image.LANCZOS)

if __name__=='__main__':
    bg=Image.new('RGBA',(1400,900),(26,26,28,255)); bg.alpha_composite(make_scene(1400,900)); bg.save('scene_test.png')
