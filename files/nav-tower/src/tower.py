import numpy as np,trimesh,json,sys
from skimage.measure import marching_cubes
from scipy.spatial import cKDTree
exec(open('build_v1.py').read().split('parts={}')[0])
t0=66.5;CW_=4.5
S2C=lambda P:(lambda L:np.c_[-L[:,0],L[:,2]-t0,L[:,1]])(S2L(P))
C2S=lambda P:L2S(np.c_[-P[:,0],P[:,2],P[:,1]+t0])
LUG=[C2S(np.array([[0,y,-38.9]]))[0] for y in(12,108)]
AX=C2S(np.array([[1,0,0]]))[0]-C2S(np.array([[0,0,0]]))[0]  # lug bolt axis in scan
def smin(a,b,k):
  h=np.clip(0.5+0.5*(b-a)/k,0,1);return b*(1-h)+a*h-k*h*(1-h)
def smax(a,b,k): return -smin(-a,-b,k)
def capsule(P,a,b,r):
  a=np.asarray(a,float);b=np.asarray(b,float);pa=P-a;ba=b-a;h=np.clip((pa@ba)/(ba@ba),0,1);return np.linalg.norm(pa-np.outer(h,ba),axis=1)-r
def capsule_r(P,a,b,ra,rb):
  a=np.asarray(a,float);b=np.asarray(b,float);pa=P-a;ba=b-a;h=np.clip((pa@ba)/(ba@ba),0,1);return np.linalg.norm(pa-np.outer(h,ba),axis=1)-(ra+(rb-ra)*h)
def ellipsoid(P,c,r):
  q=(P-c)/r;k0=np.linalg.norm(q,axis=1);k1=np.linalg.norm(q/r,axis=1);return k0*(k0-1)/(k1+1e-9)
def cyl(P,a,b,r):  # capped cylinder
  a=np.asarray(a,float);b=np.asarray(b,float);ba=b-a;L=np.linalg.norm(ba);u=ba/L;pa=P-a;t=pa@u
  rad=np.linalg.norm(pa-np.outer(t,u),axis=1)-r;ax=np.abs(t-L/2)-L/2
  return np.minimum(np.maximum(rad,ax),0)+np.linalg.norm(np.c_[np.maximum(rad,0),np.maximum(ax,0)],axis=1)
def box_local(P,c,ex,ey,ez,h):  # oriented box, axes ex,ey,ez unit in scan
  q=P-c;q=np.c_[q@ex,q@ey,q@ez];d=np.abs(q)-h
  return np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(d.max(1),0)
# ---------------- design parameters (scan coords: X lat, -Y fwd, Z up) ----------------
HL_C=np.array([0,-150.,215.]); HL_R=70; HL_D=75          # 5" headlight: lens centre, rim R, depth (guess)
TAB_C=np.array([0,-55.,385.]); TAB_TILT=50                 # tablet centre, screen normal tilt above horizontal (faces rider)
DASH_C=np.array([0,-50.,318.]); DASH_TILT=20
def rbox(q,h,r):  # rounded box in given coords
  d=np.abs(q)-(h-r);return np.linalg.norm(np.maximum(d,0),axis=1)+np.minimum(d.max(1),0)-r
CW=CW_  # cheek thickness
HWY=np.arange(0,121,6.0);HWV=np.array([39.5,42.5,42.5,42.5,42.3,40.4,36.0,32.7,31.6,31.5,31.5,32.3,35.1,39.7,42.1,42.5,42.5,42.5,42.5,42.5,42.5])
ZFV=np.array([-38.9,-49.3,-50.9,-49.3,-42.7,-37.8,-35.7,-35.4,-35.4,-35.4,-35.4,-35.4,-35.4,-36.6,-39.7,-42.9,-46.1,-49.3,-50.9,-49.3,-38.9])
def mount_sdf(P):
  c=S2C(P);X,Y,Z=c[:,0],c[:,1],c[:,2]
  hw=np.interp(Y,HWY,HWV)+0.5
  lob=np.minimum(np.hypot(Y-12,Z+38.9),np.hypot(Y-108,Z+38.9))-12
  band=rbox(np.c_[Y-60,Z+35.5],np.array([50,8.5]),5)
  prof=np.maximum(np.minimum(lob,band),-(Z+46))
  plate=np.maximum(prof,np.abs(np.abs(X)-hw-CW/2)-CW/2)
  web=rbox(np.c_[X,Y-60,Z+40],np.array([40,30,3.5]),3.5)
  neck=rbox(np.c_[X,Y-60,Z+80],np.array([24,33,38]),12)
  d=smin(np.minimum(plate,web),neck,6)
  return d
