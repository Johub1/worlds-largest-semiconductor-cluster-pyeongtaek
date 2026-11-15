# Generator reproduction status

Living project, updated continuously.

The committed Korean generator is not yet synchronized with the checked-in v7.41 dataset. On 15 November 2026, `build.py` and `utility.py` from commit `0a7cee066e50211be5221542bfe02f8297386751` were copied to an isolated working directory and `python build.py` completed successfully. Its `campus.json` contained **1,459 elements and 178 source keys**, compared with **1,474 elements and 202 source keys** in the checked-in dataset. Both contained 86,620 conceptual equipment entries; that number is not an installed equipment count.

The checked-in dataset has 16 element IDs absent from that generator output and omits one ID present there. For common IDs, boxes, rotation, fab/floor identifiers and confidence labels matched; 89 elements had different source-ID lists. The checked-in dataset also has 24 additional source keys and nine additional metadata keys. Names, descriptions and layer labels were excluded from invariant comparisons because the generator output is Korean and the checked-in dataset is English.

This test identifies a source-to-output reproduction gap. It does not invalidate the separately checked JSON, CSV or STEP files, establish site accuracy, or justify reverting the newer dataset. Use the checked-in `data/campus.json` as input to the export/viewer scripts described in the main README. Synchronizing the current generator, utility source and translation tables, then checking the bilingual packages, remains outstanding.

The isolated test covered model-data generation only. It did not execute the full translation, viewer, export or ZIP pipeline. The bundled `build_en.sh` and `i18n/apply.py` contain `/home/claude/work` paths and need environment adaptation before use elsewhere. The documentation update does not change the generator, model geometry, source links, release assets or external mirrors.

### Check regenerated model data

After running the intended generator and its English translation, compare that output with the checked-in English dataset:

```sh
python src/tools/verify_generated_data.py --generated /path/to/campus_en.json --reference data/campus.json --report regeneration-check.json
```

Exit status `0` means equal JSON content, `1` means differences, and `2` means an input or I/O error. The comparison covers all top-level sections and nested values, matches element records by ID, and also checks their order. Decimal values are compared without binary rounding; integer/decimal notation alone is ignored. Language differences are not ignored. Use the same language and intended revision. A detail limit only limits the report, not whether differences cause failure. Decimal differences in reports use a `json_decimal` string to retain their digits. Non-finite values and numbers above the supported finite binary64 range are rejected.

This command neither runs the generator nor fixes the source/output gap described above. It does not verify site accuracy, CAD exports, bilingual meaning, documentation or ZIP contents. In the isolated test on15November2026, the published generator plus published translation tables still differed from the checked-in dataset; counts alone had missed updated notes, names, supplier descriptions and metadata. The current generated output must not replace the newer dataset until those differences are resolved.
