"""Build campus_en.json from campus.json with the translation tables in i18n/."""
import json,re
W='/home/claude/work/'
K=re.compile('[가-힣]')
L=lambda n: json.load(open(W+'i18n/'+n))
EX={}
for a,b in (('notes_src.json','notes_en.json'),('misc_src.json','misc_en.json'),('src_src.json','src_en.json')):
    EX.update(dict(zip(L(a),L(b))))
import os
if os.path.exists(W+'i18n/extra.json'): EX.update(json.load(open(W+'i18n/extra.json')))
NP=dict(zip(L('names_src.json'),L('names_en.json')))
NUM=re.compile(r'\d+(?:\.\d+)?'); PF=re.compile(r'P[1-5](?![0-9])')
def name(n):
    pf=PF.findall(n); t=PF.sub('P@',n).replace('#','№'); nums=NUM.findall(t); p=NUM.sub('#',t); key=p.replace('№','#')
    if key not in NP: return None
    o=NP[key]
    if '№' in p: o=o.replace('##','№#')
    it=iter(pf); o=re.sub('P@',lambda m: next(it),o); it2=iter(nums); o=re.sub('#',lambda m: next(it2),o); return o.replace('№','#')
miss=set()
def tr(s):
    if not K.search(s): return s
    if s in EX: return EX[s]
    n=name(s)
    if n is not None: return n
    miss.add(s); return s
def walk(v):
    if isinstance(v,str): return tr(v)
    if isinstance(v,list): return [walk(x) for x in v]
    if isinstance(v,dict): return {tr(k) if isinstance(k,str) else k: walk(x) for k,x in v.items()}
    return v
if __name__=='__main__':
    D=json.load(open(W+'campus.json')); E=walk(D)
    json.dump(E,open(W+'campus_en.json','w'),ensure_ascii=False)
    print('missing',len(miss))
    for m in sorted(miss)[:60]: print(' ',m)
