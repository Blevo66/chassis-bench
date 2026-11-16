# v7 simple: big flat panels (option A of "make it simpler")

The same envelope as v6 (Kove-style pods, flat filler deck, 80 mm vertical rear face, pointed front), built from **big flat folded panels** like Joel's style photo. There are no small triangles on the sides; triangles are used only at the short front point. v6, with its 88 small triangles, is still in the folder above.

| | |
|---|---|
| Capacity | 7.7 L per half, **15.4 L total** (gross). The pods are deep; raise the pod bottoms to bring it down |
| Panels per half | rear face (flat, 80 mm tall), 3 wrap-round strips with **7 folds each**, 2 small front-point pieces, baffle |
| Flat faces | 25 per half |
| Filler pad | flat deck on `strip-2`, 127 mm clear. The 100 mm circle is etched, centre at X 229, 106 mm out from the spine centre, 513 up |
| Steel | 1.2 mm DC01, about 2.7 kg per half |

The DXFs are for the left half: mirror them for the right. Fold lines are on `ETCH_FOLD`, labelled with their angle and `out`/`IN`. Each strip closes on itself at the inner top edge.
Mock-up: `mockup-*.stl`, 3 pieces per side, all fitting the X1C bed.
Rebuild: `python3 build7.py OUTDIR && python3 render7.py OUTDIR`
