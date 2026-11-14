# Changelog

## v7.37 — 2026-11-15
- `meta.infra_plan`: history of the 450,000 m³/day in the industrial-complex support plan (345 → 450 thousand in Notice 2023-181 of 2023-06-30; unchanged in 2024-1 and 2025-121). New source `GG_2023_181`. Relation to the 340,000 basic plan still not established.
- No element changed. 196 sources (54 official, 42 international, 100 Korean).

## v7.36 — 2026-11-15
- New `meta.permit_link_corridors` (six permit records of link corridors: structure, areas, recorded floor numbers; no match to bridge boxes); pointer added to 15 bridge-element notes.
- `meta.module_oac_records`: suspended-ceiling connection hierarchy and modular method from K-ENSOL's ICR brochure (new source `KENSOL_ICR`, general product description); re-check wording corrected.
- `meta.imagery_geometry`: integrated GIS building data recorded as the next public path for ground outlines (records not obtained).
- No box changed. 1,474 elements; 195 sources (53 official, 42 international, 100 Korean).

## v7.35 — 2026-11-15
- New `meta.module_oac_records`; sources `KENSOL_H1_2026`, `KENSOL_Q1_2026` (K-ENSOL module S/C work for P3 PH4 and P4 PH2–PH4, module OAC for P4 Ph1 and PH3; OAC defined as outdoor air conditioner; modular system-ceiling method applied at Pyeongtaek from 2020).
- Notes and source lists of the eight P3/P4 FFU ceiling elements; FFU and MAU type descriptions. Boxes unchanged and still grade D.
- `meta.hvac_supplier_records`: "four lists" corrected to five list pages. KRX KIND filings counted as official sources.
- No box changed. 1,474 elements; 194 sources (52 official, 42 international, 100 Korean).

## v7.34 — 2026-11-15
- New `meta.hvac_supplier_records`; sources `SHINSUNG_2105`, `SHINSUNG_2111`, `SHINSUNG_2119` (Shinsung Engineering reference lists by contract year: DCC for P2L, EUV and P3L; AHU/OAC for P2L, EUV V2 and P4 Ph1; precision air conditioner for P4 Ph1).
- Notes and source lists of the P2 and P3 return-air shafts (24) and `V2`; DCC and MAU type descriptions. Boxes unchanged and still grade D.
- Correction: unsourced vendor names (Shinsung E&G for MAU and DCC, Hanyang ENG for DCC) removed from the "representative industry suppliers" field.
- No box changed. 1,474 elements; 192 sources (50 official, 42 international, 100 Korean).

## v7.33 — 2026-11-15
- New `meta.design_firm_records`; sources `SAMOO_P2`, `SAMOO_INSIGHT`, `POSCOANC_P5`, `EA_SR2018`. Samoo's P2-Project record (828,992 m², 8 floors + 1 basement, 2021) is recorded without assigning it to a building; one design-stage rendering compared qualitatively (not redistributed, no dimension read).
- `PAD-P5` note: POSCO A&C CM/CS record (year 2028 is a future year). `UT-12-UPW` note: CEDI stated for the P1 ultrapure water project (box remains conceptual).
- `P1-endblk` … `P4-endblk`: names and notes now say the east strip is undetermined rather than "probably a wall face".
- No box changed. 1,474 elements; 189 sources (47 official, 42 international, 100 Korean).

## v7.32 — 2026-11-15
- `meta.imagery_geometry`: orthophoto capture with a recorded scale — bright roof edges of the northern fab 526–547 m apart (two independent readings) and about 539 m here; scale-free length ÷ width about 2.57 on the orthophoto against 2.57 (Esri main body) and 2.70 (Esri with strip). No decision; no box changed. The length-only decision rule written in v7.31 is withdrawn.
- New `meta.p_number_layout` and source `SSEC_20251023`: a brokerage report labels P1–P4 north to south, as the model does.
- No element changed.

## v7.31 — 2026-11-15
- Correction: `meta.floor_area.gov_register_campus` wrongly summarised floor 1 of CT building-2 as general steel; all its records are steel-reinforced concrete (only CT building has general steel on floor 1). An error of this model's summary, not of the official record.
- `meta.imagery_geometry`: comparison with the public preview of the NGII 2025 orthophoto (P1 about 530 ± 9 m at about 2.3 m per screen pixel; does not decide the east-strip question; not an independent length check). New source `NGII_ORTHO_2025`. No image redistributed.
- No element changed. 184 sources (43 official, 42 international, 99 Korean).

