import numpy as np, trimesh
r = np.radians(25.4); A = np.array([0, np.sin(r), np.cos(r)]); B = np.array([0, np.cos(r), -np.sin(r)]); EX = np.array([1., 0, 0])
R0 = np.array([[1,0,0],[0,0.8824,-0.4705],[0,0.4705,0.8824]]); P0 = np.array([2.6,-16.2,-9.4])
def oldlocal_to_world(P):
    P = np.atleast_2d(P); v, u, t = -P[:,0], P[:,1]-2, P[:,2]-50
    return np.outer(v, EX) + np.outer(u, B) + np.outer(t, A)
def oldside_to_world(fx, z, lat=0.0):   # old scan side plot (x = -Y_scan fwd, z) -> new world
    S = np.array([lat, -fx, z], float); L = (S - P0) @ R0.T
    return oldlocal_to_world(L)[0]
def rot_axis(P, deg):
    th = np.radians(deg); k = A; P = np.atleast_2d(P)
    return P*np.cos(th) + np.cross(k, P)*np.sin(th) + np.outer(P @ k, k)*(1-np.cos(th))
