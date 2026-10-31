# Rear suspension render (31 Oct 2026)

Joel's CRF250R arm (from his STEP model), his v2 windowed rocker (traced from his Fusion screenshot, 30 mm thick with the 11 mm dogbone slot), the tapered 82 mm dogbone (10 wide at the rocker, 38 at the lug), and the XR250R 380/95 shock with the clevis at the bottom, all on the XL125R frame scan. The frame scan's rear loop is straightened onto the centreline. The wheel is a stand-in.

- [Hero, three-quarter front left](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-hero.png)
- [Left side at sag](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-side.png)
- [Linkage close-up from below](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-linkage.png)
- [Arm see-through, rocker and dogbone](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-xray.png)
- [Droop, sag and bump](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-travel.png)
- [Animation through the travel (GIF)](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-travel.gif)

## Whole bike with the CR forks

- [Side](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-bike-side.png)
- [Three-quarter front](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-bike-hero.png)
- [Animation, both ends droop to bump (GIF)](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-bike-travel.gif)
- [Three-quarter rear](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-bike-rear.png)

Whole-bike renders use Joel's Chassis Bench settings (50 mm spacer, 47 mm total offset, stack 215, slide 0, 935 mm fork, 27.5 deg to the frame vertical, 74 mm front / 79 mm rear sag, arm lug 200 / 50 with the arm model shifted ~10 mm to suit). Joel confirmed the bench's head tube position is measured (632 mm pivot to head), so the scan's front, ~70 mm out, is eased onto it with a correction that starts at zero at the shock top mount and grows smoothly to the head tube (no kinks; everything behind the shock mount untouched). Result at sag: about 29.4 deg head angle, 141 mm trail, 1413 mm wheelbase (bench: 29.1 / 139 / 1403; the small gap is Joel's v2 rocker). The animation keeps the tyres on the floor. Tube spacing (210 mm), yoke shapes and bars are stand-ins.

Notes (rear-only renders above): the linkage is solved with the arm model's own lug hole, which is 209 mm along and 56 mm below the arm line. Joel's tape on his arm said 200 / 50. With the model's lug the arm tops out at 28.4 deg down (not ~24), with 252 mm vertical wheel travel and about 30% rising rate. Shock details (clevis, seat at ~72 mm, ~78 mm OD spring) are estimates.

Rerun: step2stl.py (STEP to parts), v2profile.py (rocker outline), build.py (scene.json), then serve this folder, `npm i three@0.160.0`, and `node shot.js views.json`.
