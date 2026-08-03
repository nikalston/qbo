from PIL import Image, ImageDraw
import math

BG="#0F1418"; AMBER="#F2A93B"; DARK="#12181E"

def cap(size, pad_ratio=0.16, bg=BG):
    S=size*4
    im=Image.new("RGB",(S,S),bg); d=ImageDraw.Draw(im)
    cx=cy=S/2; R=S*(0.5-pad_ratio)
    # scalloped bottle-cap crown
    teeth=21; pts=[]
    for i in range(teeth*12):
        a=2*math.pi*i/(teeth*12)
        r=R*(1+0.085*math.cos(teeth*a))
        pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
    d.polygon(pts, fill=AMBER)
    d.ellipse([cx-R*0.70,cy-R*0.70,cx+R*0.70,cy+R*0.70], fill=bg)
    d.ellipse([cx-R*0.60,cy-R*0.60,cx+R*0.60,cy+R*0.60], fill=AMBER)
    # "Q" cut out of the inner disc
    d.ellipse([cx-R*0.38,cy-R*0.38,cx+R*0.38,cy+R*0.38], fill=bg)
    d.line([(cx+R*0.08,cy+R*0.08),(cx+R*0.46,cy+R*0.46)], fill=bg, width=int(R*0.20))
    return im.resize((size,size), Image.LANCZOS)

cap(192).save("icon-192.png")
cap(512).save("icon-512.png")
cap(180).save("icon-180.png")
cap(512, pad_ratio=0.26).save("icon-512-maskable.png")
print("icons ok")
