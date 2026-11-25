from PIL import Image, ImageDraw
full=Image.open('cut_full.png')
def crop(box): return full.crop(box)
# base pose head area (sheet coords)
from PIL import ImageChops
def headmask(box,ant):
  m=Image.new('L',full.size,0);d=ImageDraw.Draw(m);d.ellipse((143,280,413,530),fill=255)
  if ant: d.rectangle((110,195,440,305),fill=255)
  img=full.copy();a=ImageChops.multiply(img.getchannel('A'),m);img.putalpha(a);return img.crop(box)
face_tight=headmask((138,272,418,536),False)   # 頭だけ（16px用）
face_ant=headmask((106,196,450,536),True)      # 触角つきの顔（32/48・大アイコン）
def sq(img,size,bg=None,pad=0.0):
  w,h=img.size;s=max(w,h);canvas=Image.new('RGBA',(s,s),(0,0,0,0));canvas.paste(img,((s-w)//2,(s-h)//2),img)
  if pad: 
    p=int(s*pad);c2=Image.new('RGBA',(s+2*p,s+2*p),(0,0,0,0));c2.paste(canvas,(p,p),canvas);canvas=c2
  canvas=canvas.resize((size,size),Image.LANCZOS)
  if bg:
    b=Image.new('RGBA',(size,size),bg);b.alpha_composite(canvas);canvas=b
  return canvas
import os;os.makedirs('out',exist_ok=True)
from PIL import ImageFilter,ImageEnhance
f16=sq(face_tight,16).filter(ImageFilter.UnsharpMask(radius=1,percent=140,threshold=0));f32=sq(face_ant,32);f48=sq(face_ant,48)
f16.save('out/favicon-16.png');f32.save('out/favicon-32.png');f48.save('out/favicon-48.png')
f48.save('out/favicon.ico',sizes=[(16,16),(32,32),(48,48)],append_images=[f16,f32])
# ico: explicit multi-size from separate images
from PIL import IcoImagePlugin
imgs=[f16,f32,f48]
imgs[2].save('out/favicon.ico',format='ICO',sizes=[(16,16),(32,32),(48,48)],append_images=imgs[:2])
BG=(255,226,140,255)
sq(face_ant,180,BG,0.06).convert('RGB').save('out/apple-touch-icon.png')
sq(face_ant,192,BG,0.06).save('out/icon-192.png')
sq(face_ant,512,BG,0.06).save('out/icon-512.png')
# 確認用：タブ風にプレビュー
prev=Image.new('RGB',(900,260),(222,225,230));d=ImageDraw.Draw(prev)
for i,(im,sz) in enumerate([(f16,16),(f32,32),(f48,48)]):
  x=30+i*290
  d.rounded_rectangle((x,20,x+260,60),8,fill=(255,255,255));prev.paste(im.resize((16,16),Image.LANCZOS) if sz!=16 else im,(x+12,32),im.resize((16,16),Image.LANCZOS) if sz!=16 else im)
  d.text((x+36,33),f"PM試験クエスト ({sz}px→16)",fill=(40,40,40))
  big=im.resize((160,160),Image.NEAREST);prev.paste(big,(x+50,80),big)
prev.save('out/favicon_preview.png')
print('ok')
