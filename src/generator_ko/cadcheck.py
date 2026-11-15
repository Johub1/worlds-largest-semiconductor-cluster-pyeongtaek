import time,sys
t=time.time()
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID, TopAbs_FACE
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepCheck import BRepCheck_Analyzer
r=STEPControl_Reader(); st=r.ReadFile('release/models/pyeongtaek_p1-p4_buildings.step')
print('STEP read status ok:',st==IFSelect_RetDone); r.TransferRoots(); s=r.OneShape()
n=0;bad=0;ex=TopExp_Explorer(s,TopAbs_SOLID)
while ex.More():
    n+=1
    if n<=400 and not BRepCheck_Analyzer(ex.Current()).IsValid(): bad+=1
    ex.Next()
nf=0;ex=TopExp_Explorer(s,TopAbs_FACE)
while ex.More(): nf+=1; ex.Next()
b=Bnd_Box(); BRepBndLib.Add_s(s,b); print('solids',n,'faces',nf,'invalid among first 400:',bad,'bbox',[round(v,1) for v in b.Get()],'sec',round(time.time()-t))
import ezdxf
for f in ['release/drawings/layout_plan_2d.dxf','release/models/pyeongtaek_p1-p4_3d.dxf']:
    t=time.time(); d=ezdxf.readfile(f); a=d.audit(); ms=d.modelspace()
    from collections import Counter
    c=Counter(e.dxftype() for e in ms)
    print(f.split('/')[-1],'ver',d.dxfversion,'layers',len(d.layers),'entities',len(ms),dict(c.most_common(5)),'audit errors',len(a.errors),'fixes',len(a.fixes),'units',d.header.get('$INSUNITS'),'sec',round(time.time()-t))
