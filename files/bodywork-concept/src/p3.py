import sys; from common import *
V=sys.argv[1]  # 'trial' or 'rally'
s=S(); A=s.A
RALLY = V=='rally'
# ---- shapes, photo p3 pixel coords (front-left 3/4 view)
if RALLY:
    TANK='M1068 450 C1110 410 1200 392 1290 400 C1360 408 1420 440 1452 486 C1470 520 1468 560 1452 600 C1430 650 1380 700 1320 740 C1270 770 1200 780 1150 762 C1110 745 1090 700 1082 640 Z'
else:
    TANK='M1070 455 C1110 420 1190 405 1270 410 C1340 416 1405 445 1440 488 C1455 512 1456 545 1445 575 C1425 615 1380 650 1320 668 C1260 686 1190 690 1140 676 C1104 664 1088 630 1082 590 Z'
SEAT='M1420 492 C1480 470 1560 440 1650 410 C1720 388 1790 362 1840 344 C1858 340 1868 352 1858 366 C1810 392 1730 428 1640 470 C1560 508 1490 548 1452 574 C1438 560 1428 520 1420 492 Z'
SEATBASE='M1452 574 C1490 548 1560 508 1640 470 C1730 428 1810 392 1858 366 L1862 386 C1810 412 1730 448 1640 492 C1560 530 1490 572 1458 598 Z'
SIDE='M1456 600 C1500 570 1580 528 1660 490 C1690 478 1706 486 1702 512 C1694 570 1676 640 1640 700 C1610 740 1560 752 1515 740 C1478 728 1458 690 1452 640 Z'
RFEND='M1830 372 C1870 354 1910 338 1950 328 C1964 326 1970 336 1962 344 C1930 360 1894 380 1858 398 C1820 416 1790 430 1764 440 L1750 424 C1780 408 1806 386 1830 372 Z'
RVAL='M1764 440 C1790 430 1820 416 1858 398 C1894 380 1930 360 1962 344 L1960 366 C1926 382 1894 400 1862 420 C1826 438 1796 452 1770 462 Z'
FFEND='M775 880 C790 838 840 790 940 742 C1000 714 1060 690 1120 664 C1160 648 1190 640 1200 646 C1205 660 1190 676 1160 690 C1100 716 1040 742 980 772 C900 814 846 860 815 912 C805 930 770 925 775 880 Z'
FSKIRT='M815 912 C836 862 890 818 980 772 C1040 742 1100 716 1160 690 L1162 712 C1102 738 1044 764 986 794 C910 834 852 880 830 930 Z'
BASH='M1238 975 L1290 1058 L1560 1040 C1610 1034 1648 994 1660 950 L1636 942 C1620 984 1590 1004 1556 1008 L1300 1024 Z'
if RALLY:
    FAIR='M872 352 C880 334 900 326 930 324 L1000 320 C1030 320 1046 330 1050 352 C1056 400 1054 450 1044 500 C1030 560 1004 610 966 640 C950 652 934 650 924 636 C896 600 878 540 868 480 C862 430 864 384 872 352 Z'
    FLANK='M1050 352 C1068 356 1084 368 1094 388 L1092 470 C1084 520 1064 566 1036 600 C1020 618 1000 634 978 640 C1010 608 1032 560 1044 500 C1054 450 1056 400 1050 352 Z'
    SCREEN='M888 334 C886 280 900 236 928 208 C962 194 1002 198 1026 214 C1040 246 1046 296 1044 330 C1010 322 940 322 888 334 Z'
else:
    PLATE='M884 452 C888 438 900 432 918 431 L996 429 C1012 429 1022 438 1024 452 L1030 640 C1030 662 1018 676 996 678 L912 682 C890 682 878 670 876 650 Z'
# ---- shadows
for d,dx,dy,op in ([(TANK,8,22,.45),(SEAT,6,24,.5),(SIDE,6,16,.4),(RFEND,4,20,.35),(FFEND,4,20,.4),(BASH,4,10,.35)]+
                   ([(FAIR,10,18,.45)] if RALLY else [(PLATE,8,16,.4)])):
    s.shadow(d,dx,dy,op)
