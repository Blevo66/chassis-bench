import trimesh, numpy as np, scipy.sparse as sp, pyamg, sys, time, json
h = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
m = max(trimesh.load('clamp_v2.stl').split(only_watertight=False), key=lambda p: len(p.faces))
lo, hi = m.bounds
nx, ny, nz = np.ceil((hi - lo) / h).astype(int)
xc = lo[0] + h * (np.arange(nx) + .5); yc = lo[1] + h * (np.arange(ny) + .5); zc = lo[2] + h * (np.arange(nz) + .5)
G = np.stack(np.meshgrid(xc, yc, zc, indexing='ij'), -1).reshape(-1, 3)
t = time.time(); inside = m.contains(G); print('vox', inside.sum(), time.time() - t)
I = np.argwhere(inside.reshape(nx, ny, nz))
cen = G[inside]
# nodes
nid = -np.ones((nx + 1, ny + 1, nz + 1), int)
off = np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]])
EN = I[:, None, :] + off[None]
for e in EN.reshape(-1, 3): pass
flat = EN.reshape(-1, 3)
key = np.ravel_multi_index(flat.T, (nx + 1, ny + 1, nz + 1))
uk, inv = np.unique(key, return_inverse=True)
conn = inv.reshape(-1, 8); NN = len(uk)
NP = lo + h * np.stack(np.unravel_index(uk, (nx + 1, ny + 1, nz + 1)), -1)
# material (isotropic approx, PA-CF printed)
E = 4000.; nu = 0.35
lam = E * nu / ((1 + nu) * (1 - 2 * nu)); mu = E / (2 * (1 + nu))
D = np.zeros((6, 6)); D[:3, :3] = lam; D[np.arange(3), np.arange(3)] += 2 * mu; D[np.arange(3, 6), np.arange(3, 6)] = mu
xi = off * 2 - 1
def Bmat(g):
    dN = np.zeros((8, 3))
    for a in range(8):
        for k in range(3):
            v = xi[a, k] / 8.
            for j in range(3):
                if j != k: v *= (1 + xi[a, j] * g[j])
            dN[a, k] = v
    dN *= 2 / h
    B = np.zeros((6, 24))
    for a in range(8):
        B[0, 3*a] = dN[a, 0]; B[1, 3*a+1] = dN[a, 1]; B[2, 3*a+2] = dN[a, 2]
        B[3, 3*a] = dN[a, 1]; B[3, 3*a+1] = dN[a, 0]
        B[4, 3*a+1] = dN[a, 2]; B[4, 3*a+2] = dN[a, 1]
        B[5, 3*a] = dN[a, 2]; B[5, 3*a+2] = dN[a, 0]
    return B
gp = np.array(list(np.ndindex(2, 2, 2))) * 2 - 1; gp = gp / np.sqrt(3)
Ke = sum(Bmat(g).T @ D @ Bmat(g) for g in gp) * (h / 2) ** 3
B0 = Bmat(np.zeros(3))
dof = (conn[:, :, None] * 3 + np.arange(3)).reshape(-1, 24)
rows = np.repeat(dof, 24, 1).ravel(); cols = np.tile(dof, (1, 24)).ravel()
K = sp.coo_matrix((np.tile(Ke.ravel(), len(conn)), (rows, cols)), shape=(3*NN, 3*NN)).tocsr()
print('dof', 3 * NN)
# --- geometry selections (clamp coords)
def node_sel(vmask): return np.unique(conn[vmask].ravel())
rs = np.hypot(cen[:, 0], cen[:, 2])
fixed = node_sel(rs < 25 + 1.0 * h)                      # saddle contact (bonded)
a = np.array([0, -0.469, -0.883]); a /= np.linalg.norm(a)
def nut(xs):
    P0 = np.array([xs, 111.17, -6.2]); d = cen - P0; s = d @ a; r = np.linalg.norm(d - np.outer(s, a), axis=1)
    return node_sel((r > 4.5) & (r < 10) & (s > 15 - 2 * h) & (s < 15))
nutL, nutR = nut(-32.5), nut(32.5)
def hole(y):
    r = np.hypot(cen[:, 1] - y, cen[:, 2] + 48.46); return node_sel((r < 5.1 + 1.2 * h) & (np.abs(cen[:, 0]) < 12))
