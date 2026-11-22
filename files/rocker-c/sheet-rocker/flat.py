import os,sys,json,pickle,numpy as np,ezdxf
from shapely.geometry import Point,LineString,Polygon
from shapely.ops import transform
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
T=float(sys.argv[1]); J=json.load(open(f'jog_{int(T)}.json'))
O=pickle.load(open('outlines.pkl','rb')); outline=O['o2'].buffer(0)
P=np.array([0,0.]); S=np.array([-166.8,64.4]); D=np.array([-100.5,-100.3])
u=np.array([-1,-1])/np.sqrt(2); wv=np.array([-1,1])/np.sqrt(2); Q1=np.array([-45.,-35.]); TMAX=70
OFF=17.25; K=0.33; ri=T; rn=ri+K*T; th=np.radians(45)
Ls=(OFF-2*rn*(1-np.cos(th)))/np.sin(th); hr=2*rn*np.sin(th)+Ls*np.cos(th); dev=2*rn*th+Ls; extra=dev-hr
arc=rn*th; B1=arc/2; B2=arc+Ls+arc/2
print(f'T{T}: rn {rn:.2f} slant {Ls:.2f} run {hr:.2f} developed {dev:.2f} extra {extra:.2f} bend lines at {B1:.2f} / {B2:.2f} from start')
def fl(x,y,z=None):
    p=np.array([x,y]); s=(p-Q1)@u; t=(p-Q1)@wv
    if t>=TMAX or s<=0: return (x,y)
    sf= s*dev/hr if s<hr else s+extra
    q=p+u*(sf-s); return (q[0],q[1])
flat=transform(lambda x,y,z=None: tuple(np.array([fl(a,b) for a,b in zip(np.atleast_1d(x),np.atleast_1d(y))]).T), outline.segmentize(1.0))
Df=np.array(fl(*D))
holes={'P':P,'S':S,'D':Df}
# bend lines clipped to the lower arm
bl=[]
for b in (B1,B2):
    q=Q1+u*b; L=flat.intersection(LineString([q-60*wv,q+60*wv]))
    segs=[g for g in getattr(L,'geoms',[L]) if (np.array(g.coords).mean(0)-Q1)@wv<TMAX]
    bl+=segs
doc=ezdxf.new('R2010',setup=True); doc.units=ezdxf.units.MM; msp=doc.modelspace()
for n,c in (('CUT',7),('PILOT_8',1),('DRILL_10.5',3),('BEND',5),('NOTES',2)): doc.layers.add(n,color=c)
for ring in [flat.exterior]+list(flat.interiors): msp.add_lwpolyline(list(ring.coords),close=True,dxfattribs={'layer':'CUT'})
for k,c in holes.items():
    msp.add_circle(tuple(c),4.0,dxfattribs={'layer':'PILOT_8'}); msp.add_circle(tuple(c),5.25,dxfattribs={'layer':'DRILL_10.5'})
for g in bl:
    msp.add_line(*[tuple(p) for p in g.coords],dxfattribs={'layer':'BEND','linetype':'DASHED'})
gap=J['zR']-(J['zL']+T)
webs=J['webs']; ox=-20
for i,(c,a,lg) in enumerate(webs):
    x0=ox+sum(w[2] for w in webs[:i])+6*i; msp.add_lwpolyline([(x0,-130),(x0+lg,-130),(x0+lg,-130+gap),(x0,-130+gap)],close=True,dxfattribs={'layer':'CUT'})
txt=[f'SHEET ROCKER MOCK-UP  {T:g} mm mild steel (S275/DC01-ish)  CUT 2 PLATES (identical) + 4 WEBS',
     'Holes: plasma 8 mm pilot, drill to 10.5 for M10 bolts',
     f'Joggle: 2 bends 45 deg opposite ways on BEND lines, offset {OFF} mm, inside radius ~{ri:g}',
     'Both plates bend the SAME way: jog comes TOWARDS you looking at this drawing',
     f'Webs {gap:.1f} wide (= gap between plates). Tubes x2: 20 OD x 10 ID, {gap:.1f} long, at P and S']
for i,tx in enumerate(txt): msp.add_text(tx,height=3.5,dxfattribs={'layer':'NOTES'}).set_placement((-190,-150-i*6))
doc.saveas(f'sheet-rocker-{int(T)}mm-flat.dxf')
# drawing
fig,ax=plt.subplots(figsize=(11.7,8.3),dpi=160)
x,y=flat.exterior.xy; ax.fill(x,y,color='#d8dde3',ec='k',lw=1.2)
for ring in flat.interiors: ax.fill(*ring.xy,color='w',ec='k',lw=1.2)
for k,c in holes.items():
    ax.add_patch(plt.Circle(c,5.25,fc='w',ec='g',lw=1.2)); ax.add_patch(plt.Circle(c,4,fc='none',ec='r',lw=.8,ls=':'))
    ax.annotate(f'{k}  ({c[0]:.1f}, {c[1]:.1f})',c,xytext=(c[0]+9,c[1]+7),fontsize=8)
for g in bl: ax.plot(*np.array(g.coords).T,'b--',lw=1.3)
ax.annotate('bend lines (45° each, opposite ways)\njog 17.25 mm towards you',np.array(bl[0].coords).mean(0),xytext=(-15,-95),fontsize=8,color='b',arrowprops=dict(arrowstyle='->',color='b'))
for i,(c,a,lg) in enumerate(webs):
    x0=ox+sum(w[2] for w in webs[:i])+6*i; ax.add_patch(plt.Rectangle((x0,-130),lg,gap,fc='#d8dde3',ec='k')); ax.text(x0+lg/2,-130+gap/2,f'web {i+1}\n{lg}x{gap:.1f}',ha='center',va='center',fontsize=7)
    tw=np.array([np.cos(np.radians(a)),np.sin(np.radians(a))]); c=np.array(fl(*c)); ax.plot(*np.array([c-tw*lg/2,c+tw*lg/2]).T,color='#c2410c',lw=3,alpha=.6); ax.text(*(c+np.array([4,-6])),f'web {i+1}',fontsize=7,color='#c2410c')
for i,tx in enumerate(txt): ax.text(-190,-150-i*7,tx,fontsize=8)
ax.set_aspect('equal'); ax.grid(alpha=.25); ax.set_xlim(-200,170); ax.set_ylim(-190,100)
ax.set_title(f'Sheet-metal rocker mock-up, flat pattern 1:1 mm, {T:g} mm plate (origin = pivot hole, X fwd)',fontsize=10)
plt.tight_layout(); plt.savefig(f'sheet-rocker-{int(T)}mm-flat.png')
json.dump(dict(rn=rn,Ls=Ls,hr=hr,dev=dev,extra=extra,B1=B1,B2=B2,gap=gap,Df=Df.tolist(),bends=[list(map(list,g.coords)) for g in bl]),open(f'flat_{int(T)}.json','w'))
