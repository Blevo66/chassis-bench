import json,numpy as np,cadquery as cq,trimesh
from scipy.interpolate import splprep,splev
from scipy.ndimage import median_filter
V=lambda p:cq.Vector(*map(float,p))
F=json.load(open('forkaxes.json')); H=json.load(open('headaxis.json')); R2=json.load(open('refine2.json')); HB=json.load(open('headbox.json'))
v=np.array(H['v']); cH=np.array(H['c'])
L=np.array(F['L']['pt']); Rr=np.array(F['R']['pt'])
# ---- bike-aligned frame ----
lr=Rr-L; ex=lr-(lr@v)*v-((Rr-L)@np.zeros(3)); ex=lr-(lr@v)*v; ex/=np.linalg.norm(ex)
ez=np.array([0,0,1.0]); ez=ez-(ez@ex)*ex; ez/=np.linalg.norm(ez); ey=np.cross(ez,ex)
Rm=np.vstack([ex,ey,ez])
old_c0=np.array([-11.0,74.8,166.7]); old_d=np.array([-0.0445,0.4247,0.9043]); old_d/=np.linalg.norm(old_d)
def onaxis(p): return cH+((p-cH)@v)*v
HT_BOT_s=onaxis(old_c0-142*old_d); HT_TOP_s=onaxis(old_c0+19*old_d)
O=HT_BOT_s
T=lambda p:(np.atleast_2d(p)-O)@Rm.T
M=np.eye(4); M[:3,:3]=Rm; M[:3,3]=-Rm@O
json.dump(dict(scan_to_bike=M.tolist()),open('cad/transform.json','w'))
vb=Rm@v; HT_LEN=float(np.linalg.norm(HT_TOP_s-HT_BOT_s))
print('steering axis in bike frame',np.round(vb,4),'rake to Z',round(np.degrees(np.arccos(vb[2])),2),'HT len',round(HT_LEN,1))
ax=lambda h: h*vb  # origin at head-tube bottom on axis
def frame(t):
  t=t/np.linalg.norm(t); X=np.array([1.,0,0]); lat=X-(X@t)*t; lat/=np.linalg.norm(lat); return t,lat
def loft(P,Tg,W,Hh):
  wires=[]
  for p,t,w,h in zip(P,Tg,W,Hh):
    t,lat=frame(t); up=np.cross(t,lat)
    if abs(w-h)<0.3: wires.append(cq.Wire.makeCircle((w+h)/4,V(p),V(t)))
    else:
      a,b=max(w,h)/2,min(w,h)/2; maj=up if h>=w else lat
      wires.append(cq.Wire.makeEllipse(a,b,V(p),V(t),V(maj)))
  return cq.Solid.makeLoft(wires,False)
def tube_from(rows,sel,pre=(),post=(),n=None,s=1.0,size_override=None,step=14):
  rr=[r for r in rows if sel(np.array(r['c']))]
  C=T(np.array([r['c'] for r in rr])); W=np.array([r['dmin'] for r in rr]); Hh=np.array([r['dmaj'] for r in rr])
  if len(pre) and np.linalg.norm(C[-1]-np.atleast_2d(pre[-1])[0])<np.linalg.norm(C[0]-np.atleast_2d(pre[-1])[0]): C,W,Hh=C[::-1],W[::-1],Hh[::-1]
  W=median_filter(W,5,mode='nearest'); Hh=median_filter(Hh,5,mode='nearest')
  pts=np.vstack([*(np.atleast_2d(p) for p in pre),C,*(np.atleast_2d(p) for p in post)])
  w=np.r_[[W[0]]*len(pre),W,[W[-1]]*len(post)]; h=np.r_[[Hh[0]]*len(pre),Hh,[Hh[-1]]*len(post)]
  if size_override: w,h=size_override(pts,w,h)
  Ls=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))]
  tck,_=splprep(pts.T,u=Ls/Ls[-1],s=len(pts)*s,k=3)
  n=n or max(6,int(Ls[-1]/step)); u=np.linspace(0,1,n)
  P=np.array(splev(u,tck)).T; Tg=np.array(splev(u,tck,der=1)).T
  wi=np.interp(u,Ls/Ls[-1],w); hi=np.interp(u,Ls/Ls[-1],h)
  return loft(P,Tg,wi,hi),P,wi,hi
parts={}; info={}
HT_OD=50.0
parts['head_tube']=cq.Solid.makeCylinder(HT_OD/2,HT_LEN,V(ax(0)),V(vb))
# backbone: clean 180-300 + rear 425-465 (scan y), front extended into head tube; brace-merge zone bridged
bb=R2['backbone']
def bsel(c): return (180<c[1]<300)
def bbsize(P,w,h):
  return w,h
