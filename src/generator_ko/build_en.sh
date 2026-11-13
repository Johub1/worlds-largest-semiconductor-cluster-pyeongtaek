#!/bin/sh
# Build the English data, viewer and exports from the Korean master (campus.json).
set -e
cd /home/claude/work
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
