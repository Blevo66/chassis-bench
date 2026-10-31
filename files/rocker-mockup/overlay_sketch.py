import json, numpy as np, math
src=open('design.py').read().split("def gap_report")[0]
exec(src)
J=json.load(open('/tmp/claude-0/-home-claude-chassis-bench/4906d7fa-0700-5129-88f1-c51707ec55ce/scratchpad/joel_px.json'))
Hs=np.array(J['holes'])  # order: shock, pivot, dogbone (by position)
img=np.array([Hs[1][:2],Hs[2][:2],Hs[0][:2]]); dst=np.array([[0,0],Dl,Sl])
# similarity with reflection: dst = s*A@img + t
mi,md=img.mean(0),dst.mean(0); X=img-mi; Y=dst-md
U,Sg,Vt=np.linalg.svd(Y.T@X); A=U@Vt; s=Sg.sum()/(X**2).sum()
fit=lambda P:(s*(A@(np.array(P)-mi).T)).T+md
res=np.linalg.norm(fit(img)-dst,axis=1); print('px/mm',round(1/s,3),'hole fit error mm',res.round(2),'det',round(np.linalg.det(A)))
print('hole dia mm', [round(h[2]*s,1) for h in Hs])
out=fit(J['outline']); jp=Polygon(out).buffer(0)
print('Joel area', round(jp.area), 'mine', round(body.area))
# clearance through travel
worst=(99,None); worst_s=(99,None)
allp=[]
for p in poses:
    rk=affinity.translate(affinity.rotate(jp,p['rang'],origin=(0,0),use_radians=True),*p['R'])
    a=unary_union([affinity.rotate(x,p['th'],origin=(0,0),use_radians=True) for x in arm_band])
    d=rk.distance(a); 
    if d<worst[0]: worst=(d,p)
    ds=rk.distance(shock_end(p))
    if ds<worst_s[0]: worst_s=(ds,p)
    if d==0: allp.append(p)
print('Joel min gap to arm', round(worst[0],1), 'at arm', round(worst[1]['th']/D2R,1), 'n poses touching', len(allp))
if allp: print('touching arm angle range', round(allp[0]['th']/D2R,1), round(allp[-1]['th']/D2R,1))
print('Joel min gap to shock body (30 mm bridge, 40 wide guess)', round(worst_s[0],1), 'at', round(worst_s[1]['th']/D2R,1))
# overlap depth: intersection with swept arm in rocker frame
inter=jp.intersection(arm_sw); print('overlap area with arm sweep mm2', round(inter.area,1))
if not inter.is_empty:
    # max penetration depth
    pts=np.array([c for g in (inter.geoms if hasattr(inter,'geoms') else [inter]) for c in g.exterior.coords])
    dep=max(Point(*q).distance(arm_sw.exterior) for q in pts if jp.exterior.distance(Point(*q))<0.5) if len(pts) else 0
    print('worst depth into arm sweep mm ~', round(max(Point(*q).distance(jp.exterior) for q in pts),1))
json.dump({'outline':out.tolist()},open('/tmp/claude-0/-home-claude-chassis-bench/4906d7fa-0700-5129-88f1-c51707ec55ce/scratchpad/joel_rk.json','w'))
# drawing, right-side view at droop
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def W(g,p):
    g=affinity.translate(affinity.rotate(g,p['rang'],origin=(0,0),use_radians=True),*p['R']); return affinity.scale(g,-1,1,origin=(0,0))
def fillg(ax,g,**k):
    for gg in (g.geoms if hasattr(g,'geoms') else [g]):
        if gg.is_empty: continue
        q=np.array(gg.exterior.coords); ax.fill(q[:,0],q[:,1],**k)
fig,axs=plt.subplots(1,2,figsize=(20,10))
ax=axs[0]; p=poses[0]
# arm swept, shown in rocker-at-droop frame (everything the arm passes through)
fillg(ax,W(arm_sw,p),color='#9aa4ad',alpha=.45,lw=0)
fillg(ax,W(shk_sw,p),color='#3b6ea8',alpha=.18,lw=0)
fillg(ax,W(body,p),color='#e07a2e',alpha=.45,lw=0)
fillg(ax,W(jp,p),facecolor='none',edgecolor='k',lw=2.2)
fillg(ax,W(inter,p),color='red',alpha=.8,lw=0)
for c in [(0,0),tuple(Dl),tuple(Sl)]:
    q=np.array(W(Point(*c).buffer(5.2),p).exterior.coords); ax.fill(q[:,0],q[:,1],color='white',ec='k')
ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlim(-200,10); ax.set_ylim(-150,40)
ax.set_title('Right side, full droop. Black line: your sketch. Orange: my v2.\nGrey: everywhere the arm goes over the full travel. Blue: shock body (guess). Red: your sketch inside the arm\'s path')
ax=axs[1]
for p,col,lab in ((poses[0],'#2e7d32','droop'),(min(poses,key=lambda q:abs(q['th']+13.7*D2R)),'#f9a825','sag'),(poses[-1],'#c62828','bump')):
    a=unary_union([affinity.rotate(x,p['th'],origin=(0,0),use_radians=True) for x in arm_band]); a=affinity.scale(a,-1,1,origin=(0,0))
    fillg(ax,a,facecolor='none',edgecolor=col,lw=1.5,ls='--')
    rk=affinity.scale(affinity.translate(affinity.rotate(jp,p['rang'],origin=(0,0),use_radians=True),*p['R']),-1,1,origin=(0,0))
    fillg(ax,rk,facecolor=col,alpha=.25,edgecolor=col,lw=1.5,label=lab)
    ax.plot([-p['D'][0],-p['lug'][0]],[p['D'][1],p['lug'][1]],color=col,lw=4)
ax.legend(); ax.plot(0,0,'k+',ms=14); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_xlim(-260,40); ax.set_ylim(-160,110)
ax.set_title('Your sketch on the bike, right side: droop / sag / bump.\nDashed: arm cross-member + lug at the same position')
plt.tight_layout(); plt.savefig('rocker-joel-sketch-overlay.png',dpi=75)
iS=jp.intersection(shk_sw); print('overlap with shock sweep mm2', round(iS.area,1), 'bounds', [round(v) for v in iS.bounds] if not iS.is_empty else None)
pts=np.array([c for g in (iS.geoms if hasattr(iS,'geoms') else [iS]) for c in g.exterior.coords]) if not iS.is_empty else []
if len(pts): print('depth', round(max(Point(*q).distance(jp.exterior) for q in pts),1), 'dist from S', round(min(np.hypot(*(q-Sl)) for q in pts),1))
# which poses
for p in poses[::20]:
    rk=affinity.translate(affinity.rotate(jp,p['rang'],origin=(0,0),use_radians=True),*p['R'])
    print(round(p['th']/D2R,1), round(rk.distance(shock_end(p)),1))
p=poses[0]; F=W(shk_sw.buffer(3,64),p); Sw=np.array(W(Point(*Sl),p).coords[0])
from shapely.geometry import LineString
for dx in range(0,90,5):
    x=Sw[0]+dx; v=LineString([(x,-60),(x,120)]).intersection(F)
    jt=LineString([(x,-60),(x,120)]).intersection(W(jp,p))
    ylow=v.bounds[1] if not v.is_empty else None; jtop=jt.bounds[3] if not jt.is_empty else None
    print(dx, 'shock (3mm clear) starts at y', None if ylow is None else round(ylow-Sw[1],1), ' your top edge', None if jtop is None else round(jtop-Sw[1],1), '(relative to shock bolt centre)')
