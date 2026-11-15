# Reproducing the building-record comparisons

Method snapshot, 15 November 2026. Companion to [Evidence Reconciliation Notes](evidence_reconciliation.md). This describes the public web exports actually used, not an independently queried API response.

Living project, updated continuously.

## Common query settings

Use the official [Architecture HUB permit query](https://www.hub.go.kr/portal/opn/tyb/idx-acpmslg.do) and the relevant basic-summary, per-building or floor-summary menu. Select Gyeonggi-do / Pyeongtaek-si / Godeok-dong / ordinary land (대지). Query main lot 1695 or 1696 with sub-lot 0000. The displayed data month for the reviewed exports was September 2026. Select all custom output fields (맞춤형항목 전체선택) and export JSON.

Region codes in the exports: SGG_CD 41220, STDG_CD 12800, PLOT_SE_CD 0. These are public location-query fields; no service key or account credentials are needed in this note. A new query may return a revised snapshot. Record its data month before comparing it with this review.

Keep ACPMSLG_SN (permit key) and ACPMSLG_DGCB_OUN_SN (per-building key) as strings. Do not aggregate all permits at one lot. Temporary-building permits and repeated site areas are separate records. Do not remove apparently duplicate rows after dropping their keys.

## PT-A001 and PT-A002

Filter the basic-summary and per-building exports to exactly:

| Lot | ACPMSLG_SN | Basic-summary building count | Per-building rows |
|---|---|---:|---:|
|1695|1099100090586|52 main + 18 annex = 70|70|
|1696|1099100200558|14 main + 5 annex = 19|20|

Compare the basic-summary fields BDAR (building area), GFA (gross floor area) and FART_CMPTTN_GFA (floor-area-ratio calculation area) with the sums of the corresponding building-row fields. Use decimal arithmetic; retain two decimal places in square metres.

| Lot / measure, m² | Basic summary | Building-row sum | Sum minus summary |
|---|---:|---:|---:|
|1695 / BDAR|935,346.60|935,651.56|304.96|
|1695 / GFA|4,713,467.42|4,713,467.42|0.00|
|1695 / FART_CMPTTN_GFA|4,394,061.65|4,394,061.65|0.00|
|1696 / BDAR|503,106.23|545,391.95|42,285.72|
|1696 / GFA|2,160,822.49|2,321,855.03|161,032.54|
|1696 / FART_CMPTTN_GFA|1,931,951.34|1,944,820.30|12,868.96|

The 1696 parking-building row has FART_CMPTTN_GFA 13,833.63 m². Subtracting it from the building-row sum gives 1,930,986.67 m², which is 964.67 m² below the basic summary. This is why a simple parking-row removal does not fully reconcile the record.

## PT-A004

Use the [official floor-summary query](https://www.hub.go.kr/portal/opn/tyb/idx-acpmslg-flrcb.do) with the same location settings and all output fields. Join to building records by the full permit and per-building keys, not by an assumed marketing fab number. The 1695 reviewed exports contain 316 building records and 701 floor records across multiple permits. These are not counts of completed fab buildings.

Preserve each floor key and the underground/above-ground/rooftop designation. Compare floor-area sums with each building's GFA. Exact agreement of a difference with a rooftop row is a numerical observation; it does not by itself establish the legal floor-area inclusion rule. No generic rooftop exclusion rule is applied.

## PT-A005

Use the official [aggregate-register query](https://www.hub.go.kr/portal/opn/tyb/idx-bdrg-totldr.do) and [individual-building-register query](https://www.hub.go.kr/portal/opn/tyb/idx-bdrg-ttlldr.do) for Godeok-dong 1730-0000, with all output fields. The reviewed exports contained one aggregate record and nine individual building records. Preserve the register keys (BDRG_SN); these are not interchangeable with permit-building keys.

| Measure, m² | Aggregate register | Nine-building sum | Sum minus aggregate |
|---|---:|---:|---:|
|BDAR|20,081.47|20,081.46|-0.01|
|GFA|48,546.62|48,558.01|11.39|
|FART_CMPTTN_GFA|41,126.87|41,138.26|11.39|

The displayed creation date is not a complete revision history. Equal displayed dates do not prove that every underlying entry was updated simultaneously. Register dates, construction completion, commissioning and current operating capacity are separate facts.

## Limits

These query-service URLs are landing pages, not permanent links to the exported rows. The row keys and data month above identify the actual comparison. No private owner data, security-system details, images, credentials or full unrelated query exports are included. A missing result under one query is not proof that a building is unapproved or that no public record exists.
