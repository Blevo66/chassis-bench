import numpy as np, struct, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
S='/tmp/claude-0/-home-user/08d74280-4fa3-53a7-b96e-82eec05e12b5/scratchpad/frame/'
b=open(S+'clean.stl','rb').read(); n=struct.unpack('<I',b[80:84])[0]
P=np.frombuffer(b[84:84+50*n],dtype=np.dtype([('n','<3f4'),('v','<9f4'),('a','<u2')]))['v'].reshape(-1,3)
# measure void: for each Y column, find frame Z extents near centreplane (|X|<25) in Z band -110..20
m=(np.abs(P[:,0])<25)
for y in range(125,300,10):
    c=P[m & (np.abs(P[:,1]-y)<2)]
    zs=np.sort(c[(c[:,2]>-115)&(c[:,2]<25),2])
    if len(zs)==0: continue
    g=np.diff(zs); i=np.argmax(g)
    print(y,'gap',round(zs[i],1),'..',round(zs[i+1],1),'h',round(g[i],1))
fig,ax=plt.subplots(1,2,figsize=(16,8),gridspec_kw={'width_ratios':[2.2,1]})
s=P[::5]
ax[0].scatter(s[:,1],s[:,2],s=0.15,c='0.7')
box=[(137,-76),(245,-48),(245,-13),(137,3)]
ax[0].add_patch(Polygon(box,closed=True,fc=(0.2,0.5,0.9,0.35),ec='b',lw=1.5))
ax[0].add_patch(Polygon([(140,-60),(201,-60+61*0.26),(201,-60+61*0.26+34),(140,-26)],closed=True,fc=(0.1,0.1,0.1,0.5),ec='k'))
ax[0].text(150,-45,'AMPSEAL\n(points\nsideways)',fontsize=7,color='w')
ax[0].add_patch(Polygon([(141,-73),(240,-47.3),(240,-31.3),(141,-57)],closed=True,fc=(0.2,0.3,0.7,0.6),ec='navy'))
ax[0].text(185,-68,'MOSFET board',fontsize=7,color='w',rotation=14)
for y,z0,z1 in ((137,-79,6),(245,-51,-10)):
    ax[0].annotate('',(y-6,z0),(y-6,z1),arrowprops=dict(arrowstyle='<->'))
ax[0].text(108,-40,'~85',fontsize=9); ax[0].text(250,-32,'~40',fontsize=9)
ax[0].annotate('',(137,-95),(262,-95),arrowprops=dict(arrowstyle='<->')); ax[0].text(185,-104,'void ~130 long',fontsize=9)
ax[0].set_xlim(60,330); ax[0].set_ylim(-130,60); ax[0].set_aspect('equal'); ax[0].grid(True,alpha=0.3)
ax[0].set_title('Side view (frame from your scan, front to the LEFT). Blue = brain box idea, 108 long'); ax[0].set_xlabel('mm behind steering axis'); ax[0].set_ylabel('mm up')
m=(P[:,1]>140)&(P[:,1]<240)
ax[1].scatter(P[m,0][::3],P[m,2][::3],s=0.15,c='0.6')
ax[1].add_patch(Rectangle((-31,-76),62,79,fc=(0.2,0.5,0.9,0.35),ec='b',lw=1.5))
ax[1].annotate('',(-31,-90),(31,-90),arrowprops=dict(arrowstyle='<->')); ax[1].text(-12,-100,'62 wide',fontsize=9)
ax[1].set_xlim(-90,90); ax[1].set_ylim(-130,60); ax[1].set_aspect('equal'); ax[1].grid(True,alpha=0.3)
ax[1].set_title('Looking from the front, frame slice 140-240 behind axis'); ax[1].set_xlabel('mm across bike')
plt.tight_layout(); plt.savefig(S+'void-box.png',dpi=120)
