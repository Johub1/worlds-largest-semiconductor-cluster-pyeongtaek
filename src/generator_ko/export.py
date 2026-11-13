# -*- coding: utf-8 -*-
"""Export campus.json to GLB / OBJ / STL / DXF(3D + 2D plan) / STEP / CSV / per-floor PNG plans."""
import json, math, os, csv
import numpy as np, trimesh, ezdxf

D = json.load(open("campus.json"))
OUT = "release"
for d in ("models", "drawings", "drawings/floor_plans", "drawings/utility", "data"): os.makedirs(f"{OUT}/{d}", exist_ok=True)
TYPES = D["types"]; LEVELS = D["levels"]

def hex2rgba(h, a=1.0):
    h = h.lstrip("#"); return [int(h[i:i + 2], 16) for i in (0, 2, 4)] + [int(255 * a)]
def box_mesh(b, rot=0):
    x0, y0, z0, x1, y1, z1 = b
    m = trimesh.creation.box(extents=[x1 - x0, y1 - y0, z1 - z0])
    T = trimesh.transformations.rotation_matrix(math.radians(rot), [0, 0, 1]) if rot else np.eye(4)
    T2 = np.eye(4); T2[:3, 3] = [(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2]
    m.apply_transform(T2 @ T); return m
ZUP_TO_YUP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]], float)
CX, CY = 0.0, 1500.0
def recentre(m): m.apply_translation([-CX, -CY, 0]); return m
def pbr(col, a=1.0, name=""):
    return trimesh.visual.TextureVisuals(material=trimesh.visual.material.PBRMaterial(baseColorFactor=hex2rgba(col, a), metallicFactor=0.1, roughnessFactor=0.8,
                                         alphaMode="BLEND" if a < 1 else "OPAQUE", name=name))
# ------------------------------------------------------------------ meshes
scene = trimesh.Scene(); all_ext = []
EXT_L = ("외피", "지붕", "부속동", "연결 브리지", "옥상 랙", "외장 그래픽")
# named nodes for buildings; interior zone/support elements merged per (fab, floor, layer) to keep node count sane
merged = {}
for e in D["elems"]:
    m = recentre(box_mesh(e["box"], e.get("rot", 0)))
    if e["layer"] in EXT_L or e["layer"] == "지반" or not e.get("fab"):
        m.visual = pbr(e["color"], e.get("opacity", 1.0), e["layer"])
        scene.add_geometry(m, node_name=e["id"], geom_name=e["id"])
        if e["layer"] in EXT_L: all_ext.append(m)
    else:
        merged.setdefault((e["fab"], e.get("fl", ""), e["layer"], e["color"], e.get("opacity", 1.0)), []).append(m)
for i, ((fab, fl, layer, col, op), ms) in enumerate(merged.items()):
    m = trimesh.util.concatenate(ms); m.visual = pbr(col, op, layer)
    nm = f"{fab}_{fl}_{layer}_{i}".replace(" ", "_"); scene.add_geometry(m, node_name=nm, geom_name=nm)
groups = {}
for q in D["equip"]:
    x, y, z, dx, dy, dz, ti, fab, fl = q
    groups.setdefault((fab, fl, TYPES[ti]["key"]), []).append(recentre(box_mesh([x, y, z, x + dx, y + dy, z + dz])))
for (fab, fl, key), ms in groups.items():
    m = trimesh.util.concatenate(ms); m.visual = pbr(next(t["color"] for t in TYPES if t["key"] == key), 1.0, "EQ_" + key)
    scene.add_geometry(m, node_name=f"EQ_{fab}_{fl}_{key}", geom_name=f"EQ_{fab}_{fl}_{key}")
rails = {}
for r in D["rails"]:
    x, y, z, dx, dy, dz, fab, fl = r
    rails.setdefault((fab, fl), []).append(recentre(box_mesh([x, y, z, x + dx, y + dy, z + dz])))
for (fab, fl), ms in rails.items():
    m = trimesh.util.concatenate(ms); m.visual = pbr("#f4f6f8", 1.0, "OHT_RAIL")
    scene.add_geometry(m, node_name=f"OHT_{fab}_{fl}", geom_name=f"OHT_{fab}_{fl}")
PCOL = ["#3fd17a", "#ff4d4d", "#ff9f2e"]; PNAME = ["EHS_GAS_SUPPLY", "EHS_PROCESS_EXHAUST", "EHS_TREATED_EXHAUST"]
for k in range(3):
    ms = [recentre(box_mesh([p[0], p[1], p[2], p[0] + p[3], p[1] + p[4], p[2] + p[5]])) for p in D["pipes"] if p[6] == k]
    m = trimesh.util.concatenate(ms); m.visual = pbr(PCOL[k], 1.0, PNAME[k]); scene.add_geometry(m, node_name=PNAME[k], geom_name=PNAME[k])
