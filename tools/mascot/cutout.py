import numpy as np
from PIL import Image
from scipy import ndimage
im=Image.open('sheet.webp').convert('RGB');A=np.array(im).astype(np.float32);H,W,_=A.shape
bg=np.array([249,239,226],np.float32)
d=np.sqrt(((A-bg)**2).sum(2));mx=A.max(2);mn=A.min(2);sat=mx-mn;lum=A.mean(2);bgl=bg.mean()
Y=np.arange(H)[:,None]*np.ones((1,W))
shadow=(Y>720)&(sat<85)&(lum<bgl+1)&(lum>105)&(~((A[:,:,0]>200)&(A[:,:,2]<120)))  # 黄色の足は除外
fg0=(d>9)&(~shadow)
lab,n=ndimage.label(~fg0);border=set(np.unique(np.concatenate([lab[0],lab[-1],lab[:,0],lab[:,-1]])))-{0}
st=ndimage.generate_binary_structure(2,1)
sil=ndimage.binary_closing(fg0,structure=st,iterations=5)
sil=ndimage.binary_fill_holes(sil)
# 純粋な背景色の大きな穴（腕と頭のすき間など）は抜く
hole=(d<5)&sil
hl,hn=ndimage.label(hole);sz=ndimage.sum(np.ones_like(d),hl,range(1,hn+1))
for i,s in enumerate(sz,1):
  if s>250: sil&=~(hl==i)
sil=ndimage.binary_opening(sil,structure=st,iterations=2)
# 小さいゴミ除去
l3,n3=ndimage.label(sil);s3=ndimage.sum(np.ones_like(d),l3,range(1,n3+1))
for i,s in enumerate(s3,1):
  if s<1500: sil&=~(l3==i)
# アルファ：体（色が濃い）は不透明、羽など背景に近い色は半透明
core=np.clip((d-8)/26,0,1)
alpha=np.where(sil,np.maximum(core,0.62),0).astype(np.float32)
edge=ndimage.gaussian_filter(sil.astype(np.float32),0.9)
alpha=np.minimum(alpha,edge*1.15)
# 羽：ポーズごとの羽の範囲内で「低彩度・明るい」画素を羽とみなし、つるっとした半透明に描き直す
BOX=[(37,430,200,655),(369,430,490,615),(504,418,642,640),(861,437,940,580),(994,430,1110,655),(1340,418,1466,642),(1503,492,1585,690),(1820,492,1982,728),(1986,430,2093,648),(2263,430,2431,648)]
inbox=np.zeros_like(sil)
for x0,y0,x1,y1 in BOX: inbox[y0:y1,x0:x1]=True
wing=sil&inbox&(sat<55)&(lum>135)
wing=ndimage.binary_closing(wing,structure=st,iterations=3)
wing=ndimage.binary_fill_holes(wing)&sil
wl,wn=ndimage.label(wing);ws=ndimage.sum(np.ones_like(d),wl,range(1,wn+1))
for i,sz in enumerate(ws,1):
  if sz<600: wing&=~(wl==i)
ws_=ndimage.gaussian_filter(wing.astype(np.float32),1.2)
ring=ws_-ndimage.gaussian_filter(ndimage.binary_erosion(wing,iterations=4).astype(np.float32),1.2)
ring=np.clip(ring,0,1)
ring=np.clip(ring*1.6,0,1)
wcol=np.stack([238-45*ring,246-36*ring,255-22*ring],-1)
inner=ndimage.gaussian_filter(ndimage.binary_erosion(wing,iterations=10).astype(np.float32),6)
aw=0.40+0.50*ring+0.12*inner
col=np.where(wing[...,None],wcol,A)
alpha=np.where(wing,np.minimum(aw,edge*1.1),alpha)
# 羽の外側に残った背景色のにじみを除去
alpha=np.where(sil&~wing&(d<14)&inbox,0,alpha)
rgba=np.dstack([col,alpha*255]).clip(0,255).astype(np.uint8)
out=Image.fromarray(rgba,'RGBA');out.save('cut_full.png')
for bgc,fn in [((30,28,40),'check_dark.jpg'),((247,246,252),'check_light.jpg')]:
  c=Image.new('RGBA',out.size,bgc+(255,));c.alpha_composite(out);c.convert('RGB').save(fn,quality=88)
runs=[(34,484),(506,970),(981,1477),(1481,1982),(1988,2434)];names=['base','adventure','cheer','study','trophy']
for (x0,x1),nm in zip(runs,names):
  c=out.crop((max(0,x0-10),0,min(W,x1+10),H));c=c.crop(c.getbbox());c.save(f'pose_{nm}.png');print(nm,c.size)
