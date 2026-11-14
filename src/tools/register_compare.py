# Compares building-permit rows (lot Godeok-dong 1695, main permit) with model boxes. Candidates only; no geometry is changed.
import json,csv,collections,sys
W='/home/claude/work/'
SRC='/mnt/user-data/uploads/outputs/'
J=json.load(open(SRC+'SP_HUB_1695_층별개요_공식다운로드_2026-11-14.json',encoding='utf-8-sig'))['Data']
R=list(csv.DictReader(open(SRC+'SP_HUB_1695_E063_PK결합_28동_2026-11-14.csv',encoding='utf-8-sig')))
D=json.load(open(W+'campus.json')); E={e['id']:e for e in D['elems']}
F={f['id']:f for f in D['fabs']}
def area(i):
    if i in F: return F[i]['L']*F[i]['W']
    b=E[i]['box']; return (b[3]-b[0])*(b[4]-b[1])
fl=collections.defaultdict(lambda: collections.defaultdict(float))
for r in J:
    if r['ACPMSLG_SN']=='1099100090586': fl[r['ACPMSLG_DGCB_OUN_SN']][(r['FLR_SE_CD_NM'],r['FLR_NO'])]+=float(r['FLR_AREA'] or 0)
# candidate model boxes per register building name (sets are summed)
C={'FAB동':[['P1'],['P2']],'FAB동-2':[['P2'],['P1']],'FAB동-3':[['P3'],['P4']],'FAB동-4':[['P4'],['P3']],
 '복합동':[['UT-34','UT-34E']], 'EUV동':[['V2']],
 'UT동':[['UT-12E'],['UT-12'],['CUB-N']], 'UT동-2':[['UT-12E'],['UT-12'],['CUB-N']],
 '그린동-3':[['S2'],['S1']], '그린동-4':[['S2'],['S1']], '그린동':[['M5'],['M3']], '그린동-2':[['M5'],['M3']],
 'GCS동':[['E1'],['M1','M2']],
 '사무동':[['GATE-W']], '사무동-2':[['WA']], '사무동-3':[['W1'],['WD']],
 '기술동-2':[['OFF-2'],['OFF-T']], '기술동 주차타워':[['OFF-2']], '기술동':[['OFF-T']],
 '154kV동':[['SM2'],['SM1']], '154kV동-2':[['M4']], '154kV동-3':[['M4']], '154kV동-4':[['M3'],['M5']],
 '일반창고1':[['OFF-3']], '창고동':[['OFF-3']], 'CT동':[['CT-1','CT-2','CT-3','CT-4']], 'CT동-2':[['CT-1','CT-2','CT-3','CT-4']], '정수장':[]}
out=[]
for r in R:
    n=r['공식층별_건물명']; ba=float(r['건축면적_㎡']); f=fl[r['관리동별개요PK']]
    ag=sorted(k[1] for k in f if k[0]=='지상'); ug=sorted(k[1] for k in f if k[0]=='지하')
    mx=max(f.items(), key=lambda kv: kv[1])
    ug_area=sum(v for k,v in f.items() if k[0]=='지하')
    cands=C.get(n,[])
    if not cands:
        out.append(dict(register_name=n,building_area_m2=ba,total_floor_area_m2=float(r['연면적_㎡']),above_ground_floor_numbers=f"{ag[0]}-{ag[-1]}" if ag else '',basement_floor_numbers=','.join(map(str,ug)),largest_floor=f"{mx[0][0]}{mx[0][1]}",largest_floor_area_m2=round(mx[1],2),basement_area_m2=round(ug_area,2),model_ids='',model_plan_area_m2='',diff_pct='',model_name_ko='',model_grade='',status='no candidate box'))
    for c in cands:
        a=sum(area(i) for i in c); d=(a-ba)/ba*100
        ref=ba
        st='candidate (area within 5%)' if abs(d)<=5 else ('candidate (area within 15%)' if abs(d)<=15 else 'area does not match')
        if n in('CT동','CT동-2'):
            d2=(a-ug_area)/ug_area*100; st=f'compared with basement area instead: {d2:+.1f}% — relation unconfirmed'
        out.append(dict(register_name=n,building_area_m2=ba,total_floor_area_m2=float(r['연면적_㎡']),above_ground_floor_numbers=f"{ag[0]}-{ag[-1]}" if ag else '',basement_floor_numbers=','.join(map(str,ug)),largest_floor=f"{mx[0][0]}{mx[0][1]}",largest_floor_area_m2=round(mx[1],2),basement_area_m2=round(ug_area,2),
            model_ids='+'.join(c),model_plan_area_m2=round(a),diff_pct=round(d,1),model_name_ko=' / '.join((E[i]['name'] if i in E else i+' FAB') for i in c),model_grade='/'.join((E[i]['conf'] if i in E else 'B') for i in c),status=st))