def pod_sdf(P):
  pod=cyl(P,HL_C+[0,-6,0],HL_C+[0,HL_D+10,0],HL_R+12)-6
  brow=capsule_r(P,HL_C+[0,10,45],TAB_C+[0,-25,-5],60,64)
  d=smin(pod,brow,40)
  deck=ellipsoid(P,TAB_C+[0,-22,-26],np.array([90,58,46]))
  d=smin(d,deck,30)
  return d
def tower_sdf(P):
  m=mount_sdf(P);p=pod_sdf(P)
  d=smin(m,p,26)
  cl=S2C(P);X,Y,Z=cl[:,0],cl[:,1],cl[:,2]
  zf=np.interp(Y,HWY,ZFV)
  clampbox=np.maximum.reduce([np.abs(X)-np.interp(Y,HWY,HWV)-0.5,np.abs(Y-60)-60.5,zf-0.5-Z,Z+10.9])
  d=np.maximum(d,-clampbox)
  head=np.linalg.norm(S2L(P)[:,:2],axis=1)-31
  d=np.maximum(d,-head)
  d=np.maximum(d,-cyl(P,HL_C+[0,-30,0],HL_C+[0,12,0],HL_R-2))
  a=np.radians(TAB_TILT);n=np.array([0,np.cos(a),np.sin(a)]);up=np.array([0,-np.sin(a),np.cos(a)])
  d=np.maximum(d,-box_local(P,TAB_C+n*4,np.array([1.,0,0]),up,n,np.array([77,44,10])))
  a=np.radians(DASH_TILT);n2=np.array([0,np.cos(a),np.sin(a)]);up2=np.array([0,-np.sin(a),np.cos(a)])
  d=np.maximum(d,-box_local(P,DASH_C+n2*4,np.array([1.,0,0]),up2,n2,np.array([42,31,9])))
  for L in LUG: d=np.maximum(d,-cyl(P,L-AX*80,L+AX*80,5.5))
  return d
if __name__=='__main__':
  h=2.0;xs=np.arange(-140,141,h);ys=np.arange(-260,90,h);zs=np.arange(30,470,h)
  G=np.stack(np.meshgrid(xs,ys,zs,indexing='ij'),-1).reshape(-1,3)
  D=np.concatenate([tower_sdf(G[i:i+400000]) for i in range(0,len(G),400000)]).reshape(len(xs),len(ys),len(zs))
  v,f,_,_=marching_cubes(D,0,spacing=(h,h,h));v+=[xs[0],ys[0],zs[0]]
  m=trimesh.Trimesh(v,f);m=max(m.split(only_watertight=False),key=lambda x:len(x.faces))
  print('tower bbox',m.bounds.round(0),'watertight',m.is_watertight,'vol cm3',round(m.volume/1000))
  m.export('tower_plug.stl')
  sw=L2S(np.load('sw40.npy'));Pf=L2S(np.load('Pf.npy'))
  for nm,fn in(('mount',mount_sdf),('pod',pod_sdf)):
    bb=(sw[:,1]<110)&(sw[:,2]>10);Q=sw[bb];sd=np.concatenate([fn(Q[i:i+400000]) for i in range(0,len(Q),400000)]);j=sd.argmin();print(nm,'vs sweep %.1f'%sd[j],'clamp coords',S2C(Q[j:j+1])[0].round(0))
  for P,nm in((sw,'steer sweep 40'),(Pf,'frame')):
    bb=(P[:,0]>-160)&(P[:,0]<160)&(P[:,1]>-280)&(P[:,1]<110)&(P[:,2]>10)&(P[:,2]<490);Q=P[bb]
    sd=np.concatenate([tower_sdf(Q[i:i+400000]) for i in range(0,len(Q),400000)])
    j=sd.argmin();print(nm,'min clearance %.1f mm at scan'%sd[j],Q[j].round(0),'local',S2L(Q[j:j+1])[0].round(0))
  print('lugs scan',[l.round(1) for l in LUG],'axis',AX.round(3))