parts['backbone'],P,wi,hi=tube_from(bb,bsel,pre=[ax(110)+np.array([0,0,0]),T(np.array([-14.5,165,82]))[0]],post=[T(np.array([-24,345,2]))[0]],s=2.0)
info['backbone']=(np.round(wi[[1,len(wi)//3,-2]],1).tolist(),np.round(hi[[1,len(hi)//3,-2]],1).tolist())
# downtube
dt=R2['downtube']
parts['downtube'],P,wi,hi=tube_from(dt,lambda c:(-325<c[2]<-90),pre=[ax(40),T(np.array([-10,105,-20]))[0]],s=1.0,
   size_override=lambda P,w,h:(np.where(P[:,2]>T(np.array([0,0,-90]))[0][2],31.4,w),np.where(P[:,2]>T(np.array([0,0,-90]))[0][2],32.0,h)))
info['downtube']=(np.round(wi[[2,len(wi)//2,-1]],1).tolist(),np.round(hi[[2,len(hi)//2,-1]],1).tolist())
# brace
br=R2['brace']
parts['brace'],P,wi,hi=tube_from(br,lambda c:(160<c[1]<292),pre=[T(np.array([-11,128,-62]))[0]],post=[T(np.array([-23,330,4]))[0]],s=1.0)
info['brace']=(np.round(np.median(wi),1),np.round(np.median(hi),1))
# rear rails (as scanned)
parts['rear_tube_right'],P,wi,hi=tube_from(R2['rearA'],lambda c:(c[1]>414),pre=[T(np.array([-5,405,-42]))[0]],s=0.6)
info['rear_tube_right']=(np.round(np.median(wi),1),np.round(np.median(hi),1))
parts['rear_tube_left'],P,wi,hi=tube_from(R2['rearB'],lambda c:(c[1]>399 and c[2]>-170),pre=[T(np.array([-30,398,-30]))[0]],s=0.6)
info['rear_tube_left']=(np.round(np.median(wi),1),np.round(np.median(hi),1))
# head gusset + rear junction: ruled lofts through the scan's own cross-sections
SL=json.load(open('slices.json'))
def slloft(S):
  ws=[cq.Wire.makePolygon([V(p) for p in T(np.array(x['pts']))],close=True) for x in S]
  return cq.Solid.makeLoft(ws,True)
parts['head_gusset']=slloft(SL['head'])
parts['rear_junction']=slloft(SL['rear'])
# tank bosses: measured centre (scan) y~117.8 z~60, Ø27 (scan), tips x=-52.1 / +29.0
for side,tipx,inx in (('L',-52.1,-30.0),('R',29.0,10.0)):
  a=T(np.array([inx,117.8,60.0]))[0]; b=T(np.array([tipx,117.8,60.0]))[0]
  parts['tank_boss_'+side]=cq.Solid.makeCylinder(13.5,float(np.linalg.norm(b-a)),V(a),V((b-a)/np.linalg.norm(b-a)))
frame_body=None
for k,s_ in parts.items(): frame_body=s_ if frame_body is None else frame_body.fuse(s_)
frame_body=frame_body.clean()
bore=cq.Solid.makeCylinder(20,HT_LEN+2,V(ax(-1)),V(vb))
for h0 in (-1,HT_LEN-14): bore=bore.fuse(cq.Solid.makeCylinder(23.5,15,V(ax(h0)),V(vb)))
frame_body=frame_body.cut(bore)
# forks (reference bodies), Ø43 stanchions on scanned axes, bottom of bottom yoke to top of top yoke
forks={}
for k in 'LR':
  p=T(np.array(F[k]['pt']))[0]; dv=Rm@np.array(F[k]['dir'])
  # span: bottom-yoke bottom (h~-175 old) to top-yoke top (h~+60 old) measured along steering axis
  hb=(T(onaxis(old_c0-178*old_d))[0])@vb; ht=(T(onaxis(old_c0+62*old_d))[0])@vb
  t0=(hb-p@vb)/(dv@vb); t1=(ht-p@vb)/(dv@vb)
  forks['fork_tube_'+k]=cq.Solid.makeCylinder(21.5,float(t1-t0),V(p+t0*dv),V(dv))
axis_ref=cq.Solid.makeCylinder(1.0,400,V(ax(-180)),V(vb))
asm=cq.Assembly(name='xl125r_frame')
asm.add(frame_body,name='frame',color=cq.Color(0.2,0.3,0.7))
for k,s_ in forks.items(): asm.add(s_,name=k,color=cq.Color(0.7,0.7,0.7))
asm.add(axis_ref,name='steering_axis_ref',color=cq.Color(1,0,0))
asm.save('cad/xl125r-frame-clean.step')
cq.exporters.export(cq.Workplane().add(frame_body),'cad/xl125r-frame-clean.stl',tolerance=0.1,angularTolerance=0.1)
allb=frame_body
for s_ in forks.values(): allb=allb.fuse(s_)
cq.exporters.export(cq.Workplane().add(allb),'cad/xl125r-frame-with-forks.stl',tolerance=0.1,angularTolerance=0.1)
# aligned copy of the scan for overlay
sc=trimesh.load('fill2.stl'); sc.apply_transform(M); sc.export('cad/frame-scan-watertight-bike-aligned.stl')
print('valid',frame_body.isValid(),'vol',round(frame_body.Volume()))
for k,vv in info.items(): print(k,vv)
for k,s_ in parts.items():
  bb=s_.BoundingBox(); print(k,s_.isValid(),round(s_.Volume()),[round(x) for x in (bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax)])
print(type(frame_body),len(frame_body.Solids()))