ms = [recentre(box_mesh([d[0] - .6, d[1] - .6, d[2] - .6, d[0] + .6, d[1] + .6, d[2] + .6])) for d in D["dets"]]
m = trimesh.util.concatenate(ms); m.visual = pbr("#ff3df0", 1.0, "EHS_GAS_DETECTOR_CONCEPT"); scene.add_geometry(m, node_name="EHS_GAS_DETECTOR_CONCEPT", geom_name="EHS_GAS_DETECTOR_CONCEPT")
SNAME = ["STRUCT_COLUMN_CONCEPT", "STRUCT_PLENUM_TRUSS_CONCEPT", "CSF_LATERAL_RACK_CONCEPT", "CLEANROOM_OVERHEAD_PIPE_DUCT_CONCEPT"]; SCOL = ["#8c949e", "#69727c", "#b7a36a", "#c9d3dc"]
for k in range(4):
    ms = [recentre(box_mesh([p[0], p[1], p[2], p[0] + p[3], p[1] + p[4], p[2] + p[5]])) for p in D["struct"] if p[6] == k]
    if ms: m = trimesh.util.concatenate(ms); m.visual = pbr(SCOL[k], 1.0, SNAME[k]); scene.add_geometry(m, node_name=SNAME[k], geom_name=SNAME[k])
FNAME = ["EHS_SAFETY_SHOWER_EYEWASH_CONCEPT", "EHS_EXTINGUISHER_HYDRANT_CABINET_CONCEPT", "EHS_EXIT_DOOR_CONCEPT"]; FCOL = ["#19c37d", "#e02424", "#00e676"]; FDIM = [(0.9, 0.9, 2.3), (0.8, 0.35, 1.3), (1.8, 0.25, 2.2)]
for k in range(3):
    d = FDIM[k]; ms = [recentre(box_mesh([p[0] - d[0] / 2, p[1] - d[1] / 2, p[2], p[0] + d[0] / 2, p[1] + d[1] / 2, p[2] + d[2]])) for p in D["safety"] if p[3] == k]
    if ms: m = trimesh.util.concatenate(ms); m.visual = pbr(FCOL[k], 1.0, FNAME[k]); scene.add_geometry(m, node_name=FNAME[k], geom_name=FNAME[k])
USYS = D["usys"]; UNAME = lambda i: "UTIL_" + USYS[i][0].replace(".", "_")
for i, sy in enumerate(USYS):
    ms = [recentre(box_mesh([p[0], p[1], p[2], p[0] + p[3], p[1] + p[4], p[2] + p[5]])) for p in D["util"] if p[6] == i]
    if not ms: continue
    m = trimesh.util.concatenate(ms); m.visual = pbr(sy[2], 1.0, UNAME(i)); scene.add_geometry(m, node_name=UNAME(i), geom_name=UNAME(i))
sc2 = scene.copy(); sc2.apply_transform(ZUP_TO_YUP)
open(OUT + "/models/pyeongtaek_p1-p4_full.glb", "wb").write(sc2.export(file_type="glb"))
scene.export(OUT + "/models/pyeongtaek_p1-p4_full.obj", include_normals=False)
trimesh.util.concatenate(all_ext).export(OUT + "/models/pyeongtaek_p1-p4_exterior.stl")
print("mesh ok: nodes", len(scene.geometry), "faces", sum(len(g.faces) for g in scene.geometry.values()))

# ------------------------------------------------------------------ DXF 3D
LAY = {"외피": "A-SHELL", "지붕": "A-ROOF", "옥상 랙": "M-ROOFRACK", "외장 그래픽": "A-GRAPHIC", "층 슬래브": "S-SLAB", "클린룸 구역": "A-CLEANROOM",
       "공정 구역": "A-PROCESS-AREA", "옐로 룸": "A-YELLOW-ROOM", "FFU 천장": "M-FFU-CEILING", "서브팹 구역": "A-SUBFAB", "플레넘 구역": "A-PLENUM", "코어": "A-CORE", "서포트 구역": "A-SUPPORT",
       "서포트 시설": "A-SUPPORT-ROOMS", "참조 설계(반입구)": "A-REFERENCE-MOVEIN-CONCEPT", "공조": "M-HVAC", "유틸리티 설비": "M-UTILITY-PLANT", "지도 표기 지점": "A-MAP-LABELLED-POINT", "충전·교체 지점": "M-FILL-EXCHANGE-POINT", "부속동": "A-AUX", "연결 브리지": "A-BRIDGE", "지반": "C-GROUND"}
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.M; doc.header["$INSUNITS"] = 6; msp = doc.modelspace()
for i, v in enumerate(LAY.values()): doc.layers.add(v, color=(i % 7) + 1)
def add_mesh(m, layer):
    if layer not in doc.layers: doc.layers.add(layer, color=(len(doc.layers) % 7) + 1)
    mesh = msp.add_mesh(dxfattribs={"layer": layer})
    with mesh.edit_data() as md:
        md.vertices = [tuple(v) for v in m.vertices]; md.faces = [tuple(f) for f in m.faces]