keys=list(out[0].keys())
with open(W+'regcmp/register_vs_model.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.DictWriter(fh,fieldnames=keys); w.writeheader(); w.writerows(out)
for o in out: print(o['register_name'],'|',o['building_area_m2'],'|',o['above_ground_floor_numbers'],'B'+o['basement_floor_numbers'],'|',o['largest_floor'],o['largest_floor_area_m2'],'|',o['model_ids'],o['model_plan_area_m2'],o['diff_pct'],'|',o['status'])

# ---- English and Korean deliverables
EN={'FAB동':'FAB building','FAB동-2':'FAB building-2','FAB동-3':'FAB building-3','FAB동-4':'FAB building-4','복합동':'Complex building','EUV동':'EUV building','UT동':'UT building','UT동-2':'UT building-2','CT동':'CT building','CT동-2':'CT building-2','그린동':'Green building','그린동-2':'Green building-2','그린동-3':'Green building-3','그린동-4':'Green building-4','GCS동':'GCS building','정수장':'Water treatment plant','사무동':'Office building','사무동-2':'Office building-2','사무동-3':'Office building-3','기술동':'Technology building','기술동-2':'Technology building-2','기술동 주차타워':'Technology building parking tower','154kV동':'154 kV building','154kV동-2':'154 kV building-2','154kV동-3':'154 kV building-3','154kV동-4':'154 kV building-4','일반창고1':'General warehouse 1','창고동':'Warehouse building'}
FLK={'지상':'above ground ','지하':'basement '}
pk={r['공식층별_건물명']:r['관리동별개요PK'][-7:] for r in R}
KO_ST={'candidate (area within 5%)':'후보(면적 5% 이내)','candidate (area within 15%)':'후보(면적 15% 이내)','area does not match':'면적 불일치','no candidate box':'후보 상자 없음'}
def write(path,lang):
    rows=[]
    for o in out:
        n=o['register_name']; d=dict(o)
        d['building_key_suffix']=pk[n]
        if lang=='en':
            d['register_name']=EN[n]; d.pop('model_name_ko')
            lf=d['largest_floor']; d['largest_floor']=FLK.get(lf[:2],'')+lf[2:]
        else:
            st=d['status']; d['status']=KO_ST.get(st, st.replace('compared with basement area instead:','지하층 면적과 비교:').replace('— relation unconfirmed','— 관계 미확인'))
        rows.append(d)
    ks=['register_name','building_key_suffix']+[k for k in rows[0] if k not in('register_name','building_key_suffix')]
    with open(path,'w',newline='',encoding='utf-8-sig') as fh:
        w=csv.DictWriter(fh,fieldnames=ks); w.writeheader(); w.writerows(rows)
write(W+'regcmp/register_vs_model_en.csv','en'); write(W+'regcmp/register_vs_model_ko.csv','ko')
# per-floor table (all 28 buildings)
with open(W+'regcmp/permit_floor_areas_en.csv','w',newline='',encoding='utf-8-sig') as fh:
    w=csv.writer(fh); w.writerow(['register_name','building_key_suffix','floor_class','floor_number','floor_area_m2_summed_over_rows','rows'])
    cnt=collections.Counter((r['ACPMSLG_DGCB_OUN_SN'],r['FLR_SE_CD_NM'],r['FLR_NO']) for r in J)
    for r in R:
        f=fl[r['관리동별개요PK']]
        for (cls,no),v in sorted(f.items(), key=lambda kv:({'지하':0,'지상':1}.get(kv[0][0],2),kv[0][1])):
            w.writerow([EN[r['공식층별_건물명']],r['관리동별개요PK'][-7:],{'지상':'above ground','지하':'basement','옥탑':'rooftop structure'}.get(cls,cls),no,round(v,2),cnt[(r['관리동별개요PK'],cls,no)]])
print('written', len(out))
