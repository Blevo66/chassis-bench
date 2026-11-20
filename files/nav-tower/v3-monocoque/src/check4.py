import sys, json, glob, os; sys.path.insert(0,'tw3'); from common import *
from scipy.spatial import cKDTree
sw = np.load('tw3/sweep40.npy'); fr = trimesh.load('tw3/xl125r-frame-clean.stl')
# only keep sweep pts near tower region to shrink tree
m = (sw[:,1] < 140) & (np.abs(sw[:,0]) < 200) & (sw[:,2] > -60); Ts = cKDTree(sw[m][::2]); print('sweep pts', m.sum()//2)
fs = fr.sample(400000); Tf = cKDTree(fs)
res = {}
for f in sorted(glob.glob('tw3/out4/*.stl')):
    k = os.path.basename(f)[:-4]; mesh = trimesh.load(f)
    p = np.vstack([mesh.sample(20000), mesh.vertices])
    ds, i = Ts.query(p); df, j = Tf.query(p)
    if k == 'neck_carbon':  # ignore the boss contact faces
        loc = np.c_[p@EX, p@B, p@A]; bossz = np.zeros(len(p), bool)
        for (u,t) in [(20,35),(20,100)]: bossz |= (np.hypot(loc[:,1]-u, loc[:,2]-t) < 16) & (np.abs(loc[:,0]) < 39)
        dfn = df[~bossz].min()
    else: dfn = df.min()
    res[k] = (round(float(ds.min()),1), round(float(dfn),1)); w = p[np.argmin(ds)]
    print(f'{k:28s} sweep {ds.min():6.1f} (at fwd {-w[1]:.0f} Z {w[2]:.0f} X {w[0]:.0f})   frame {dfn:6.1f}')
L = json.load(open('tw3/out4/layout.json'))
eyes = {'standing': oldside_to_world(-430, 1150), 'seated': oldside_to_world(-600, 880)}
d_ = np.array([np.sin(np.radians(35)), np.cos(np.radians(35))]); n_ = np.array([-d_[1], d_[0]])
for nm, c in [('dash', np.array(L['DC'])), ('tablet', np.array(L['BC']) + n_*16)]:
    for en, e in eyes.items():
        ev = np.array([-e[1], e[2]]); v = ev - c; dist = np.linalg.norm(v)
        print(nm, en, 'below eye', round(np.degrees(np.arctan2(v[1], -v[0]))), 'off-square', round(np.degrees(np.arccos(v @ n_ / dist))), 'dist', round(dist))
json.dump(res, open('tw3/out4/clearance.json','w'), indent=1)
