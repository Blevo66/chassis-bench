"""2D topology optimisation of the rocker side profile (SIMP, after Andreassen et al. 'top88'), in Joel's sketch outline.
Design space = Joel's Fusion sketch minus everything the arm and shock sweep through (+ clearance). Bosses are kept solid.
Pivot bolt fixed; loads at the dogbone and shock bolts from the linkage at full bump and at sag (two load cases).
Run: python3 topopt.py   (numpy, scipy, shapely, scikit-image, matplotlib, manifold3d, trimesh)"""
import math, json, time
import numpy as np, scipy.sparse as sp
from scipy.sparse.linalg import factorized
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity, vectorized
import design as DS                      # reuses the sweep, keep-outs and bosses (also rebuilds the v2 files)
from geom import G, sweep, rot, D2R

H = 0.8           # element size, mm
VOLFRAC = 0.42    # fraction of the design space kept
PENAL, RMIN = 3.0, 2.2   # SIMP penalty, filter radius (mm)
ITERS = 90
RING = 6.0        # solid wall kept round each hole (mm)
CLEAR, CLEAR_SHK = 5.0, 3.0
# --- design space
sketch = Polygon(json.load(open('joel-sketch-outline-rocker-coords.json'))['outline']).buffer(0)
keep_out = unary_union([DS.arm_sw.buffer(CLEAR, 64), DS.shk_sw.buffer(CLEAR_SHK, 64)])
Rh, Dh, Sh = (0.0, 0.0), tuple(DS.Dl), tuple(DS.Sl)
HR = DS.HOLE/2
bosses = unary_union([Point(*c).buffer(HR + RING, 64) for c in (Rh, Dh, Sh)])
space = unary_union([sketch.difference(keep_out), bosses])
if space.geom_type != 'Polygon': space = max(space.geoms, key=lambda g: g.area)
minx, miny, maxx, maxy = space.bounds
minx -= 2; miny -= 2
nelx, nely = int((maxx - minx)/H) + 3, int((maxy - miny)/H) + 3
xc = minx + (np.arange(nelx) + .5)*H; yc = miny + (np.arange(nely) + .5)*H
X, Y = np.meshgrid(xc, yc, indexing='ij')                   # element centres, [ix, iy]
inside = vectorized.contains(space, X, Y)
solid = vectorized.contains(bosses, X, Y)
holes = np.zeros_like(inside)
for c in (Rh, Dh, Sh): holes |= (X - c[0])**2 + (Y - c[1])**2 < HR**2
bolt = holes.copy()                                          # bolts modelled as stiff solid in the holes
active = inside & ~solid & ~holes
print(f'grid {nelx} x {nely}, design elements {active.sum()}')
# --- loads (rocker coords) for each case, from the linkage
P = sweep(); y0 = rot((580, 0), P[0]['th'])[1]
def pick(w): return min(P, key=lambda q: abs(rot((580, 0), q['th'])[1] - y0 - w))
def cr(a, b): return a[0]*b[1] - a[1]*b[0]
cases = []
for name, w, Fs in (('bump', 267, 10600.0), ('sag', 100, None)):
    p = pick(w); R = np.array(p['R']); S = np.array(p['S']); D = np.array(p['D']); T = np.array(G['shockTop']); L = np.array(p['lug'])
    Fsv = -(T - S)/np.linalg.norm(T - S)*(Fs or 108*((G['eye'] - p['L']) + 3))
    ud = (L - D)/np.linalg.norm(L - D); Fd = -cr(S - R, Fsv)/cr(D - R, ud); Fdv = Fd*ud
    to_rk = lambda v: np.array(rot(v, -p['rang']))
    cases.append((name, to_rk(Fsv), to_rk(Fdv)))
    print(name, 'shock', to_rk(Fsv).round(0), 'dogbone', to_rk(Fdv).round(0))
# --- FE (bilinear quads, plane stress, unit thickness; E scaled)
E0, Emin, nu = 1.0, 1e-9, 0.3
A11 = np.array([[12, 3, -6, -3], [3, 12, 3, 0], [-6, 3, 12, -3], [-3, 0, -3, 12]])
A12 = np.array([[-6, -3, 0, 3], [-3, -6, -3, -6], [0, -3, -6, 3], [3, -6, 3, -6]])
B11 = np.array([[-4, 3, -2, 9], [3, -4, -9, 4], [-2, -9, -4, -3], [9, 4, -3, -4]])
B12 = np.array([[2, -3, 4, -9], [-3, 2, 9, -2], [4, 9, 2, 3], [-9, -2, 3, 2]])
KE = 1/(1 - nu**2)/24*(np.block([[A11, A12], [A12.T, A11]]) + nu*np.block([[B11, B12], [B12.T, B11]]))
# node numbering: node (i, j) -> i*(nely+1) + j, i along x, j along y (y up)
nn = (nelx + 1)*(nely + 1); ndof = 2*nn
I, J = np.meshgrid(np.arange(nelx), np.arange(nely), indexing='ij')
n1 = (I*(nely + 1) + J).ravel(); n2 = ((I + 1)*(nely + 1) + J).ravel()
# element nodes counter-clockwise from bottom-left: (i,j), (i+1,j), (i+1,j+1), (i,j+1); top88 ordering adapted
nodes = np.c_[n1, n2, n2 + 1, n1 + 1]
edof = np.c_[2*nodes[:, 0], 2*nodes[:, 0] + 1, 2*nodes[:, 1], 2*nodes[:, 1] + 1, 2*nodes[:, 2], 2*nodes[:, 2] + 1, 2*nodes[:, 3], 2*nodes[:, 3] + 1]
# KE above is for top88's node order (bl? it uses ul,ur,lr,ll with y down); rebuild a clean Q4 stiffness instead
def q4_ke(nu):
    C = 1/(1 - nu**2)*np.array([[1, nu, 0], [nu, 1, 0], [0, 0, (1 - nu)/2]])
    k = np.zeros((8, 8)); g = 1/math.sqrt(3)
    xy = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], float)
    for xi in (-g, g):
        for eta in (-g, g):
            dN = 0.25*np.array([[-(1 - eta), (1 - eta), (1 + eta), -(1 + eta)], [-(1 - xi), -(1 + xi), (1 + xi), (1 - xi)]])
            Jm = dN @ xy; dNx = np.linalg.solve(Jm, dN); B = np.zeros((3, 8))
            B[0, 0::2] = dNx[0]; B[1, 1::2] = dNx[1]; B[2, 0::2] = dNx[1]; B[2, 1::2] = dNx[0]
            k += B.T @ C @ B*np.linalg.det(Jm)
    return k
