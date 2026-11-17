# XL125R rear side tanks + slim front pair (idea, 17 Nov)

Joel: "maybe try rear tanks?" So the fuel is split: a **slimmer front pair** (the v9 twin half-saddles with the pod bottoms raised and narrowed) plus **a faceted rear side tank each side**, outboard of the rear frame rails, under the seat line and behind your legs.

| | Front pair (slim v9) | Rear pair | Total |
|---|---|---|---|
| Capacity (gross) | 9.2 L (4.6 each) | 3.1 L (1.56 each) | **12.3 L** |
| Size | X 20 to 357, 328 wide, pod bottoms ~310 above pivot (v9 was 178) | X -80 to -380, Y 147 to 246 each side (~490 across), Z 228 to 350 | |
| Folds | longest 149 mm | longest 120 mm, 5 ring strips + 2 small end faces | |
| Steel 1.2 mm | ~2.3 kg each | ~0.8 kg each | |

Clearance to the frame scan: rear left 10 mm. The scan's rear loop is skewed in Y, so the right reads 67 mm; trust the mock-up, not that number. The rear tyre at full bump and the chain stay well inboard (tyre ±55 mm, tanks start at 147 out).

## Things this changes
- **Feed:** the rear tanks' bottoms (~230-285 above the pivot) are lower than the front pods' (~310), so they **can't drain into the front**. Either give them their own tap tee'd into the carb line (needs the float bowl below ~220 above the pivot: measure it), or fit a small 12 V transfer pump into the front pods like the modern rally bikes do.
- **Exhaust:** the low-route pipe and silencer must not come up the right side under the seat, or the right rear tank has to be shorter/higher.
- **Fillers:** each rear tank needs its own small cap (or link both rears with a crossover under the mudguard and fill one).
- **Mounts:** inner face is flat against the rail; clamp to the rail with two P-clips/rubber-lined saddles each, plus a lower strap to the subframe strut. Nothing welded to the frame.
- Weight sits behind and low, which is what you want on a rally bike, but it's off the back wheel's unsprung side so fine.

## Files
- `rear.py` builds the rear tanks (`python3 rear.py OUT`), `render_rear.py OUT FRONTDIR` renders both pairs together.
- `rear-flat-strip-1..5.dxf`, `rear-flat-end-front/rear.dxf`: LEFT tank, mirror for right. Layers CUT / ETCH_FOLD / NOTE like the front.
- `mockup-rear-tank-{left,right}-{front,rear}.stl`: 2 pieces each, 150 long, fit the X1C bed.
- `front-slim/`: the slim front pair, built with `ZBF=300 YOF=172 python3 ../twin-saddle/build9.py front-slim` (same parts list as v9).
- `front-plus-rear-views.png`, `front-plus-rear-3d.png`, `rear-flat-patterns.png`.
