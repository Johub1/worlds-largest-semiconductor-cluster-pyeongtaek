# Samsung Electronics Pyeongtaek Campus P1–P4 — open 3D model (unofficial), v7.25 (English edition)

> **Status: living project, updated continuously.** This model is revised whenever new public material is found or an error is reported; the current version and every change are listed in `CHANGELOG.md`. Corrections backed by a public source are welcome through GitHub Issues. Latest version: https://github.com/Johub1/worlds-largest-semiconductor-cluster-pyeongtaek

**DOI (v7.23 only):** [10.5281/zenodo.24209049](https://doi.org/10.5281/zenodo.24209049). This DOI identifies the archived v7.23 package, not the files in this repository after v7.23; a later version gets its own DOI once its GitHub release is archived on Zenodo

**Mirrors (v7.23):** [Zenodo](https://zenodo.org/records/24209049) · [Hugging Face](https://huggingface.co/datasets/Johojun/pyeongtaek-semiconductor-campus-open-model) · [Kaggle](https://www.kaggle.com/datasets/hojunjoooo/pyeongtaek-campus-open-3d-model-v7-23) · [Internet Archive](https://archive.org/details/pyeongtaek_p1-p4_open_model_v7.23_en) · [Printables](https://www.printables.com/model/1913576-pyeongtaek-semiconductor-campus-p1-p4-open-model-v) · [Sketchfab](https://skfb.ly/pQ8or). Announcement: [LinkedIn](https://www.linkedin.com/feed/update/urn:li:activity:7527149024009670656/). The GitHub repository is always the newest version; mirrors may lag behind.

An educational, open-source 3D model of the world's largest semiconductor manufacturing cluster, built **only from public material**.

> **Unofficial.** This project is not affiliated with, endorsed by, or reviewed by Samsung Electronics or any other company named here. No non-public drawings, internal documents or information obtained through site access were used. Building outlines are measured from public satellite imagery. Heights and floor arrangement are partly estimated. **The interior equipment layout, utility routes and EHS layers are a generic reference design (concept), not the actual facility layout.** Positions of security equipment (cameras, access control, guard routes) are deliberately not modelled. No company logos are used.

![exterior](preview/01_exterior.png)

## At a glance

| Item | Content |
|---|---|
| Scope | The wider Pyeongtaek complex: fabs P1, P2, P3, P4, the EUV building (V2), utility buildings, cooling tower banks, office and support buildings, the KEPCO Godeok substation lot, the Linde Korea plant, the Godeok public wastewater treatment plant, the P5 construction site, the Air Products and Air First gas plants, the Samsung logistics warehouse west of Complex 2, and map points for supplier sites and construction camps |
| Building elements | 1,458 elements (boxes and cylinders) with name, layer, confidence grade, source keys and a note each |
| Concept interior | 86,620 equipment boxes of 26 types on 8 floors per fab, 608 OHT rail segments, 10,440 structural members |
| Concept utilities | 29 systems in 8 groups, 1,521 route segments (thermal, PCW, gas, exhaust, wastewater, chemicals, UPW, power) |
| Concept EHS | 960 gas/exhaust flow lines, 1,152 gas detector points, 1,552 emergency equipment points, 15,320 egress travel-distance samples |
| Sources | 180 keyed sources in three tiers: 39 official/register/map, 42 international (Reuters, TrendForce, DIGITIMES, Linde, Air Products, GE Vernova, journals, patents, standards), 99 Korean press and local |
| Units, origin | metres; local tangent plane at WGS84 37.02 N, 127.06 E; X east, Y north, Z up |
| Imagery date | 2025-12-22 (0.5 m) for dimensions; zoom-18 mosaic re-acquired 2026-11-12 for re-checks |

## Files

| Path | Content |
|---|---|
| `viewer/index.html` | Single-file browser viewer that works offline (data and three.js r128 are inlined). Fab and floor selection, section cuts, layer toggles, EHS and utility layers, click for evidence and sources |
| `models/pyeongtaek_p1-p4_full.glb` | Whole model, glTF binary (15 MB) |
| `models/pyeongtaek_p1-p4_full.obj` + `material.mtl` | Whole model, OBJ (60 MB) |
| `models/pyeongtaek_p1-p4_exterior.stl` | Exterior shell only (for printing or massing) |
| `models/pyeongtaek_p1-p4_buildings.step` | CAD solids: buildings, slabs, zones, support rooms (equipment excluded for size) |
| `models/pyeongtaek_p1-p4_3d.dxf` | 3D DXF, 166 layers |
| `drawings/layout_plan_2d.dxf` | 2D layout plan in model coordinates, 178 layers such as `3F_ETCH`, `3F_EHS_EGRESS_DIST_M` |
| `drawings/floor_plans/` | 36 floor plans (4 fabs × 9 levels) with supplier legends |
| `drawings/ehs/` | 4 egress travel-distance screening sheets (lower cleanroom) |
| `drawings/utility/` | Campus utility concept plans and a flow summary sheet |
| `data/campus.json` | The full model as data (everything the viewer and exports are made from) |
| `data/*.csv` | Elements, equipment, floors, phases, vendors, structure, EHS and utility tables |
| `preview/` | 27 screenshots of the viewer |
| `src/` | Export, viewer and check scripts that run on `data/campus.json`; `src/generator_ko/` holds the original generator and the translation tables (see "Rebuilding") |
| `SOURCES.md` | All 180 sources with URLs, grouped by tier |
| `CONSULTATION.md` | Record of what other AI models proposed and what was adopted, verified, held or rejected |

## Coordinates

- Local metric frame: `X = (lon − 127.06) × 88,782`, `Y = (lat − 37.02) × 111,194.9`, Z up from ground.
- `data/*.csv` and `drawings/layout_plan_2d.dxf` use these coordinates directly.
- The 3D exports (GLB, OBJ, STL, STEP, 3D DXF) are shifted by −1,500 m in Y so that the campus sits near the origin. GLB uses the glTF convention (Y up).
- Rotated boxes carry `rot` in degrees, counter-clockwise about Z around the box centre.

## Confidence grades

| Grade | Meaning |
|---|---|
| A | Confirmed by official material, press or regulatory filings |
| B | Dimensions estimated from public satellite imagery (0.5 m resolution, error of a few metres) |
| M | Confirmed by a public map label or the public building register (a map coordinate may be an entrance or a representative point, not a building outline) |
| C | Estimate or assumption |
| D | Generic concept, not site-specific information |

Existence, building match, location, shape and numbers are graded separately in the notes. A request to "make it definite" does not raise a grade; only a source does.

## Source priority

Source priority: (1) official material and filings of Samsung Electronics and its contractors, and public registers; (2) international wire services and trade media outside Korea (Reuters, TrendForce, DIGITIMES, etc.); (3) Korean press. Where one fact has several sources, the higher tier is listed first. International outlets often cite Korean reports, so the original report is kept alongside.

Korean press still makes up most of the list because contract amounts, phase names, the substation, water volumes and permits are reported in detail only locally; `SOURCES.md` explains this and groups every source by tier.

## Fab dimensions and cleanroom area

| Fab | Main body (m) | Incl. east end block (m) | Width (m) | Height (m) | Model cleanroom area, two levels (㎡) | Brokerage report figure (㎡) |
|---|---|---|---|---|---|---|
| P1 | 519 | 549 | 201 | 83 (C) | 135,598 | about 135,300 |
| P2 | 521 | 552 | 204 | 83 (C) | 138,908 | about 148,500 |
| P3 | 623 | 651 | 208 | 83 (C) | 174,748 | about 181,500 |
| P4 | 617 | 654 | 208 | 83 (C) | 172,852 | about 181,500 |

- P1: the press plan figure that names P1 (about 520 m × 200 m, Etoday 2022-09-07) agrees with the satellite measurement. The 83 m comes from a ZDNet article (518 × 201 × 83 m) that speaks of "the production line of the Pyeongtaek campus" without naming P1, so the height is a model assumption from a press figure whose subject is unsettled (corrected in v7.25; it was shown as grade A before).
- P2, P3, P4 heights are not public; in drone photos taken from the west the four fabs look about the same height, so the same 83 m is kept as a concept assumption — it is not a copy of a confirmed P1 height.
- Press figures that disagree with the measurement (for example "P3 700 m") are recorded in the notes; the measurement is used.
- Area policy: official material of Samsung Electronics, Samsung C&T, Samsung E&A and Samsung Heavy Industries comes first; press figures are reference only. Official figures found: campus site 2.89 million㎡ / 2.83 million㎡ (Samsung newsrooms), whole Pyeongtaek complex total floor area 3,967,000㎡ (Samsung C&T portfolio), and a figure worded as "total floor area 128,900㎡" for P2 (Samsung Newsroom; Samsung E&A utility project page) whose scope is unsettled — it is not used as the floor area of the P2 fab and is not compared with the model plan. No per-building areas for P1, P3 or P4 were found in official material.

## Floor arrangement (estimated; floor heights are assumed)

| Level | Elevation (m) | Use |
|---|---|---|
| RF | 66– | Roof: exhaust scrubbers, fans, stacks, pipe racks |
| 8F | 56–66 | FFU plenum and roof truss (upper) |
| 7F | 48.5–56 | Upper cleanroom (FAB) |
| 6F | 41–48.5 | CSF · clean subfab (upper) |
| 5F | 33–41 | FSF · utility subfab (upper) |
| 4F | 24–33 | FFU plenum and truss (lower) |
| 3F | 16.5–24 | Lower cleanroom (FAB) |
| 2F | 9–16.5 | CSF · clean subfab (lower) |
| 1F | 0–9 | FSF · utility subfab (lower) |

Public basis: 8 floors above ground (construction supervisor record for P2), four cleanrooms on two levels (trade press), a visitor window corridor on P1 3F (press), and the FAB + CSF + FSF three-level structure of 300 mm lines (peer-reviewed occupational hygiene paper).

Floor labels such as 3F and 7F in this model, in the viewer and in the generator's phase table are concept levels of the generic section above. The filings say only "lower level" and "upper level"; they do not give floor numbers, heights or boundaries.

## Phase positions (P3, P4)

| Fab | Lower west | Lower east | Upper west | Upper east |
|---|---|---|---|---|
| P3 | Ph1 (C, inferred) | Ph3 (A) | Ph2 (A) | Ph4 (A) |
| P4 | Ph1 (A) | Ph2 (A) | Ph3 (A) | Ph4 (A) |

Positions come from the contract names in regulatory filings by Samsung C&T, Samsung E&A and Samsung Heavy Industries (for example "P4 Ph1 (lower west) FAB building / complex building finishing work"). P1 and P2 could not be confirmed.

## Surrounding facilities (added in v7.17)

Model extent is now about 3.9 km × 3.6 km (X −1,950 to 1,950 m, Y −650 to 2,900 m).

| Facility | Basis for identity | Geometry | What is modelled |
|---|---|---|---|
| Air Products Korea Pyeongtaek plant (northeast, adjacent) | Kakao Map and Google Maps labels; company press releases | Read from zoom-18 satellite imagery, ±5 m | Site pad, 3 domed tanks, 4 buildings, process equipment area, 2 cooling towers |
| Air First Pyeongtaek plant (about 1 km south) | Kakao Map label; press | Read from satellite imagery | Site pad, 2 domed tanks, 3 building groups, process equipment area |
| Samsung Electronics logistics warehouse (west of Complex 2, Godeok-dong 1696-1) | Kakao Map label | Read from satellite imagery: about 177 × 320 m, height about 21 m from shadow length | Main building and 3 annexes |
| Linde Korea plant, Godeok public wastewater treatment plant, KEPCO Godeok lot | Building register and map labels (earlier versions) | Imagery | As before |
| Samsung E&A construction camps, SEMES office, Wonik IPS site, Hanyang ENG | Kakao Map labels | Points only | Map markers |

- **Logistics warehouse**: press in 2025-12 reported that the CDC logistics centre on the planned P6 site would be demolished by May 2026 and that the demolition permit had been issued. A CDC (Central Distribution Center) handles finished products, and Samsung Electronics is building a home-appliance CDC of about 110,000㎡ in the Pyeongtaek Poseung district (started 2025-03, completion targeted 2027-06). Read together, this is a product distribution centre being relocated, not a fab materials warehouse being closed. No source states directly that the modelled building is that CDC or that Poseung replaces it, so both are inferences; the imagery is dated 2025-12-22 and the current state was not confirmed.
- **What each neighbour supplies** (from company material, filings and press; stored in each element's note):

| Company | Role at Pyeongtaek | Basis |
|---|---|---|
| Air Products Korea | Nitrogen, oxygen, argon, hydrogen; ultra-high-purity nitrogen plants, hydrogen generators, a liquefier, bulk specialty gas supply system; supplies fab 1 | Company press release, trade press, Korean press |
| Air First | Oxygen, nitrogen, argon, hydrogen by underground pipeline to P3 and P4; ASU and SMR at the plant | Press; company job posting |
| Linde Korea | Main industrial gas supplier to the complex; eighth on-site air separation unit; on-site hydrogen | Company press releases |
| Samsung E&A | Green building, substation, complex building, air pollution control, UT building, rooftop exhaust, UPW, water treatment | Regulatory filings, project pages |
| SEMES | Overhead hoist transport (OHT) in P1 | Official video, tour press |
| Wonik IPS | Deposition equipment (PECVD, ALD, thermal); reported orders for the second Pyeongtaek fab | Company site, ETNews English |
| Hanyang ENG | General piping (P4, P5), hook-up and CCSS installation | Regulatory filings, press |

- A marker shows where a company has a site; what is done at that particular site was not confirmed.
- Tanks and process equipment are simplified as boxes; their heights are arbitrary. Uses of individual buildings inside the gas plants are estimates from shape.
- See `preview/24_surroundings_wide.png` to `27_air_first_plant.png`.

## Bridges and parking

- **17 bridges** in the layer `Connecting bridges`, drawn in bright blue and labelled in the viewer: overbridges between each fab and the utility building beside it, links to the EUV building, a road-crossing bridge to the office complex, and two truss pipe rack bridges. Press reports that buildings are linked by overbridges carrying people, wafers, gases and chemicals; the individual positions are read from satellite imagery, and heights are assumed.
- **Parking**: the Complex 2 parking building (public building register: 42,285.72㎡ building area, 20.99 m, 4 floors and 1 basement, 4,858 indoor spaces), the technology building parking tower and the office complex parking tower (public map labels), and the employee parking lot with its solar canopy (OSM boundary; canopy location estimated).
- See `preview/23_west_bridges_parking.png`.

## Products by line (official announcements and press only)

Only what appears in Samsung Electronics official announcements and press is listed. The zone inside a building is given only where it is public; otherwise it is marked 'zone not public'. Product mix changes often with demand, so read each entry with its date.

| Fab | Zone | Product | Basis | Source keys (highest tier first) |
|---|---|---|---|---|
| P1 | Whole building (zone not public) | **DRAM · NAND** | Press on a P1 tour (2022-09): advanced DRAM and NAND are made here. Press 2025-11: a mixed NAND/DRAM line, with conversion of part of NAND to DRAM under review | `PROD_P1N`, `INT_RTR_BIDEN`, `PROD_P1` |
| P2 | Whole building (zone not public) | **EUV DRAM · V-NAND · foundry** | Samsung Electronics official (2020-08): started with EUV 1z LPDDR5 DRAM, as a combined line that also makes V-NAND and foundry products. Foundry line construction started 2020-05, NAND line 2020-06. Press 2026-03: 4, 5 and 7 nm foundry lines operating in P2 and P3 | `INT_SE_P2`, `OFF_SE_P2`, `PROD_P2F`, `PROD_FDRY` |
| P3 | Whole building (zone not public) | **NAND · DRAM · foundry** | Press on a Samsung Electronics announcement (2022-09): NAND first, with wafer input from 2022-07, then DRAM and foundry in turn | `INT_DT_P3`, `PROD_P3`, `PROD_P1` |
| P3 | Ph2 (upper west) | **Foundry** | Press: 'PH2 of P3, an existing foundry line'. Press also reports a bridge installed to link it with P4 PH2 | `PROD_BR` |
| P4 | Ph1 (lower west) | **NAND + DRAM hybrid** | Press: the cleanroom is split in half between NAND and DRAM. Reports differ on the DRAM generation (1a in one, 1c in another) | `INT_TF_P4`, `INT_TF_P4B`, `PROD_P4A`, `PROD_P4B`, `PROD_P4C` |
| P4 | Ph3 (upper west) | **1c DRAM only** | Press: a 1c DRAM-only line. One report says dividing the 300 m cleanroom into two or three sections for different product lines was discussed | `INT_TF_P4`, `INT_TF_DBL`, `PROD_P4A`, `PROD_P4B`, `PROD_P4C` |
| P4 | Ph4 (upper east) | **DRAM (1c)** | Press: being built as a DRAM-only space | `INT_TF_P4`, `INT_DT_P4`, `PROD_P4A`, `PROD_P4B` |
| P4 | Ph2 (lower east) | **1c DRAM (for HBM4)** | Press: changed from an original foundry/memory hybrid plan to a 1c DRAM line (decided 2025-12). Main construction from 2026 Q2, ready for operation targeted for the first half of 2027 (plan) | `INT_TF_P4`, `INT_DT_P4`, `PROD_P1N`, `PROD_P4D`, `PROD_P4B` |
| P5 | Whole building (under construction) | **HBM and DRAM focus (mix not finalized)** | Press (2026-02): planned with three levels so that HBM, DRAM and foundry can be allocated by level; product mix not finalized | `INT_RTR_P5`, `PROD_P5` |

- P1–P4 each have four cleanrooms on two levels, and one cleanroom can be split into two or three sections that make different products; press reports describe P4 Ph1 as half NAND and half DRAM.
- Where a product is tied to a phase, the phase position comes from the contract names in filings (see the phase table). **Which half of a split cleanroom makes which product is not public**, so the model does not draw that boundary.
- The model's equipment layout stays a generic concept on every floor; it is not changed to imitate a NAND, DRAM or foundry line.
- The table is also shown in the viewer (right panel, "Products by line") and stored in `data/campus.json` under `meta.products`.

## What is confirmed from public sources (grade A or M)

- **P4 consists of four facilities**: FAB building, complex building, substation, green building (wastewater treatment). Filings name "green building, substation and complex building, air pollution control, UPW finishing work".
- **Ultrapure water plant in the complex building** (press on a subcontractor filing). Its position inside the building is not public, so only a concept box is placed.
- **Green buildings**: two on campus; underground water treatment of about 34,000㎡, about 70,000 t a day, six wastewater streams, screen doors on chemical piping, central control room, 97% automation (official disclosure, 2021).
- **Wastewater path**: campus green building (primary treatment) → Godeok public wastewater treatment plant → Seojeongni stream → Jinwi stream → Anseong stream → Pyeongtaek lake (press on a provincial inspection, 2026-10). PFAS results published in 2026-10 were sampled at the public plant's final outlet, which also receives water from other facilities; the model does not attribute them to one source.
- **Power**: 345 kV Godeok–Seoanseong line (23.5 km, completed 2023-09, 2 GW for P1–P4, cost borne by Samsung Electronics); 500 kV Bukdangjin–Godeok HVDC with a converter station at Godeok.
- **KEPCO Godeok lot (building register, Godeok-dong 1730)**: site 102,076㎡; converter station 7,745.67㎡ building area, 23.80 m high; substation 4,861.36㎡, 32.85 m; substation-2 4,671.44㎡, 33.45 m; plus STATCOM, spare-parts warehouse and office buildings. The OSM boundary area differs from the registered site area by 0.4%.
- **Complex 2 parking building (register, Godeok-dong 1696)**: building area 42,285.72㎡, total floor area 161,032.54㎡, height 20.99 m, 4 floors and 1 basement, 4,858 indoor spaces. The plan read from imagery is within 1% of the registered building area.
- **Linde Korea Pyeongtaek plant (register, Godeok-dong 1722)** and **Godeok public wastewater treatment plant (Godeok-dong 1721)**: site and building areas from the register; layouts read from imagery (within 2.5% and 7% of the registered areas).
- **Water**: 220,000 t of industrial water a day from the Han River Paldang system (press, with fabs 1 and 2 operating); a plan to supply 372,000 t a day of treated sewage from Suwon, Hwaseong and Osan from about 2030.
- **Gases**: Air Products Korea (northeast, adjacent), Linde Korea (southwest) and Air First (about 1 km south) supply by underground pipeline; plant positions are from public maps. Pipe routes are not public.
- **Solar**: 0.4 MW → 0.7 MW of parking-lot solar at the Pyeongtaek site (sustainability reports), not used for production lines (press).
- **Process-gas abatement**: POU scrubbers and rooftop RCS at semiconductor sites (sustainability report). Count and position at Pyeongtaek are not public.
- **OHT**: SEMES, about 1,850 vehicles in P1 (press and official video).

## What remains an estimate, and why

- Which annex is the green building, the UT building, the CT building, the 154 building or the GCS building: the names are public, the building match is not. P4 identifications rest on captions of an unofficial site-observation channel; P1–P3 are by analogy.
- Which model box is "Technology building-2" of the register (6,412.72㎡, 67.90 m, 11 floors): the building read from imagery at the Google Maps "Technology building" point is only about 3,400㎡, so no match is claimed.
- Office buildings 1, 2, 3, the office complex and the FAB buildings do not appear in the public register query results; their names come from public map labels (grade M) and their heights are assumed.
- The campus receiving voltage and the route from the KEPCO substation are not confirmed; the feeder shown is a concept.

## Concept interior, utilities and EHS (grade D)

- **Interior**: a typical 300 mm fab layout with a central spine, bays on both sides, process zones (photo, etch, deposition, diffusion, CMP, clean, implant, metrology), stockers and OHT rails. Equipment boxes use representative outlines; suppliers are shown as text with two classes — companies confirmed in press or filings related to this site, and representative industry suppliers (delivery to this site not confirmed).
- **Utilities**: chilled water, condenser water, heat recovery, PCW, bulk and specialty gas, four exhaust streams, three wastewater streams, chemicals, UPW and reclaim, power (HV, MV, LV, UPS, emergency, solar). Each group lists flow sequence, literature figures, public site facts, limits and sources. A worked check of the PCW heat balance is included: `Q = ρ·V·cp·ΔT = 1000 × (1121.9/3600) × 4.186 × 3.2 ≈ 4,175 kW ≈ 1,187 RT`, matching a published benchmark.
- **Connectivity check**: `src/check_connect.py` tests geometric reachability of each system's segments; results are in `data/utility_connectivity_check.csv`.
- **EHS**: gas supply and exhaust flow lines, gas detector points, emergency showers, extinguishers, exits, and an egress travel-distance screening against 30 / 50 / 61 / 75 / 100 m reference lines. Screening result for the assumed stairs (about 70 m spacing): maximum 122–171 m, 49–52% of the floor within 61 m, 66–71% within 75 m. **This is a screening of the model's own assumptions, not a compliance assessment of the real building**; zones beyond 75 m mean the stair assumption is sparser than reality.
- **Move-in openings**: weak evidence, so they live in a separate layer that is hidden by default.

## What v7.19 adds (supplier and logistics research)

Every statement below comes from the cited public source; nothing was measured on site.

| Facility | What the public record says | Still an estimate |
|---|---|---|
| Air Products Korea plant | 2015 contract for industrial bulk gases and a bulk specialty gas supply system; second ultra-high-purity nitrogen plant on stream in 2018-01 with two more announced; a further contract in 2026 | Which building or tower is which unit |
| Air First plant | Selected in 2021 as gas supplier for the third fab; 100,000 m² site; supplies P3 and part of P4; about 40% of the company's gas output; about 729.6 kW rooftop solar; more supply facilities under construction | Unit layout; the model box excludes the construction zone |
| Linde Korea plant | Phase-1 ASU plant completed and started (trade press 2019); several ASUs and hydrogen plants, purifiers and pipelines; an eighth on-site ASU announced in 2025 | Unit layout |
| Samsung logistics warehouse (map label) | A Pyeongtaek integrated logistics centre (CDC) was completed in 2018 and handles most Samsung home appliances; two outlets reported in 2025-12 that the CDC on the planned P6 site would be demolished; a replacement appliance CDC is being built at Poseung; in 2026 the next fab was reported as a P5 twin (P5-2) with excavation under way | Labelled "relocation planned" from v7.20. That the map-labelled building is that CDC remains an inference (an unofficial YouTube layout graphic places P5 Fab 2 over this corner), and whether it still stands is unknown (imagery is dated 2025-12-22) |
| Wonik IPS, Hanyang ENG sites | CVD/ALD tool maker; piping and central chemical supply system specialist | What is done at these two sites |

## What v7.21 adds (detail pass after the eighth consultation)

| Change | Basis | Limit |
|---|---|---|
| 13 storage tanks are now cylinders in the viewer, GLB/OBJ/STL, STEP, 3D DXF and the 2D plans (9 at the three gas plants read from imagery, 4 concept tanks) | Round plan shape visible in imagery; diameter is the shorter plan side | Dome roofs are flattened; heights stay arbitrary. Cold boxes and process blocks stay as boxes because an enclosure can be rectangular even when the column inside is round |
| Linde north-east building height 20 m → 22.55 m, grade M | Building register (Godeok-dong 1722, main building No. 38: 2,796.08 m², 22.55 m) against a 2,756 m² plan, 1.4% apart | The match rests on area comparison |
| Public wastewater plant: register heights recorded in the note (30.2 m, 13.2 m, 18.1 m) | Building register (Godeok-dong 1721) | Which box is which building is unsettled, so model heights are unchanged |
| New preview 28 (Linde plant) | — | — |

Fab heights: all four fabs use 83 m as an assumption (grade C in the viewer table); the press figure behind it does not name a fab, and measurement boundary, legal height and floor heights are unconfirmed. The register query for the campus lot returned only two records (a gate building and Technical Building 2, 67.9 m, 11 storeys), not the fabs.

## What v7.22 adds (rooftop zones and a shadow-ratio height check)

**Rooftop equipment zones.** Nine semi-transparent zones were added on the west and east perimeter bands of each fab and between the two central roofs of P3, where the 2025-12-22 imagery shows dense steel lattice and piping. Plan extents are read from imagery (grade B); the 6 m height is arbitrary and the equipment type is not identified, so the name stays neutral.

**Shadow-ratio check.** No acquisition time is published for the imagery, so sun angles were not used. Instead, shadows in the same image were compared with the P1 model height of 83 m, itself an assumption from a press figure that does not name P1 — so the check tests whether the fabs are alike, not their absolute heights.

| Measurement in the imagery | Value | Result |
|---|---|---|
| P1 north wall shadow on the ground | about 163 m (lines at X −130…−70) | calibration: 83 m ÷ 163 m ≈ 0.51 m of height per metre of shadow |
| Shadow of the P1 south roof band on the central roof | about 29 m (26–32 m) | the casting edge is about 15 m (13–17 m) above the central roof; the model has 16 m (rack top 89 m, central roof 73 m), so the 10 m roof step is not contradicted |
| P2 shadow tip on the roof of the building between P2 and P1 (that roof is about 19 m high from its own 37 m shadow) | tip about 131 m from the P2 north wall | P2 ≈ 86 m ± 4 m, consistent with the 83 m assumed |
| P3 | gap to P2 is only 55 m | not measurable |
| P4 | utility buildings start 50 m north and rise out of the shadow | not determined |

Limits: readings are ±3 m; the ground is assumed level; which edge casts each shadow is an interpretation. The P2–P4 height grade stays C.

## What v7.23 adds (16 more supplier locations)

Sixteen further supplier locations registered on Kakao Map inside the model area were added as map-label markers (queried 2026-11-14; grade M for position). The role column is a general description of each company's published main business; it was not checked against individual documents here, and what each site does or delivers to the campus is not confirmed.

| Marker | Role (general) | X, Y (m) |
|---|---|---|
| Applied Materials Korea (Kakao Map label) | US semiconductor equipment maker (deposition, etch, CMP, ion implantation, metrology). Named as a P1 tool supplier in tour coverage | 1018, 2234 |
| KLA Pyeongtaek (Kakao Map label) | US maker of semiconductor inspection and metrology equipment. Named as a P1 tool supplier in tour coverage | -447, 2628 |
| Lam Research Korea Pyeongtaek office (Kakao Map label) | US semiconductor equipment maker (etch and deposition) | -494, 327 |
| Tokyo Electron Korea Pyeongtaek office (Kakao Map label) | Japanese semiconductor equipment maker (coater/developer tracks, etch, deposition, cleaning) | -561, 2739 |
| KCTech Pyeongtaek office (Kakao Map label) | Korean semiconductor equipment and materials company (CMP tools, cleaning tools, slurry) | -622, 2858 |
| Unisem Pyeongtaek CS centre (Kakao Map label) | Korean maker of semiconductor support equipment (gas scrubbers, chillers) | -635, 123 |
| PSK Pyeongtaek manufacturing plant (Kakao Map label) | Korean semiconductor equipment maker (dry strip tools for photoresist removal) | 937, 2052 |
| PSK Holdings Pyeongtaek manufacturing plant (Kakao Map label) | Korean maker of back-end semiconductor equipment (descum, reflow) | 946, 2302 |
| STI Pyeongtaek office (Kakao Map label) | Korean maker of central chemical supply systems (CCSS) and cleaning equipment | 451, 231 |
| Hansung Cleantech (Kakao Map label) | Korean contractor for ultrapure water and water treatment facilities | 464, -123 |
| Merck (Kakao Map label) | Site of the electronics materials business of Merck of Germany (semiconductor materials and specialty gases) | 1871, 1652 |
| Versum Materials SPC Korea (Kakao Map label) | Semiconductor specialty gas and materials company (Versum Materials was acquired by Merck in 2019) | 1800, 1680 |
| FST Pyeongtaek site (Kakao Map label) | Korean semiconductor parts and equipment company (pellicles, chillers) | -891, 2161 |
| Wonik IPS (Mogok-dong) (Kakao Map label) | Another registered location of the deposition equipment maker Wonik IPS | 1001, 1200 |
| KC ENC (Kakao Map label) | Korean contractor for gas and chemical supply systems | -811, 151 |
| Samsung C&T Pyeongtaek camp (construction site office) (Kakao Map label) | Samsung C&T Engineering and Construction Group is, per its filings, in charge of the structure and the fit-out of the fab and complex buildings at Pyeongtaek | -1246, 1641 |

Found on the map but outside the modelled ground, so listed here only: Lam Research Pyeongtaek site (Godeok-dong 1977-1), Global Standard Technology Pyeongtaek (Gajae-dong 345-27), Samsung Electronics DS Division supplier EHS academy (Godeok-myeon, Jiwon 1-gil 16). Many small engineering and construction firms also appear in the same search and were left out because their role could not be identified.

## What v7.24 adds (cooling towers from imagery, evidence intake)

**Rooftop of the utility building between P3 and P4.** The 2025-12-22 imagery shows rows of circular fans with vapour plumes on this roof. Five rows were added as presumed cooling towers (plan extent grade B), with 98 fan cylinders placed at an approximate 13 m pitch (grade C: the real count, maker and capacity are not confirmed), plus two rows of blue-topped modules whose use is not identified. Heights are arbitrary. Preview 29.

**P1 roof racks.** In the imagery the outer strip of the perimeter band on the west half of P1 is roof surface. The south and north racks now cover the full band depth only on the east half; on the west half two new elements (P1-rack-S2, P1-rack-N2) cover the inner strip only.

**P5 site note.** A second press figure for P5 Fab 1 (211 m × 638 m, triple fab, about 100 m high, 1.45 million m²; Hankook Ilbo 2026-10-30, opened and checked) now stands next to the earlier 650 m × 195 m figure. Because they differ, the model still draws only the site extent.

**Layers by flow.** Air (FFU ceiling, plenum zones), wafer transport (OHT aisles, rails and vehicles in the concept interior), people (cores and the egress samples of the EHS layer) and piping (utility systems) are separate layers in the viewer and separate DXF layers. All of them are concept layers; the sources added in this version describe the principle only and do not raise any position to a higher grade.

**Evidence intake.** Bundles of 48 items in total (SP-E001–E048) were received from the companion financial-analysis workstream and judged as follows. "Already in" means the model had it before; "held" means it is not used as geometry.

| Item | Subject | Verdict | Where / why |
|---|---|---|---|
| SP-E001 | "Single fab" building area about 120,000 m², total floor area about 990,000 m² (Samsung Semiconductor newsroom, 2025-08-21) | Already a source, not used as a dimension | Opened and checked here: the article says "single fab" and "one of our fab facilities" at the Pyeongtaek campus without naming which fab. It was already cited as key `SITE_AREA` for the 2.89 million m² campus figure. The measured footprints are about 135,600 (P1), 138,900 (P2), 174,700 (P3) and 172,900 m² (P4), so 120,000 m² is not fitted to any of them |
| SP-E002 | P3 "about 700 m" long (press) | Held, with a measurement | Imagery gives 623 m for the main body and 651 m with the end block |
| SP-E003 | P1 about 2,000 tools (press) | Already in | Source key TOOLS, concept layer only |
| SP-E004 | One production set (cleanroom + sub-fab below + air handling above) about 30 m high (press, said of P5) | Concept | Matches the model's generic section; not used as a P1–P4 dimension |
| SP-E005 | P4 phases Ph1–Ph4 as lower-west, lower-east, upper-west, upper-east | Already in, updated | Viewer phase table; "lower/upper" is vertical and is not drawn as plan quadrants. Latest amended periods and amounts (checked against DART originals by Codex and Astra, not opened here) are in `campus.json` → `meta.p4_phases.filings_latest`: Ph1 2023-03-01 to 2025-12-31, Ph2 2023-07-15 to 2027-12-31, Ph3 2024-06-17 to 2026-03-31, Ph4 2025-07-18 to 2027-04-30. These are the fit-out periods stated in the filings, not actual start or operation dates. The Ph2 amount is VAT-excluded while the others are VAT-included, so they must not be summed as they stand |
| SP-E024 | P3 phases: Ph1 lower west, Ph2 upper west, Ph3 lower east, Ph4 upper east (Samsung C&T filings, originals checked by Codex and by the financial-analysis workstream) | Already in, basis upgraded | The viewer phase table already had this arrangement; the P3 Ph1 entry was an inference and now cites the filing. P3 and P4 number their phases differently (P4: Ph2 lower east, Ph3 upper west), so phase numbers are kept per fab and never copied between fabs. Boundaries, floor numbers and coordinates stay unconfirmed |
| Withdrawn by the sender | Splitting P4 into four plan zones (from SP-E005); fitting the P3 footprint to 120,000 m² (from SP-E001) | Not applied | Neither was ever applied to the model |
| Profit sensitivity figures | — | Not used | No profit or cost figure is put into the building model |
| SP-E006 | Buildings named in contract titles (fab, complex, green, substation, air pollution control, UPW) | Already in | Phase table scope line |
| SP-E007 | P3 filings by Samsung E&A: green building structure and water plant phase 2, 154 kV structure | Record only | Checked against originals by Astra. They show that such contracts exist; location, completion, number of buildings and power capacity are not in the filings, so nothing is placed |
| SP-E020 | Kolon Global filing "Pyeongtaek P5 water plant 3-gi" | Record only | Checked by Codex. What "3-gi" means (three units, third unit or third phase) is not defined in the filing, so no water plant is drawn or multiplied |
| SP-E019, E021 | Gas supply tunnel, P5 work packages | Held | Not opened here; amounts and package numbers are never turned into size or position |
| SP-E008 | P5 Fab 1 dimensions | In (note only) | Element PAD-P5, v7.24 |
| SP-E009 | P5 triple fab through a floor-area ratio increase from 350% to 490% in zone A1-1 | Held, official text recorded | Astra obtained Gyeonggi Province Notice No. 2026-189 (2026-07-30): zone A1-1 stays at 350% or less. No later notice approving 490% was found, which is not proof that it was refused. Element PAD-P5 note and source key GG_2026_189, v7.24. The triple fab stays a press-reported plan |
| SP-E010, E015, E022 | Fab 2 site 661 m × 194 m, new substations, capacity | Held | Plans or press not opened here |
| SP-E011 | P4–P5 bridge about 360 m | Held | Article not retrievable; connection points unknown, so no bridge is drawn |
| SP-E012, E013 | 345 kV Godeok–Seoanseong line, 500 kV HVDC | Already in | Power group sources |
| SP-E014 | Godeok substation floor area 100,000 m² (press) | Held, conflict | The building register gives 48,546.62 m² for the converter station and substation lot; the register value stays |
| SP-E016 | Green building 34,000 m², 70,000 t/day, 2.6 km discharge pipe | Held | Article not opened here; the model keeps the official 81,600 m³/day for the P3 green building |
| SP-E017 | Industrial water and reclaimed sewage supply | Already in | Water group sources |
| SP-E018 | Site area 2.89 million m² vs about 3.9 million m² | Partly in | Official 2.89/2.83 million m² (Samsung) in the model. Notice No. 2026-189 gives 3,905,709.9 m² for the whole industrial complex and 2,861,212.4 m² of manufacturing land; these are different scopes, and whether either equals Samsung's 2.89 million m² is not confirmed |
| SP-E023 | Company-wide water flow | Held | Not separable for Pyeongtaek |
| SP-E025 | Notice No. 2026-189: zone A1-1 at 350% or less | In (note) | Same as SP-E009: element PAD-P5 note, source GG_2026_189 |
| SP-E026 | Whole complex 3,905,709.9 m², manufacturing land 2,861,212.4 m² (notice); GH overview 3,906 thousand m² | Recorded | Same as SP-E018. No model boundary is fitted to either figure; Samsung's 2.89 million m² is kept as Samsung's own figure |
| SP-E027 | Public wastewater treatment basic plan: 340,000 m³/day in four stages; discharge Seojeongni Stream → Jinwi Stream → Anseong Stream | Recorded side by side | 340,000 m³/day comes from the basic plan for the public facility (2011 document and a 2022 reprint); 450,000 m³/day comes from the 2026 industrial complex plan (R8). They are different documents and how they relate is not settled; neither is said to replace the other. A later consolidated notice (Han River Basin Environmental Office No. 2026-15, 2026-01-13) exists, but its text for this facility was not obtained (R7 open). Not used for geometry |
| SP-E028 | Stage capacities and the stage-3 building (9,874 m² treatment facility, a separate 9,081 m² building with B2–3F) from contractor material | Held | Stage figures conflict (R7 open); the contractor sentence about 62,000 t/day does not itself say "stage 2". The storey count applies to one building only and its position inside the lot is unknown, so the existing PUB-WWTP boxes are unchanged. The register heights already in the PUB-WWTP note stay |
| SP-E029 | GH overview: older water and energy plan values | Not used | Superseded in date by the 2026 notice; the odd power unit is not used or corrected |
| SP-E030 | Samsung E&A project page: Pyeongtaek water plant 130,000 m³/day, 145,000 after expansion; stage 1 for P1–P2, expansion for P3 Ph1, stage 2 for P3–P4 | Recorded, no element | Process-water treatment, not UPW capacity; page date unknown; no position, so no water plant is drawn. In `meta.infra_plan` |
| SP-E031 | Press figures for water supplied and used | Held | Definitions differ between articles |
| SP-E032 | Air emission capacities from EIA or integrated permit | Not found | No stack count or capacity is put into the model |
| SP-E033–E036 | Notice pages 10–12: power demand, water supply plan, wastewater, heat demand of the whole complex | Recorded | Same as R8, `meta.infra_plan`; heat demand (5,370,360 Gcal/year) is listed here only |
| SP-E037 | Integrated environmental permit completed 2024-12-30 (press quoting the ministry); rooftop combined process-gas treatment (RCS) described in press | Held | Permit documents and capacities not obtained. The existing rooftop zones keep their neutral name; no RCS count or position is added |
| SP-E038 | Later consolidated notice on the public wastewater basic plan (No. 2026-15, 2026-01-13) exists; stage figures are unverified candidates | Recorded | Same row as SP-E027; no stage capacity is used |
| SP-E039 | Samsung E&A project page: P2 Phase 1 water treatment, EPC, completed 2020, 86,000 m³/day; scope lists air pollution control, water plant, ultrapure water production, wastewater treatment and reuse | Recorded as system types | The five system types already exist as concept utility groups. 86,000 m³/day is a project size, not the capacity of a green building, UPW output or an operating figure; nothing is sized or placed from it |
| SP-E040 | Press: P4 as four kinds of facility (fab, complex, substation, green) with precast concrete quantities | Wording corrected | Element S1 note now says "four kinds of facility (a press classification, not a count of separate buildings)". Quantities conflict between articles (substation 15,000 vs 18,000 m³; items sum to 215,000 vs an estimated total of 200,000 m³) and are not used. "Steel plus precast" is a general trade description, not a confirmed P4 structure |
| SP-E041 | Samsung C&T patent on segmented precast waffle beams; press description of composite columns at P5 | Concept only | The 3.6 m in the patent is the transport width given as background, not a span or a Pyeongtaek module. Beam and column items are different members. No dimension is taken into the model |
| SP-E042 | Press (Seoul Economic Daily, 2026-04-23): half of P4 operating; east zones to follow after temporary use approval in July and November | Held | A plan reported in April, not a confirmed status. Temporary use approval, tool move-in, set-up, trial run and production are separate stages; no operating state is shown per zone |
| SP-E043 | Samsung glossary article: air flows from ceiling filters down through the perforated floor | Source added to existing concept elements | 16 "FFU ceiling" elements (grade D) now also cite `OFF_SS_FAB101`. No new element, no grade change. The article names no fab and gives no height, flow or filter count |
| SP-E044 | Samsung glossary and newsroom (2025-09-04): OHT on ceiling rails carries FOUPs; one vehicle about 100 km a day | Source added to existing concept elements | 16 "central aisle · interbay OHT" elements (grade D) now also cite `OFF_SS_FAB101` and `OFF_SS_OHT`. The existing concept rails and vehicles are reused; the 100 km figure is not used for route length, speed or vehicle count, and nothing is said about a P4–P5 link |
| SP-E045 | Samsung page: Pyeongtaek Line 1 as a 1:520 block model showing air showers, dry cooling coils and ULPA filters | Source added to existing concept elements | 16 "FFU ceiling" and 16 "plenum zone" elements now also cite `OFF_SS_LEGO`, as a list of element kinds only. A promotional model is not a drawing; positions and counts are unchanged |
| SP-E046 | Samsung newsroom articles (2022-10-26 and 2022-09-23): rooftop combined process-gas treatment (RCS) with catalyst, developed in 2009; treatment efficiency raised "up to 95%" | Held, principle recorded | Originals checked by Astra, not opened here. A general technology description: it is not a measured efficiency for any Pyeongtaek fab, every gas or every operating condition, and not a reduction rate of total emissions. Units, positions, capacities and connections are unknown, so the rooftop zones keep their neutral name and no RCS unit is placed |
| SP-E047 | Samsung community page on the 2025-10-21 meeting: chemicals are handled in "five manufacturing buildings" and in gas and chemical supply buildings | Held | Original checked by Astra, not opened here. The wording counts chemical-handling facilities; which five buildings, whether each is a fab and whether they operate is not stated. They are not mapped to P1–P5 and no fifth fab or supply building is added |
| SP-E048 | Samsung job interview (2018-09-06): facility work in three groups — utility supply, water treatment, environmental treatment; article on water (2020-05-22) | No change | Originals checked by Astra, not opened here. The three groups describe one job family, not the whole infrastructure (power is separate), so the model keeps its eight concept utility groups. The three uses of water are not merged into ultrapure water |
| R8 | Notice pages 10–12: 3,324,190 kVA, 478,950 m³/day water, 449,211 m³/day wastewater, 450,000 m³/day public facility | Recorded | `meta.infra_plan` in `campus.json`, v7.24. Plan figures for the whole complex; not converted into geometry, counts or pipe sizes |

## What v7.25 adds (sixth evidence bundle, one duplicate removed)

No box was moved, resized or regraded in this version. One element was removed and five notes were extended.

- Removed `UT-34-CT`: an assumed cooling tower zone (grade C) from an earlier version. It overlapped the rows `CT34-R4` and `CT34-R5` and the two rows of unidentified blue modules that v7.24 read from imagery, so the same roof area was described twice and in two different ways. 1,458 elements remain.
- `UT-12` (utility building between P1 and P2): the note now says that the "240,000 refrigeration tons" on the Samsung E&A page is the company's expression of cooling size and is not converted into a daily volume, an operating load or a number of machines; that the meaning of "CT" and the scope of the floor-area figure on that page are unsettled; and that the description is not carried over to P3 and P4.
- `KEPCO-PAD` (substation lot): the earlier note said the press figure of about 100,000 m² "corresponds to" the site area in the register. That was an inference. The note now records the three figures side by side — press about 100,000 m², register site area 102,076 m², register total floor area 48,546.62 m² — and leaves the relation open.
- `BR-34a`, `BR-34b`, `BR-34c` (overbridges at the P3–P4 utility building): a press photo caption is recorded as a concept note with the new source key `DEALSITE_BR`. Geometry is unchanged.
- `PUB-WWTP`: the note now says that a use-approval date in the register is not a start-of-operation date or a capacity.

Overlap check before intake: the public wastewater plant (4 elements `PUB-WWTP*`), the KEPCO lot (`KEPCO-PAD`, `SS-*`), the three overbridges `BR-34a/b/c`, the two pipe rack bridges `BR-PR1/2` and the office buildings (`GATE-W`, `WA`, `WD`, `W1`) already existed, so no element was added for any of the ten items.

| ID | Claim received | Verdict | Where / why |
|---|---|---|---|
| SP-E049 | Samsung E&A project page: P2 utility project — chilled water, steam, compressed air and industrial water for the lines; "up to about 240,000 refrigeration tons"; UT and CT buildings laid out in blocks | Recorded (note only) | `UT-12` note, v7.25. Reviewed by Codex; not reopened here in this version (the page was already source `P2_UT`). No position, count or floor is derived, and nothing is copied to P3 or P4 |
| SP-E050 | Supplier notice: final shipment of modules for the P2 UT/CT buildings (2020-09-04) | Reference only | Kind and number of modules are not given; nothing to model |
| SP-E051 | Supplier track record: cooling towers ordered by phase for P2, P3 and P4 | Held, unverified | The page returned 403/502 to Astra and is not reachable here either. The relayed rows are not used; no statement is made about who built the cooling towers, and the 98 fan cylinders stay an approximation read from imagery |
| SP-E052 | In the filings, company pages and searches reviewed, nothing was found that names a UT or CT building for P3 or P4 | Agreed, unchanged | `UT-34` stays "presumed utility building" (grade B plan from imagery); `CT34-R1`–`R5` stay "presumed cooling tower rows". The P2 arrangement is not copied |
| SP-E053 | No building register entry for the P1 or P2 fab was found in the areas queried | Agreed, unchanged | Fab heights and floor levels stay assumptions (see "What remains an estimate") |
| SP-E054 | Press: office building 1 has 9 storeys, office building 2 has 11 | Already in | Elements `GATE-W` and `WA` already carry these as press figures; heights stay assumed |
| SP-E055 | Press (2026-08-11): an overbridge of about 360 m for wafers is being built "in front of P4" | Held | Which face of P4, which P5 building, height and floor are not public. The P4–P5 bridge is still not drawn |
| SP-E056 | Press photo caption (Dealsite, published 2025-06-24, modified 2025-08-25): four bridges in all at P4 PH2 and P3 PH2, with the complex building between them; SEMES OHT expected | Concept note | `BR-34a/b/c` notes and source `DEALSITE_BR`, v7.25. Article checked by Codex and Astra; it could not be reopened here. Connection points, floors and coordinates are unknown; "PH2" is kept as printed and is not read as the same floor or height in both fabs; "expected" is not "installed". The count of four is not matched to the three overbridges and two pipe rack bridges in the model |
| SP-E057 | Building register, Godeok-dong 1721: three buildings of the public wastewater plant with storeys, heights and areas | Already in, wording added | The register heights (30.2 m, 13.2 m, 18.1 m) were recorded in v7.21. Which box is which building is still unsettled, so box heights stay arbitrary. The rows relayed in this bundle are a transcription; Codex checked only their sums (total floor area matches 21,840.49 m²; building areas differ by 24.36 m²). The stage-3 floor area of 9,080.72 m² is numerically close to a contractor's published 9,081 m² |
| SP-E058 | Building register, Godeok-dong 1730: KEPCO converter station and substations with storeys, heights and areas | Already in, wording corrected | `KEPCO-PAD` note, v7.25. Existing `SS-*` boxes were matched to register buildings by comparing areas and say so; no further height is changed or copied. Sum of the per-building floor areas differs from the register total by 11.39 m² (Codex arithmetic) |

Seventh bundle (campus lots in the building register) and the sender's corrections to the sixth:

| ID | Claim received | Verdict | Where / why |
|---|---|---|---|
| SP-E059 | Register, Godeok-dong 1695: Technology building-2 (11 floors and 1 basement, 67.90 m, building area 6,412.72 m²) and North gate building (2 floors, 10.32 m) | Already in, wording tightened | In the model since v7.12 from this workstream's own register query: `NGATE-BLD` and `meta.floor_area.gov_register_campus`. Queried again on 2026-11-14 through the Building HUB connector: every figure in the transcription matches (no request URL or raw response file is held). Technology building-2 is still not assigned to a box — `OFF-T` about 3,400 m², `OFF-2` about 6,020 m², `WA` about 7,050 m² against 6,412.72 m² — and its floors and height are not used for the P2 fab. The meta text no longer says "only two buildings are published" (it is a query result) and no longer says Office building 2 and Technology building-2 are different buildings |
| SP-E060 | Register, Godeok-dong 1696: parking building of Complex 2 (4 floors and 1 basement, 20.99 m, building area 42,285.72 m², 4,858 indoor spaces) | Already in | `PARK-2` (plan from imagery, 1% from the register area; height from the register). Re-queried 2026-11-14, figures match. The main use "factory" in the register does not make it a production fab, and registered spaces are not occupancy or traffic |
| SP-E061 | Site areas: 1,833,839.5 m² (lot 1695) and 804,237.8 m² (lot 1696), sum 2,638,077.3 m² | Recorded side by side | `meta.floor_area.gov_register_campus`. The extent of the 37 additional lots and the campus boundary are unverified; no boundary in the model is changed to fit 2.89 million m² or 2,861,212.4 m² |
| SP-E062 | No register entry or floor levels for the P1 and P2 fabs yet; permit pages 2–8 and two more districts still to be queried | Agreed, unchanged | Fab heights and floor levels stay assumptions |
| Corrections to E051, E056, E057, E058 | Sender withdraws the cooling-tower ownership wording, the "not the same floor" reading of PH2, "partly resolved" for the wastewater plant, and the reading of the press 100,000 m² as a site-area error | Consistent | The v7.25 notes above were already written within these limits; nothing to undo |

Eighth bundle and two data audits by Codex (meta wording only; no geometry change):

| ID | Claim received | Verdict | Where / why |
|---|---|---|---|
| SP-E063 | Building-permit per-building summary, lot 1695: 28 transcribed rows of 10,000 m² or more under the main permit, five of them with floor areas of 530,000–720,000 m² | Recorded, held | `meta.floor_area.gov_register_campus`. 156 of 316 entries were queried (rows 41–200 not), no raw response is held, and the rows have no building name, floor count or height. The five large rows are not assigned to P1–P5, the sums (4,669,137.36 m² for the 28 rows, 3,152,674.05 m² for the top five) are not a campus total, and no floor count or height is derived from areas. Codex saw 701 floor-level permit rows for the lot on the official site (data month 2026-09) but has not received the file |
| Namwoong Construction track record (Astra) | "Pyeongtaek line 3 FAB new construction — complex building", B1–9F, 2021-01-14 to 2022-04-30, prime contractor Samsung C&T | Source candidate only | It is the complex building, not the P3 fab and not P1 or P2. No height or position; no box is matched or changed |
| `P2_FLOORS` (Hanbang Ubis supervision record, already a source) | "Samsung Electronics Pyeongtaek P2", posted 2023-11-14, B1F–8F, 592,077 m² (original checked by Astra) | Wording limited | `meta.floor_area.reference_press`. The record does not separate fab, complex building and utility, so it is a project-level figure and not the legal floor count of the P2 fab alone |
| `P1_DIM` (Astra compared both articles) | Etoday names P1 and gives about 520 m × 200 m, no height; ZDNet gives 518 × 201 × 83 m for "the production line" without naming P1 | Corrected | Source text `P1_DIM`, fab notes of P1–P4, viewer height grade of P1 (A → C). The plan figure stays; 83 m is kept in the geometry as an assumption and is not moved to P3 or presented as a measurement |
| KRX filing 2022-11-24 (Astra) | Samsung Engineering contract title "[P3 Ph4] green building and UT building, rooftop exhaust, UPW finishing works" | Name recorded | `UT-34` note and source `KRX_P3PH4`. This corrects the earlier statement that no document names a UT building for P3 (SP-E052); floors, height, number of buildings and identity with the complex building stay unconfirmed, and the box is unchanged |
| Hansung Cleantech company brochure 2023 (Astra) | Work titles "P3 ultrapure water new construction — complex building 4F facility works" (p. 45) and complex-building facility works for P3 Ph2/3/4 and P4 Ph1 (p. 44) | Source candidate only | A work on the 4th floor, not a four-storey building; not merged with the Namwoong B1–9F record. No box is matched |
| Meta audit (Codex) | Old conclusions left in `meta.floor_area` | Corrected | `official.P2` no longer treats 128,900 m² as the P2 fab floor area; `check` (model plan "may be 13% small") is withdrawn; `gov_register` says the values are transcriptions and gives the per-stage approval dates of the wastewater plant; `gov_register_parcels` counts rows, not buildings; the permit-query scope is updated |

Also corrected: the `OFF-2` note called the building a candidate for Office building 2, which contradicted `WA`; it now only compares its plan with the register area.

## Verification done for this release

v7.25: Korean and English data files compared element by element (1,458 ids, source keys, grades and boxes identical; no duplicate id; no untranslated note).

| Check | Result |
|---|---|
| Fab bodies and all annexes overlaid on the zoom-18 satellite mosaic (about 0.48 m/px) | All four fab outlines and the east, west and north annexes fall on the imagery; three technology-cluster buildings were re-oriented in v7.13 after this check |
| STEP read back with the OpenCascade kernel (v7.25 build) | 1,234 solids, 7,071 faces; the first 400 solids pass the shape validity check |
| DXF read back and audited with ezdxf | 2D: 119,633 entities on 178 layers, 0 audit errors; 3D: 1,678 meshes on 166 layers, 0 audit errors; units metres |
| Registered areas vs. plans read from imagery | Parking building 1%, Linde site 2.5%, wastewater plant 7%, KEPCO lot 0.4% |
| Viewer | Loads without page errors, with no network requests; all 23 previews regenerated from this version |
| Bridges and parking | 12 bridges checked against imagery; 5 structures that were missing (2 overbridges between the UT building and P2, 1 link between the west support building and P2, 2 pipe rack bridges east of the P3–P4 utility building) were added |

Not done: the files were not opened in a commercial CAD program (only with open-source kernels and parsers).

## Not modelled, on purpose

- Security equipment positions, access control, guard buildings and watch posts.
- Anything the author may know from past work at the site. The author worked for about two years as contract EHS staff for a construction contractor at Pyeongtaek; the model uses the public sources listed, not that work.
- Third-party imagery, video frames and vendor CAD (not redistributed here).
- Facilities whose location is not public (temperature-reduction facility, PFAS pilot unit, Complex 2 ancillary buildings, KEPCO accessory buildings without a match).

## Limits

- Building plans carry an error of a few metres; heights other than P1 and the registered buildings are assumptions.
- Imagery is oblique: roofs appear displaced from footprints, which was taken into account when reading outlines.
- Map labels are points, not outlines, and OpenStreetMap is not an official source.
- Press figures differ in date and basis (for example water supplied vs. water used); the notes keep date and basis together.
- The interior, utilities and EHS layers must not be read as a description of the real plant.

## Work with other AI models

The model was reviewed in seven rounds with Gemini and with Codex (GPT-6 Astra). Their factual claims were used only when verified independently; unverified claims were held. See `CONSULTATION.md`.

## Licence

Two licences apply. Model, data, drawings, previews and documentation: **CC BY 4.0** (`LICENSE`). Program code in `src/` and the viewer HTML/JavaScript: **MIT** (`LICENSE-CODE`); the bundled three.js files keep their own MIT notice (`src/vendor/THREE_LICENSE`). Suggested credit: "Samsung Pyeongtaek Campus P1–P4 open model (unofficial), built only from public sources". Not covered: third-party imagery (not included), OpenStreetMap data (ODbL, used for cross-checking only), and any trademarks. Company names are used only to identify facilities and suppliers.

## Rebuilding

```
pip install trimesh ezdxf cadquery numpy matplotlib
cd src
python export.py        # reads ../data/campus.json, writes models, drawings and CSVs to ./out
python mkview.py        # writes index.html from viewer_template.html
python check_connect.py # utility connectivity table
```

The model data is authored by a generator whose strings are in Korean (`src/generator_ko/build.py`, `utility.py`). `src/generator_ko/i18n/` holds the translation tables that produce the English `campus.json`, viewer and export script; `build_en.sh` shows the order.

## Corrections

If any element is factually wrong or is believed not to derive from public information, open an issue naming the element id and it will be reviewed.
