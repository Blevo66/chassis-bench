import sys; sys.path.insert(0,'tw3'); from common import *
yb=trimesh.load('tw3/yoke-bottom.stl'); yt=trimesh.load('tw3/yoke-top.stl'); hb=trimesh.load('tw3/handlebar.stl')
tubes=[]
for s in (1,-1):
    th=np.random.default_rng(0).uniform(0,2*np.pi,40000); t=np.random.default_rng(1).uniform(-36,204,40000)
    lat=s*91+21.5*np.cos(th); u=-22+21.5*np.sin(th)
    tubes.append(np.outer(lat,EX)+np.outer(u,B)+np.outer(t,A))
steer=np.vstack([yb.sample(60000), yt.sample(80000), hb.sample(80000)]+tubes)
sw=np.vstack([rot_axis(steer,a) for a in np.arange(-40,40.1,2)])
np.save('tw3/sweep40.npy', sw.astype(np.float32)); np.save('tw3/steer0.npy', steer.astype(np.float32))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fp=np.load('tw3/frame_pts.npy')
fig,axs=plt.subplots(1,3,figsize=(24,10))
for ax,(lo,hi,nm) in zip(axs,[(0,25,'|X|<25 (spine)'),(25,46,'25<|X|<46 (feet)'),(46,115,'46<|X|<115 (body)')]):
    m=(np.abs(sw[:,0])>=lo)&(np.abs(sw[:,0])<hi); q=sw[m]
    H,xe,ye=np.histogram2d(-q[:,1],q[:,2],bins=[np.arange(-300,400,3),np.arange(-150,600,3)])
    ax.contourf((xe[:-1]+xe[1:])/2,(ye[:-1]+ye[1:])/2,(H.T>0).astype(float),levels=[.5,1.5],colors=['#f6cccc'])
    f=fp[np.abs(fp[:,0])<115]; ax.scatter(-f[:,1],f[:,2],s=.2,c='#555')
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.set_title(nm); ax.set_xlim(-300,350); ax.set_ylim(-150,600)
    for nmb,(u,t) in {'A':(20,100),'B':(20,35)}.items():
        w=u*B+t*A; ax.plot(-w[1],w[2],'go',ms=10)
    ax.set_xticks(range(-300,351,50))
plt.tight_layout(); plt.savefig('tw3/envelopes.png',dpi=55)
