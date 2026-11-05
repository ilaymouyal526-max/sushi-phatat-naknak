"""Fuji from Hokusai's 'Fine Wind, Clear Morning' (public domain), recoloured to the ad's black & gold.
mode 'print' = keep Hokusai's texture as gold-on-black;  mode 'clean' = flat clean vector-like fills."""
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
REF='ref/hokusai_red_fuji_PD.jpg'
GOLD=np.array([214,178,110]); GOLD_HI=np.array([246,222,160]); GOLD_LO=np.array([110,82,40]); CREAM=np.array([246,238,220])

def masks():
    im=Image.open(REF).convert('RGB'); a=np.array(im).astype(int); r,g,b=a[...,0],a[...,1],a[...,2]
    lum=0.3*r+0.59*g+0.11*b
    red=((r-g>45)&(r-b>45)) | ((r-b>25)&(r-g>15)&(lum<140))
    rm=Image.fromarray((red*255).astype('uint8')).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    rmn=np.array(rm)>0
    H,W=rmn.shape; hull=np.zeros_like(rmn)
    def runs(row):
        d=np.diff(np.concatenate([[0],row.astype(int),[0]])); st=np.nonzero(d==1)[0]; en=np.nonzero(d==-1)[0]-1
        return list(zip(st,en))
    # summit: first row with a solid red run of >=10px
    y0=next(y for y in range(H) if any(e-s>=10 for s,e in runs(rmn[y])))
    s0,e0=max(runs(rmn[y0]),key=lambda t:t[1]-t[0]); curL,curR=s0,e0
    for y in range(y0,H):
        rs=[(s,e) for s,e in runs(rmn[y]) if e>=curL-6 and s<=curR+6]   # runs touching current cone
        if rs:
            nl=min(s for s,e in rs); nr=max(e for s,e in rs)
            curL=min(curL,max(nl,curL-4)); curR=max(curR,min(nr,curR+4))   # flanks spread at most 4px/row
        hull[y,curL:curR+1]=True
    # smooth hull edge
    hm=Image.fromarray((hull*255).astype('uint8')).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.2))
    hull=np.array(hm)>128
    yy=np.arange(H)[:,None].repeat(W,1)
    snow=hull & (lum>140) & (r-g<55) & (yy<int(H*0.45))
    sky=~hull
    cloud=sky & (lum>150)
    return a,lum,hull,snow,cloud

def render(mode='clean', crop=(190,70,960,412)):
    a,lum,hull,snow,cloud=masks()
    H,W=hull.shape; out=np.zeros((H,W,4),float)
    yy=np.arange(H)[:,None].repeat(W,1)
    top=np.nonzero(hull.any(1))[0][0]
    # vertical gradient on the mountain: bright gold at summit -> deep gold lower down
    f=np.clip((yy-top)/(H*0.55),0,1)[...,None]
    base=GOLD_HI*(1-f)+GOLD_LO*f
    if mode=='print':
        tex=(lum/255.0)[...,None]                 # keep Hokusai's woodgrain texture
        col=base*(0.55+0.6*tex)
    else:
        col=base
    out[hull,:3]=np.clip(col[hull],0,255); out[hull,3]=255
    s=snow
    if mode=='clean':
        sm=Image.fromarray((snow*255).astype('uint8')).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.0))
        s=(np.array(sm)>100)&hull
    out[s,:3]=CREAM; out[s,3]=255
    # fade the mountain foot into black (the print's forest)
    fade=np.clip(1-(yy-(top+H*0.48))/(H*0.22),0,1)
    out[...,3]*=fade
    # Hokusai's cloud pattern as faint gold in the sky
    cm=cloud
    if mode=='clean':
        cmi=Image.fromarray((cloud*255).astype('uint8')).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.MaxFilter(3))
        cm=(np.array(cmi)>128)&~hull
    cl=np.zeros_like(out); cl[cm,:3]=GOLD; cl[cm,3]=55
    clouds=Image.fromarray(cl.astype('uint8'),'RGBA').crop(crop)
    img=Image.fromarray(out.astype('uint8'),'RGBA').crop(crop)
    # gold outline along the mountain silhouette
    hm=Image.fromarray((hull*255).astype('uint8')).crop(crop)
    edge=hm.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.MaxFilter(3))
    e=np.array(edge)>60
    e[:, -4:]=False; e[-4:,:]=False   # no outline along the crop border
    o=np.array(img); fy=fade[crop[1]:crop[3],crop[0]:crop[2]]
    o[e,:3]=GOLD; o[e,3]=(255*fy[e]).astype('uint8')
    return Image.fromarray(o,'RGBA'), clouds

def with_sun(layers):
    img,clouds=layers
    w,h=img.size; r=int(h*0.15); cx,cy=int(w*0.24),int(h*0.24)
    out=clouds.copy(); sd=ImageDraw.Draw(out)
    sd.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(196,48,38,255),outline=(214,178,110,255),width=3)
    out.alpha_composite(img); return out

def make_fuji_hokusai(w,h,mode='clean'):
    return with_sun(render(mode)).resize((w,h),Image.LANCZOS)

if __name__=='__main__':
    for m in ('print','clean'):
        f=with_sun(render(m)); bg=Image.new('RGBA',f.size,(26,26,28,255)); bg.alpha_composite(f); bg.save(f'fuji_hokusai_{m}.png')
