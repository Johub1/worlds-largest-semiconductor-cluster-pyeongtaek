# Changelog

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
