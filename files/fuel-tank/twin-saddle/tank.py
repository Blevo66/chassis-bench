"""Twin half-saddle tank for the XL125R, faceted fold-up steel.
Frame coords as the Fusion scan: mm, origin swingarm pivot, X fwd, Y left, Z up."""
import numpy as np, trimesh, json, sys

P = dict(
  spine_y=6.0,        # spine centreline (scan)
  inner_gap=37.0,     # inner wall distance from spine centre (spine ~28 half width + rubber)
  top_slope=0.18,     # top facet falls this much per mm outward
  x_front=345.0, x_rear=20.0,
  front=dict(zt=560., yo=160., zb=315., c=34., c2=55., k=35.),
  rear =dict(zt=460., yo=118., zb=340., c=26., c2=22., k=50.),
)

def section(s, P):
    yi=P['inner_gap']; t=P['top_slope']
    zt,yo,zb,c,c2=s['zt'],s['yo'],s['zb'],s['c'],s['c2']
    yB=yo-c; zB=zt-t*(yB-yi)
    zC=zB-c                      # 45 deg shoulder
    zD=zb+c2; yE=yo-c2           # 45 deg lower chamfer
    # A inner-top, B top-outer, C shoulder-low, D outer-low, E bottom-outer, F inner-bottom
    k=s.get('k',0.)
    assert yi+k < yo-c2-5, 'inner chamfer runs into the lower outer chamfer'              # 45 deg inner-bottom chamfer (clears seat-rail fork / carb)
    return np.array([[yi,zt],[yB,zB],[yo,zC],[yo,zD],[yE,zb],[yi+k,zb],[yi,zb+k]])

NAMES=['A inner top','B top outer','C shoulder','D side low','E bottom outer','F bottom inner','G inner wall low']

def half_points(P, side=+1):
    pts=[]
    for x,key in ((P['x_front'],'front'),(P['x_rear'],'rear')):
        S=section(P[key],P)
        for y,z in S: pts.append([x, P['spine_y']+side*y, z])
    return np.array(pts)   # 0..6 front, 7..13 rear

def half_mesh(P, side=+1):
    return trimesh.convex.convex_hull(half_points(P,side))

if __name__=='__main__':
    for sd in (+1,-1):
        m=half_mesh(P,sd); print('side',sd,'vol L %.2f'%(m.volume/1e6), 'faces',len(m.facets))
    print(section(P['front'],P)); print(section(P['rear'],P))