## v7.30 — 2026-11-15
- `ROAD-NW` added (public cross road north-west of the campus, grade B, rotated rectangle). 1,474 elements. No existing box changed.
- `KEPCO-PAD` note separates the register summary (48,546.62 m²) from the per-building sum (48,558.01 m²), both from official exports.
- `meta.floor_area.gov_register_campus`: structure and use records of the FAB and CT buildings; model structure stays conceptual.
- README: table of the evidence that would settle each open item; SP-E058 row rewritten to the current state.

## v7.29 — 2026-11-15
- Two ground-level road elements read from imagery: `ROAD-W2` and `ROAD-W3` (rotated rectangles, grade B, ±10 m). 1,473 elements. No existing box changed.
- `meta.imagery_geometry`: seven tiles verified identical to the tiles served now (by hash); substation heights quoted from the official title-section export.
- README: block areas of Notice No. 2026-189 that add up to the lot 1696 permit site area; OpenStreetMap outlines not adopted; east-side railway and roads held.

## v7.28 — 2026-11-15
- Imagery metadata confirmed on Esri's official metadata layer (acquisition 2025-12-22, 0.5 m, WV02, Vantor; no viewing-angle field). `meta.imagery_geometry` corrected: the "date may differ between tiles" remark withdrawn, the 80–120 m figure marked exploratory, no shift applied. New source `ESRI_META`.
- New `meta.permit_basic_summary` from the full-column basic-summary exports for lots 1695 and 1696, including the unresolved difference between the basic and per-building totals for 1696.
- Three ground-level elements read from imagery: `ROAD-W`, `ROAD-S`, `RAIL-E` (grade B). 1,471 elements. No existing element changed.
- README evidence rows SP-E038 and SP-E063 and the v7.26 opening paragraph rewritten to the current state.
- 183 sources (42 official, 42 international, 99 Korean).

## v7.27 — 2026-11-15
- Finding recorded, no geometry changed: the public satellite imagery is oblique. The "east end blocks" of the fabs show the wall graphic and are most likely the east walls seen between roof edge and wall foot; roof-read outlines may lie too far west by about 0.3 × height. New `meta.imagery_geometry`; `P1`–`P4-endblk` renamed; `UT-34E` note. Plan corrections are deferred until orthorectified outlines are checked.
- Viewer legend: grade B reads "plan read from imagery (heights assumed)"; Korean label left in the English viewer for `UT-34` fixed.
- `meta.infra_plan`: first approval date of the Godeok stage split stated as not established. `HUB_FLR_1695` and 36 notes describe the full-column exports; earlier route kept as history.
- `data/register_vs_model.csv`: status wording "area-similar candidate"; new columns for fab plans without the east strip (1.3–7.3% smaller than the permit building areas).
- `src/tools/register_compare.py`: command-line arguments, documented inputs and SHA-256; no absolute paths.

## v7.26 — 2026-11-15
- Permit record joined to building names: 701 floor-level rows downloaded by Codex from the official Building HUB site (lot Godeok-dong 1695, data month 2026-09) joined with the 28 per-building rows. All rows read by script here. New derived tables `data/register_vs_model.csv` and `data/permit_floor_areas.csv`; the downloaded file is not redistributed.
- Building areas compared with model boxes: the four fabs and the EUV building agree within 5%, but FAB building / -2 against P1 / P2 and FAB building-3 / -4 against P3 / P4 cannot be told apart by area. Recorded as candidates in the notes of 36 elements (new source `HUB_FLR_1695`); no existing box moved, resized or regraded.
- `UT-34` renamed: "presumed UT building" → "candidate for the complex building or a UT building — unsettled".
- `meta.floor_area`: the 3,967,000 m² figure is now labelled as the Samsung C&T P-PJT portfolio floor area with scope and reference date not stated; the permit summary text updated.
- Ten new roof elements read from imagery on the building between P1 and P2 (`UT12-RF-N1`–`N6`, `UT12-RF-S1`–`S3`, `UT12-RF-SP`), grade B, type and height unknown. 1,468 elements.
- Follow-up: permit summary in `meta.floor_area` updated with Codex's full-column export (316 per-building rows, 701 floor rows with unique keys; 70 buildings in the main permit); `meta.infra_plan` records the official 340,000 m³/day basic-plan capacity for Godeok (new source `R7_2026_15`) beside the 450,000 m³/day of the complex notice.
- 182 sources (41 official, 42 international, 99 Korean).

