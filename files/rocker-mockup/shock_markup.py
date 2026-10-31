import numpy as np, math, json
from PIL import Image
from scipy import ndimage
from skimage import measure
im=np.array(Image.open('/root/.claude/uploads/4906d7fa-0700-5129-88f1-c51707ec55ce/b9e45def-image.png').convert('RGB')).astype(int)
part=(abs(im[:,:,0]-76)<7)&(abs(im[:,:,1]-85)<7)&(abs(im[:,:,2]-89)<7)
part=ndimage.binary_opening(part,iterations=2)
part=ndimage.binary_closing(part,iterations=3)
lab,n=ndimage.label(part); part=lab==(np.argmax(np.bincount(lab.ravel())[1:])+1)
filled=ndimage.binary_fill_holes(part)
# holes: approximate centres given, refine by centroid of non-part pixels within 30 px
def cen(c):
    y,x=np.mgrid[0:im.shape[0],0:im.shape[1]]; m=(~part)&filled&((x-c[0])**2+(y-c[1])**2<30**2)
    return (x[m].mean(), y[m].mean())
S=cen((128,218)); R=(797.0,296.0); D=cen((545,710))
print('px holes',S,R,D)
con=max(measure.find_contours(filled.astype(float),0.5),key=len); px=np.c_[con[:,1],con[:,0]]
src=open('design.py').read().split("def gap_report")[0]; exec(src)
img=np.array([R,D,S]); dst=np.array([[0,0],Dl,Sl])
mi,md=img.mean(0),dst.mean(0); X=img-mi; Y=dst-md
U,Sg,Vt=np.linalg.svd(Y.T@X); A=U@Vt; s=Sg.sum()/(X**2).sum()
fit=lambda P:(s*(A@(np.array(P)-mi).T)).T+md
print('mm/px',round(s,4),'fit err',np.linalg.norm(fit(img)-dst,axis=1).round(2),'det',round(np.linalg.det(A)))
jp=Polygon(fit(px)).buffer(0)
res=[]
for p in poses:
    rk=affinity.translate(affinity.rotate(jp,p['rang'],origin=(0,0),use_radians=True),*p['R'])
    a=unary_union([affinity.rotate(x,p['th'],origin=(0,0),use_radians=True) for x in arm_band])
    red=affinity.rotate(Polygon([(q[0]+ARM_SHIFT[0],q[1]+ARM_SHIFT[1]) for q in ARM['cross']]),p['th'],origin=(0,0),use_radians=True)
    res.append((p['th']*180/math.pi, rk.distance(a), rk.distance(red), rk.distance(shock_end(p))))
for i in (0,len(res)//4,len(res)//2,-1): print([round(v,1) for v in res[i]])
m=min(res,key=lambda r:r[1]); print('min arm gap',[round(v,1) for v in m]); print('min bench outline gap',round(min(r[2] for r in res),1)); m2=min(res,key=lambda r:r[3]); print('min shock gap',[round(v,1) for v in m2])
print('area', round(jp.area), 'bounds', [round(v) for v in jp.bounds], 'filled px', filled.sum())
Image.fromarray((filled*255).astype(np.uint8)).save('/tmp/claude-0/-home-claude-chassis-bench/4906d7fa-0700-5129-88f1-c51707ec55ce/scratchpad/mask2.png')
iS=jp.intersection(shk_sw)
pts=[c for g in (iS.geoms if hasattr(iS,'geoms') else [iS]) for c in g.exterior.coords]
print('shock overlap area',round(iS.area),'depth',round(max(Point(*q).distance(jp.exterior) for q in pts),1),'dist from shock bolt',round(min(math.hypot(q[0]-Sl[0],q[1]-Sl[1]) for q in pts),1))
# what body half-width would just clear? test narrower placeholders
from shapely.geometry import Point, box
from shapely.ops import nearest_points
def prof():
    # shock profile in shock coords: x along axis from bolt, y across
    ears=unary_union([Point(0,0).buffer(12,64), box(0,-12,BR,12)])
    parts=[box(BR,-18,72,18), box(72,-39,80,39), box(80,-38,200,38)]
    return unary_union(parts), parts[0], unary_union(parts[1:]), ears
import sys
BR=float(sys.argv[1]) if len(sys.argv)>1 else 35
P,CLV,SPR,EARS=prof()
def place(g,p):
    S=np.array(p['S']); top=np.array(G['shockTop']); u=(top-S)/np.linalg.norm(top-S)
    a=math.degrees(math.atan2(u[1],u[0]))
    return affinity.translate(affinity.rotate(g,a,origin=(0,0)),*S)
def rk(p): return affinity.translate(affinity.rotate(jp,p['rang'],origin=(0,0),use_radians=True),*p['R'])
for nm,g in (('clevis',CLV),('spring',SPR)):
    r=min((rk(p).distance(place(g,p)),p['th']*180/math.pi) for p in poses); print(nm,'min gap',[round(v,1) for v in r])
env=unary_union([world_to_rocker(place(P,p),p) for p in poses])
env_c=unary_union([world_to_rocker(place(CLV,p),p) for p in poses])
droop=world_to_rocker(place(P,poses[0]),poses[0])
cut=jp.intersection(env.buffer(3,64)); print('cut area',round(cut.area))
inv=lambda Q:(np.linalg.inv(A)@((np.array(Q)-md).T/s)).T+mi
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(im.shape[1]/80,im.shape[0]/80),dpi=80)
ax.imshow(im.astype(np.uint8)); ax.axis('off')
def outline(g,**kw):
    for h in (g.geoms if hasattr(g,'geoms') else [g]):
        q=inv(np.array(h.exterior.coords)); ax.plot(q[:,0],q[:,1],**kw)
outline(env,color='orange',lw=1.5,ls='--')
outline(droop,color='deepskyblue',lw=2.5)
outline(world_to_rocker(place(EARS,poses[0]),poses[0]),color='deepskyblue',lw=1.5,ls=':')
for h in (cut.geoms if hasattr(cut,'geoms') else [cut]):
    if h.area<1: continue
    q=inv(np.array(h.exterior.coords)); ax.fill(q[:,0],q[:,1],color='red',alpha=.7)
edge=env.buffer(3,64).exterior.intersection(jp.buffer(1))
for h in (edge.geoms if hasattr(edge,'geoms') else [edge]):
    q=inv(np.array(h.coords)); ax.plot(q[:,0],q[:,1],color='yellow',lw=2.5)
c=inv([np.array(droop.centroid.coords[0])])[0]
ax.annotate(f'Shock at full droop (blue)\nslot {BR:.0f} deep (ears dotted, rocker sits between them)\nbody 36 wide, spring seat 78 OD at 72 mm',c,xytext=(c[0]-60,c[1]-120),color='deepskyblue',fontsize=12,fontweight='bold',bbox=dict(fc='white',alpha=.85))
if cut.area>1:
    cc=inv([np.array(cut.centroid.coords[0])])[0]
    ax.annotate('REMOVE (red), yellow = new edge 3 mm clear\norange dashed = shock swept droop to bump',cc,xytext=(cc[0]+60,cc[1]+90),color='red',fontsize=12,fontweight='bold',arrowprops=dict(color='red'),bbox=dict(fc='white',alpha=.85))
plt.savefig('/home/claude/chassis-bench/files/rocker-mockup/rocker-joel-v2-shock-markup.png' if BR==35 else f'/tmp/claude-0/-home-claude-chassis-bench/4906d7fa-0700-5129-88f1-c51707ec55ce/scratchpad/mk{BR:.0f}.png',bbox_inches='tight',pad_inches=0)
