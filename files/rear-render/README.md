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
- [Three-quarter rear](https://raw.githubusercontent.com/Blevo66/chassis-bench/claude/project-thread-bk4fwa/files/rear-render/render-bike-rear.png)

Front end from Joel's numbers: CR yokes 20 mm offset, axle 40 mm ahead of the tube centreline (60 mm total), legs 100 mm below the axle, 935 mm from the top of the fork to the axle fully extended, with a 50 mm internal spacer (885 mm extended), tube tops flush with the top yoke, 75 mm front sag. The head tube angle comes off the frame scan. The bike is pitched so both tyres touch the ground (front 346 mm radius, rear 323) with 95 mm of rear sag. That gives about 24.6 deg head angle, 92 mm trail and a 1391 mm wheelbase (without the spacer: 26.4 deg, 105 mm, 1412 mm), all as good as the scan. Tube spacing (210 mm), the yoke shapes and the bars are stand-ins.

Notes: the linkage is solved with the arm model's own lug hole, which is 209 mm along and 56 mm below the arm line. Joel's tape on his arm said 200 / 50. With the model's lug the arm tops out at 28.4 deg down (not ~24), with 252 mm vertical wheel travel and about 30% rising rate. Shock details (clevis, seat at ~72 mm, ~78 mm OD spring) are estimates.

Rerun: step2stl.py (STEP to parts), v2profile.py (rocker outline), build.py (scene.json), then serve this folder, `npm i three@0.160.0`, and `node shot.js views.json`.
