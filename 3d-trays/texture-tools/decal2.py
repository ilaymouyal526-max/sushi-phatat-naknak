from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import sys
def decal(src,box,out,size=512,sharp=1.0):
    im=Image.open(src).convert('RGB').crop(box).resize((size,size),Image.LANCZOS)
    if sharp!=1: im=ImageEnhance.Sharpness(im).enhance(sharp)
    m=Image.new('L',(size*4,size*4),0); ImageDraw.Draw(m).ellipse((6,6,size*4-6,size*4-6),fill=255)
    m=m.resize((size,size),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.2))
    im.putalpha(m); im.save(out,'WEBP',quality=90)
s,x0,y0,x1,y1,out=sys.argv[1:7]; decal(s,(int(x0),int(y0),int(x1),int(y1)),out,sharp=float(sys.argv[7]) if len(sys.argv)>7 else 1)
