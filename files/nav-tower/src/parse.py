import re,sys,numpy as np,pickle
f=sys.argv[1]
txt=open(f).read()
ents={}
for m in re.finditer(r'#(\d+)\s*=\s*([A-Z_0-9]+)\s*\((.*?)\)\s*;',txt,re.S):
    ents[int(m.group(1))]=(m.group(2),m.group(3))
P={};V={}
for k,(t,a) in ents.items():
    if t=='CARTESIAN_POINT':
        nums=re.findall(r'\(([^()]*)\)\s*$',a)
        P[k]=[float(x) for x in nums[0].split(',')]
for k,(t,a) in ents.items():
    if t=='VERTEX_POINT':
        V[k]=P[int(re.findall(r'#(\d+)',a)[0])]
tris=[];solid_of={}
# map faces to shells
for k,(t,a) in ents.items():
    if t=='CLOSED_SHELL':
        for fid in re.findall(r'#(\d+)',a): solid_of[int(fid)]=k
for k,(t,a) in ents.items():
    if t=='ADVANCED_FACE':
        b=int(re.findall(r'#(\d+)',a)[0])
        loop=int(re.findall(r'#(\d+)',ents[b][1])[0])
        oes=[int(x) for x in re.findall(r'#(\d+)',ents[loop][1])]
        pts=[]
        for oe in oes:
            ta=ents[oe][1]; ids=[int(x) for x in re.findall(r'#(\d+)',ta)]
            ec=ids[-1]; ori='.T.' in ta.split(',')[-1]
            ea=[int(x) for x in re.findall(r'#(\d+)',ents[ec][1])]
            v0,v1=ea[0],ea[1]
            pts.append(V[v0] if ori else V[v1])
        tris.append((solid_of.get(k,0),pts))
print(len(tris), set(len(p) for s,p in tris))
units=[ (t,a) for k,(t,a) in ents.items() if 'UNIT' in t][:8]; print(units)
pickle.dump(tris,open('tris.pkl','wb'))