# ---- bash plate
s.part(BASH,'url(#alu)',hi='<path d="M1300 1028 L1556 1012 C1600 1006 1630 984 1646 948" fill="none" stroke="#fff" stroke-width="8" opacity="0.8" filter="url(#b3)"/>',ao=10)
for x,y in ((1330,1040),(1450,1034),(1580,1022)):
    A(f'<circle cx="{x}" cy="{y}" r="6" fill="#3b3f43"/><circle cx="{x-2}" cy="{y-2}" r="2.5" fill="#ddd"/>')
# ---- rear mudguard + light + plate
s.part(RVAL,'#c9cac6',ao=8)
s.part(RFEND,'url(#white)',hi='<path d="M1770 432 C1840 398 1900 364 1960 336" stroke="#c8241f" stroke-width="7" fill="none"/>'
       '<path d="M1790 410 C1860 378 1930 342 1990 312" stroke="#fff" stroke-width="6" opacity="0.9" fill="none" filter="url(#b3)"/>',ao=10)
s.part('M1922 356 L1958 340 L1960 360 L1924 376 Z','#7a0c0c',hi='<path d="M1928 358 L1954 346 L1955 356 L1929 368 Z" fill="#ff3a2a"/>')
A('<path d="M1936 372 L1942 370 L1948 412 L1942 414 Z" fill="#1a1a1a"/>')
s.shadow('M1910 404 L1986 380 L1990 432 L1914 458 Z',3,8,.4,'b6')
s.part('M1910 404 L1986 380 L1990 432 L1914 458 Z','#f3f1e8',ao=4,
       hi='<text x="1950" y="430" text-anchor="middle" font-family="Liberation Sans Narrow, Liberation Sans, sans-serif" font-weight="700" font-size="17" fill="#151515" transform="rotate(-17 1950 430)">KNH 262Y</text>')
if RALLY:  # tail rack / tool tube
    A('<path d="M1700 418 L1880 334 M1716 446 L1896 362" stroke="#2a2c2e" stroke-width="9" stroke-linecap="round"/>')
    s.part('M1745 455 L1800 430 L1812 470 L1758 496 Z','#1e2022',ao=4)
# ---- side panel
s.part(SIDE,'url(#white)',hi='<path d="M1456 600 C1500 570 1580 528 1660 490 C1690 478 1706 486 1702 512 L1700 530 C1620 556 1530 600 1462 640 Z" fill="url(#red)"/>'
       '<path d="M1470 690 C1540 650 1620 610 1690 580" stroke="#fff" stroke-width="8" opacity="0.6" filter="url(#b6)" fill="none"/>',ao=18)
oval(s,1585,640,64,46,-24,'66',72)
for x,y in ((1478,612),(1680,505),(1520,728),(1650,660)):
    A(f'<circle cx="{x}" cy="{y}" r="6" fill="#2a2c2e"/><circle cx="{x-2}" cy="{y-2}" r="2.4" fill="#bbb"/>')
# ---- seat
A(f'<path d="{SEATBASE}" fill="#121417"/>')
s.part(SEAT,'url(#seat)',hi='<path d="M1440 500 C1560 452 1700 400 1846 348" fill="none" stroke="#9fb4ff" stroke-width="10" opacity="0.55" filter="url(#b6)"/>'
       '<path d="M1450 545 C1560 494 1700 430 1850 360" fill="none" stroke="#000" stroke-width="2" opacity="0.4" stroke-dasharray="6 6"/>',ao=12)
# ---- tank
if RALLY:
    th=('<path d="M1452 560 C1400 600 1300 640 1180 660 L1084 668 L1086 700 L1180 696 C1300 682 1410 640 1460 600 Z" fill="url(#red)"/>'
        '<path d="M1458 610 C1400 650 1300 690 1190 704 L1090 712 L1094 736 L1190 732 C1300 716 1404 676 1456 640 Z" fill="url(#blue)"/>'
        '<path d="M1110 440 C1180 412 1300 410 1400 452" stroke="#fff" stroke-width="22" opacity="0.95" fill="none" filter="url(#b12)"/>'
        '<text x="1270" y="612" text-anchor="middle" font-family="Liberation Sans, sans-serif" font-style="italic" font-weight="900" font-size="58" fill="#c21f1a" transform="rotate(8 1270 612)">XL185R</text>'
        '<path d="M1300 740 C1360 720 1420 680 1450 640" stroke="#000" stroke-width="40" opacity="0.25" fill="none" filter="url(#b16)"/>')
