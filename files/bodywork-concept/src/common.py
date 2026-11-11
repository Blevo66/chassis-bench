W,H=2576,1932
class S:
    def __init__(s): s.o=[]; s.uid=0
    def A(s,x): s.o.append(x)
    def part(s,d,base,hi='',ao=None,stroke='#00000080',sw=2.5):
        s.uid+=1;i=s.uid
        s.A(f'<clipPath id="c{i}"><path d="{d}"/></clipPath><path d="{d}" fill="{base}"/><g clip-path="url(#c{i})">')
        if ao: s.A(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.5" stroke-width="{ao}" filter="url(#b12)"/>')
        s.A(hi+'</g>')
        s.A(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
    def shadow(s,d,dx=6,dy=14,op=0.45,blur='b16'):
        s.A(f'<path d="{d}" transform="translate({dx} {dy})" fill="#000" opacity="{op}" filter="url(#{blur})"/>')
    def svg(s):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'+DEFS+'\n'.join(s.o)+'</svg>')
DEFS='''<defs>
<filter id="b3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="b6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="b12" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="b16" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>
<linearGradient id="white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbfbf8"/><stop offset="0.55" stop-color="#e3e3df"/><stop offset="1" stop-color="#a4a5a2"/></linearGradient>
<linearGradient id="whiteL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#c9cac6"/><stop offset="0.5" stop-color="#f6f6f3"/><stop offset="1" stop-color="#b8b9b5"/></linearGradient>
<linearGradient id="red" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9342a"/><stop offset="1" stop-color="#8f1515"/></linearGradient>
<linearGradient id="blue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2d53ad"/><stop offset="1" stop-color="#101f52"/></linearGradient>
<linearGradient id="seat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3556aa"/><stop offset="0.5" stop-color="#1c3577"/><stop offset="1" stop-color="#0b1535"/></linearGradient>
<linearGradient id="alu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#eceeef"/><stop offset="0.4" stop-color="#b3b8bc"/><stop offset="0.55" stop-color="#d3d7da"/><stop offset="1" stop-color="#6c7277"/></linearGradient>
<linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#dfeaf2" stop-opacity="0.55"/><stop offset="1" stop-color="#3e5263" stop-opacity="0.55"/></linearGradient>
<radialGradient id="lamp" cx="0.38" cy="0.35" r="0.75"><stop offset="0" stop-color="#ffffff"/><stop offset="0.35" stop-color="#e9edf0"/><stop offset="0.8" stop-color="#8d969c"/><stop offset="1" stop-color="#3a3f44"/></radialGradient>
<radialGradient id="yel" cx="0.4" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffe36a"/><stop offset="1" stop-color="#d9a913"/></radialGradient>
</defs>'''
def lamp(s,cx,cy,rx,ry,rot=0):
    s.A(f'<g transform="rotate({rot} {cx} {cy})"><ellipse cx="{cx}" cy="{cy}" rx="{rx+5}" ry="{ry+5}" fill="#3a3d40"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#lamp)"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx*.4}" ry="{ry*.4}" fill="#f5f2e6" opacity="0.8"/>'
        f'<path d="M{cx-rx} {cy} L{cx+rx} {cy} M{cx} {cy-ry} L{cx} {cy+ry}" stroke="#fff" stroke-width="1.5" opacity="0.35"/>'
        f'<ellipse cx="{cx-rx*.3}" cy="{cy-ry*.4}" rx="{rx*.3}" ry="{ry*.18}" fill="#fff" opacity="0.9" filter="url(#b3)"/></g>')
def oval(s,cx,cy,rx,ry,rot,num='66',fs=None):
    fs=fs or int(ry*1.6)
    s.A(f'<g transform="rotate({rot} {cx} {cy})"><ellipse cx="{cx+3}" cy="{cy+4}" rx="{rx}" ry="{ry}" fill="#000" opacity="0.25" filter="url(#b6)"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#yel)" stroke="#111" stroke-width="4"/>'
        f'<text x="{cx}" y="{cy+fs*0.36}" text-anchor="middle" font-family="Impact, Anton, Arial Black, sans-serif" font-weight="900" font-size="{fs}" fill="#141414" transform="scale(1 1)">{num}</text></g>')
