#!/bin/sh
# Build the English data, viewer and exports from the Korean master (campus.json).
set -e
cd "${GEN_WORK:-$(dirname "$0")}"
export GEN_WORK="$(pwd)"
python3 i18n/apply.py
python3 i18n/code_en.py
sed -i 's/<html lang="ko"/<html lang="en"/' viewer_template_en.html
sed -i 's/^OUT = "release"/OUT = "release_en"/; s/json.load(open("campus.json"))/json.load(open("campus_en.json"))/; s/textwrap.wrap(t, 96)/textwrap.wrap(t, 165)/; s/g\["limit"\], 100)/g["limit"], 175)/; s/\[:34\] for k in g\["src"\])\[:150\]/[:40] for k in g["src"])[:230]/' export_en.py
sed -i 's/fig.legend(hs, ls, loc="lower center", ncol=2/fig.legend(hs, ls, loc="lower center", bbox_to_anchor=(0.5, 0.022), ncol=2/' export_en.py
python3 mkview_en.py
mkdir -p release_en/viewer release_en/src release_en/preview
python3 export_en.py > export_en.log 2>&1
tail -3 export_en.log
cp index_en.html release_en/viewer/index.html
# v7.26: derived permit comparison tables (inputs are not redistributed)
# (only in the maintainer's workspace, where the permit exports exist; the published tables are already in data/)
if [ -d regcmp ]; then
  cp regcmp/register_vs_model_en.csv release_en/data/register_vs_model.csv
  cp regcmp/permit_floor_areas_en.csv release_en/data/permit_floor_areas.csv
  mkdir -p release_en/src/tools && cp regcmp/compare.py release_en/src/tools/register_compare.py
fi