for e in D["elems"]:
    lay = LAY[e["layer"]] + (("-" + e["fl"]) if e.get("fl") and e["layer"] not in EXT_L else "")
    add_mesh(box_mesh(e["box"], e.get("rot", 0)), lay)
for (fab, fl, key), ms in groups.items():
    m = trimesh.util.concatenate(ms); m.apply_translation([CX, CY, 0]); add_mesh(m, f"EQ-{fl}-{key}")
for k in range(3):
    ms = [box_mesh([p[0], p[1], p[2], p[0] + p[3], p[1] + p[4], p[2] + p[5]]) for p in D["pipes"] if p[6] == k]
    add_mesh(trimesh.util.concatenate(ms), PNAME[k].replace("_", "-"))
for i, sy in enumerate(USYS):
    ms = [box_mesh([p[0], p[1], p[2], p[0] + p[3], p[1] + p[4], p[2] + p[5]]) for p in D["util"] if p[6] == i]
    if ms: add_mesh(trimesh.util.concatenate(ms), "U-" + sy[0].replace(".", "-") + "-CONCEPT")
doc.saveas(OUT + "/models/pyeongtaek_p1-p4_3d.dxf")

# ------------------------------------------------------------------ DXF 2D plan (true coordinates, layer per floor+type)
doc = ezdxf.new("R2010", setup=True); doc.units = ezdxf.units.M; msp = doc.modelspace()
doc.styles.add("KO", font="malgun.ttf")
def lay(n, c=7):
    if n not in doc.layers: doc.layers.add(n, color=c)
    return n
def rect(x0, y0, x1, y1, layer, **kw):
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs=dict(layer=layer, **kw))
def text(s, x, y, h, layer="TEXT"):
    msp.add_text(s, height=h, dxfattribs={"layer": lay(layer), "style": "KO"}).set_placement((x, y))
for f in D["fabs"]:
    rect(f["x0"], f["y0"], f["x1"], f["y1"], lay("OUTLINE"))
    text(f"{f['id']} FAB  본체 {f['Lmain']} m (단부 포함 {f['L']} m) x {f['W']} m  [위성영상 실측]", f["x0"], f["y1"] + 6, 8)
for e in D["elems"]:
    b = e["box"]
    if e["layer"] in ("부속동", "연결 브리지") and not e.get("rot"):
        rect(b[0], b[1], b[3], b[4], lay("AUX", 8)); text(e["name"], b[0] + 1, b[1] + 1, 3.5)
    if e["layer"] in ("클린룸 구역", "서브팹 구역", "플레넘 구역") and not e["id"].endswith("ffu"):
        rect(b[0], b[1], b[3], b[4], lay(f"{e['fl']}_ZONE", 3)); text(e["name"], b[0] + 2, b[4] - 6, 3.0, f"{e['fl']}_TEXT")
    if e["layer"] == "공정 구역" and "spine" not in e["id"]:
        text(e["name"], b[0] + 1, b[4] - 12, 2.5, f"{e['fl']}_TEXT")
    if e["layer"] == "서포트 시설":
        rect(b[0], b[1], b[3], b[4], lay(f"{e['fl']}_SUPPORT", 4))
for q in D["equip"]:
    x, y, z, dx, dy, dz, ti, fab, fl = q
    rect(x, y, x + dx, y + dy, lay(f"{fl}_{TYPES[ti]['key']}", (ti % 6) + 1))
for r in D["rails"]:
    x, y, z, dx, dy, dz, fab, fl = r
    a, b2 = ((x + dx / 2, y), (x + dx / 2, y + dy)) if dx < dy else ((x, y + dy / 2), (x + dx, y + dy / 2))
    msp.add_line(a, b2, dxfattribs={"layer": lay(f"{fl}_OHT", 9)})
for p in D["pipes"]:
    rect(p[0], p[1], p[0] + p[3], p[1] + p[4], lay(f"EHS_{PNAME[p[6]][4:]}", [3, 1, 30][p[6]]))
for d in D["dets"]:
    msp.add_circle((d[0], d[1]), 0.9, dxfattribs={"layer": lay(f"{d[5]}_EHS_GAS_DETECTOR", 6)})
for q in D["egress"]:
    msp.add_text(str(q[5]), height=1.6, dxfattribs={"layer": lay(f"{q[7]}_EHS_EGRESS_DIST_M", 2)}).set_placement((q[0] + 1, q[1] + 2))
