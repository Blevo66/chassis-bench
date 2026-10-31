# Joel's v2 rocker (Fusion screenshot) -> outline polygon in his sketch frame (mm, pivot 0,0, x fwd, y up)
from PIL import Image; import numpy as np, json
from skimage import measure
from shapely.geometry import Polygon, Point
from scipy import ndimage
a=np.array(Image.open('v2.png').convert('RGB')).astype(int)
body=(np.abs(a-[77,86,90]).sum(2)<30)
body=ndimage.binary_closing(body,iterations=3)

body=ndimage.binary_opening(body,iterations=3)
lab,n=ndimage.label(body); big=np.argmax(np.bincount(lab.ravel())[1:])+1; body=lab==big
# holes appear as non-body inside: keep windows by not filling them -> recompute fill for windows
solid=ndimage.binary_fill_holes(body)
win=ndimage.binary_closing(solid&~body,iterations=3)&solid
win=ndimage.binary_opening(win,iterations=2)
body=solid&~win
S=4.4125  # px/mm from hole spacing (pivot->shock 669 px = 151.6 mm)
P0=np.array([797,296])
def tomm(c): return np.c_[(c[:,1]-P0[0])/S, -(c[:,0]-P0[1])/S]
cs=measure.find_contours(np.pad(body,1).astype(float),0.5)
polys=[Polygon(tomm(c-1)).simplify(0.3) for c in cs]
polys.sort(key=lambda p:-p.area)
outer=polys[0]; holes=[p for p in polys[1:] if p.area>150 and outer.contains(p.centroid)]
print('outer area',outer.area, 'holes',[round(h.area) for h in holes], [tuple(np.round(h.centroid.coords[0],1)) for h in holes])
json.dump({'outer':list(outer.exterior.coords),'holes':[list(h.exterior.coords) for h in holes]},open('v2_profile.json','w'))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(14,6)); ax[0].imshow(body); ax[1].plot(*outer.exterior.xy)
for h in holes: ax[1].plot(*h.exterior.xy)
ax[1].set_aspect('equal'); plt.savefig('v2chk.png',dpi=50)
