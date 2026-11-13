# Publishing notes and post texts

Texts for each site. Every listing carries the same status line: **living project, updated continuously — the latest version is always at https://github.com/Johub1/worlds-largest-semiconductor-cluster-pyeongtaek**.

## Repository description (GitHub, Hugging Face, Zenodo) — one line
Unofficial open 3D model of the Samsung Electronics Pyeongtaek campus (fabs P1–P4), built only from public sources, with a concept interior, utility systems and EHS layers for education.

## Topics / tags
semiconductor, fab, cleanroom, 3d-model, gltf, step, dxf, ehs, process-safety, open-data, digital-twin, education

## GitHub
- Large files: `pyeongtaek_p1-p4_full.obj` (about 60 MB) and `pyeongtaek_p1-p4_3d.dxf` (about 62 MB) are under the 100 MB hard limit but above the 50 MB warning. `.gitattributes` routes model files to Git LFS; alternatively attach them to a Release.
- GitHub Pages: publish `viewer/index.html` (single file, works offline) as the project page.

## Sketchfab / GrabCAD — model description
An unofficial massing model of the world's largest semiconductor manufacturing complex: four fabs (each about 520–650 m long, 200 m wide, 83 m high), the EUV building, utility buildings, cooling towers, office buildings, bridges, the neighbouring substation, gas plant and wastewater plant. Outlines are measured from public satellite imagery; heights and floor arrangement are partly estimated. The interior is a generic 300 mm fab concept, not the real layout. Every element carries a confidence grade and source keys. Licence CC BY 4.0. Not affiliated with Samsung Electronics.
- Upload `models/pyeongtaek_p1-p4_full.glb` to Sketchfab and `models/pyeongtaek_p1-p4_buildings.step` to GrabCAD.

## LinkedIn — post
I built an open 3D model of the Samsung Electronics Pyeongtaek campus, the largest semiconductor manufacturing complex in the world, using public sources only.

What is in it:
- Four fabs, P1 to P4, with outlines measured from public satellite imagery
- Eight floors per fab with a concept interior: cleanroom, clean subfab, utility subfab, plenum
- Concept utility systems: chilled water, process cooling water, gases, exhaust, wastewater, chemicals, ultrapure water, power
- EHS layers: gas detection points, emergency equipment, and an egress travel-distance screening
- Products by line, from official announcements and press
- 170+ sources, each claim graded A to D by how well it is supported

What it is not: it is not the real equipment layout. Interior, utility routes and EHS layers are a generic reference design, and security equipment is deliberately left out. The project is unofficial and not affiliated with Samsung Electronics.

Why: as a safety engineering student I wanted a model that shows how a modern fab is put together, from the substation to the scrubber stack, that anyone can open in a browser.

Files: glTF, OBJ, STL, STEP, DXF, CSV and a single-file viewer. Licence: CC BY 4.0 for the model and documents, MIT for the code.

This is a living project and I keep updating it as new public material appears. Latest version and change log: https://github.com/Johub1/worlds-largest-semiconductor-cluster-pyeongtaek

## Zenodo / Hugging Face — abstract
This dataset is an unofficial, education-oriented 3D model of the Samsung Electronics Pyeongtaek campus (fabs P1–P4) compiled exclusively from public material: official newsrooms and sustainability reports, regulatory filings, the public building register, public maps, public satellite imagery, international and Korean press, peer-reviewed papers and patents. Building outlines are measured from imagery; the interior, utility systems and EHS layers are a generic reference design. Each element carries a confidence grade (A official, B imagery, M map or register, C estimate, D concept) and source keys. Formats: glTF, OBJ, STL, STEP, DXF, CSV, JSON and an offline HTML viewer.