holes = np.unique(np.r_[hole(10.08), hole(83.15)])
print('sel', len(fixed), len(nutL), len(nutR), len(holes))
def dist_force(nodes, F, M, c):
    r = NP[nodes] - c; n = len(nodes)
    # f_i = A + Bv x r_i ; constraints sum f = F, sum r x f = M
    S = r.sum(0); RR = sum(np.dot(ri, ri) * np.eye(3) - np.outer(ri, ri) for ri in r)
    X = lambda v: np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    # sum f = n A + sum Bv x r = n A - X(S) Bv ; sum r x f = X(S) A + RR Bv
    Mtx = np.block([[n * np.eye(3), -X(S)], [X(S), RR]])
    sol = np.linalg.solve(Mtx, np.r_[F, M]); A, Bv = sol[:3], sol[3:]
    f = A + np.cross(Bv, r); return f
def solve(cases):
    f = np.zeros((NN, 3))
    for nodes, F, M, c in cases: f[nodes] += dist_force(nodes, np.array(F, float), np.array(M, float), c)
    free = np.ones(3 * NN, bool); free[(fixed[:, None] * 3 + np.arange(3)).ravel()] = False
    Kf = K[free][:, free]; ml = pyamg.smoothed_aggregation_solver(Kf, B=None)
    u = np.zeros(3 * NN); u[free] = ml.solve(f.ravel()[free], tol=1e-8, accel='cg', maxiter=400)
    ue = u[dof]; eps = ue @ B0.T; sig = eps @ D
    sx, sy, sz, txy, tyz, txz = sig.T
    vm = np.sqrt(0.5 * ((sx - sy) ** 2 + (sy - sz) ** 2 + (sz - sx) ** 2) + 3 * (txy ** 2 + tyz ** 2 + txz ** 2))
    return u.reshape(-1, 3), vm, sig
# loads
mass = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0; g = 9.81
CG = np.array([0, 90., -180.])          # GUESS: tower CG in clamp coords
HC = np.array([0, 46.6, -48.46])         # keel-hole pair centre
down = -np.array([0, 0.8824, -0.4705])   # scan-down in clamp coords
fwd = np.array([0, -0.4705, -0.8824])    # roughly forward (perp to axis... approx)
def tower(Fvec):
    M = np.cross(CG - HC, Fvec); return (holes, Fvec, M, HC)
pre = float(sys.argv[2]) if len(sys.argv) > 2 else 2000.
Pdir = -a
cases = {
 'A preload only': [(nutL, pre * Pdir, [0,0,0], NP[nutL].mean(0)), (nutR, pre * Pdir, [0,0,0], NP[nutR].mean(0))],
}
cases['B preload + 15g vertical bump'] = cases['A preload only'] + [tower(mass * g * 15 * down)]
cases['C preload + 6g sideways'] = cases['A preload only'] + [tower(mass * g * 6 * np.array([1., 0, 0]))]
cases['D preload + 30g crash forward/down'] = cases['A preload only'] + [tower(mass * g * 30 * (down + fwd) / np.linalg.norm(down + fwd))]
cases['B0 15g bump, no preload'] = [tower(mass * g * 15 * down)]
res = {}
for k, c in cases.items():
    t = time.time(); u, vm, sig = solve(c)
    p999 = np.percentile(vm, 99.9); mx = vm.max(); imx = np.argmax(vm)
    syy = sig[:, 1]; it = np.argmax(syy)
    res[k] = dict(vm_max=mx, vm_999=p999, at=cen[imx].round(1).tolist(), interlayer_tension_max=syy.max(), it_at=cen[it].round(1).tolist(),
                  umax=np.linalg.norm(u, axis=1).max())
    print(k, {a: (np.round(b, 2) if not isinstance(b, list) else b) for a, b in res[k].items()}, round(time.time() - t, 1))
    np.save(f'vm_{k[0]}{"0" if "no pre" in k else ""}.npy', vm)
np.save('cen.npy', cen)
json.dump(res, open('fea_res.json', 'w'), indent=1)
