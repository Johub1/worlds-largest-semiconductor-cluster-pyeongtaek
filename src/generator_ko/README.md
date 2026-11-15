# Korean generator, translation tables and build procedure

Living project, updated continuously.

## Current source-context update (16 November 2026)

The current data/viewer pipeline produces 1,474 elements and 203 source keys. One Green-dong source and one metadata object were added; existing geometry, equipment arrays and grades are unchanged. Text reads explicitly use UTF-8 and generated text uses LF. Translation warnings escape console characters that cannot be represented.

Fresh package checks on Windows and Linux ran build, translation, both viewers, same-language verification and root viewer paths with UTF-8 mode disabled and an ASCII console. Generated data and viewers matched their package references byte-for-byte. CAD export was not rerun for this update; the historical export checks below concern the earlier dataset and are not a fresh export claim.

To regenerate the current English data and viewer without rerunning CAD export:

```sh
cd src/generator_ko
python3 build.py
python3 i18n/apply.py
python3 i18n/code_en.py
python3 mkview_en.py
python3 ../tools/verify_generated_data.py --generated campus_en.json --reference ../../data/campus.json
```

## Historical v7.42 check (15 November 2026)

The historical v7.42 source snapshot contained the generator, utility source, translation tables and build scripts used to produce that release. It was synchronized from the maintainer's working copy for v7.42; the earlier snapshot in this folder (which produced 1,459 elements and 178 source keys) has been replaced.

Isolated check on 15 November 2026 (a fresh copy of `src/generator_ko`, `src/tools`, `src/vendor` and `data/` in a new directory, no other files):

- `python3 build.py` → `campus.json` (Korean master): 1,474 elements, 202 source keys.
- `python3 i18n/apply.py` → `campus_en.json`; `python3 ../tools/verify_generated_data.py --generated campus_en.json --reference ../../data/campus.json` → exit 0, no differences (the two files are byte-identical).
- The Korean `campus.json` compared with the Korean package's `data/campus.json` → exit 0 (equal content; serialization differs).
- `sh build_en.sh` → the English viewer and the CSV tables in `data/` are byte-identical to the published files. The DXF files differ only in their creation-time header fields; the STEP file differs only in its timestamp and entity numbering (the multiset of 425,972 entities is identical after renumbering).

That check demonstrated regeneration of the v7.42 dataset from that historical snapshot. It does not verify site accuracy, which is described by the confidence grades in the data.

## Procedure

Requirements: Python 3 with `trimesh ezdxf cadquery numpy matplotlib` (exports) — the generator and translation steps use only the standard library.

```sh
cd src/generator_ko
python3 build.py                 # Korean master: campus.json
python3 i18n/apply.py            # English data: campus_en.json (prints "missing 2": two URLs that stay in Korean)
python3 ../tools/verify_generated_data.py --generated campus_en.json --reference ../../data/campus.json
sh build_en.sh                   # English viewer and exports into ./release_en (models, drawings, data CSVs)
python3 cadcheck.py              # optional: STEP read-back and DXF audit of ./release_en
```

`i18n/apply.py`, `i18n/code_en.py` and `build_en.sh` work in their own folder; set `GEN_WORK` to use another working directory. `mkview.py`/`mkview_en.py` look for `vendor/` next to them or one level up (`src/vendor`). The maintainer's workspace also builds a Korean package (`python3 mkview.py`, `python3 export.py` with `OUT = "release"`) and the permit comparison tables (`regcmp/`, inputs not redistributed); `build_en.sh` skips the latter when `regcmp/` is absent.

How the translation works: `build.py` writes all text in Korean. `i18n/apply.py` replaces each Korean string with its English entry from `names_en.json`, `notes_en.json`, `src_en.json`, `misc_en.json` and `extra.json` (exact-match tables; `extra.json` holds the entries added since v7.25). `i18n/code_en.py` produces `viewer_template_en.html` and `export_en.py` from the Korean viewer template and export script.

## Not included

Third-party imagery, the permit-register exports used for `data/register_vs_model.csv`, and the internal review files of the collaborating workstreams.

