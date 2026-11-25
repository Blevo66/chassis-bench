# Left bar controller housing v2, CURRENT (2026-11-25)
Joel: buttons in an ARC, indicators side by side, one above and two below. v2 = arch of 5 on a 26 mm radius: LIGHTS on top,
INDICATOR L (inboard) and R (outboard) either side, MODE bottom-inboard, HORN bottom-outboard (thumb side, raised ring).
Which button sits where is my reading; swap freely. 75 wide x 64 tall x 59 deep, ~115 g solid ASA, no clashes.
Source ../src/lctrl2.py, renders ../renders/lc2-*.png, files xl-left-controller-v2-*. Same guesses as v1.

## v1 (5 buttons in rows)
For a 22.2 mm bar (Joel). The MCP23017 button chip stays inside the controller (Joel's pick). 4-core screened cable out the bottom.
- Body: 52 wide x 76 tall, rider face carries 5 x 12 mm buttons (horn bottom with a raised ring, indicators L/R middle, lights/mode top). Open bottom.
- Front clamp cap: 4 x M4 from the front into heat-sets, two above and two below the bar.
- Bottom lid: 4 x M3, MCP23017 breakout on 2 posts, TPU grommet for the 5 mm cable, 3 mm drain. TPU seal ring.
- ~93 g solid (ASA), printed parts only. No clashes; cable is a squeeze fit in the grommet on purpose.
GUESSES: button size and depth (generic 12 mm IP67), MCP23017 breakout size, cable and grommet size. Clutch perch not modelled.
Source: ../src/lctrl1.py. Renders: ../renders/lc1-*.png. Assembly: xl-left-controller-v1-assembly.step