## v7.25 — 2026-11-14
- No box moved, resized or regraded. Removed `UT-34-CT`, an assumed cooling tower zone from an earlier version that overlapped the rows `CT34-R4`/`CT34-R5` and the unidentified blue modules read from imagery in v7.24; 1,458 elements.
- Notes extended on `UT-12` (the "240,000 refrigeration tons" is a size expression, not a daily volume, load or count; not copied to P3/P4), `BR-34a/b/c` (press photo caption on four bridges recorded as a concept note, new source `DEALSITE_BR`) and `PUB-WWTP` (use-approval date is not an operation date).
- `KEPCO-PAD` note corrected: the press figure of about 100,000 m² is no longer said to correspond to the register's site area; press, site area and total floor area are recorded side by side.
- Evidence intake for ten more items (SP-E049–E058) in README; none required a new element.
- Seventh bundle (SP-E059–E062): the register rows for lots 1695 and 1696 were already in the model; they were queried again and match. `meta.floor_area.gov_register_campus` reworded (query result, not a building count; Technology building-2 left unassigned; lot areas 1,833,839.5 m² and 804,237.8 m² recorded without fitting any boundary). Stale wording removed from the `OFF-2` note.
- `meta.floor_area` reworded after a data audit by Codex: the 128,900 m² figure is no longer treated as the P2 fab floor area and the "model plan may be 13% small" check is withdrawn; register values are marked as transcriptions; permit-query scope updated with SP-E063 (28 large rows, not assigned to any fab). The 592,077 m² / B1–8F supervision record is kept as a project-level figure.
- Height wording corrected: the 83 m press figure does not name P1, so the P1 height is now shown as an assumption (viewer grade A → C) and P2–P4 as the same concept assumption; geometry unchanged. `UT-34` note records that a KRX filing names a "UT building" for P3 (new source `KRX_P3PH4`).
- 180 sources.
- STEP read-back: 1,234 solids, 7,071 faces; DXF audit 0 errors; Korean and English data identical in ids, sources, grades and boxes.

## v7.24 — 2026-11-14
- Utility building between P3 and P4: five presumed cooling tower rows with 98 fan cylinders and two rows of unidentified blue modules, read from imagery; 1,457 elements. Preview 29.
- P1 roof racks corrected from imagery: full band depth on the east half only, inner strip on the west half (new elements P1-rack-S2, P1-rack-N2); 1,459 elements in total.
- Three Samsung pages (glossary on fabs, OHT article, Line 1 block model) opened, checked and attached as sources to existing concept elements: FFU ceiling, interbay OHT aisles, plenum zones. No new element and no grade change.
- P5 site note: second press figure for Fab 1 (211 m × 638 m) recorded next to the earlier one.
- Evidence intake table for 48 items received from the financial-analysis workstream (README). P4 phase filing periods recorded in `meta.p4_phases.filings_latest`; the P3 Ph1 position now cites the filing instead of an inference.
- CITATION.cff restored: it was empty in the v7.20–v7.23 packages because of a script error; copies of v7.23 already distributed still contain the empty file.
- Announcement posted on LinkedIn (link in README).
- PAD-P5 note and source GG_2026_189: the official notice of 2026-07-30 keeps zone A1-1 at a floor-area ratio of 350% or less; the triple fab stays a press-reported plan.
- README summary table corrected (1,457 elements, tier counts); the v7.23 DOI is no longer given as the DOI of this version in CITATION.cff.
- `meta.infra_plan`: plan figures for the whole industrial complex from Notice No. 2026-189 (power demand in kVA, water, wastewater), recorded as notes only.
- STEP read-back: 1,235 solids, 7,077 faces; DXF audit 0 errors.

## v7.23 — 2026-11-14
- Published: GitHub release, Zenodo DOI 10.5281/zenodo.24209049, and mirrors on Hugging Face, Kaggle, Internet Archive, Printables and Sketchfab (links in README).
- 16 more supplier locations from Kakao Map added as markers (Applied Materials, KLA, Lam Research, Tokyo Electron, KCTech, Unisem, PSK, PSK Holdings, STI, Hansung Cleantech, Merck, Versum Materials, FST, a second Wonik IPS location, KC ENC, Samsung C&T camp); 1,352 elements.
- README cleanroom-area column: the figures come from a brokerage report, not from Samsung.

