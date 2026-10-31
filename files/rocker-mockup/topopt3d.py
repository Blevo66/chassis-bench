"""3D topology optimisation (SIMP, voxels) of Joel's Fusion rocker (joel-rocker-sketch.step, meshed to STL with gmsh).
Frame: Joel's sketch = right-side view at full droop, pivot hole at 0,0, x + = forwards, y up, z across the bike (part is z -15..15).
Half model (z >= 0) with a symmetry plane at z = 0. Keep-outs: everything the arm and shock sweep through, plus clearance.
Pivot hole fixed. Two load cases (full bump, sag) at the dogbone hole (both clevis ears) and the shock hole."""
import sys, math, json, time
import numpy as np, scipy.sparse as sp, pyamg, trimesh
from scipy.sparse.linalg import cg
from shapely.geometry import Point
from shapely.ops import unary_union
from shapely import affinity, contains_xy
import design as DS
from geom import G, sweep, rot

STL = sys.argv[1] if len(sys.argv) > 1 else 'joel_rocker.stl'
H = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
VOLFRAC, PENAL, RMIN, ITERS = float(sys.argv[4]) if len(sys.argv) > 4 else 0.30, 3.0, (float(sys.argv[5]) if len(sys.argv) > 5 else 1.6)*H, int(sys.argv[3]) if len(sys.argv) > 3 else 60
CLEAR, CLEAR_SHK, RING = 5.0, 3.0, 5.0
PIV, DOG, SHK = (0.0, 0.0), (-57.3, -93.9), (-151.7, 17.6)        # Joel's hole centres
HOLE_R = {PIV: 6.04, DOG: 5.09, SHK: 5.09}
p0 = DS.poses[0]
to_sk = lambda g: affinity.scale(affinity.rotate(g, p0['rang'], origin=(0, 0), use_radians=True), -1, 1, origin=(0, 0))
keep_out = to_sk(unary_union([DS.arm_sw.buffer(CLEAR, 64), DS.shk_sw.buffer(CLEAR_SHK, 64)]))
mesh = trimesh.load(STL)
lo, hi = mesh.bounds
nx, ny, nz = [int(math.ceil((hi[i] - lo[i])/H)) for i in range(2)] + [int(math.ceil(hi[2]/H))]
xc = lo[0] + (np.arange(nx) + .5)*H; yc = lo[1] + (np.arange(ny) + .5)*H; zc = (np.arange(nz) + .5)*H
X, Y, Z = np.meshgrid(xc, yc, zc, indexing='ij')
pts = np.c_[X.ravel(), Y.ravel(), Z.ravel()]
inside = mesh.contains(pts).reshape(X.shape)
# a voxel counts if its centre is inside Joel's solid
ko = contains_xy(keep_out, X, Y)
def near(c, r): return (X - c[0])**2 + (Y - c[1])**2 <= r**2
holes = near(PIV, HOLE_R[PIV]) | near(DOG, HOLE_R[DOG]) | near(SHK, HOLE_R[SHK])
rings = (near(PIV, HOLE_R[PIV] + RING) | near(DOG, HOLE_R[DOG] + RING) | near(SHK, HOLE_R[SHK] + RING)) & inside & ~holes
dom = inside & ~ko & ~holes | rings
bolt = holes & (inside | near(PIV, HOLE_R[PIV]) | near(SHK, HOLE_R[SHK])) & (np.abs(Z) < hi[2])
# the dogbone sits in the slot: only the ears carry its bolt
bolt &= ~(near(DOG, HOLE_R[DOG]) & ~inside)
print(f'grid {nx}x{ny}x{nz} (half), solid voxels {dom.sum()}, kept-out {(inside & ko).sum()}', flush=True)
# loads in the sketch frame
P = sweep(); y0 = rot((580, 0), P[0]['th'])[1]
def pick(w): return min(P, key=lambda q: abs(rot((580, 0), q['th'])[1] - y0 - w))
def cr(a, b): return a[0]*b[1] - a[1]*b[0]
cases = []
for name, w, Fs in (('bump', 267, 10600.0), ('sag', 100, None)):
    p = pick(w); R = np.array(p['R']); S = np.array(p['S']); D = np.array(p['D']); T = np.array(G['shockTop']); L = np.array(p['lug'])
    Fsv = -(T - S)/np.linalg.norm(T - S)*(Fs or 108*((G['eye'] - p['L']) + 3))
    ud = (L - D)/np.linalg.norm(L - D); Fd = -cr(S - R, Fsv)/cr(D - R, ud); Fdv = Fd*ud
    sk = lambda v: (lambda r: np.array([-r[0], r[1]]))(rot(rot(v, -p['rang']), p0['rang']))
    cases.append((name, sk(Fsv)/2, sk(Fdv)/2))      # half model carries half the load
    print(name, 'shock', sk(Fsv).round(0), 'dogbone', sk(Fdv).round(0), '(full part; the half model takes half)', flush=True)
