from PIL import Image, ImageDraw, ImageFilter
import sys
def decal(src,cx,cy,r,out,size=512):
    im=Image.open(src).convert('RGB').crop((cx-r,cy-r,cx+r,cy+r)).resize((size,size),Image.LANCZOS)
    m=Image.new('L',(size*4,size*4),0); ImageDraw.Draw(m).ellipse((8,8,size*4-8,size*4-8),fill=255)
    m=m.resize((size,size),Image.LANCZOS).filter(ImageFilter.GaussianBlur(1.5))
    im.putalpha(m); im.save(out,'WEBP',quality=88)
args=sys.argv[1:]
decal(args[0],int(args[1]),int(args[2]),int(args[3]),args[4])
