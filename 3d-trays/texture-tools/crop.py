from PIL import Image, ImageDraw
import json,sys
C=json.load(open('crops.json'))
tiles=[]
for k,(src,box) in C.items():
    im=Image.open(f'jpg/{src}.jpg').crop(tuple(box)); im.save(f'crops/{k}.jpg',quality=92)
    t=im.copy(); t.thumbnail((300,300)); tiles.append((k,t))
W=4; sheet=Image.new('RGB',(W*310,((len(tiles)+W-1)//W)*330),'white'); d=ImageDraw.Draw(sheet)
for i,(k,t) in enumerate(tiles):
    x,y=(i%W)*310,(i//W)*330; sheet.paste(t,(x,y)); d.text((x+4,y+305),k,fill='black')
sheet.save('crops_sheet.jpg',quality=88)