# hex8 element stiffness (unit cube, E = 1, nu = 0.3)
def hex_ke(nu=0.3):
    lam, mu = nu/((1 + nu)*(1 - 2*nu)), 1/(2*(1 + nu))
    C = np.zeros((6, 6)); C[:3, :3] = lam; C[range(3), range(3)] += 2*mu; C[range(3, 6), range(3, 6)] = mu
    nodes = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]], float); s = nodes*2 - 1
    k = np.zeros((24, 24)); g = 1/math.sqrt(3)
    for a in (-g, g):
        for b in (-g, g):
            for c in (-g, g):
                dN = np.array([s[:, 0]*(1 + s[:, 1]*b)*(1 + s[:, 2]*c), s[:, 1]*(1 + s[:, 0]*a)*(1 + s[:, 2]*c), s[:, 2]*(1 + s[:, 0]*a)*(1 + s[:, 1]*b)])/8
                J = dN @ nodes; dNx = np.linalg.solve(J, dN); B = np.zeros((6, 24))
                B[0, 0::3] = dNx[0]; B[1, 1::3] = dNx[1]; B[2, 2::3] = dNx[2]
                B[3, 0::3] = dNx[1]; B[3, 1::3] = dNx[0]; B[4, 1::3] = dNx[2]; B[4, 2::3] = dNx[1]; B[5, 0::3] = dNx[2]; B[5, 2::3] = dNx[0]
                k += B.T @ C @ B*np.linalg.det(J)
    return k
KE = hex_ke()*H         # scale for element size (stiffness ~ E*h)
# elements = voxels in dom or bolt; nodes renumbered over those only
el = np.argwhere(dom | bolt); ne = len(el)
off = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]])
gid = lambda i, j, k: (i*(ny + 1) + j)*(nz + 1) + k
cn = np.stack([gid(el[:, 0] + o[0], el[:, 1] + o[1], el[:, 2] + o[2]) for o in off], 1)
uniq, inv = np.unique(cn, return_inverse=True); cn = inv.reshape(cn.shape); nn = len(uniq)
edof = np.repeat(3*cn, 3, axis=1) + np.tile([0, 1, 2], 8)
ii = uniq // ((ny + 1)*(nz + 1)); jj = (uniq // (nz + 1)) % (ny + 1); kk = uniq % (nz + 1)
NX, NY, NZ = lo[0] + ii*H, lo[1] + jj*H, kk*H
fixed = []
fixed += list(3*np.where(NZ == 0)[0] + 2)                                   # symmetry plane
pv = np.where((NX - PIV[0])**2 + (NY - PIV[1])**2 <= HOLE_R[PIV]**2)[0]; fixed += list(3*pv) + list(3*pv + 1) + list(3*pv + 2)
fixed = np.unique(fixed); ndof = 3*nn; free = np.setdiff1d(np.arange(ndof), fixed)
F = np.zeros((ndof, len(cases)))
for k, (_, fs, fd) in enumerate(cases):
    for c, f, zmin in ((SHK, fs, 0), (DOG, fd, 5.5)):
        nd = np.where(((NX - c[0])**2 + (NY - c[1])**2 <= HOLE_R[c]**2) & (NZ >= zmin))[0]
        F[3*nd, k] += f[0]/len(nd); F[3*nd + 1, k] += f[1]/len(nd)
