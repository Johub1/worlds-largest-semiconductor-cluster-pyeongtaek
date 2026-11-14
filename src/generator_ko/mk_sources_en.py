import json,re,collections
d=json.load(open('/home/claude/work/campus_en.json')); s=d['sources']
KR=r'\.co\.kr|\.kr/|//kr\.|daum\.net|naver|pstatic|namu\.wiki|dealsite|thelec|etnews|ddaily|newsis|hankyung|edaily|etoday|kedglobal|koreatimes|youtube|albamon|investchosun|bloter|sisajournal|sankun|chickstockfi|pressian|e2news|pttimes|kyeonggi|ajunews|electimes|seoulfn|segye|ptsisa|newstomato|ferrotimes|nate\.com|fnnews|skecoplant|asiae|mt\.co|businesspost|digitaltoday|4th\.kr|smarttoday|dnews|theguru|h2news|khan\.|sedaily|zdnet\.co|dailyinvest|newsprime|e-focus|ebn|sbs\.|yna\.|kcc'
OFF=r'samsung\.com|samsungsemiconductor|samsungcnt|samsungena|secc\.co|dart\.fss|data\.go\.kr|law\.go\.kr|hub\.go\.kr|arcgisonline|openstreetmap|kakao|google\.[a-z.]+/maps|map\.|eum\.go\.kr|gg\.go\.kr'
def tier(k,v):
    u=(v[1] if len(v)>1 else '') or ''; t=v[0]
    if re.search(OFF,u) or re.match(r'(Samsung (Electronics|Semiconductor|Newsroom|C&T|E&A|Engineering)|MOLIT|Kakao Map|Google Maps|Esri|OpenStreetMap|Enforcement Decree|Phase positions|National map)',t): return 1
    if re.search(KR,u) or not u: return 3
    return 2
T={1:[],2:[],3:[]}
for k,v in s.items(): T[tier(k,v)].append((k,v))
names={1:"Tier 1 — official material, filings, public registers, public maps and imagery",2:"Tier 2 — international wire services, trade media, journals, patents and standards bodies",3:"Tier 3 — Korean press and other local or unofficial sources"}
L=["# Sources","","All material is public. Keys are the ones used in `data/campus.json`.","",d['meta']['source_policy']+".","","Third-party imagery, video frames and vendor CAD were consulted but are not redistributed in this package.",""]
for t in (1,2,3):
    L+=[f"## {names[t]} ({len(T[t])})","","| Key | Source | URL |","|---|---|---|"]
    L+=[f"| `{k}` | {v[0].replace('|','/')} | {v[1] if len(v)>1 and v[1] else ''} |" for k,v in T[t]]; L.append("")
L+=["## Why Korean press remains in the list","","Contract amounts, phase names, the substation, water supply volumes and local permits are reported in detail only by Korean outlets and Korean regulatory filings. International outlets such as Reuters, TrendForce and DIGITIMES cover the fab-level facts (which line makes what, investment decisions, schedules) and frequently cite those same Korean reports. Where both exist, the international source is listed first and the original report is kept so that the claim can be traced.",""]
open('/home/claude/work/release_en/SOURCES.md','w').write('\n'.join(L)); print({t:len(T[t]) for t in T}); print([k for k,v in T[2]])
