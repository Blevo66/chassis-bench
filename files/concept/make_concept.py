import math, sys
W,H=2576,1932
overlay = len(sys.argv)>1
o=[]
def A(s): o.append(s)
def pts(p): return ' '.join(f'{x:.1f},{y:.1f}' for x,y in p)
def poly(p,fill,stroke='none',sw=0,extra=''):
    A(f'<polygon points="{pts(p)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>')
def path(d,fill='none',stroke='none',sw=0,extra=''):
    A(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round" {extra}/>')
def line(a,b,stroke,sw,extra=''):
    A(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" {extra}/>')
def ell(c,rx,ry,fill,stroke='none',sw=0,rot=0,extra=''):
    A(f'<ellipse cx="{c[0]:.1f}" cy="{c[1]:.1f}" rx="{rx}" ry="{ry}" transform="rotate({rot} {c[0]:.1f} {c[1]:.1f})" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def tube(a,b,w,col,hi=None):
    line(a,b,'#00000055',w+6)
    line(a,b,col,w)
    if hi: 
        # highlight offset up-left
        dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); nx,ny=-dy/L,dx/L
        if ny>0: nx,ny=-nx,-ny
        s=w*0.22
        line((a[0]+nx*s,a[1]+ny*s),(b[0]+nx*s,b[1]+ny*s),hi,w*0.22)

A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A('''<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#2b3d5c"/><stop offset="0.45" stop-color="#c9775a"/><stop offset="0.68" stop-color="#f2c38b"/><stop offset="1" stop-color="#f6dfb4"/></linearGradient>
<linearGradient id="ground" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#b8875a"/><stop offset="1" stop-color="#6e4a2f"/></linearGradient>
<linearGradient id="tank" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#ffffff"/><stop offset="0.6" stop-color="#eceef2"/><stop offset="1" stop-color="#c9ced8"/></linearGradient>
<linearGradient id="red" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#e8352b"/><stop offset="1" stop-color="#a5161a"/></linearGradient>
<linearGradient id="blue" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#2c55b8"/><stop offset="1" stop-color="#132a6b"/></linearGradient>
<linearGradient id="alu" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#f4f6f8"/><stop offset="0.45" stop-color="#b9c0c8"/><stop offset="0.55" stop-color="#d6dbe0"/><stop offset="1" stop-color="#7d858e"/></linearGradient>
<linearGradient id="chrome" x1="0" y1="0" x2="1" y2="0">
 <stop offset="0" stop-color="#6b7178"/><stop offset="0.35" stop-color="#ffffff"/><stop offset="0.6" stop-color="#9aa1a8"/><stop offset="1" stop-color="#4c5157"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="#f7d77a"/><stop offset="0.5" stop-color="#c99a2e"/><stop offset="1" stop-color="#8a6516"/></linearGradient>
<linearGradient id="seat" x1="0" y1="0" x2="0" y2="1">
 <stop offset="0" stop-color="#3a3f4a"/><stop offset="1" stop-color="#111318"/></linearGradient>
<linearGradient id="screen" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="#cfe3ee" stop-opacity="0.75"/><stop offset="1" stop-color="#5f7f99" stop-opacity="0.55"/></linearGradient>
<radialGradient id="lamp" cx="0.4" cy="0.35" r="0.7">
 <stop offset="0" stop-color="#ffffff"/><stop offset="0.5" stop-color="#fff3c4"/><stop offset="1" stop-color="#b9a46a"/></radialGradient>
<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">
 <stop offset="0" stop-color="#fff6d8"/><stop offset="0.4" stop-color="#ffe2a0" stop-opacity="0.8"/><stop offset="1" stop-color="#ffd18a" stop-opacity="0"/></radialGradient>
<filter id="blur"><feGaussianBlur stdDeviation="18"/></filter>
<filter id="soft"><feGaussianBlur stdDeviation="2"/></filter>
</defs>''')
# --- background
A(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
A('<circle cx="560" cy="1150" r="420" fill="url(#sun)"/>')
# distant hills / sea cliffs
path('M0 1120 L220 1070 L420 1095 L700 1040 L980 1080 L1250 1055 L1560 1090 L1820 1045 L2100 1085 L2350 1060 L2576 1090 L2576 1300 L0 1300 Z','#8a6a72','none',0,'opacity="0.55"')
path('M0 1170 C400 1140 800 1150 1200 1160 C1600 1170 2000 1140 2576 1150 L2576 1932 L0 1932 Z','url(#ground)')
# track ruts
path('M0 1790 L2576 1460','none','#5a3a22',16,'opacity="0.3"')
path('M0 1610 L2576 1330','none','#5a3a22',10,'opacity="0.22"')
# shadow under bike
ell((1400,1605),860,58,'#2a1a10',rot=-7.4,extra='opacity="0.5" filter="url(#blur)"')
ell((690,1688),190,26,'#1a0f08',extra='opacity="0.6" filter="url(#blur)"')
ell((2110,1505),150,20,'#1a0f08',extra='opacity="0.6" filter="url(#blur)"')

# geometry (photo pixel space)
FA=(2100,1215); FAX=(2128,1236)  # front wheel centre, near axle
RA=(682,1368); RAX=(680,1385)
PIV=(1262,1168)
TY=(1745,455); BY=(1872,668)

def wheel(c,rx,ry,disc=None):
    # tyre
    ell(c,rx,ry,'#1b1b1d')
    n=46
    for i in range(n):
        t=2*math.pi*i/n
        x=c[0]+(rx+9)*math.cos(t); y=c[1]+(ry+9)*math.sin(t)
        ang=math.degrees(math.atan2(ry*math.sin(t)*rx, rx*math.cos(t)*ry))
        A(f'<rect x="{x-11:.1f}" y="{y-9:.1f}" width="22" height="18" rx="3" fill="#1b1b1d" transform="rotate({ang+90:.1f} {x:.1f} {y:.1f})"/>')
    ell(c,rx-4,ry-4,'none','#2e2e33',6)
    # sidewall text band
    ell(c,rx-30,ry-30,'none','#26262b',22)
    # rim
    rrx,rry=rx*0.79,ry*0.79
    ell(c,rrx,rry,'none','url(#gold)',26)
    ell(c,rrx-14,rry-14,'none','#7a5a14',3)
    ell(c,rrx+12,rry+12,'none','#f9e7ae',2,extra='opacity="0.7"')
    # spokes
    for i in range(36):
        t=2*math.pi*i/36
        a=(c[0]+rrx*0.97*math.cos(t), c[1]+rry*0.97*math.sin(t))
        t2=t+(0.35 if i%2 else -0.35)
        b=(c[0]+30*math.cos(t2), c[1]+30*math.sin(t2))
        line(a,b,'#c9ccd1',3)
    if disc:
        r=disc
        ell(c,r*rx/ry*0.98,r,'#8d939b','#5b6168',4)
        for i in range(10):
            t=2*math.pi*i/10
            ell((c[0]+r*0.72*math.cos(t)*rx/ry,c[1]+r*0.72*math.sin(t)),9,9,'#4b5057')
        ell(c,r*0.5*rx/ry,r*0.5,'#c2c7cd','#6b7178',3)
    # hub
    ell(c,46,46,'url(#gold)','#6b5014',3)
    ell(c,16,16,'#3a3a3a')

# ---------- far-side / back layer
# far fork leg (behind wheel)
tube((TY[0]-40,TY[1]+20),(FA[0]-55,FA[1]-20),44,'#9da4ab')
# rear wheel & front wheel
wheel(RA,355,322,disc=118)
wheel(FA,292,288)

# ---------- rear frame stays (seat rail and lower stay)
RED='#c8241f'
tube((1440,760),(1258,1175),30,RED,'#ef6a5c')            # main rear downtube behind engine
tube((1300,735),(1060,860),22,RED,'#ef6a5c')
tube((870,730),(1270,1160),22,RED,'#ef6a5c')             # rear stay to pivot
tube((700,640),(1480,770),26,RED,'#ef6a5c')              # seat rail (mostly hidden)

# ---------- shock (XR250R, yellow spring)
ST=(1345,800); SB=(1120,1095)
tube(ST,SB,30,'#2a2c30')
dx,dy=SB[0]-ST[0],SB[1]-ST[1]; L=math.hypot(dx,dy); ux,uy=dx/L,dy/L; nx,ny=-uy,ux
# reservoir
tube((ST[0]+ux*20-nx*36,ST[1]+uy*20-ny*36),(ST[0]+ux*150-nx*36,ST[1]+uy*150-ny*36),34,'#c6ccd2','#ffffff')
for k in range(14):
    s=70+k*17
    a=(ST[0]+ux*s+nx*42,ST[1]+uy*s+ny*42); b=(ST[0]+ux*(s+9)-nx*42,ST[1]+uy*(s+9)-ny*42)
    line(a,b,'#e8b512',13); line(a,b,'#ffd84a',5)
ell(SB,15,15,'#9aa1a8','#444',3)

# ---------- engine XL185
# crankcase
path('M1300 1010 C1380 975 1470 965 1555 975 C1585 1010 1592 1090 1575 1160 C1560 1200 1520 1215 1470 1215 L1345 1212 C1310 1200 1292 1150 1292 1100 Z','url(#alu)','#555c63',4)
path('M1340 1040 C1400 1020 1480 1015 1540 1025 C1555 1070 1552 1130 1538 1170 L1360 1175 C1340 1140 1335 1085 1340 1040 Z','none','#7f878f',4)
ell((1405,1110),30,30,'#cfd4d9','#6b7178',4)
ell((1480,1060),40,34,'none','#8a929a',4)
for bx,by in ((1350,1030),(1545,1035),(1555,1160),(1360,1180),(1450,1185)): ell((bx,by),6,6,'#5a6067')
# cylinder with fins
cyl=[(1440,995),(1612,985),(1628,845),(1452,835)]
poly(cyl,'#5a6067')
for k in range(9):
    y0=842+k*17
    poly([(1440-6+k*0.8,y0),(1636-k*0.5,y0+2),(1634-k*0.5,y0+9),(1440-6+k*0.8,y0+7)],'#c9ced4')
# head + red rocker cover
poly([(1452,838),(1630,850),(1636,800),(1462,786)],'#b6bcc3','#5a6067',3)
path('M1458 790 C1470 760 1600 760 1626 798 L1630 808 L1460 798 Z','url(#red)','#7e1414',3)
# carb + intake
tube((1440,880),(1365,900),40,'#9aa1a8','#e6e9ec')
ell((1345,905),26,30,'#6d737a')
# front engine cradle (red bracket) and downtube
tube((1795,650),(1615,1040),34,RED,'#ef6a5c')
poly([(1570,1000),(1640,985),(1650,1080),(1585,1095)],RED,'#8d1714',3)

# ---------- exhaust (low level, right side)
hdr='M1622 880 C1668 900 1680 960 1670 1040 C1662 1120 1650 1190 1600 1228 C1540 1262 1420 1262 1330 1252 C1250 1244 1205 1205 1170 1140 C1130 1065 1085 990 1020 935'
path(hdr,'none','#4a3a35',26)
path(hdr,'none','#c9a27a',12,'opacity="0.8"')
path(hdr,'none','#fff4e0',3,'opacity="0.6"')
# silencer
path('M1035 900 L760 760 C740 750 718 770 728 792 L742 812 L1010 960 C1040 975 1060 925 1035 900 Z','url(#alu)','#4c5157',4)
path('M770 772 L1020 905','none','#ffffff',4,'opacity="0.7"')
ell((735,790),20,30,'#2a2c30',rot=-28)
# heat shield straps
for t in (0.25,0.65):
    x=1035+(760-1035)*t; y=900+(760-900)*t
    line((x+12,y-18),(x-14,y+30),'#3e444a',8)

# ---------- swingarm (CRF250R alloy) with Pro-Link sticker
arm=[(1290,1110),(1290,1215),(1240,1245),(1060,1290),(722,1418),(668,1412),(650,1380),(670,1350),(980,1150),(1030,1095),(1140,1072),(1225,1080)]
poly(arm,'url(#alu)','#59606a',5)
path('M1250 1100 L1000 1160 L700 1360','none','#ffffff',6,'opacity="0.65"')
path('M1270 1210 L1050 1268 L720 1400','none','#4b525a',5,'opacity="0.6"')
# chain adjuster/axle
ell(RAX,26,26,'#d6dbe0','#555',4); ell(RAX,11,11,'#333')
# pivot bolt
ell(PIV,24,24,'#d0d5da','#4c5157',4); ell(PIV,9,9,'#333')
# sticker
A('<g transform="translate(925,1235) rotate(-26)">'
  '<rect x="-115" y="-26" width="230" height="52" rx="8" fill="#111"/>'
  '<rect x="-109" y="-20" width="218" height="40" rx="5" fill="none" stroke="#d72d24" stroke-width="3"/>'
  '<text x="0" y="12" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-style="italic" font-weight="900" font-size="33" fill="#fff" letter-spacing="1">Pro-Link</text></g>')
# rocker + dogbone (rocker H style, under the arm front)
poly([(1240,1170),(1215,1265),(1150,1300),(1135,1270),(1190,1215)],'#4a4f56','#25282c',3)
tube((1150,1290),(1090,1215),18,'#6a7077')
ell((1240,1172),12,12,'#9aa1a8')

# ---------- rear mudguard (retro Honda, printed) + tail light + plate
path('M1150 690 C1000 660 860 640 740 625 C620 612 500 620 420 650 C380 668 352 700 340 735 L370 740 C395 705 440 690 520 682 C640 672 800 692 980 742 C1060 765 1120 770 1160 760 Z','url(#tank)','#8d939b',4)
path('M1150 700 C980 672 820 650 700 640 C560 632 460 645 400 690','none','#c8241f',10)
# tail light + plate
poly([(560,668),(612,662),(616,690),(564,697)],'#8b0f10','#3a0606',3)
poly([(570,672),(606,668),(608,684),(572,688)],'#ff4a3a')
poly([(590,700),(600,700),(615,780),(604,782)],'#222')
poly([(520,775),(700,768),(706,850),(526,858)],'#f6f4ec','#222',4)
A('<text x="613" y="827" text-anchor="middle" font-family="Arial Narrow, Arial, sans-serif" font-weight="700" font-size="44" fill="#111" transform="rotate(-2 613 827)">KNH 262Y</text>')

# ---------- seat
path('M1475 690 C1350 660 1150 640 960 628 C860 622 790 622 750 640 C735 650 742 668 760 672 C880 680 1050 700 1200 735 C1320 760 1420 768 1470 760 Z','url(#blue)','#0d1a44',4)
path('M1460 700 C1300 670 1100 652 900 640 C830 636 780 640 760 650','none','#5d82e0',6,'opacity="0.6"')
# seat base
path('M1470 760 C1400 770 1300 765 1200 742 C1050 708 900 688 760 672 L770 690 C900 705 1060 730 1200 760 C1320 785 1420 790 1470 780 Z','#15171c')

# ---------- side panel with number board 66
path('M1440 790 C1360 778 1270 760 1150 740 C1110 760 1085 820 1095 900 C1100 935 1130 960 1170 965 L1410 965 C1450 940 1470 860 1440 790 Z','url(#tank)','#8d939b',4)
path('M1440 790 C1360 778 1270 760 1150 740 C1135 750 1120 768 1110 790 L1452 822 Z','#c8241f')
ell((1290,880),112,64,'#f9d63a','#111',5,rot=-4)
A('<text x="1290" y="920" text-anchor="middle" font-family="Impact, Arial Black, sans-serif" font-weight="900" font-size="112" fill="#111" transform="rotate(-4 1290 880)">66</text>')

# ---------- tank (big 80s rally) with shrouds
tankp='M1745 535 C1730 500 1680 470 1610 468 C1520 466 1430 500 1360 560 C1320 595 1300 640 1300 690 C1360 700 1440 705 1490 720 C1530 790 1560 870 1600 905 C1650 900 1700 860 1720 800 C1740 720 1760 610 1745 535 Z'
path(tankp,'url(#tank)','#7d858e',5)
# stripes red/blue (80s HRC style)
path('M1735 590 C1660 560 1520 560 1400 620 C1350 645 1320 670 1305 690 L1340 695 C1380 660 1470 618 1560 606 C1630 598 1700 610 1740 628 Z','url(#red)')
path('M1742 640 C1680 625 1590 630 1500 660 C1450 676 1410 700 1395 708 L1432 712 C1470 692 1560 668 1640 666 C1690 665 1725 674 1744 682 Z','url(#blue)')
path('M1600 470 C1520 468 1440 500 1380 548','none','#ffffff',8,'opacity="0.9"')
A('<text x="1612" y="790" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-style="italic" font-weight="900" font-size="58" fill="#c8241f" transform="rotate(-8 1612 790)">XL185R</text>')
A('<text x="1612" y="830" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="22" fill="#1e3a8a" letter-spacing="6" transform="rotate(-8 1612 830)">RALLY</text>')
# filler cap
ell((1545,478),40,10,'#c3c9cf','#555',3,rot=-6)

# ---------- bash plate
path('M1290 1200 L1330 1250 L1600 1245 C1650 1240 1690 1200 1700 1150 L1680 1140 C1660 1190 1620 1215 1580 1218 L1340 1220 Z','url(#alu)','#4c5157',4)

# ---------- front: near fork leg, fender, fairing, bars
# near fork stanchion + slider
tube(TY,(2005,965),46,'url(#chrome)')
line(TY,(2005,965),'#d9dde1',6,'opacity="0.0"')
tube((2000,950),(2140,1330),60,'#a7aeb5','#e7eaed')
ell((2004,955),33,15,'#2a2c30',rot=-20)     # dust seal
ell(FAX,24,24,'#d6dbe0','#555',4); ell(FAX,9,9,'#333')
# yokes
poly([(1650,430),(1830,420),(1845,480),(1660,492)],'url(#alu)','#4c5157',4)
poly([(1790,640),(1925,635),(1930,690),(1800,700)],'url(#alu)','#4c5157',4)
# high front fender (80s CR)
path('M1850 700 C1950 690 2080 700 2180 740 C2240 765 2280 800 2290 830 L2262 832 C2230 800 2150 770 2060 755 C1970 742 1890 745 1840 752 C1790 760 1760 775 1745 790 L1735 770 C1760 735 1800 708 1850 700 Z','url(#tank)','#7d858e',4)
path('M1860 712 C1980 705 2120 725 2230 780','none','#c8241f',8)
# fairing (Dakar style twin lamp)
path('M1800 300 C1830 290 1870 300 1890 330 L1905 380 L1850 395 Z','url(#screen)','#4b5f70',3)
fair='M1760 520 C1770 440 1800 380 1850 360 C1910 345 1960 380 1990 440 C2015 495 2020 560 2005 620 C1990 660 1940 680 1880 670 C1830 662 1790 640 1770 600 Z'
path(fair,'url(#tank)','#6e767f',5)
path('M1985 430 C2010 480 2018 540 2008 600 L1975 590 C1985 540 1980 480 1960 440 Z','url(#red)')
# headlights twin
for c in ((1925,470),(1940,580)):
    ell(c,40,46,'#2a2c30',rot=-12)
    ell(c,32,38,'url(#lamp)',rot=-12)
    ell((c[0]-8,c[1]-10),9,9,'#ffffff',extra='opacity="0.9"')
# screen in front of bars
path('M1820 368 C1830 300 1860 255 1905 240 C1925 270 1935 320 1940 380 C1910 360 1860 360 1820 368 Z','url(#screen)','#4b5f70',3)
# handlebars (gold, as on the mock-up) with handguard
tube((1690,440),(1585,345),20,'url(#gold)')
tube((1585,345),(1480,322),20,'url(#gold)')
tube((1505,328),(1450,316),30,'#1c1c1e')
path('M1600 320 C1560 300 1500 300 1470 320 C1460 345 1480 365 1520 362 C1550 360 1580 350 1600 340 Z','#c8241f','#5a0d0b',3,'opacity="0.95"')
tube((1735,440),(1775,345),20,'url(#gold)')
tube((1775,345),(1800,300),24,'#1c1c1e')
path('M1772 300 C1790 270 1830 268 1846 290 C1850 312 1825 330 1800 330 Z','#c8241f','#5a0d0b',3)
# roadbook / clocks
poly([(1720,420),(1800,410),(1810,375),(1730,384)],'#20232a','#000',3)

# ---------- title block
A('<g font-family="Helvetica, Arial, sans-serif">'
  '<text x="120" y="210" font-size="92" font-weight="900" font-style="italic" fill="#ffffff" letter-spacing="2">XL185R RALLY</text>'
  '<rect x="122" y="235" width="470" height="10" fill="#c8241f"/><rect x="122" y="252" width="470" height="10" fill="#1e3a8a"/>'
  '<text x="122" y="320" font-size="40" fill="#ffffff" opacity="0.92">Concept · Land&#8217;s End Trial, Easter 2028</text>'
  '<text x="122" y="372" font-size="30" fill="#ffffff" opacity="0.75">1982 XL125R frame · XL185 engine · CR250R Showa forks · CRF250R arm · XR250R shock</text>'
  '</g>')
A('</svg>')
svg='\n'.join(o)
if overlay:
    svg=svg.replace('<rect width="2576" height="1932" fill="url(#sky)"/>','<image href="../photo.jpg" width="2576" height="1932"/><g opacity="0.55">').replace('</svg>','</g></svg>')
open('overlay.svg' if overlay else 'concept.svg','w').write(svg)