iK = np.repeat(edof, 24, axis=1).ravel(); jK = np.tile(edof, (1, 24)).ravel()
# filter over the element list
from scipy.spatial import cKDTree
tr = cKDTree(el*H); pairs = tr.query_pairs(RMIN, output_type='ndarray')
dd = np.linalg.norm((el[pairs[:, 0]] - el[pairs[:, 1]])*H, axis=1)
w = RMIN - dd
Hf = sp.coo_matrix((np.r_[w, w, np.full(ne, RMIN)], (np.r_[pairs[:, 0], pairs[:, 1], np.arange(ne)], np.r_[pairs[:, 1], pairs[:, 0], np.arange(ne)])), shape=(ne, ne)).tocsr()
Hs = np.asarray(Hf.sum(1)).ravel()
isbolt = bolt[el[:, 0], el[:, 1], el[:, 2]]; isring = (rings & ~bolt)[el[:, 0], el[:, 1], el[:, 2]]
act = ~isbolt & ~isring; fixed_solid = isbolt | isring
x = np.where(act, VOLFRAC, 1.0); xP = x.copy()
target = VOLFRAC*act.sum()
Us = [None]*len(cases); t0 = time.time()
for it in range(ITERS):
    E = 1e-9 + xP**PENAL*(1 - 1e-9); E[isbolt] = 10.0
    K = sp.csr_matrix((np.kron(E, KE.ravel()), (iK, jK)), shape=(ndof, ndof)); Kf = K[free][:, free].tocsr()
    ml = pyamg.smoothed_aggregation_solver(Kf, B=None, max_coarse=2000) if it % 5 == 0 else ml
    dc = np.zeros(ne); c = 0.0
    for k in range(len(cases)):
        U = np.zeros(ndof)
        U[free], info = cg(Kf, F[free, k], x0=Us[k], rtol=1e-6, maxiter=400, M=ml.aspreconditioner())
        Us[k] = U[free]
        ce = np.einsum('ij,jk,ik->i', U[edof], KE, U[edof]); c += (E*ce).sum(); dc += -PENAL*xP**(PENAL - 1)*ce
    dc = Hf @ (dc/Hs)
    l1, l2, mv = 0.0, 1e12, 0.12
    while (l2 - l1)/(l1 + l2 + 1e-30) > 1e-4:
        lm = .5*(l1 + l2)
        xn = np.clip(x*np.sqrt(np.maximum(-dc, 0)/lm), np.maximum(0, x - mv), np.minimum(1, x + mv)); xn[fixed_solid] = 1
        xpn = (Hf @ xn)/Hs; xpn[fixed_solid] = 1
        if xpn[act].sum() > target: l1 = lm
        else: l2 = lm
    ch = np.abs(xn - x).max(); x, xP = xn, xpn
    print(f'it {it:3d} compliance {c:.4g} change {ch:.3f} {time.time() - t0:.0f}s', flush=True)
    if it > 20 and ch < 0.01: break
rho = np.zeros((nx, ny, nz)); rho[el[:, 0], el[:, 1], el[:, 2]] = xP
np.save('topopt3d_density.npy', rho); json.dump({'lo': lo.tolist(), 'H': H, 'shape': [nx, ny, nz]}, open('topopt3d_grid.json', 'w'))

# ---- stress check: final design thresholded at 0.5, steel, "massive jump" = JUMP x the full-bump load
JUMP = float(sys.argv[6]) if len(sys.argv) > 6 else 3.0
Es = 200e3                                    # MPa (N/mm2); KE was built for E = 1 and scaled by H
solidm = (xP > 0.5) | isbolt
E2 = np.where(solidm, 1.0, 1e-6); E2[isbolt] = 10.0
K = sp.csr_matrix((np.kron(E2*Es, KE.ravel()), (iK, jK)), shape=(ndof, ndof)); Kf = K[free][:, free].tocsr()
ml = pyamg.smoothed_aggregation_solver(Kf, max_coarse=2000)
nu = 0.3; lam, mu = nu/((1 + nu)*(1 - 2*nu)), 1/(2*(1 + nu))
Cm = np.zeros((6, 6)); Cm[:3, :3] = lam; Cm[range(3), range(3)] += 2*mu; Cm[range(3, 6), range(3, 6)] = mu
dN = np.array([[-1,1,1,-1,-1,1,1,-1],[-1,-1,1,1,-1,-1,1,1],[-1,-1,-1,-1,1,1,1,1]])/4/H   # centre of the cube
B = np.zeros((6, 24)); B[0, 0::3] = dN[0]; B[1, 1::3] = dN[1]; B[2, 2::3] = dN[2]
B[3, 0::3] = dN[1]; B[3, 1::3] = dN[0]; B[4, 1::3] = dN[2]; B[4, 2::3] = dN[1]; B[5, 0::3] = dN[2]; B[5, 2::3] = dN[0]
U = np.zeros(ndof); U[free], info = cg(Kf, JUMP*F[free, 0], rtol=1e-8, maxiter=2000, M=ml.aspreconditioner())
sg = (Es*(Cm @ B @ U[edof].T)).T
vm = np.sqrt(0.5*((sg[:, 0]-sg[:, 1])**2 + (sg[:, 1]-sg[:, 2])**2 + (sg[:, 2]-sg[:, 0])**2) + 3*(sg[:, 3]**2 + sg[:, 4]**2 + sg[:, 5]**2))
body = solidm & ~isbolt
v = vm[body]
print(f'STRESS at {JUMP:.0f}x full bump: max {v.max():.0f} MPa, 99.5% {np.percentile(v, 99.5):.0f}, 99% {np.percentile(v, 99):.0f}, 95% {np.percentile(v, 95):.0f}  (solid frac {body.sum()/act.sum():.2f})', flush=True)
np.save('topopt3d_vm.npy', np.c_[el, vm])
