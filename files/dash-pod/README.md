# Dash pod and tablet models (for placing in Fusion)

**STEP (use these in Fusion):** `xl-dash-pod.step` and `galaxy-tab-a9-rough.step` are proper solids, each with coloured bodies: the pod has shell, TPU seal, screen glass and screws. The scripts that build them (CadQuery) are `pod.py` and `tab.py`. The STEPs use the same axes and origins as the STLs below. The STEP pod has 2.6 mm pilot holes in the back bosses, which are placeholders.


Units are mm, and Z is up. When Fusion asks for units on insert, pick millimetres.

| File | What it is |
| --- | --- |
| `xl-dash-pod.stl` | Printed pod as modelled: shell, visor, seal line, back cover with bosses and exit spigot, screen glass. 132.6 W x 98.6 H, 53 deep including the visor and spigot. |
| `xl-dash-pod-with-loom.stl` | The same pod plus the boot, the Tesa-wrapped tail and the three DTM plugs hanging below. Use it for clearance checks. |
| `galaxy-tab-a9-rough.stl` | Rough Galaxy Tab A9 (8.7"): 211 x 124.7 x 8 mm, R9 corners, landscape. The screen area is 0.3 mm proud. |

**Axes**
- X is to the rider's right.
- Y is forward, away from the rider, so the screens face -Y.
- Z is up.

**Origins**
- Pod: the centre of its front face, round the screen. The visor sticks out 13 mm towards the rider.
- Tab: the centre of its back face.

**Status:** the pod is concept-level. Its size will change once the MOS board arrives and gets measured, because the shell wraps a 122 x 87.5 mm board. The mounting bosses on the back are 60 mm apart and 6 mm radius, and they're placeholders. The tablet sizes are from Samsung's spec as I remember it, so check them against your actual tab.