KE = q4_ke(nu)
iK = np.kron(edof, np.ones((8, 1), int)).ravel(); jK = np.kron(edof, np.ones((1, 8), int)).ravel()
# supports: every node inside the pivot hole fixed (pinned bolt)
NX, NY = np.meshgrid(minx + np.arange(nelx + 1)*H, miny + np.arange(nely + 1)*H, indexing='ij'); NX = NX.ravel(); NY = NY.ravel()
def nodes_in(c, r): return np.where((NX - c[0])**2 + (NY - c[1])**2 <= r**2)[0]
fixed = np.r_[2*nodes_in(Rh, HR), 2*nodes_in(Rh, HR) + 1]
free = np.setdiff1d(np.arange(ndof), fixed)
F = np.zeros((ndof, len(cases)))
for k, (_, fs, fd) in enumerate(cases):
    for c, f in ((Sh, fs), (Dh, fd)):
        nd = nodes_in(c, HR); F[2*nd, k] += f[0]/len(nd); F[2*nd + 1, k] += f[1]/len(nd)
# density filter
rr = int(math.ceil(RMIN/H)); rows, cols, vals = [], [], []
ex = np.arange(nelx*nely)
for di in range(-rr + 1, rr):
    for dj in range(-rr + 1, rr):
        w = RMIN/H - math.sqrt(di*di + dj*dj)
        if w <= 0: continue
        i2, j2 = I.ravel() + di, J.ravel() + dj; ok = (i2 >= 0) & (i2 < nelx) & (j2 >= 0) & (j2 < nely)
        rows.append(ex[ok]); cols.append((i2*nely + j2)[ok]); vals.append(np.full(ok.sum(), w))
Hf = sp.csr_matrix((np.concatenate(vals), (np.concatenate(rows), np.concatenate(cols))), shape=(nelx*nely, nelx*nely)); Hs = np.asarray(Hf.sum(1)).ravel()
act = active.ravel(); sol = (solid | bolt).ravel(); voidm = ~(act | sol)
x = np.where(act, VOLFRAC*inside.sum()/max(1, act.sum()), 0.0); x[sol] = 1.0
target = VOLFRAC*inside.sum() - (solid & ~holes).sum()        # material to place in the active area
xP = x.copy(); t0 = time.time(); hist = []
for it in range(ITERS):
    E = Emin + xP**PENAL*(E0 - Emin); E[bolt.ravel()] = 10.0       # bolts much stiffer
    K = sp.csr_matrix((np.kron(E, KE.ravel()), (iK, jK)), shape=(ndof, ndof)); K = (K + K.T)/2
    solve = factorized(K[free][:, free].tocsc())
    dc = np.zeros(nelx*nely); c = 0.0
    for k in range(F.shape[1]):
        U = np.zeros(ndof); U[free] = solve(F[free, k])
        ce = np.einsum('ij,jk,ik->i', U[edof], KE, U[edof])
        c += (E*ce).sum(); dc += -PENAL*xP**(PENAL - 1)*(E0 - Emin)*ce
    dc = np.asarray(Hf @ (dc/Hs)).ravel()
    l1, l2, move = 0.0, 1e12, 0.15
    while (l2 - l1)/(l1 + l2 + 1e-30) > 1e-4:
        lm = 0.5*(l1 + l2)
        xn = np.clip(x*np.sqrt(np.maximum(-dc, 0)/lm), np.maximum(0, x - move), np.minimum(1, x + move))
        xn[sol] = 1; xn[voidm] = 0
        xpn = np.asarray(Hf @ xn).ravel()/Hs; xpn[sol] = 1; xpn[voidm] = 0
        if xpn[act].sum() > target: l1 = lm
        else: l2 = lm
    ch = np.abs(xn - x).max(); x = xn; xP = xpn; hist.append(c)
    if it % 10 == 0 or it == ITERS - 1: print(f'it {it:3d}  compliance {c:.4g}  change {ch:.3f}  {time.time() - t0:.0f}s', flush=True)
np.save('topopt_density.npy', xP.reshape(nelx, nely))
json.dump({'minx': minx, 'miny': miny, 'H': H, 'nelx': nelx, 'nely': nely}, open('topopt_grid.json', 'w'))
