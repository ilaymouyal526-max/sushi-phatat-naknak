import numpy as np
from PIL import Image, ImageDraw, ImageFilter
T='/root/.claude/projects/-home-user-sushi-phatat-naknak/f008169a-e3fe-5e15-a4e1-236ae64ffc3e/tool-results/mcp-Higgsfield-blob-'
F={'pnk':'1793027477435-812ymd','ses':'1793027477435-c4pht3','ins':'1793027477435-f2s5ar','drg':'1793027477436-w2n3jh',
   'tmp':'1793027494428-91bbg0','tmy':'1793027494428-eyeyvr','sap':'1793027494429-jpbs6g','sat':'1793027494429-gp2zao',
   'vgp':'1793027507517-nhdlgd','tmc':'1793027507517-bq3549'}
TI={'rice':'1793027507517-txrduw','ses':'1793027507517-nfeuwc','pink':'1793027534666-f6gg8b','flake':'1793027534667-zeee0y',
    'avo':'1793027543565-chaqay','nori':'1793027543566-k1o644','tempura':'1793027523141-exmb0a'}
out='trays/assets/'
for k,f in F.items():
    im=Image.open(T+f+'.jpg').convert('RGB'); a=np.asarray(im).astype(int)
    mask=a.max(axis=2)>45; ys,xs=np.where(mask)
    x0,x1=np.percentile(xs,[0.3,99.7]); y0,y1=np.percentile(ys,[0.3,99.7])
    cx,cy=(x0+x1)/2,(y0+y1)/2; r=max(x1-x0,y1-y0)/2*1.01
    c=im.crop((int(cx-r),int(cy-r),int(cx+r),int(cy+r))).resize((512,512),Image.LANCZOS)
    m=Image.new('L',(2048,2048),0); ImageDraw.Draw(m).ellipse((4,4,2044,2044),fill=255); m=m.resize((512,512),Image.LANCZOS)
    # keep the photo's own black background outside the food transparent too
    fg=Image.fromarray(((np.asarray(c).max(axis=2)>38)*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1))
    alpha=Image.fromarray(np.minimum(np.asarray(m),np.asarray(fg)).astype('uint8'))
    c.putalpha(alpha); c.save(out+f'face-{k}.webp','WEBP',quality=88)
for k,f in TI.items():
    im=np.asarray(Image.open(T+f+'.jpg').convert('RGB').resize((512,512),Image.LANCZOS)).astype(float)
    sh=np.roll(np.roll(im,256,0),256,1); n=512; fe=96
    d=np.minimum(np.arange(n),np.arange(n)[::-1]); w1=np.clip(d/fe,0,1); w=np.minimum.outer(w1,w1)[...,None]
    Image.fromarray((im*w+sh*(1-w)).clip(0,255).astype('uint8')).save(out+f'tile-{k}.webp','WEBP',quality=86)
print('done')