else:
    th=('<path d="M1448 540 C1400 572 1300 600 1180 610 L1084 612 L1086 640 L1180 640 C1300 632 1410 600 1452 568 Z" fill="url(#red)"/>'
        '<path d="M1444 584 C1400 612 1300 640 1190 652 L1092 656 L1098 676 L1190 676 C1300 666 1400 638 1438 612 Z" fill="url(#blue)"/>'
        '<path d="M1110 446 C1180 418 1300 418 1395 456" stroke="#fff" stroke-width="22" opacity="0.95" fill="none" filter="url(#b12)"/>'
        '<text x="1265" y="570" text-anchor="middle" font-family="Liberation Sans, sans-serif" font-style="italic" font-weight="900" font-size="52" fill="#c21f1a" transform="rotate(7 1265 570)">XL185R</text>')
s.part(TANK,'url(#white)',hi=th,ao=24)
A('<ellipse cx="1300" cy="414" rx="34" ry="9" transform="rotate(8 1300 414)" fill="#c3c9cf" stroke="#444" stroke-width="3"/>')
# ---- front mudguard
s.part(FSKIRT,'#c4c5c1',ao=8)
s.part(FFEND,'url(#whiteL)',hi='<path d="M760 900 C800 840 880 790 960 752 C1040 712 1120 676 1190 650" stroke="#c8241f" stroke-width="8" fill="none"/>'
       '<path d="M790 870 C850 810 940 764 1020 726" stroke="#fff" stroke-width="8" opacity="0.9" fill="none" filter="url(#b3)"/>',ao=10)
# ---- front: headlamp plate or rally fairing
if RALLY:
    s.shadow(FLANK,8,14,.4)
    s.part(FLANK,'url(#white)',hi='<path d="M1020 560 L1094 470 L1094 520 L1010 620 Z" fill="url(#red)"/>'
           '<path d="M1060 380 C1070 420 1070 480 1064 520" stroke="#000" stroke-width="20" opacity="0.15" fill="none" filter="url(#b6)"/>',ao=10)
    s.part(FAIR,'url(#white)',hi='<path d="M860 560 C920 572 990 572 1060 556 L1060 700 L860 700 Z" fill="url(#red)"/>'
           '<path d="M860 530 C920 542 990 542 1060 526 L1060 546 C990 562 920 562 860 550 Z" fill="url(#blue)"/>'
           '<path d="M890 346 C930 336 990 334 1030 340" stroke="#fff" stroke-width="10" opacity="0.9" fill="none" filter="url(#b6)"/>',ao=16)
    A('<path d="M896 386 L1032 380 L1026 446 C990 458 930 460 900 450 Z" fill="#2c2f32"/>'
      '<path d="M902 392 L1026 386 L1021 440 C988 451 932 453 905 444 Z" fill="url(#lamp)"/>'
      '<path d="M904 416 L1024 412 M964 389 L964 450" stroke="#fff" stroke-width="1.5" opacity="0.4"/>'
      '<ellipse cx="934" cy="402" rx="20" ry="7" fill="#fff" opacity="0.85" filter="url(#b3)"/>'
      '<text x="962" y="512" text-anchor="middle" font-family="Liberation Sans, sans-serif" font-weight="900" font-size="44" fill="#141414">66</text>')
    s.part(SCREEN,'url(#screen)',hi='<path d="M900 300 C904 260 918 230 936 214" stroke="#fff" stroke-width="5" opacity="0.7" fill="none" filter="url(#b3)"/>',stroke='#33404a')
else:
    s.part(PLATE,'url(#yel)',hi='<path d="M890 450 C930 436 990 434 1020 448" stroke="#fff" stroke-width="10" opacity="0.6" fill="none" filter="url(#b6)"/>',ao=12,stroke='#222')
    lamp(s,954,512,38,56,0)
    A('<text x="954" y="660" text-anchor="middle" font-family="Liberation Sans, sans-serif" font-weight="900" font-size="54" fill="#141414">66</text>')
open(f'paint_{V}.svg','w').write(s.svg())
