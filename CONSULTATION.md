# Consultation record

The model was reviewed in six rounds with two other AI models: Gemini and Codex (GPT-6 Astra). The rule throughout: a design suggestion can be adopted on its merits, but a **factual claim is used only after it is verified against a source**. Claims that could not be verified were held, and the model says so here.

## Round 1 — Gemini (2026-11-11)

Gemini said it answered without live web access, so only independently verified facts were used.

**Adopted (design suggestions)**
- Add EHS layers: vertical gas supply/exhaust flow, gas detector positions, egress travel distance.
- Show yellow lighting in the photo zone (also seen directly in official video).
- Put disclaimers in the README, viewer and drawings.
- Name suppliers as text, not logos; do not include satellite imagery textures.

**Adopted after independent verification**
- Shinsung E&G cleanroom supply to Pyeongtaek (press and filing).
- STI CCSS supply to Pyeongtaek (press).
- Sebo MEC mechanical works at Pyeongtaek (filing summary).
- Eight floors in two stacked levels with an east/west split (consistent with contract names in filings and cleanroom area figures).

**Held (no source found)**
- A floor count from a construction-management record and a building height of 83–88 m.
- A table of tool outline dimensions (no URL given).
- Deliveries to Pyeongtaek by several named equipment makers (kept only as representative industry suppliers).
- Layout of the green building, complex building and substation (general statements with no building match).
- A floor-height table (marked by Gemini itself as an estimate).

## Round 2 — Gemini (2026-11-11), utility systems

**Adopted (design suggestions)**
- Draw chilled water, condenser water and air circulation separately; distinguish low- and medium-temperature chilled water; show waste-heat recovery as an optional system.
- Separate bulk gas and specialty gas routes; mark tanker filling points and cylinder exchange points.
- Segregate exhaust (acid, alkali, organic, heat) and collect wastewater by composition to the green building.
- Chemicals: unloading (quality check) → storage → CCSS → VMB; slurry in a circulation loop.
- Power: extra-high-voltage receiving → dual medium-voltage feeders → electrical-room transformers → low voltage; UPS and emergency power separate.

**Adopted after independent verification**
- Supply by Air Products and other gas companies (four press reports: split among Air Products, Linde and Air First, underground pipelines).
- 345 kV and 154 kV supply (power-industry and daily press: Godeok–Seoanseong 23.5 km, 2 GW).
- Green buildings (local press: two, about 70,000 t a day).

**Held**
- Most specific figures for pressure, purity, velocity and temperature (only MAU chilled water and PCW temperatures read directly in the literature are used).
- Clause contents of several SEMI, FM Global and Korean BAT documents (titles only; text not read).
- 22.9 kV distribution and the low-voltage step-down levels (shown only as an assumption of usual Korean practice).

## Round 3 — Codex, GPT-6 Astra (2026-11-11)

Astra said it had not checked original documents or site material.

**Adopted**
- Replace "measured" with "dimensions estimated from satellite imagery" and state resolution and error.
- Separate CHW, CW and PCW; show PCW as a closed loop that is not consumed.
- Do not force one gas configuration; distinguish "transfer/filling connection" from "cylinder exchange area".
- Do not present POU → rooftop scrubber → stack as the only configuration; label stack output as treated exhaust.
- Electrical rooms instead of per-floor transformers; UPS for selected critical loads only; normal, UPS and emergency power kept apart.
- System identifiers (CHW.S / CHW.R, EXH.ACID, WW.F, ELEC.UPS …).
- A table of evidence and limits per system; publish the heat-balance check `Q = ρ·V·cp·ΔT`.
- Keep the wording that the egress result is an assumption-based screening, not a code-compliance finding.

**Recorded as future work**
- Object/port/connection graph with source-to-end verification; split GLB with lazy loading; per-building STEP; DXF blocks.
- Reference level names (L01–L08); keyboard navigation and a searchable equipment list.
- Cause–consequence–safeguard tables for safety scenarios (PCW flow loss, exhaust degradation, gas leak, power failure).
- An evidence ledger (source, date, screen position and object id per claim).

**Not adopted, with reason**
- The view that phase positions lack evidence: the positions are written in the contract names of filings, so they were kept (only P3 Ph1 is marked as inferred).
- A list of standards and textbooks offered as sources: the texts were not read, so they are not in the source list.

## Round 4 — review of the v4 result (2026-11-11)

Gemini raised three points: chilled water headers in the plenum risk leaks into the cleanroom; a south/north exhaust split lengthens routes compared with an east/west split; electrical rooms only on the north side increase low-voltage drop.

Astra's cross-review: all three are best recorded as **review hypotheses**; whether the real Pyeongtaek layout does one or the other cannot be judged without drawings.

**Outcome**
- The three points are written into the "limits" text of the relevant systems as review hypotheses. The layout was not changed, because neither option has public evidence.
- Astra's proposed minimal connectivity check was implemented as `src/check_connect.py`; it found four broken stretches in the chemical system, which were fixed.
- A cross-system cascade/interlock table suggested by Gemini is recorded as future work.

## Round 5 — substation, water, solar, grading (2026-11-12)