for p in D["struct"]:
    if p[6] == 0: rect(p[0], p[1], p[0] + p[3], p[1] + p[4], lay(f"{p[8]}_STRUCT_COLUMN", 8))
    else: rect(p[0], p[1], p[0] + p[3], p[1] + p[4], lay(f"{p[8]}_" + SNAME[p[6]], 9))
for p in D["safety"]:
    msp.add_circle((p[0], p[1]), [0.8, 0.5, 0.9][p[3]], dxfattribs={"layer": lay(f"{p[5]}_" + FNAME[p[3]], [3, 1, 3][p[3]])})
for p in D["util"]:
    sy = USYS[p[6]]; a, b2 = ((p[0] + p[3] / 2, p[1]), (p[0] + p[3] / 2, p[1] + p[4])) if p[3] < p[4] else ((p[0], p[1] + p[4] / 2), (p[0] + p[3], p[1] + p[4] / 2))
    if max(p[3], p[4]) > 1.5: msp.add_line(a, b2, dxfattribs={"layer": lay("UTIL_" + sy[0] + "_CONCEPT", (p[6] % 6) + 1)})
    else: msp.add_circle((p[0] + p[3] / 2, p[1] + p[4] / 2), 0.6, dxfattribs={"layer": lay("UTIL_" + sy[0] + "_RISER", (p[6] % 6) + 1)})
for e in D["elems"]:
    if e["layer"] in ("유틸리티 설비", "충전·교체 지점"):
        b = e["box"]; rect(b[0], b[1], b[3], b[4], lay("UTIL_PLANT" if e["layer"] == "유틸리티 설비" else "UTIL_FILL_EXCHANGE_POINT", 2)); text(e["name"], b[0] + 0.5, b[4] + 0.8, 1.8, "UTIL_TEXT")
text("DISCLAIMER: Unofficial concept model built only from public sources. Interior layout is generic (not the actual facility layout). 비공식 개념 모델 · 공개 자료만 사용 · 내부 배치는 실제가 아님.", 760, 2330, 7)
lx, ly = 760, 2300
text("범례 / LEGEND — 설비 종류와 공급사 (공개자료 기반 · 개념 배치)", lx, ly, 9)
for i, t in enumerate(TYPES):
    y = ly - 22 - i * 20
    text(f"[{t['role']}] {t['key']}  {t['ko']} — {t['shape']}", lx, y + 1, 5)
    text("업계 대표 공급사(이 현장 납품 여부 미확인): " + t["vendors"] + ("   |   현장 관련 보도·공시: " + t["vendors_site"] if t["vendors_site"] else ""), lx, y - 6, 4)
yb = ly - 22 - len(TYPES) * 20 - 10
text("주의: 공개된 자료만으로 제작. 설비 배치는 일반적 300mm 팹 구조를 따른 개념도이며 실제 삼성전자 배치가 아님.", lx, yb, 7)
text("OHT: SEMES (현장 투어 보도·공식 영상에서 확인)", lx, yb - 14, 6)
text("층 레이어: 1F/5F=FSF, 2F/6F=CSF, 3F/7F=클린룸, 4F/8F=플레넘, RF=옥상. 원하는 층 레이어만 켜서 보세요.", lx, yb - 28, 6)
doc.saveas(OUT + "/drawings/layout_plan_2d.dxf")
print("dxf ok")

