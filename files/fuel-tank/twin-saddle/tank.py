"""Twin half-saddle tank for the XL125R, Kove-rally style deep side pods, faceted fold-up steel.
Frame coords as the Fusion scan: mm, origin swingarm pivot, X fwd, Y left, Z up.
Section (left half, looking forward), all edge directions fixed so front/rear edges stay parallel
(every face planar, so the patterns unfold exactly):
 A inner top -> B top outer (top falls outward) -> C (45 shoulder) -> D (vertical outer side)
 -> E (45 lower outer chamfer) -> F bottom inner -> H (vertical lower inner wall, clear of engine)
 -> I (45 slope up-inward over the head) -> back up the vertical upper inner wall (against the spine) to A."""
import numpy as np, trimesh

P = dict(
  spine_y=6.0,        # spine centreline in the scan
  inner_gap=37.0,     # upper inner wall, from spine centre
  top_slope=0.18,     # top facet falls this much per mm outward
  x_front=345.0, x_rear=20.0,
  # zt top, yo outer, zb bottom, c shoulder, c2 lower outer chamfer, yl lower inner wall (engine), k inner chamfer, zs top of lower inner wall
  front=dict(zt=560., yo=175., zb=230., c=40., c2=30., yl=120., k=0., zs=320.),
  rear =dict(zt=460., yo=118., zb=340., c=26., c2=22., yl=86., k=0., zs=350.),
)

def section(s, P):
    yi=P['inner_gap']; t=P['top_slope']
    zt,yo,zb,c,c2,yl,k,zs=(s[q] for q in ('zt','yo','zb','c','c2','yl','k','zs'))
    yB=yo-c; zB=zt-t*(yB-yi); zC=zB-c
    zD=zb+c2; yE=yo-c2
    zI=zs+(yl-yi)            # 45 deg slope from lower wall top in to the upper wall
    pts=[[yi,zt],[yB,zB],[yo,zC],[yo,zD],[yE,zb],[yl,zb],[yl,zs],[yi,zI]]
    # sanity: no negative or tiny edge lengths
    assert yB>yi+5 and zC>zD+5 and yE>yl+5 and zs>zb+5 and zt>zI+5, (s, pts)
    return np.array(pts,float)

NAMES=['A inner top','B top outer','C shoulder','D side low','E bottom outer','F bottom inner','H lower wall top','I spine wall bottom']

def sections3(P, side=+1, xf=None, xr=None):
    xf=P['x_front'] if xf is None else xf; xr=P['x_rear'] if xr is None else xr
    out=[]
    for x,key in ((xf,'front'),(xr,'rear')):
        S=section(P[key],P); out.append(np.array([[x,P['spine_y']+side*y,z] for y,z in S]))
    return out

def half_mesh(P, side=+1):
    F,R=sections3(P,side); n=len(F)
    V=np.vstack([F,R]); faces=[]
    for i in range(n):
        j=(i+1)%n
        faces+= [[i,j,n+j],[i,n+j,n+i]]
    # caps
    for off,S in ((0,F),(n,R)):
        tri=trimesh.creation.triangulate_polygon(__import__('shapely.geometry',fromlist=['Polygon']).Polygon(S[:,1:]),engine='earcut')[1]
        # map tri vertices back to section indices
        V2=trimesh.creation.triangulate_polygon(__import__('shapely.geometry',fromlist=['Polygon']).Polygon(S[:,1:]),engine='earcut')[0]
        idx=[int(np.argmin(np.linalg.norm(S[:,1:]-v,axis=1))) for v in V2]
        for t in tri: faces.append([off+idx[t[0]],off+idx[t[1]],off+idx[t[2]]])
    m=trimesh.Trimesh(V,faces,process=True)
    m.merge_vertices(); trimesh.repair.fix_normals(m); trimesh.repair.fix_winding(m)
    return m

if __name__=='__main__':
    for sd in (1,-1):
        m=half_mesh(P,sd); print(sd,'L %.2f'%(m.volume/1e6),'watertight',m.is_watertight)
