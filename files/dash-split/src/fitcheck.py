# Clearance between the brain box (outer cuboid) and the clean frame model, in box-local coords.
import numpy as np, struct, math, sys
F=sys.argv[1]
b=open(F,'rb').read(); n=struct.unpack('<I',b[80:84])[0]
P=np.frombuffer(b[84:84+50*n],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))['v'].reshape(-1,3).astype(float)
A=math.radians(15.2); Y0F,Z0F,XOFF=144.0,-75.5,float(sys.argv[2]) if len(sys.argv)>2 else -5.0
L,Y0,Y1,H=(105.0,-50.0,60.0,40.0) if len(sys.argv)<4 else tuple(map(float,sys.argv[3].split(",")))
u=P[:,1]-Y0F; v=P[:,2]-Z0F
x=u*math.cos(A)+v*math.sin(A); z=-u*math.sin(A)+v*math.cos(A); y=P[:,0]-XOFF
dx=np.maximum(np.maximum(0-x,x-L),0); dy=np.maximum(np.maximum(Y0-y,y-Y1),0); dz=np.maximum(np.maximum(0-z,z-H),0)
d=np.sqrt(dx*dx+dy*dy+dz*dz)
inside=(dx==0)&(dy==0)&(dz==0)
print('frame points inside box:',int(inside.sum()))
i=np.argsort(d)[:5]
for k in i: print('clearance %.1f at box-local x %.1f y %.1f z %.1f  (frame X %.1f Y %.1f Z %.1f)'%(d[k],x[k],y[k],z[k],*P[k]))
for side,mask in (('under (z<0)',z<0),('over (z>H)',z>H),('front (x<0)',x<0)):
    m=mask&(dy==0)&(((x>=0)&(x<=L))|(side.startswith('front')))
    if m.any(): print(side,'min %.1f'%d[m].min())
