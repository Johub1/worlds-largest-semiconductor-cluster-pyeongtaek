# Generator reproduction status

Living project, updated continuously.

The committed Korean generator is not yet synchronized with the checked-in v7.41 dataset. On 15 November 2026, `build.py` and `utility.py` from commit `0a7cee066e50211be5221542bfe02f8297386751` were copied to an isolated working directory and `python build.py` completed successfully. Its `campus.json` contained **1,459 elements and 178 source keys**, compared with **1,474 elements and 202 source keys** in the checked-in dataset. Both contained 86,620 conceptual equipment entries; that number is not an installed equipment count.

The checked-in dataset has 16 element IDs absent from that generator output and omits one ID present there. For common IDs, boxes, rotation, fab/floor identifiers and confidence labels matched; 89 elements had different source-ID lists. The checked-in dataset also has 24 additional source keys and nine additional metadata keys. Names, descriptions and layer labels were excluded from invariant comparisons because the generator output is Korean and the checked-in dataset is English.

This test identifies a source-to-output reproduction gap. It does not invalidate the separately checked JSON, CSV or STEP files, establish site accuracy, or justify reverting the newer dataset. Use the checked-in `data/campus.json` as input to the export/viewer scripts described in the main README. Synchronizing the current generator, utility source and translation tables, then checking the bilingual packages, remains outstanding.

The isolated test covered model-data generation only. It did not execute the full translation, viewer, export or ZIP pipeline. The bundled `build_en.sh` and `i18n/apply.py` contain `/home/claude/work` paths and need environment adaptation before use elsewhere. The documentation update does not change the generator, model geometry, source links, release assets or external mirrors.
