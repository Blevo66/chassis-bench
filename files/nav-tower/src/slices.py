import numpy as np,matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
Pr=np.load('Pr.npy');Pf=np.load('Pf.npy');LOCK=45
angs=np.radians(np.arange(-LOCK,LOCK+1,2))
sw=[]
for a in angs:
  c,s=np.cos(a),np.sin(a);sw.append(np.c_[c*Pr[:,0]-s*Pr[:,1],s*Pr[:,0]+c*Pr[:,1],Pr[:,2]])
sw=np.concatenate(sw);np.save('sw45.npy',sw[::2])
ts=[30,70,110,150,175,200,240,280,330,380]
fig,ax=plt.subplots(2,5,figsize=(25,11))
for a,t0 in zip(ax.flat,ts):
  for P,cl,s in[(sw,'#f4a0a0',1),(Pr,'#c00000',1),(Pf,'#444',1)]:
    m=abs(P[:,2]-t0)<4;a.scatter(P[m,0],P[m,1],s=s,c=cl)
  a.set_xlim(-420,420);a.set_ylim(250,-350);a.set_aspect('equal');a.grid(alpha=.3)
  a.set_title(f'slice {t0} mm up the steering axis');a.axhline(0,c='b',lw=.4);a.axvline(0,c='b',lw=.4)
  a.set_xlabel('lateral (mm)');a.set_ylabel('forward is UP the page (mm)')
plt.tight_layout();plt.savefig('slices.png',dpi=45)