## v7.22 — 2026-11-13
- README now states that this is a living project that is updated continuously (added 2026-11-14).
- Nine rooftop equipment zones read from imagery (west/east bands of P1–P4, centre of P3); 1,336 elements.
- Shadow-ratio height check documented: P1 roof step not contradicted; P2 ≈ 86 m ± 4 m against the 83 m assumed; P3 and P4 not determined.
- STEP read-back: 1,112 solids, 6,633 faces; DXF audit 0 errors.

## v7.21 — 2026-11-13
- Storage tanks exported as cylinders in every format (13 elements); cold boxes and process blocks deliberately kept as boxes.
- Linde north-east building height set from the building register (22.55 m); register heights of the public wastewater plant recorded.
- Eighth consultation (Codex, GPT-6 Astra) recorded in CONSULTATION.md; its checks on area figures, rooftop naming and height assumptions found no conflicting use in the model.
- New preview 28. STEP read-back: 1,103 solids, 6,579 faces; DXF audit 0 errors.

## v7.20 — 2026-11-13
- Logistics warehouse renamed "relocation planned" in the model, viewer label and CSV; note cites an unofficial layout graphic as a reference only.
- STEP and DXF read-back repeated on this build: 1,103 solids, 6,618 faces, no invalid solid in the first 400 checked; both DXF files audit with 0 errors.
- 1 source added (173 in total).
- Licence split: code under MIT (`LICENSE-CODE`), everything else stays CC BY 4.0.

## v7.19 — 2026-11-13
- Supplier and logistics notes extended from company announcements, trade press and brokerage reports: Air Products (2015, 2018), Air First (2021 official release, 2026 plant report), Linde (2019), the 2018 Pyeongtaek CDC, the P5-2 reports, Wonik IPS and Hanyang ENG.
- 12 sources added (172 in total). No geometry changed.

## v7.18 — 2026-11-13
- Logistics warehouse note rewritten: the press describes a CDC (product distribution centre) on the planned P6 site, with a new CDC under construction at Poseung; the building match remains an inference.
- Supplier roles added to the notes of the gas plants and map markers, from company material, filings and press (Air Products, Air First, Linde, Samsung E&A, SEMES, Wonik IPS, Hanyang ENG).

## v7.17 — 2026-11-13
- Extended to the wider Pyeongtaek complex (about 3.9 km × 3.6 km): Air Products Korea plant, Air First plant, Samsung logistics warehouse and annexes, and map markers for construction camps and supplier sites. 28 new elements.
- Viewer: the default section cut now covers the extended area; labels for the gas plants, the warehouse, the Linde plant and the public wastewater treatment plant.
- New previews 24 to 27.

## v7.16 — 2026-11-13
- Added 5 structures read from satellite imagery: two overbridges (UT building–P2), one link (west support building–P2), two truss pipe rack bridges. Bridges are now bright blue and labelled; parking buildings and the employee parking lot are labelled.
- Viewer works offline: three.js r128 and OrbitControls (MIT licence) are inlined.
- Eight more international sources for gases, power and water (Linde and Air Products press releases, GE Vernova HVDC case study, Samsung Semiconductor Global Newsroom, Korea JoongAng Daily, The Korea Times).
- Removed two outdated sentences about the technology building from the notes.
- New previews: `22_products_by_line.png`, `23_west_bridges_parking.png`.

## v7.15 — 2026-11-13
- Source priority rule: official material and registers, then international wire and trade media, then Korean press. `SOURCES.md` grouped by tier.
- Eight international sources for fab-level facts (Reuters, Samsung Newsroom U.S., TrendForce, DIGITIMES).

## v7.14 — 2026-11-13
- English edition: data, viewer, drawings and documentation.
- Products by line (official announcements and press), shown in the viewer and stored in `meta.products`.
- Verification: fab bodies and annexes overlaid on zoom-18 imagery; STEP and DXF read back with open-source CAD libraries.

## v7.13 and earlier — 2026-11-11 to 2026-11-12
- Satellite re-reading of the technology cluster, the KEPCO Godeok lot, the Linde plant and the public wastewater treatment plant.
- Public building register data for the KEPCO lot, the Complex 2 parking building, the north gate building and adjacent facilities.
- Utility systems (29 systems), EHS layers, connectivity check, confidence grade M for public map labels.
