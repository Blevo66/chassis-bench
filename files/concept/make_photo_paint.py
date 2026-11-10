import math
W,H=2576,1932
o=[]; A=o.append
uid=[0]
def part(d, base, hi=None, ao=None, stroke='#00000066', extra_inside=''):
    """shape with clip-based soft shading"""
    uid[0]+=1; i=uid[0]
    A(f'<clipPath id="c{i}"><path d="{d}"/></clipPath>')
    A(f'<path d="{d}" fill="{base}"/>')
    A(f'<g clip-path="url(#c{i})">')
    if ao: A(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.45" stroke-width="{ao}" filter="url(#b12)"/>')
    if hi: A(hi)
    A(extra_inside)
    A('</g>')
    A(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2"/>')
def shadow(d,dx=6,dy=14,op=0.45,blur='b16'):
    A(f'<path d="{d}" transform="translate({dx} {dy})" fill="#000" opacity="{op}" filter="url(#{blur})"/>')

A(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
A('''<defs>
<filter id="b3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
<filter id="b6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
<filter id="b12" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="12"/></filter>
<filter id="b16" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="16"/></filter>
<filter id="b30" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="30"/></filter>
<linearGradient id="white" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fbfbfa"/><stop offset="0.55" stop-color="#e6e6e3"/><stop offset="1" stop-color="#a9aaa8"/></linearGradient>
<linearGradient id="red" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d8332a"/><stop offset="1" stop-color="#8f1515"/></linearGradient>
<linearGradient id="blue" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a4fa6"/><stop offset="1" stop-color="#101f52"/></linearGradient>
<linearGradient id="seat" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2d4c9c"/><stop offset="0.5" stop-color="#1c3577"/><stop offset="1" stop-color="#0b1535"/></linearGradient>
<linearGradient id="alu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e9ebec"/><stop offset="0.4" stop-color="#b3b8bc"/><stop offset="0.55" stop-color="#cfd3d6"/><stop offset="1" stop-color="#6c7277"/></linearGradient>
<linearGradient id="ss" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a7f76"/><stop offset="0.35" stop-color="#e8e2da"/><stop offset="0.6" stop-color="#a1928a"/><stop offset="1" stop-color="#4a3f3a"/></linearGradient>
<linearGradient id="screen" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#d9e6ee" stop-opacity="0.55"/><stop offset="1" stop-color="#46596a" stop-opacity="0.5"/></linearGradient>
<radialGradient id="lamp" cx="0.38" cy="0.35" r="0.75"><stop offset="0" stop-color="#ffffff"/><stop offset="0.35" stop-color="#e9edf0"/><stop offset="0.8" stop-color="#8d969c"/><stop offset="1" stop-color="#3a3f44"/></radialGradient>
<radialGradient id="yel" cx="0.4" cy="0.3" r="0.8"><stop offset="0" stop-color="#ffe36a"/><stop offset="1" stop-color="#d9a913"/></radialGradient>
</defs>''')

# ---------- shapes (photo pixel coords)
TANK='M1748 538 C1734 498 1684 466 1610 464 C1518 462 1428 498 1358 560 C1318 596 1298 642 1300 692 C1362 702 1440 707 1492 722 C1530 792 1560 872 1600 908 C1652 902 1702 862 1722 800 C1742 720 1762 612 1748 538 Z'
SEAT='M1478 688 C1350 656 1150 636 960 624 C860 618 790 618 748 636 C730 648 738 670 760 676 C880 684 1050 704 1200 739 C1320 764 1420 772 1472 764 Z'
SEATBASE='M1472 764 C1400 774 1300 769 1200 746 C1050 712 900 692 760 676 L772 696 C900 710 1060 736 1200 766 C1320 790 1420 794 1472 784 Z'
SIDE='M1440 790 C1360 778 1270 760 1150 742 C1108 762 1084 822 1094 900 C1100 936 1130 962 1172 966 L1408 966 C1450 940 1470 860 1440 790 Z'
RFEND='M1150 690 C1000 660 860 640 740 625 C620 612 500 620 420 650 C380 668 352 700 340 735 L372 742 C398 708 442 692 520 684 C640 674 800 694 980 744 C1060 767 1120 772 1160 762 Z'
FFEND='M1790 712 C1890 700 2040 704 2160 742 C2228 764 2272 800 2286 832 L2258 836 C2228 806 2150 776 2060 762 C1970 750 1890 752 1840 760 C1800 766 1772 778 1756 792 L1744 772 C1756 742 1770 720 1790 712 Z'
FAIR='M1790 520 C1800 440 1840 380 1912 360 C1964 344 2016 376 2044 436 C2068 492 2072 556 2058 616 C2044 658 1998 680 1944 672 C1880 666 1820 650 1796 604 Z'
SCREEN='M1850 380 C1866 304 1900 258 1946 240 C1970 272 1984 324 1990 392 C1950 370 1895 366 1850 380 Z'
BASH='M1296 1196 L1336 1250 L1602 1246 C1652 1240 1694 1200 1704 1150 L1684 1140 C1664 1190 1624 1214 1584 1216 L1342 1218 Z'
SIL='M1035 898 L760 758 C738 748 716 770 726 792 L740 814 L1010 962 C1042 978 1062 924 1035 898 Z'
HDR='M1622 880 C1668 900 1682 960 1672 1040 C1664 1120 1652 1190 1602 1230 C1542 1264 1420 1264 1330 1254 C1250 1246 1205 1206 1170 1140 C1130 1065 1085 990 1020 935'

# ---------- contact shadows onto the photo
for d,dx,dy,op in ((TANK,8,22,0.45),(SEAT,6,26,0.5),(SIDE,6,18,0.4),(RFEND,4,24,0.35),(FFEND,4,20,0.4),(FAIR,8,18,0.4),(SIL,4,16,0.4)):
    shadow(d,dx,dy,op)

# ---------- exhaust header + silencer
A(f'<path d="{HDR}" fill="none" stroke="#2e2622" stroke-width="28" stroke-linecap="round"/>')
A(f'<path d="{HDR}" fill="none" stroke="#9c8068" stroke-width="20" stroke-linecap="round"/>')
A(f'<path d="{HDR}" fill="none" stroke="#d9c7b0" stroke-width="7" stroke-linecap="round" transform="translate(-2 -5)" filter="url(#b3)"/>')
part(SIL,'url(#alu)',hi='<path d="M770 768 L1022 900" stroke="#fff" stroke-width="14" opacity="0.8" filter="url(#b6)"/>',ao=18)
A('<ellipse cx="735" cy="790" rx="20" ry="30" transform="rotate(-28 735 790)" fill="#1e1e1e"/>')
for t in (0.22,0.62):
    x=1035+(760-1035)*t; y=898+(758-898)*t
    A(f'<line x1="{x+12:.0f}" y1="{y-20:.0f}" x2="{x-16:.0f}" y2="{y+32:.0f}" stroke="#2f3337" stroke-width="9"/>')

# ---------- bash plate
part(BASH,'url(#alu)',hi='<path d="M1340 1222 L1590 1220 C1640 1214 1675 1190 1690 1150" fill="none" stroke="#fff" stroke-width="8" opacity="0.8" filter="url(#b3)"/>',ao=10)
for x,y in ((1380,1236),(1500,1236),(1620,1226)):
    A(f'<circle cx="{x}" cy="{y}" r="7" fill="#3b3f43"/><circle cx="{x-2}" cy="{y-2}" r="3" fill="#ddd"/>')

# ---------- rear mudguard + plate + light
part(RFEND,'url(#white)',hi='<path d="M1150 700 C980 672 820 650 700 640 C560 632 460 645 400 690" fill="none" stroke="#c8241f" stroke-width="12"/>'
     '<path d="M1120 678 C900 646 700 626 520 640" fill="none" stroke="#fff" stroke-width="10" opacity="0.9" filter="url(#b6)"/>',ao=16)
A('<path d="M597 700 L607 700 L620 778 L608 780 Z" fill="#1a1a1a"/>')
part('M558 666 L612 660 L617 692 L563 699 Z','#7a0c0c',hi='<path d="M568 670 L606 666 L608 684 L570 688 Z" fill="#ff3a2a" opacity="0.9"/><path d="M572 672 L600 669" stroke="#fff" stroke-width="3" opacity="0.6"/>')
shadow('M520 775 L700 768 L706 850 L526 858 Z',4,10,0.4,'b6')
part('M520 775 L700 768 L706 850 L526 858 Z','#f3f1e8',ao=6,
     extra_inside='<text x="613" y="827" text-anchor="middle" font-family="Arial Narrow, Arial, sans-serif" font-weight="700" font-size="44" fill="#151515" transform="rotate(-2 613 827)">KNH 262Y</text>')

# ---------- seat
A(f'<path d="{SEATBASE}" fill="#121417"/>')
part(SEAT,'url(#seat)',hi='<path d="M1450 690 C1300 662 1100 645 900 634 C830 630 785 634 762 646" fill="none" stroke="#8fa8ff" stroke-width="12" opacity="0.55" filter="url(#b6)"/>'
     '<path d="M1460 700 C1300 680 1100 664 880 650" fill="none" stroke="#000" stroke-width="2" opacity="0.4" stroke-dasharray="6 6"/>',ao=14)

# ---------- side panel + number board
part(SIDE,'url(#white)',hi='<path d="M1440 790 C1360 778 1270 760 1150 742 C1134 752 1120 768 1110 790 L1452 822 Z" fill="url(#red)"/>'
     '<path d="M1110 820 C1250 830 1380 845 1446 850" stroke="#fff" stroke-width="10" opacity="0.7" filter="url(#b6)"/>',ao=20)
A('<g transform="rotate(-4 1290 880)"><ellipse cx="1293" cy="884" rx="112" ry="64" fill="#000" opacity="0.25" filter="url(#b6)"/>'
  '<ellipse cx="1290" cy="880" rx="112" ry="64" fill="url(#yel)" stroke="#111" stroke-width="5"/>'
  '<text x="1290" y="920" text-anchor="middle" font-family="Impact, Arial Black, sans-serif" font-weight="900" font-size="112" fill="#141414">66</text></g>')
for x,y in ((1135,775),(1430,812),(1170,950),(1400,950)):
    A(f'<circle cx="{x}" cy="{y}" r="8" fill="#2a2c2e"/><circle cx="{x-2}" cy="{y-2}" r="3" fill="#bbb"/>')

# ---------- tank
part(TANK,'url(#white)',
  hi='<path d="M1736 592 C1660 562 1520 562 1400 622 C1350 647 1320 672 1305 692 L1340 697 C1380 662 1470 620 1560 608 C1630 600 1700 612 1741 630 Z" fill="url(#red)"/>'
     '<path d="M1743 642 C1680 627 1590 632 1500 662 C1450 678 1410 702 1395 710 L1432 714 C1470 694 1560 670 1640 668 C1690 667 1725 676 1745 684 Z" fill="url(#blue)"/>'
     '<path d="M1700 500 C1640 480 1530 482 1430 540" fill="none" stroke="#fff" stroke-width="26" opacity="0.95" filter="url(#b12)"/>'
     '<path d="M1720 520 C1650 500 1560 500 1470 540" fill="none" stroke="#fff" stroke-width="6" opacity="0.9" filter="url(#b3)"/>'
     '<path d="M1500 740 C1560 830 1600 880 1640 900" fill="none" stroke="#000" stroke-width="40" opacity="0.25" filter="url(#b16)"/>'
     '<text x="1612" y="790" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-style="italic" font-weight="900" font-size="58" fill="#c21f1a" transform="rotate(-8 1612 790)">XL185R</text>'
     '<text x="1612" y="830" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-weight="700" font-size="22" fill="#1b357f" letter-spacing="6" transform="rotate(-8 1612 830)">RALLY</text>',
  ao=26)
A('<ellipse cx="1545" cy="476" rx="40" ry="10" transform="rotate(-6 1545 476)" fill="#c3c9cf" stroke="#444" stroke-width="3"/>')

# ---------- front fender (near fork re-pasted on top later)
part(FFEND,'url(#white)',hi='<path d="M1800 730 C1950 712 2100 728 2230 785" fill="none" stroke="#c8241f" stroke-width="10"/>'
     '<path d="M1810 716 C1960 706 2100 716 2200 752" fill="none" stroke="#fff" stroke-width="8" opacity="0.9" filter="url(#b3)"/>',ao=12)

# ---------- fairing, lamps, screen
A('<path d="M1846 540 L1800 520 L1800 600 L1846 610 Z" fill="#202224"/>')  # tower bracket
part(FAIR,'url(#white)',
  hi='<path d="M2040 430 C2066 480 2074 540 2064 600 L2030 590 C2040 540 2034 480 2014 440 Z" fill="url(#red)"/>'
     '<path d="M1880 400 C1920 370 1980 372 2010 410" fill="none" stroke="#fff" stroke-width="14" opacity="0.9" filter="url(#b6)"/>'
     '<path d="M1850 620 C1890 660 1970 676 2040 640" fill="none" stroke="#000" stroke-width="30" opacity="0.3" filter="url(#b12)"/>',ao=18)
for c in ((1990,470),(2002,574)):
    A(f'<g transform="rotate(-14 {c[0]} {c[1]})">'
      f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="33" ry="40" fill="#5c6166"/>'
      f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="29" ry="36" fill="url(#lamp)"/>'
      f'<ellipse cx="{c[0]}" cy="{c[1]}" rx="12" ry="15" fill="#f4f1e6" opacity="0.8"/>'
      f'<path d="M{c[0]-29} {c[1]} L{c[0]+29} {c[1]} M{c[0]} {c[1]-36} L{c[0]} {c[1]+36}" stroke="#ffffff" stroke-width="1.5" opacity="0.35"/>'
      f'<ellipse cx="{c[0]-9}" cy="{c[1]-14}" rx="9" ry="6" fill="#fff" opacity="0.9" filter="url(#b3)"/></g>')
part(SCREEN,'url(#screen)',hi='<path d="M1900 360 C1905 310 1925 275 1945 260" stroke="#fff" stroke-width="6" opacity="0.7" filter="url(#b3)"/>',stroke='#33404a')

A('</svg>')
open('paint.svg','w').write('\n'.join(o))