# ------------------------------------------------------------------ CSV / JSON
with open(OUT + "/data/elements.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["id", "name", "layer", "fab", "floor", "x0", "y0", "z0", "x1", "y1", "z1", "rot_deg", "grade", "sources", "note"])
    for e in D["elems"]: w.writerow([e["id"], e["name"], e["layer"], e.get("fab", ""), e.get("fl", ""), *e["box"], e.get("rot", 0), e["conf"], ";".join(e["src"]), e["note"]])
with open(OUT + "/data/equipment_concept.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["fab", "floor", "role", "type", "type_ko", "x0", "y0", "z0", "dx", "dy", "dz", "grade"])
    for q in D["equip"]:
        x, y, z, dx, dy, dz, ti, fab, fl = q; w.writerow([fab, fl, TYPES[ti]["role"], TYPES[ti]["key"], TYPES[ti]["ko"], x, y, z, dx, dy, dz, "D"])
with open(OUT + "/data/vendors.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["role", "type", "type_ko", "shape", "site_reported(현장 관련 보도·공시)", "industry_major_suppliers(업계 일반, 현장 납품 미확인)"])
    for t in TYPES: w.writerow([t["role"], t["key"], t["ko"], t["shape"], t["vendors_site"], t["vendors"]])
    w.writerow(["FAB", "OHT", "웨이퍼 이송(OHT)", "천장 레일 주행 대차", "SEMES (투어 보도·공식 영상)", "SEMES, Daifuku, Murata Machinery"])
with open(OUT + "/data/floors.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["floor", "z_bottom_m(assumed)", "z_top_m(assumed)", "role", "name", "contents"])
    for l in LEVELS: w.writerow(l)
with open(OUT + "/data/phases.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["fab", "half(W/E)", "floor", "phase", "basis"])
    for fab, d in D["phase"].items():
        for k, v in d.items(): w.writerow([fab, *k.split("|"), *v])
with open(OUT + "/data/ehs_pipes_concept.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["x0", "y0", "z0", "dx", "dy", "dz", "kind(0=gas supply,1=process exhaust,2=treated exhaust)", "fab", "cleanroom_floor"]); w.writerows(D["pipes"])
with open(OUT + "/data/ehs_gas_detectors_concept.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["x", "y", "z", "zone(0=FAB,1=CSF,2=FSF)", "fab", "floor"]); w.writerows(D["dets"])
with open(OUT + "/data/ehs_egress_travel_distance.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["x0", "y0", "z", "dx", "dy", "travel_distance_m(model assumption)", "fab", "floor"]); w.writerows(D["egress"])
with open(OUT + "/data/utility_segments_concept.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["system", "system_ko", "group", "x0", "y0", "z0", "dx", "dy", "dz", "fab_or_plant", "grade"])
    for p in D["util"]: w.writerow([USYS[p[6]][0], USYS[p[6]][1], USYS[p[6]][3], *p[:6], p[7], "D"])
with open(OUT + "/data/utility_systems.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["group", "title", "systems", "flow_order", "typical_values_from_literature", "public_facts_about_pyeongtaek", "limits", "source_keys", "source_urls"])
    for g in D["ugroups"]:
        w.writerow([g["key"], g["title"], "; ".join(sy[0] for sy in USYS if sy[3] == g["key"]), " | ".join(g["flow"]), " | ".join(g["values"]), " | ".join(g["site"]), g["limit"], ";".join(g["src"]), " ".join(D["sources"][k][1] for k in g["src"])])
with open(OUT + "/data/structure_concept.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["x0", "y0", "z0", "dx", "dy", "dz", "kind(0=column,1=plenum truss,2=CSF lateral rack,3=cleanroom overhead pipe/duct bundle)", "fab", "floor"]); w.writerows(D["struct"])
with open(OUT + "/data/ehs_emergency_equipment_concept.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f); w.writerow(["x", "y", "z", "kind(0=safety shower/eyewash,1=extinguisher/hydrant cabinet,2=exit door)", "fab", "floor"]); w.writerows(D["safety"])
json.dump(D, open(OUT + "/data/campus.json", "w"), ensure_ascii=False)

# ------------------------------------------------------------------ per-floor PNG plans
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib import font_manager
fp = None
for p in font_manager.findSystemFonts():
    if "NotoSansCJK" in p and "Regular" in p: fp = p; break
if fp: font_manager.fontManager.addfont(fp); plt.rcParams["font.family"] = font_manager.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False
for f in D["fabs"]:
    for fl, z0, z1, role, nm, what in LEVELS:
        fig, ax = plt.subplots(figsize=(22, 9.5), dpi=110); fig.patch.set_facecolor("#0e1620"); ax.set_facecolor("#152131")
        ax.add_patch(Rectangle((f["x0"], f["y0"]), f["x1"] - f["x0"], f["y1"] - f["y0"], fill=False, ec="#e7edf4", lw=1.6))
        for e in D["elems"]:
            if e.get("fab") != f["id"] or e.get("fl") != fl: continue
            b = e["box"]
            if e["layer"] in ("클린룸 구역", "서브팹 구역", "플레넘 구역", "서포트 구역", "공정 구역", "코어", "서포트 시설", "공조", "지붕") and not e["id"].endswith("ffu"):
                a = {"공정 구역": 0.25, "서포트 구역": 0.35, "공조": 0.3, "플레넘 구역": 0.25}.get(e["layer"], 0.9)
                ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fc=e["color"], ec="#0e1620", lw=0.3, alpha=a, zorder=1 if e["layer"] != "서포트 시설" else 3))
                if e["layer"] == "공정 구역" and "spine" not in e["id"]:
                    ax.text((b[0] + b[3]) / 2, b[4] + 2.5, e["name"].replace("(개념)", "").replace(" 구역", ""), color="#e7edf4", fontsize=6.5, ha="center", va="bottom", rotation=30)
                if e["layer"] == "클린룸 구역":
                    ph = D["phase"].get(f["id"], {}).get(("W" if e["id"].endswith("-W") else "E") + "|" + fl)
                    ax.text((b[0] + b[3]) / 2, b[1] - 3, ("서편" if e["id"].endswith("-W") else "동편") + (f" · {ph[0]}" if ph else ""), color="#f2cc3a", fontsize=11, ha="center", va="top", weight="bold")
                if e["id"].endswith("smock") or e["id"] == "P1-3F-window" or e["id"].endswith("movein"):
                    ax.text((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, ("장비 반입 홀" if e["id"].endswith("movein") else e["name"].split(fl + " ")[-1].replace("(추정)", "")), color="#0e1620", fontsize=6, ha="center", va="center", zorder=5)
        used = {}
        for q in D["equip"]:
            x, y, z, dx, dy, dz, ti, fab, l = q
            if fab != f["id"] or l != fl: continue
            ax.add_patch(Rectangle((x, y), dx, dy, fc=TYPES[ti]["color"], ec="none", zorder=4)); used[ti] = used.get(ti, 0) + 1
        for p in D["struct"]:
            if p[7] == f["id"] and p[8] == fl: ax.add_patch(Rectangle((p[0], p[1]), p[3], p[4], fc=SCOL[p[6]], ec="none", alpha=0.9 if p[6] == 0 else 0.25, zorder=3))
        sfx = [[], [], []]; sfy = [[], [], []]
        for p in D["safety"]:
            if p[4] == f["id"] and p[5] == fl: sfx[p[3]].append(p[0]); sfy[p[3]].append(p[1])
        for k in range(3):
            if sfx[k]: ax.scatter(sfx[k], sfy[k], s=[14, 9, 16][k], c=FCOL[k], marker=["P", "s", "^"][k], zorder=7, linewidths=0, label=["비상 샤워·세안(개념)", "소화기·소화전함(개념)", "비상구(개념)"][k])
        if any(sfx): ax.legend(loc="upper right", fontsize=7, frameon=False, labelcolor="#e7edf4")
        for r in D["rails"]:
            x, y, z, dx, dy, dz, fab, l = r
            if fab == f["id"] and l == fl: ax.add_patch(Rectangle((x, y), dx, dy, fc="#ffffff", ec="none", alpha=0.7, zorder=5))
        ax.set_xlim(f["x0"] - 12, f["x1"] + 12); ax.set_ylim(f["y0"] - 22, f["y1"] + 26); ax.set_aspect("equal")
        ax.tick_params(colors="#93a4b8", labelsize=7); [s.set_color("#2a3b50") for s in ax.spines.values()]
        ax.set_xlabel("X 동쪽 (m)", color="#93a4b8", fontsize=8); ax.set_ylabel("Y 북쪽 (m)", color="#93a4b8", fontsize=8)
        ax.set_title(f"{f['id']} {fl} · {nm}    [층 구성: 추정 / 배치: 개념도 — 실제 삼성전자 배치 아님 · 공개 자료만 사용]", color="#e7edf4", fontsize=12, loc="left")
        hs = [Rectangle((0, 0), 1, 1, fc=TYPES[ti]["color"]) for ti in used]
        ls = [f"{TYPES[ti]['ko']} — {TYPES[ti]['vendors']}" + (f"  ★현장 보도·공시: {TYPES[ti]['vendors_site']}" if TYPES[ti]["vendors_site"] else "") for ti in used]
        if role == "FAB": hs.append(Rectangle((0, 0), 1, 1, fc="#ffffff")); ls.append("OHT 레일 — ★현장 확인: SEMES (그 외 업계: Daifuku, Murata)")
        if hs:
            lg = fig.legend(hs, ls, loc="lower center", ncol=2, fontsize=7.5, frameon=False, labelcolor="#e7edf4", title="설비와 공급사 (★ 외에는 업계 대표 공급사, 이 현장 납품 여부 미확인)")
            lg.get_title().set_color("#93a4b8"); lg.get_title().set_fontsize(8)
        fig.text(0.01, 0.005, what, color="#93a4b8", fontsize=7.5)
        fig.subplots_adjust(left=0.05, right=0.99, top=0.94, bottom=0.24 if hs else 0.08)
        fig.savefig(f"{OUT}/drawings/floor_plans/{f['id']}_{fl}.png", facecolor=fig.get_facecolor()); plt.close(fig)
os.makedirs(OUT + "/drawings/ehs", exist_ok=True)
from matplotlib.colors import BoundaryNorm, ListedColormap
cmap = ListedColormap(["#2e9e5b", "#8fc93a", "#e8d21a", "#f0a020", "#e8632a", "#c8202a"]); norm = BoundaryNorm([0, 30, 50, 61, 75, 100, 400], 6)
summary = []
for f in D["fabs"]:
    for fl in ("3F", "7F"):
        tiles = [q for q in D["egress"] if q[6] == f["id"] and q[7] == fl]; d = [q[5] for q in tiles]
        pc = lambda t: round(100 * sum(v <= t for v in d) / len(d))
        summary.append([f["id"], fl, max(d), pc(61), pc(75), pc(100)])
        if fl != "3F": continue
        fig, ax = plt.subplots(figsize=(20, 7.6), dpi=110); fig.patch.set_facecolor("#0e1620"); ax.set_facecolor("#152131")
        ax.add_patch(Rectangle((f["x0"], f["y0"]), f["x1"] - f["x0"], f["y1"] - f["y0"], fill=False, ec="#e7edf4", lw=1.6))
        for q in tiles: ax.add_patch(Rectangle((q[0], q[1]), q[3], q[4], fc=cmap(norm(q[5])), ec="#0e1620", lw=0.2))
        for e in D["elems"]:
            if e.get("fab") == f["id"] and e.get("fl") == fl and "stair" in e["id"]:
                b = e["box"]; ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fc="#ffffff", ec="#0e1620", zorder=5))
        ax.add_patch(Rectangle((f["core"][0], f["cr"][2]), f["core"][1] - f["core"][0], f["cr"][3] - f["cr"][2], fc="#ffffff", alpha=0.85, zorder=5))
        ax.set_xlim(f["x0"] - 12, f["x1"] + 12); ax.set_ylim(f["y0"] - 10, f["y1"] + 10); ax.set_aspect("equal")
        ax.tick_params(colors="#93a4b8", labelsize=7); [s.set_color("#2a3b50") for s in ax.spines.values()]
        ax.set_title(f"{f['id']} {fl} 피난 보행거리 스크리닝 — 모델에 가정한 계단·중앙 코어(흰색) 기준. 실제 건물 평가 아님", color="#e7edf4", fontsize=12, loc="left")
        hs = [Rectangle((0, 0), 1, 1, fc=c) for c in cmap.colors]
        lg = fig.legend(hs, ["30 m 이하 (건축법 시행령 제34조 기본)", "50 m 이하 (내화구조)", "61 m 이하 (IBC H-5, 200 ft)", "75 m 이하 (자동화 생산시설 공장)", "100 m 이하 (무인화 공장)", "100 m 초과"], loc="lower center", ncol=3, fontsize=8, frameon=False, labelcolor="#e7edf4", bbox_to_anchor=(0.5, 0.01))
        fig.text(0.05, 0.125, f"최대 {max(d)} m · 61 m 이내 {pc(61)}% · 75 m 이내 {pc(75)}% · 100 m 이내 {pc(100)}%  |  계단 위치·간격(약 70 m)은 가정값. 75 m 초과 구역은 모델의 계단 가정이 실제보다 부족함을 뜻함.", color="#93a4b8", fontsize=8)
        fig.subplots_adjust(left=0.05, right=0.99, top=0.93, bottom=0.2); fig.savefig(f"{OUT}/drawings/ehs/{f['id']}_{fl}_egress.png", facecolor=fig.get_facecolor()); plt.close(fig)
with open(OUT + "/data/ehs_egress_summary.csv", "w", newline="", encoding="utf-8-sig") as fcsv:
    w = csv.writer(fcsv); w.writerow(["fab", "floor", "max_m", "pct_within_61m", "pct_within_75m", "pct_within_100m"]); w.writerows(summary)
print("png ok", summary[0])

# ------------------------------------------------------------------ utility plan + block-flow PNGs
GROUPS = [g["key"] for g in D["ugroups"]]
def uplan(keys, fname, title, xlim=(-720, 780), ylim=(610, 2330), size=(15, 16.5)):
    fig, ax = plt.subplots(figsize=size, dpi=110); fig.patch.set_facecolor("#0e1620"); ax.set_facecolor("#152131")
    for e in D["elems"]:
        b = e["box"]
        if e["layer"] in ("부속동", "연결 브리지") and not e.get("rot"): ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fc="#22303f", ec="#3a4d63", lw=0.5))
        if e["layer"] in ("유틸리티 설비", "충전·교체 지점"):
            ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fc=e["color"], ec="#0e1620", lw=0.3, alpha=0.9, zorder=4))
    for f in D["fabs"]:
        ax.add_patch(Rectangle((f["x0"], f["y0"]), f["x1"] - f["x0"], f["y1"] - f["y0"], fc="#1b2838", ec="#e7edf4", lw=1.2))
        ax.text(f["x0"] + 8, f["y1"] - 8, f["id"], color="#e7edf4", fontsize=13, va="top", weight="bold", zorder=6)
    used = []
    for p in D["util"]:
        sy = USYS[p[6]]
        if sy[3] not in keys: continue
        ax.add_patch(Rectangle((p[0], p[1]), max(p[3], 1.2), max(p[4], 1.2), fc=sy[2], ec="none", zorder=5))
        if p[6] not in used: used.append(p[6])
    for e in D["elems"]:
        if e["layer"] == "충전·교체 지점" or e["id"] in ("GAS-YARD", "SS-GIS", "UT-34-CT", "UT-12-UPW", "UT-34-UPW", "UT-12-CH1", "UT-34-CH1", "S1-WW-AA", "S2-WW-AA"):
            b = e["box"]; ax.text((b[0] + b[3]) / 2, b[4] + 4, e["name"].split(" — ")[0].replace("(개념)", "").replace("(개념, 위치 임의)", "")[:26], color="#f2cc3a", fontsize=6, ha="center", zorder=7)
    ax.set_xlim(*xlim); ax.set_ylim(*ylim); ax.set_aspect("equal"); ax.tick_params(colors="#93a4b8", labelsize=7); [s_.set_color("#2a3b50") for s_ in ax.spines.values()]
    ax.set_title(title + "\n[일반 참조 설계(등급 D) — 실제 평택캠퍼스의 배관·덕트·전력 경로 아님 · 공개 자료만 사용]", color="#e7edf4", fontsize=12, loc="left")
    used.sort(); lg = fig.legend([Rectangle((0, 0), 1, 1, fc=USYS[i][2]) for i in used], [f"{USYS[i][0]} — {USYS[i][1]}" for i in used], loc="lower center", ncol=2, fontsize=7.5, frameon=False, labelcolor="#e7edf4")
    fig.subplots_adjust(left=0.05, right=0.99, top=0.95, bottom=0.05 + 0.011 * (len(used) + 1)); fig.savefig(f"{OUT}/drawings/utility/{fname}", facecolor=fig.get_facecolor()); plt.close(fig)
uplan(GROUPS, "campus_utility_all.png", "평택캠퍼스 P1–P4 유틸리티 계통 개념 평면(전체)")
for i, g in enumerate(D["ugroups"]):
    uplan([g["key"]], f"campus_utility_{i+1:02d}.png", "유틸리티 계통 개념 평면 — " + g["title"])
# block-flow sheet (text): flow order / literature values / public site facts per group
import textwrap
fig = plt.figure(figsize=(16, 40), dpi=100); fig.patch.set_facecolor("#0e1620"); y = 0.99
fig.text(0.03, y, "유틸리티 계통 흐름 요약 — 공급 → 사용 → 환수·처리 (일반 참조 설계) / 평택캠퍼스 공개 사실", color="#e7edf4", fontsize=15, weight="bold"); y -= 0.0117
for g in D["ugroups"]:
    fig.text(0.03, y, g["title"], color="#f2cc3a", fontsize=12, weight="bold"); y -= 0.0075
    for head, items, col in (("흐름", g["flow"], "#e7edf4"), ("문헌 수치", g["values"], "#b9c7d6"), ("평택 공개 사실", g["site"], "#9fe0b0")):
        for t in items:
            for k, ln in enumerate(textwrap.wrap(t, 96)):
                fig.text(0.04, y, (f"[{head}] " if k == 0 else "        ") + ln, color=col, fontsize=8.6); y -= 0.0057
    for ln in textwrap.wrap("한계: " + g["limit"], 100): fig.text(0.04, y, ln, color="#93a4b8", fontsize=8.2); y -= 0.0056
    fig.text(0.04, y, "출처: " + ", ".join(D["sources"][k][0].split(":")[0][:34] for k in g["src"])[:150], color="#6f8197", fontsize=7.4); y -= 0.0091
fig.savefig(f"{OUT}/drawings/utility/utility_flow_summary.png", facecolor=fig.get_facecolor()); plt.close(fig)
print("utility png ok, y left", round(y, 3))

# ------------------------------------------------------------------ STEP (buildings, slabs, zones, support rooms; equipment excluded for size)
try:
    import cadquery as cq
    asm = cq.Assembly(name="Pyeongtaek_P1_P4"); n = 0
    for e in D["elems"]:
        if e["layer"] in ("FFU 천장", "공정 구역", "공조", "옐로 룸"): continue
        x0, y0, z0, x1, y1, z1 = e["box"]
        s = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0)
        loc = cq.Location(cq.Vector((x0 + x1) / 2 - CX, (y0 + y1) / 2 - CY, (z0 + z1) / 2), cq.Vector(0, 0, 1), e.get("rot", 0))
        c = hex2rgba(e["color"])
        asm.add(s, name=e["id"].replace(" ", "_"), loc=loc, color=cq.Color(c[0] / 255, c[1] / 255, c[2] / 255, e.get("opacity", 1.0))); n += 1
    asm.save(OUT + "/models/pyeongtaek_p1-p4_buildings.step"); print("step ok", n)
except Exception as ex:
    print("STEP failed:", ex)