**Gemini**
- An earlier held claim (Godeok #2 substation total floor area 17,853㎡) was confirmed in a contractor's track record and adopted.
- A claim about the green building's location, citing a specific newsroom article, could not be found and was held; Gemini later corrected itself that the article could not be confirmed.
- A claim of parallel 154 kV and 345 kV receiving had no supporting article and was held (campus receiving voltage is marked unconfirmed).

**Codex (GPT-6 Astra)**
- Judge existence, building match, location, shape and numbers separately, and show the type of source → a new grade **M** (public map label) was introduced.
- A map POI may be an entrance or representative point, and OSM is not an official source → caution added; names from maps are graded M, not A.
- "A user's request does not strengthen evidence" → six facilities without evidence stay as estimates, with the reason stated.
- Supply and use are different measures → date and basis are written next to water figures.
- Do not call 0.4 → 0.7 MW of solar an expansion unless the series has one basis → report figures are listed as given.

## Round 6 — interior detail and joint reading of sources (2026-11-12)

**Codex (GPT-6 Astra)** read sources directly: a Samsung newsroom article on wastewater treatment, a press article on a P1 tour, and pages of a sustainability report. It could not open the YouTube videos, one news article (403) or a journal PDF.
- It found the GCS building and supply bridges in the press article; the original was re-read and the fact added.
- Corrections adopted: 1,850 OHT vehicles is a count, not evidence for rail spacing (now "assumption for visualization"); "30 m spacing because of the ANSI 10-second rule" does not follow (now described as a first-pass layout).
- Video observations made by Claude (FOUPs, OHT, yellow lighting, docks) were **not** re-confirmed by Astra, and this is stated.

**Gemini** said it watched the video; its scene times matched the frame order read independently. Its claims that the glass-door equipment carries a "high-pressure gas" sign and that a reddish bar on tools is an OHT bumper could not be read at frame resolution or were its own guesses → held ("purpose unconfirmed").

## Round 7 — v7, preparation for publication (2026-11-12)

**Codex (GPT-6 Astra)**
- Could not open the two YouTube videos → the video reading is recorded as confirmed by Claude alone.
- Complex building and 154 building: grade C is right, but separate "identified by an unofficial channel (P4)" from "by analogy (P1–P3)" → adopted.
- A contract name in a filing does not prove a match to a captioned block, and the name "154 building" does not fix the receiving voltage or transformer arrangement → adopted (routes are stated as an independent concept design).
- Hide weakly supported move-in openings from the default exterior and offer them as a reference-design toggle → adopted.
- Separate planned and actual dates in schedule tables; separate sampling point from source in the PFAS reports → adopted.
- Priorities before publication: claim-to-source mapping, licence split, review for sensitive information, statement of limits, trademarks and unofficial status.

**Gemini**
- Excluding CCTV, excluding logo images and adding disclaimers are appropriate → adopted.
- Dimensions and standards cited for move-in openings (a SEMI S8 clause, SEMI E72, a 4–6 m × 5–6 m opening) could not be verified → held; the opening size in the model stays an arbitrary value.
- "Use MIT or Apache 2.0 to prevent unauthorized commercial use" → not adopted, because those licences permit commercial use. CC BY 4.0 is kept.

## Round 8 — how to add detail (2026-11-13)

**Codex (GPT-6 Astra)** was given a text description of v7.20 (it did not open the model or the source list) and asked for a priority list, usable public sources, a procedure for heights, and likely errors. Its main points:

- Priorities: fix large shapes, heights, materials and the scope of each source before adding more boxes. Top five: fab and utility-building outlines and roof steps; façade panels and colour bands; separating tanks, cold boxes and exposed columns at the gas plants; roads, parking and green areas; the large rooftop silhouettes.
- Do not turn every gas-plant tower into a cylinder: a cold box is a rectangular insulated enclosure around the columns.
- Heights: fix which height is meant (register height, roof surface, parapet, rooftop plant, highest stack); check the building register per building; shadow measurement only with a known acquisition time, with the error stated; never derive storey heights by dividing total height by storeys.
- Likely errors to check: using "25 football pitches" (a cleanroom figure) as a P3 footprint; using a utility-building project area as a whole-fab area; naming every rooftop outlet a scrubber; copying one interior to all four fabs without marking it as concept; treating a supply contract as proof of a pipe route.
- It could not find the environmental impact assessment for the campus, official elevations of P1–P4, or dimensioned material for the Air Products and Air First plants.

**What was done with it (v7.21):** tanks with a round plan in imagery became cylinders and everything else stayed a box; one Linde building height was taken from the register; the listed error candidates were checked against the generator — neither area figure is used, the repeated interior is already graded as concept, and P2–P4 heights are already marked as an assumption. Outlines with roof steps, façade panels, roads and rooftop silhouettes are not done yet.

## Submission of an advance notice (2026-11-13)

An advance notice describing the project, its public-source basis and how to request a correction was emailed to the contact address that Samsung Electronics lists on its semiconductor website and to the compliance and press addresses of its US semiconductor subsidiary. Codex independently confirmed that no public contact form is offered on the checked pages of that website. No reply had been received when this release was packaged; silence is not treated as approval. The notice was sent on 2026-11-13 (KST). Any reply received will be added to this section in a later release.
