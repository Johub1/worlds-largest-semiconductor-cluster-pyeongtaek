# Reading the model's estimates

Living project, updated continuously.

The model aims to explain Pyeongtaek Campus using public evidence and explicit approximations. It is not a surveyed replica. An unavailable internal drawing does not prevent a useful conceptual representation.

| Feature | How to read it |
|---|---|
| Building footprints | Public-imagery measurements and mapped outlines provide context; roof edges, wall bases, dates and building identities may differ. |
| FAB height | The current P1–P4 envelope height is an 83 m modeling assumption. The underlying press dimension does not conclusively identify an individual fab. It is not a legal building-register height or an independently measured height for all four fabs. |
| Internal levels | The repeated subfab, cleanroom and air-plenum section explains functional relationships. Its elevations and level labels are conceptual, not surveyed floor levels or a direct translation of permit-floor numbers. |
| Phase labels | Filing descriptions support lower/upper and east/west work scopes. P3 and P4 have different phase sequences; conceptual partition lines are not as-built process boundaries. |
| Process tools and utilities | Displayed equipment, pipes and internal transport represent typical functions and relationships. Their counts, models and coordinates do not establish installed assets. |
| Construction and materials | A named supplier reference supports its stated scope. General catalog dimensions, capacities and methods remain separate from verified project deliveries. |

Future height estimates may compare public aerial views with mapped dimensions or nearby buildings. Such estimates should identify their reference, image date and uncertainty. No new aerial height measurement is claimed by this note. Visual detail and numerical precision do not, by themselves, increase factual confidence.

## How the conceptual equipment count is produced

The 86,620 equipment entries count rendered boxes, not 86,620 machines. The generator places repeated illustrative bays within the modeled cleanroom envelopes, using a 13 m bay pitch, chosen process-area weights, tool-envelope dimensions and spacing. Its tool routine may represent one illustrative assembly with multiple boxes: for example, a loader, equipment body and separate FOUP/load-port components. Utility, handling and auxiliary boxes are also included in the same equipment array.

The count therefore describes the generated reference scene. It is not derived from a disclosed Samsung asset register or inferred from wafer-start capacity, sales or construction spending. No production-capacity-to-tool-count conversion is implemented in this generator. A physical tool-count estimate would need, among other inputs, a separately supported process and throughput model including utilization, yield and product mix. These inputs are examples, not a sufficient estimation method. Translating such an estimate into a rendered scene would then require separate rules for how many boxes represent an assembly. Those campus-specific inputs and mappings have not been established here. Box-type totals must not be read as installed scanner, etcher or other machine counts.

The modeled external massing can be useful even while these internal quantities and positions remain conceptual. Changing the illustrative bay spacing or representation detail would change the scene count without establishing a different actual factory inventory.

OHT vehicle placement uses a separate illustrative calibration. The generator divides the total length of P1's modeled rail segments by an approximately 1,850-vehicle press figure to set a spacing; the generated P1 scene contains 1,848 vehicle boxes. The same spacing is reused on the different modeled rail lengths of P2–P4, so their totals are scene results, not separately reported inventories. This is a press-figure-based spacing rule, not a verified inventory or a production-capacity calculation.


FFU entries are illustrative 10 × 10 m blocks representing grouped ceiling units. The 4,420 blocks are not an installed fan-filter-unit count. EUV scene entries also split assemblies into body, light-source and auxiliary boxes, so their type totals are not a scanner inventory.

## Why the envelope uses 83 m

The 83 m height comes from a [25 August 2022 ZDNet Korea report](https://zdnet.co.kr/view/?no=20220825080050), which gives a Pyeongtaek production line as 518 m long, 201 m wide and 83 m high without identifying a fab number. The model retains 83 m as a common illustrative envelope. Similarity in public aerial views does not independently measure the height of P1–P4. The measurement boundary, legal-register definition and internal elevations remain unconfirmed.

Support-building register heights describe different buildings. They provide context, but cannot calibrate a fab without matched building identity and an independent measurement method. Exploratory image-lean comparisons also depend on uncertain camera geometry and the interpretation of the visible roof or wall strip. An offset estimated from the assumed 83 m starts from that assumption. These checks do not independently validate 83 m. No new aerial measurement or numerical confidence interval is claimed.

## P5 remains a construction-site approximation

The model already includes `PAD-P5`, a grade-C approximation of the Complex 2 construction-site extent, labelled as under construction. It does not specify the individual P5 fab envelopes. Conflicting reported dimensions and cleanroom configurations remain source-specific plans, rather than approved geometry.

Samsung's [10 February 2026 community-meeting record](https://download.semiconductor.samsung.com/resources/others/pyeongtaek-20260312.pdf), page 2, records a presentation on P5 construction progress and expected construction staffing, without numerical progress or completion evidence. Shinhan SNG's [October 2026 order announcement, posted on 3 November](https://shsng.com/ko/business_order?mode=view&no=1282), identifies additional steelwork in section 3 of Samsung C&T's P5 FAB2 construction. The announcement identifies an order, not installation or completion. Its FAB2 label is not assigned to FAB1, a particular model box, or precise coordinates. These records support retaining a construction-site representation; they do not supply a new measured building shape.

See the [water-treatment scope note](godeok_environmental_review_context.md#sewage-and-industrial-wastewater-statistics-have-different-scopes) for the separate public sewage and industrial wastewater facilities. The model's illustrative utilities do not combine their capacities.
