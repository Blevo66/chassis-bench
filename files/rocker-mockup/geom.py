# Rocker B, 82 dogbone on the XR tab of the Chassis Bench, re-solved in Python (same maths as index.html pose()).
import math, re, json
D2R = math.pi/180
def rot(p,a): c,s=math.cos(a),math.sin(a); return (p[0]*c-p[1]*s, p[0]*s+p[1]*c)
def dist(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])
def circles(c0,r0,c1,r1):
    d=dist(c0,c1)
    if d<1e-9 or d>r0+r1 or d<abs(r0-r1): return None
    a=(r0*r0-r1*r1+d*d)/(2*d); h=math.sqrt(max(0,r0*r0-a*a))
    ex,ey=(c1[0]-c0[0])/d,(c1[1]-c0[1])/d; m=(c0[0]+a*ex,c0[1]+a*ey)
    return [(m[0]-h*ey,m[1]+h*ex),(m[0]+h*ey,m[1]-h*ex)]
G = dict(armLen=580, armAngle=21.9, lug=(200,-50), R=(22,-29), shockTop=(-55,292), rD=111, rS=152.7, incl=65, dog=82, eye=380, stroke=95)
ARM_SHIFT=(4,1)
src=open('/tmp/claude-0/-home-claude-chassis-bench/4906d7fa-0700-5129-88f1-c51707ec55ce/scratchpad/yj.html').read()
m=re.search(r"const CRF250_ARM = (\{.*?\});", src).group(1)
m=re.sub(r"(\w+):", r'"\1":', m)
ARM=json.loads(m)
def pose(th, prevD=None, g=G):
    R=g['R']; other=rot(g['lug'],th)
    s=circles(R,g['rD'],other,g['dog'])
    if not s: return None
    D = (min(s,key=lambda q:dist(q,prevD)) if prevD else s[1])
    ang=math.atan2(D[1]-R[1],D[0]-R[0])+g['incl']*D2R
    S=(R[0]+g['rS']*math.cos(ang),R[1]+g['rS']*math.sin(ang))
    return dict(th=th,R=R,D=D,S=S,lug=other,L=dist(S,g['shockTop']),rang=math.atan2(D[1]-R[1],D[0]-R[0]))
def sweep(g=G):
    """Full droop (shock at its eye to eye) to full bump (eye - stroke), in 0.05 deg steps."""
    th0=-g['armAngle']*D2R; p0=pose(th0,None,g); th=th0; prev=p0['D']; down=[]
    while p0['L']<g['eye']:                     # arm hangs lower than the measured angle until the shock tops out
        th-=0.05*D2R; p=pose(th,prev,g); prev=p['D']; down.insert(0,p)
        if p['L']>=g['eye']: break
    out=down+[p0]; prev=p0['D']; th=th0
    while True:
        th+=0.05*D2R; p=pose(th,prev,g)
        if not p: break
        prev=p['D']; out.append(p)
        if p['L']<=g['eye']-g['stroke']: break
    return out
def arm_world(poly, th): return [rot((q[0]+ARM_SHIFT[0],q[1]+ARM_SHIFT[1]),th) for q in poly]
if __name__=='__main__':
    P=sweep(); a,b=P[0],P[-1]
    print('droop L',round(a['L'],1),'bump L',round(b['L'],1),'arm deg',round(a['th']/D2R,1),round(b['th']/D2R,1))
    print('travel', round(dist(rot((580,0),a['th']),rot((580,0),b['th'])),1), 'vertical', round(rot((580,0),b['th'])[1]-rot((580,0),a['th'])[1],1))
    print('rocker rotates', round((b['rang']-a['rang'])/D2R,1))
    for p in (a,b): print({k:tuple(round(x,1) for x in v) if isinstance(v,tuple) else round(v,3) for k,v in p.items()})
