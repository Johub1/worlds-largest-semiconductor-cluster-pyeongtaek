import json
import re,os
_V=os.path.join(os.path.dirname(os.path.abspath(__file__)),'vendor')
def _inline(h):
    # three.js r128 and OrbitControls (MIT licence) are inlined so the viewer works offline
    for pat,fn in ((r'<script src="[^"]*three\.min\.js"></script>','three.min.js'),(r'<script src="[^"]*OrbitControls\.js"></script>','OrbitControls.js')):
        js=open(os.path.join(_V,fn),encoding='utf-8').read().replace('</script','<\\/script')
        h=re.sub(pat,lambda m:'<script>'+js+'</script>',h,count=1)
    return h
D=json.load(open('campus_en.json'))
slim=dict(meta=D['meta'],fabs=D['fabs'],levels=D['levels'],types=D['types'],sources=D['sources'],phase=D['phase'],pipes=D['pipes'],dets=D['dets'],egress=D['egress'],cr_report=D['cr_report'],struct=D['struct'],safety=D['safety'],usys=D['usys'],ugroups=D['ugroups'],util=D['util'],
  elems=[{k:v for k,v in e.items() if not (k=='rot' and not v) and not (k=='opacity' and v==1.0) and not (k=='note' and not v) and not (k in ('fab','fl') and not v)} for e in D['elems']],
  equip=D['equip'],rails=D['rails'])
h=_inline(open('viewer_template_en.html',encoding='utf-8').read()).replace('/*__DATA__*/',json.dumps(slim,ensure_ascii=False,separators=(',',':')))
open('index_en.html','w',encoding='utf-8').write(h); print(len(h)//1024,'KB')
