import re
# -*- coding: utf-8 -*-
"""
Samsung Pyeongtaek Campus P1~P4 — open massing + floor-by-floor concept-interior model generator (v4).
Built ONLY from publicly available material (press figures, regulatory-filing news, official newsroom,
public satellite imagery, OpenStreetMap, official/real-estate YouTube footage). See SOURCES.md.

Coordinates: X = east, Y = north, Z = up, metres. Origin: WGS84 37.0200 N, 127.0600 E.
Grades: A = official/press figure, B = measured on public satellite imagery,
        C = estimate/assumption, D = generic concept (NOT site-specific).
"""
import json

ELEMS, EQUIP, RAILS = [], [], []
STRUCT, SAFETY = [], []   # interior detail (v6): [x,y,z,dx,dy,dz,kind,fab,fl] kind 0 column / 1 truss / 2 CSF lateral rack / 3 cleanroom overhead pipe-duct bundle ; [x,y,z,kind,fab,fl] kind 0 shower·eyewash / 1 extinguisher·hydrant cabinet / 2 exit door
PIPES, DETS, EGRESS = [], [], []   # EHS concept layers
SUP = 25.0   # support-strip width (m): calibrated so cleanroom areas match the brokerage-report figures

def add(id, name, layer, box, color, conf, src, note="", rot=0, opacity=1.0, fab="", fl=""):
    x0, y0, z0, x1, y1, z1 = box
    assert x1 > x0 and y1 > y0 and z1 > z0, (id, box)
    ELEMS.append(dict(id=id, name=name, layer=layer, box=[round(v, 2) for v in box], color=color,
                      conf=conf, src=src, note=note, rot=rot, opacity=opacity, fab=fab, fl=fl))

def eq(x, y, z, dx, dy, dz, key, fab, fl):
    EQUIP.append([x, y, z, dx, dy, dz, TI[key], fab, fl])

# ---------------------------------------------------------------- equipment catalogue (envelopes = grade D)
# role: FAB / CSF / FSF / PLN / ROOF ; size = (length along bay, depth, height) m
TYPES = [
 dict(key="PHOTO", role="FAB", ko="포토(트랙+스캐너)", color="#e8c21a", size=(11.0, 4.5, 3.2),
      shape="트랙(도포·현상)과 스캐너를 나란히 붙인 2동체 + 전면 EFEM",
      vendors_site="ASML (P3에 EUV 장비 반입 보도)", vendors="스캐너: ASML, Nikon, Canon / 트랙: TEL, SEMES"),
 dict(key="ETCH", role="FAB", ko="식각", color="#d9534f", size=(6.0, 4.2, 2.8), shape="전면 EFEM + 이송 모듈 + 공정 챔버 묶음",
      vendors_site="", vendors="Lam Research, TEL, Applied Materials, SEMES"),
 dict(key="CVD", role="FAB", ko="증착(CVD/ALD/PVD)", color="#4f8fd9", size=(6.5, 4.2, 3.0), shape="전면 EFEM + 클러스터 본체",
      vendors_site="Applied Materials (P1 투어 보도)", vendors="Applied Materials, Lam Research, TEL, 원익IPS, 주성엔지니어링, 유진테크, ASM"),
 dict(key="DIFF", role="FAB", ko="확산/열처리(종형 퍼니스)", color="#e08a3c", size=(7.0, 3.5, 3.6), shape="전면 로더 + 키 큰 종형로 본체",
      vendors_site="", vendors="TEL, Kokusai Electric, 원익IPS, 유진테크"),
 dict(key="CMP", role="FAB", ko="CMP(평탄화)", color="#7a5cc9", size=(5.5, 4.0, 2.6), shape="전면 EFEM + 연마·세정 본체",
      vendors_site="", vendors="Applied Materials, Ebara, 케이씨텍"),
 dict(key="WET", role="FAB", ko="세정/습식", color="#34b3a0", size=(9.0, 3.5, 2.6), shape="전면 EFEM + 긴 세정 챔버 열",
      vendors_site="", vendors="SEMES, SCREEN, TEL, 케이씨텍"),
 dict(key="IMP", role="FAB", ko="이온주입", color="#a23b72", size=(8.0, 4.5, 2.8), shape="전면 EFEM + 빔라인 본체",
      vendors_site="", vendors="Applied Materials(Varian), Axcelis"),
 dict(key="METRO", role="FAB", ko="계측/검사", color="#8fbf4f", size=(3.5, 2.8, 2.4), shape="전면 EFEM + 소형 본체",
      vendors_site="KLA (P1 투어 보도)", vendors="KLA, Hitachi High-Tech, Applied Materials, Onto Innovation"),
 dict(key="STK", role="FAB", ko="스토커(FOUP 보관)", color="#c9ced6", size=(4.0, 2.5, 5.5), shape="천장 가까이 올라가는 수직 보관함",
      vendors_site="", vendors="SEMES, Daifuku, Murata Machinery"),
 dict(key="EUV", role="FAB", ko="EUV 노광기", color="#ffe45c", size=(14.0, 4.5, 4.2), shape="스캐너 본체 + 광원(소스) 용기. 약 180 t·1 MW 이상(공개 수치), 외형 치수는 근사",
      vendors_site="ASML (P3 EUV 장비 반입 보도)", vendors="ASML (전 세계 유일 공급사)"),
 # --- CSF (clean sub-fab, directly under the cleanroom)
 dict(key="RFG", role="CSF", ko="RF 제너레이터·파워 랙", color="#8d7fb8", size=(6.0, 1.2, 2.2), shape="장비 바로 아래 줄지어 선 전원 랙",
      vendors_site="", vendors="MKS, Advanced Energy, 뉴파워프라즈마"),
 dict(key="VMB", role="CSF", ko="가스 박스·VMB(밸브 매니폴드)", color="#5aa9a3", size=(2.0, 1.2, 2.3), shape="가스 분배 캐비닛",
      vendors_site="한양이엔지 (공시: P4 1단계 일반배관 4공구 최종 약 1,513억 원, P5 일반배관 1공구 약 1,481억 원 · 보도: P4 페이즈3 훅업·CCSS 설치)", vendors="한양이엔지, 원익홀딩스, 케이씨"),
 dict(key="EUVAUX", role="CSF", ko="EUV 구동 레이저·보조 캐비닛", color="#b59a2e", size=(12.0, 3.0, 2.6), shape="EUV 장비 아래층에 놓이는 레이저·전원·냉각 캐비닛 열",
      vendors_site="", vendors="ASML(Cymer), TRUMPF(구동 레이저)"),
 # --- FSF (facility sub-fab)
 dict(key="PUMP", role="FSF", ko="드라이 펌프 스키드", color="#6f7f8f", size=(4.0, 1.2, 1.8), shape="2~3단 적층 진공펌프 랙",
      vendors_site="", vendors="Edwards, Ebara, 엘오티베큠"),
 dict(key="SCR", role="FSF", ko="스크러버(POU 배기 처리)", color="#b06a4a", size=(2.2, 2.0, 3.2), shape="원통·박스형 가스 처리기",
      vendors_site="", vendors="GST(글로벌스탠다드테크놀로지), 유니셈, Edwards"),
 dict(key="CHL", role="FSF", ko="칠러·열교환기", color="#4a86b0", size=(2.5, 1.5, 2.2), shape="박스형 냉각 유닛",
      vendors_site="", vendors="유니셈, GST, 에프에스티(FST)"),
 dict(key="CDS", role="FSF", ko="케미컬 공급(CCSS/CDS)·슬러리", color="#3f8f5f", size=(5.0, 2.5, 3.0), shape="탱크·펌프 캐비닛",
      vendors_site="에스티아이 (평택 3기 Ph3·Ph4, 4기 Ph1·Ph2 CCSS 공급 보도)", vendors="에스티아이(STI), 한양이엔지, 오션브릿지"),
 dict(key="ELEC", role="FSF", ko="변압기·배전반", color="#566370", size=(8.0, 4.0, 4.0), shape="수배전 큐비클 열",
      vendors_site="", vendors="LS일렉트릭, 효성중공업, HD현대일렉트릭"),
 # --- plenum
 dict(key="FFU", role="PLN", ko="FFU(팬 필터 유닛) 블록", color="#dfe7ee", size=(10.0, 10.0, 0.6), shape="1.2 m 각 FFU를 블록 단위로 묶어 표현",
      vendors_site="신성이엔지 (평택 P1~4 클린룸 공급 보도, 삼성물산과 평택 클린룸 시스템 천정 공사 약 276억 원 계약 공시 2021)", vendors="신성이엔지, 에이펙스(APEX)"),
 dict(key="MAU", role="PLN", ko="외조기(MAU)", color="#7fa6c9", size=(14.0, 6.0, 5.0), shape="대형 공조기 박스",
      vendors_site="", vendors="신성이엔지, 삼성E&A(시공)"),
 dict(key="DCC", role="PLN", ko="DCC(건식 냉각 코일)", color="#59b6c7", size=(8.0, 1.0, 3.0), shape="리턴 에어 샤프트 안의 코일 벽",
      vendors_site="P4 'Ph4 DCC 공구' 공사명 공개", vendors="신성이엔지, 한양이엔지"),
 # --- roof
 dict(key="RSC", role="ROOF", ko="옥상 스크러버·배기팬", color="#c7b08a", size=(7.0, 5.0, 5.0), shape="산·알칼리·유기 배기 처리 탑 + 팬",
      vendors_site="삼성엔지니어링 P3 '옥상배기' 수행 공시", vendors="삼성E&A, GST, 유니셈"),
 dict(key="FOUP", role="FAB", ko="로드 포트 위 FOUP(웨이퍼 용기)", color="#23272e", size=(0.45, 0.4, 0.34), shape="장비 전면 로드 포트에 올려진 검은 용기(공식 영상에서 확인). 보도: OHT 한 대가 웨이퍼 24매, 약 8~9 kg을 운반",
      vendors_site="삼성전자 공식 영상(2026-06)에서 장비 전면의 FOUP 확인", vendors="FOUP: Entegris, Miraial, Shin-Etsu Polymer 등 / 로드 포트 규격: SEMI E15.1"),
 dict(key="TBAR", role="FAB", ko="장비 전면 적갈색 수평 바", color="#8f1d2c", size=(0.12, 2.4, 0.12), shape="장비 전면 상부를 가로지르는 적갈색 바(공식 영상에서 형상 확인, 용도 미확인)",
      vendors_site="삼성전자 공식 영상(2026-06)의 클린룸·옐로 룸 장면", vendors="-"),
 dict(key="OHTV", role="FAB", ko="OHT 대차(천장 이송 차량)", color="#ffffff", size=(0.9, 0.6, 0.7), shape="천장 레일에 매달려 FOUP을 나르는 흰색 대차(공식 영상에서 확인). 대수는 P1 보도 수치(약 1,850대)에 맞췄고, 레일 위 간격·위치는 시각화용 가정",
      vendors_site="SEMES · P1에 약 1,850대(보도)", vendors="SEMES, Daifuku, Murata Machinery"),
 dict(key="STACK", role="ROOF", ko="배기 스택", color="#e3e6ea", size=(2.0, 2.0, 9.0), shape="배기 굴뚝", vendors_site="", vendors="-"),
]
TI = {t["key"]: i for i, t in enumerate(TYPES)}

# ---------------------------------------------------------------- floor stack (grade C)
LEVELS = [  # floor, z0, z1, role, name, what/why
 ("1F", 0.0, 9.0, "FSF", "FSF · 유틸리티 서브팹(하부)", "드라이 펌프·스크러버·칠러, 케미컬 공급, 변압기·배전. 오염·발열원을 클린룸에서 떼어 놓는 층"),
 ("2F", 9.0, 16.5, "CSF", "CSF · 클린 서브팹(하부)", "장비 바로 아래. RF 제너레이터·파워 랙, 가스 박스·VMB, 배관 래터럴. 클린룸에서 내려온 공기가 지나는 리턴 공간"),
 ("3F", 16.5, 24.0, "FAB", "하층 클린룸(FAB)", "공정 장비·스토커·OHT. 액세스 플로어 위 장비, 천장에 FFU. P1은 3층에 시창 투어 통로(보도)"),
 ("4F", 24.0, 33.0, "PLN", "FFU 플레넘·트러스(하부)", "FFU로 공기를 내려보내는 공급 공간. 외조기(MAU), DCC, 구조 트러스"),
 ("5F", 33.0, 41.0, "FSF", "FSF · 유틸리티 서브팹(상부)", "상층 클린룸용 펌프·스크러버·칠러, 케미컬·전력 분배"),
 ("6F", 41.0, 48.5, "CSF", "CSF · 클린 서브팹(상부)", "상층 클린룸 바로 아래 전원 랙·가스 박스"),
 ("7F", 48.5, 56.0, "FAB", "상층 클린룸(FAB)", "공정 장비·스토커·OHT"),
 ("8F", 56.0, 66.0, "PLN", "FFU 플레넘·지붕 트러스(상부)", "상층 클린룸 공급 공간, MAU·DCC"),
 ("RF", 66.0, 95.0, "ROOF", "옥상", "배기 스크러버·팬·스택, 배관 랙. 외곽대가 중앙 지붕보다 높음(드론 영상)"),
]
ZONE_COL = {"FSF": "#3d4854", "CSF": "#4d6072", "FAB": "#f3efe2", "PLN": "#9aa7b5"}
FACADE = "#b4bac1"; BASE = "#7f858c"; ROOF = "#3c6fd6"; RING = "#c3c8ce"; RACK = "#e9edf1"
M_RED = "#d0232b"; M_BLUE = "#1f5fc4"; M_YEL = "#f2cc3a"
PITCH = 13.0

# Phase naming per fab-half/level, from regulatory-filing news (contract titles)
PHASE = {
 "P3": {("W", "3F"): ("Ph1", "하층서편 — 삼성물산 공시(계약명, 2026-11-14 Codex가 원문 대조)"), ("W", "7F"): ("Ph2", "상층서편 — 삼성중공업 공시. 파운드리 라인으로 보도"),
        ("E", "3F"): ("Ph3", "하층동편 — 삼성물산·삼성중공업 공시"), ("E", "7F"): ("Ph4", "상층동편(상부동편) — 삼성물산 공시")},
 "P4": {("W", "3F"): ("Ph1", "하서 — 삼성물산 공시. 낸드+D램(1a) 하이브리드로 보도"), ("E", "3F"): ("Ph2", "하동 — 보도. HBM4용 1c D램 라인으로 결정 보도"),
        ("W", "7F"): ("Ph3", "상서 — 삼성물산 공시. 1c D램 라인으로 보도"), ("E", "7F"): ("Ph4", "상동 — 보도. D램 중심으로 전환 보도")},
}

AREAS = [("DIFF", 2), ("CVD", 3), ("PHOTO", 3), ("ETCH", 4), ("CMP", 1.5), ("WET", 2), ("IMP", 1), ("METRO", 1.5)]
def area_sequence(n):
    tot = sum(w for _, w in AREAS); acc = 0; bounds = []
    for k, w in AREAS:
        acc += w; bounds.append((k, acc / tot))
    seq = []
    for i in range(n):
        f = (i + 0.5) / n
        for k, b in bounds:
            if f <= b: seq.append(k); break
    return seq

def bays(cx0, cx1):
    n = int((cx1 - cx0 - 6) // PITCH)
    xoff = cx0 + ((cx1 - cx0) - n * PITCH) / 2
    return n, [xoff + i * PITCH + PITCH / 2 for i in range(n)], xoff

def tool(key, bx, sgn, y, z, fab, fl):
    """composite tool: EFEM/loader at the aisle + body behind it. sgn=+1 east side of aisle, -1 west."""
    L, D, Hh = TYPES[TI[key]]["size"]
    ef = 1.3
    xa = bx + 1.5 if sgn == 1 else bx - 1.5 - ef          # EFEM
    xb = bx + 1.5 + ef if sgn == 1 else bx - 1.5 - D       # body
    eq(xa, y + L / 2 - min(L, 2.4) / 2, z, ef, min(L, 2.4), 2.3, key, fab, fl)
    if key not in ("STK",):
        fx = (bx + 1.5 - 0.5) if sgn == 1 else (bx - 1.5 + 0.05)      # load-port shelf on the aisle side, FOUP top ~1.25 m
        for k in (-0.55, 0.1):
            eq(fx, y + L / 2 + k, z + 0.9, 0.45, 0.4, 0.34, "FOUP", fab, fl)
        eq(fx + 0.15, y + L / 2 - min(L, 2.4) / 2, z + 2.05, 0.12, min(L, 2.4), 0.12, "TBAR", fab, fl)
    if key == "PHOTO":      # track + scanner side by side
        eq(xb, y, z, D - ef, L * 0.45, 2.6, key, fab, fl)
        eq(xb, y + L * 0.5, z, D - ef, L * 0.5, 3.4, key, fab, fl)
    elif key == "ETCH":     # transfer module next to the EFEM + chamber block behind
        tm = 1.2
        if sgn == 1:
            eq(xb, y + 0.6, z, tm, L - 1.2, 2.2, key, fab, fl); eq(xb + tm, y, z, D - ef - tm, L, Hh, key, fab, fl)
        else:
            eq(xb + D - ef - tm, y + 0.6, z, tm, L - 1.2, 2.2, key, fab, fl); eq(xb, y, z, D - ef - tm, L, Hh, key, fab, fl)
    else:
        eq(xb, y, z, D - ef, L, Hh, key, fab, fl)

def cleanroom(fab, floor, cx0, cx1, cy0, cy1, zf):
    z = zf + 0.9
    ymid = (cy0 + cy1) / 2; spine = 8.0
    n, centres, xoff = bays(cx0, cx1)
    seq = area_sequence(n)
    for dy in (-1.2, 1.2):
        RAILS.append([cx0 + 2, ymid + dy - 0.15, z + 4.6, cx1 - cx0 - 4, 0.3, 0.25, fab, floor])
    add(f"{fab}-{floor}-{int(cx0)}-spine", f"{fab} {floor} 중앙 통로(스파인) · 인터베이 OHT", "공정 구역", [cx0, ymid - spine / 2, z, cx1, ymid + spine / 2, z + 0.04],
        "#c9c2ad", "D", ["LAYOUT", "YT"], "중앙 스파인에서 양쪽 베이로 갈라지는 일반적 300mm 팹 배치", fab=fab, fl=floor)
    # process-area floor strips
    i = 0
    while i < n:
        j = i
        while j + 1 < n and seq[j + 1] == seq[i]: j += 1
        t = TYPES[TI[seq[i]]]
        if seq[i] == "PHOTO":
            add(f"{fab}-{floor}-{int(cx0)}-yellow-{i}", "포토 구역 황색 조명(옐로 룸)", "옐로 룸", [xoff + i * PITCH + 0.3, cy0 + 0.5, z + 0.05, xoff + (j + 1) * PITCH - 0.3, cy1 - 0.5, z + 5.6],
                "#f5d21f", "C", ["YT"], "공식 영상에서 포토 베이가 황색 조명인 것을 확인(감광액 보호). 위치는 개념", opacity=0.10, fab=fab, fl=floor)
        add(f"{fab}-{floor}-{int(cx0)}-area-{i}", f"{t['ko']} 구역(개념)", "공정 구역", [xoff + i * PITCH + 0.3, cy0 + 0.5, z, xoff + (j + 1) * PITCH - 0.3, cy1 - 0.5, z + 0.03],
            t["color"], "D", ["LAYOUT"], "공정별 구역 나눔은 개념. 실제 구역 배치 아님. 대표 공급사: " + t["vendors"], opacity=0.22, fab=fab, fl=floor)
        i = j + 1
    zc, zs = zf - 7.5, zf - 16.5        # CSF floor, FSF floor below this cleanroom
    for bi, bx in enumerate(centres):
        key = seq[bi]; L = TYPES[TI[key]]["size"][0]
        if key in ("ETCH", "CVD", "DIFF", "IMP"):      # EHS concept: gas up, exhaust down to pump/scrubber, treated exhaust to roof
            for yy in (cy0 + 20, cy1 - 20):
                PIPES.append([bx + 0.8, yy, zc + 2.3, 0.35, 0.35, z + 1.2 - (zc + 2.3), 0, fab, floor])
                PIPES.append([bx - 1.2, yy, zs + 2.0, 0.35, 0.35, z + 1.0 - (zs + 2.0), 1, fab, floor])
            PIPES.append([bx - 0.3, cy0 + 4, zs + 6.4, 0.6, cy1 + 8 - (cy0 + 4), 0.6, 2, fab, floor])
            PIPES.append([bx - 0.4, cy1 + 8, zs + 6.4, 0.8, 0.8, 85.0 - (zs + 6.4), 2, fab, floor])
        DETS.append([bx, ymid + 12, z + 2.6, 0, fab, floor]); DETS.append([bx, ymid - 12, z + 2.6, 0, fab, floor])
        for dx in (-3.1, 1.9):         # dense overhead utility pipe / duct bundles above the OHT rails (seen in the official video; position concept)
            STRUCT.append([round(bx + dx, 2), cy0 + 3, z + 5.25, 1.2, round(cy1 - cy0 - 6, 2), 0.55, 3, fab, floor])
        if key in ("WET", "CMP"):      # ANSI/ISEA Z358.1: reachable within 10 s (about 16.8 m) -> one unit every 30 m of bay aisle
            yy = cy0 + 12
            while yy < cy1 - 6:
                if abs(yy - ymid) > spine / 2 + 1: SAFETY.append([round(bx - 1.3, 2), round(yy, 2), z, 0, fab, floor])
                yy += 30.0
        if bi % 2 == 0:
            for dy in (-spine / 2 + 0.3, spine / 2 - 0.3): SAFETY.append([round(bx + 6.2, 2), round(ymid + dy, 2), z, 1, fab, floor])
        DETS.append([bx, cy0 + 20, zc + 2.6, 1, fab, {"3F": "2F", "7F": "6F"}[floor]]); DETS.append([bx, cy0 + 12, zs + 3.5, 2, fab, {"3F": "1F", "7F": "5F"}[floor]])
        for side in (1, -1):
            lo, hi = (ymid + spine / 2, cy1 - 3) if side == 1 else (cy0 + 3, ymid - spine / 2)
            sL, sD, sH = TYPES[TI["STK"]]["size"]
            sy = lo + 0.5 if side == 1 else hi - 0.5 - sL
            eq(bx - 1.5 - sD, sy, z, sD, sL, sH, "STK", fab, floor)
            RAILS.append([bx - 0.15, lo, z + 4.6, 0.3, hi - lo, 0.25, fab, floor])
            y = lo + 6.5 if side == 1 else lo + 1.0
            end = hi - 1.0 if side == 1 else hi - 6.5
            while y + L <= end:
                tool(key, bx, 1, y, z, fab, floor); tool(key, bx, -1, y, z, fab, floor)
                y += L + 1.2

def egress(fab, floor, hx0, hx1, cya, cyb, zf, stairs_x, core_edge):
    """travel distance (m) from each 6.5 m tile to the nearest exit IN THIS MODEL (assumed stairs + central core)."""
    ymid = (cya + cyb) / 2; t = 6.5
    x = hx0
    while x < hx1 - 0.1:
        y = cya
        while y < cyb - 0.1:
            cx, cy = min(x + t / 2, hx1), min(y + t / 2, cyb)
            dn = min((cyb - cy) + abs(cx - sx) + 12 for sx in stairs_x)
            ds = min((cy - cya) + abs(cx - sx) + 12 for sx in stairs_x)
            dc = abs(cy - ymid) + abs(cx - core_edge)
            EGRESS.append([round(x, 1), round(y, 1), zf + 0.95, round(min(t, hx1 - x), 1), round(min(t, cyb - y), 1), round(min(dn, ds, dc)), fab, floor])
            y += t
        x += t

def csf(fab, floor, cx0, cx1, cy0, cy1, zf):
    n, centres, _ = bays(cx0, cx1)
    L, D, Hh = TYPES[TI["RFG"]]["size"]; vL, vD, vH = TYPES[TI["VMB"]]["size"]
    for bx in centres:
        y = cy0 + 5
        while y + L < cy1 - 5:
            eq(bx + 2.2, y, zf, D, L, Hh, "RFG", fab, floor); eq(bx - 2.2 - D, y, zf, D, L, Hh, "RFG", fab, floor)
            eq(bx - vD / 2, y + L + 1.0, zf, vD, vL, vH, "VMB", fab, floor)
            y += 12.0

def fsf(fab, floor, cx0, cx1, cy0, cy1, zf):
    n, centres, _ = bays(cx0, cx1)
    pL, pD, pH = TYPES[TI["PUMP"]]["size"]; sL, sD, sH = TYPES[TI["SCR"]]["size"]; cL, cD, cH = TYPES[TI["CHL"]]["size"]
    for bi, bx in enumerate(centres):
        y = cy0 + 6
        while y + 9 < cy1 - 6:
            eq(bx - 3.2, y, zf, pD, pL, pH, "PUMP", fab, floor); eq(bx + 2.0, y, zf, pD, pL, pH, "PUMP", fab, floor)
            eq(bx - sD / 2, y + pL + 0.8, zf, sD, sL, sH, "SCR", fab, floor)
            if bi % 2 == 0: eq(bx + 3.6, y + pL + 0.8, zf, cD, cL, cH, "CHL", fab, floor)
            y += 11.0
        if bi % 3 == 0:
            SAFETY.append([round(bx + 6.0, 2), cy0 + 2.0, zf, 0, fab, floor]); SAFETY.append([round(bx + 6.0, 2), round((cy0 + cy1) / 2, 2), zf, 1, fab, floor]); SAFETY.append([round(bx + 6.0, 2), cy1 - 2.0, zf, 1, fab, floor])

def plenum(fab, floor, cx0, cx1, cy0, cy1, zf):
    L, D, Hh = TYPES[TI["FFU"]]["size"]
    x = cx0 + 1.5
    while x + L < cx1:
        y = cy0 + 1.5
        while y + D < cy1:
            eq(x, y, zf - 0.6, L, D, Hh, "FFU", fab, floor); y += D + 1.5
        x += L + 1.5

def fab(pid, x0, x1, y0, y1, endx, H, roofs, official, src):
    name = f"{pid} FAB"; t = 1.5; S = dict(fab=pid)
    add(f"{pid}-wall-S", f"{name} 남측 외벽", "외피", [x0, y0, 0, x1, y0 + t, H], FACADE, "B", src, official, **S)
    add(f"{pid}-wall-N", f"{name} 북측 외벽", "외피", [x0, y1 - t, 0, x1, y1, H], FACADE, "B", src, official, **S)
    add(f"{pid}-wall-W", f"{name} 서측 외벽", "외피", [x0, y0 + t, 0, x0 + t, y1 - t, H], FACADE, "B", src, official, **S)
    add(f"{pid}-wall-E", f"{name} 동측 외벽(단부 블록)", "외피", [x1 - t, y0 + t, 0, x1, y1 - t, H], FACADE, "B", src, official, **S)
    add(f"{pid}-endblk", f"{name} 동측 단부 블록(복합동 추정 — 복합동의 존재·용도는 공시·보도, 이 블록과의 대응은 P4 채널 주석·타 동 유추) 경계벽", "외피", [endx - 0.5, y0 + t, 0, endx + 0.5, y1 - t, H], FACADE, "B", src + ["P4_4FAC", "EA_P4", "HSCT", "OFF_CT_SMART"],
        "위성영상에서 본체와 구분되는 동측 단부 블록. 공시의 'FAB동/복합동' 중 복합동일 가능성(추정)", **S)
    for nm, bx in (("S", [x0 - 0.2, y0 - 0.2, 0, x1 + 0.2, y0, 14]), ("N", [x0 - 0.2, y1, 0, x1 + 0.2, y1 + 0.2, 14]),
                   ("W", [x0 - 0.2, y0, 0, x0, y1, 14]), ("E", [x1, y0, 0, x1 + 0.2, y1, 14])):
        add(f"{pid}-base-{nm}", f"{name} 하부 띠(짙은 회색)", "외장 그래픽", bx, BASE, "C", ["YT"], "드론 영상의 외장 색 구분을 단순화", **S)
    rz = H - 10.0
    rx0 = min(r[0] for r in roofs); rx1 = max(r[1] for r in roofs); ry0 = roofs[0][2]; ry1 = roofs[0][3]
    add(f"{pid}-ring-S", f"{name} 옥상 외곽대(남)", "지붕", [x0 + t, y0 + t, rz, x1 - t, ry0, H], RING, "B", src + ["YT"], "외곽대가 중앙 지붕보다 높음(드론 영상). 단차 10 m는 가정", fl="RF", **S)
    add(f"{pid}-ring-N", f"{name} 옥상 외곽대(북)", "지붕", [x0 + t, ry1, rz, x1 - t, y1 - t, H], RING, "B", src + ["YT"], "", fl="RF", **S)
    add(f"{pid}-ring-W", f"{name} 옥상 외곽대(서)", "지붕", [x0 + t, ry0, rz, rx0, ry1, H], RING, "B", src + ["YT"], "", fl="RF", **S)
    add(f"{pid}-ring-E", f"{name} 옥상 외곽대(동)", "지붕", [rx1, ry0, rz, x1 - t, ry1, H], RING, "B", src + ["YT"], "", fl="RF", **S)
    for k, r in enumerate(roofs):
        add(f"{pid}-roof-{k+1}", f"{name} 중앙 지붕 {k+1}", "지붕", [r[0], r[2], rz - 1, r[1], r[3], rz], ROOF, "B", src + ["YT"], "위성영상의 중앙 지붕(청색) 범위", fl="RF", **S)
    if len(roofs) == 2:
        add(f"{pid}-roof-core", f"{name} 중앙 옥상 설비대", "지붕", [roofs[0][1], ry0, rz - 1, roofs[1][0], ry1, H - 3], RING, "B", src, "두 지붕 사이 옥상 설비 구역", fl="RF", **S)
    add(f"{pid}-rack-S", f"{name} 옥상 대기방지시설·배관 랙(남)", "옥상 랙", [x0 + 30, y0 + 6, H, endx - 10, ry0 - 6, H + 6], RACK, "C", ["ESRI", "YT", "YT_DAL2", "EA_P4", "EA_P3"],
        "위성·드론 영상에 보이는 옥상 철골 랙을 단순 박스로 표현. 삼성E&A 공시의 공사명에 P4는 '대기방지', P3는 '옥상배기'가 들어 있음(공사 범위 명칭 — 랙 전체의 기능을 뜻하지는 않음). 현장 관찰 유튜브 채널의 P4 주석 사진은 옥상 구조물을 '대기방지 시설'로 표기(비공식 주석)", opacity=0.3, fl="RF", **S)
    add(f"{pid}-rack-N", f"{name} 옥상 대기방지시설·배관 랙(북)", "옥상 랙", [x0 + 30, ry1 + 6, H, endx - 10, y1 - 6, H + 6], RACK, "C", ["ESRI", "YT"], "", opacity=0.3, fl="RF", **S)
    # v7.22: rooftop equipment zones on the west/east ring (and between two central roofs), read from imagery
    RKN = "위성영상(2025-12-22 촬영분)에서 옥상 외곽대 위에 철골 격자와 배관이 밀집해 보이는 구역을 단순 박스로 표현. 평면 범위는 팹 가장자리와 중앙 지붕 사이를 판독한 것이고 높이 6 m는 임의. 개별 설비의 종류·기능은 확인하지 못함"
    add(f"{pid}-rack-W", f"{name} 옥상 설비 구역(서) — 철골 격자·배관(위성 판독)", "옥상 랙", [x0 + 6, ry0 + 3, H, rx0 - 3, ry1 - 3, H + 6], RACK, "B", ["ESRI"], RKN, opacity=0.3, fl="RF", **S)
    add(f"{pid}-rack-E", f"{name} 옥상 설비 구역(동) — 철골 격자·배관(위성 판독)", "옥상 랙", [rx1 + 3, ry0 + 3, H, (rx1 + 48 if pid == "P4" else endx - 6), ry1 - 3, H + 6], RACK, "B", ["ESRI"], RKN, opacity=0.3, fl="RF", **S)
    if len(roofs) == 2 and roofs[1][0] - roofs[0][1] > 12:
        add(f"{pid}-rack-M", f"{name} 옥상 설비 구역(중앙) — 철골 격자·배관(위성 판독)", "옥상 랙", [roofs[0][1] + 3, ry0 + 3, H - 3, roofs[1][0] - 3, ry1 - 3, H + 3], RACK, "B", ["ESRI"], RKN, opacity=0.3, fl="RF", **S)
    # rooftop exhaust scrubbers + stacks along the ring (concept spacing)
    rL, rD, rH = TYPES[TI["RSC"]]["size"]; sL, sD, sH = TYPES[TI["STACK"]]["size"]
    for yy in (y0 + (ry0 - y0) / 2 - rD / 2, ry1 + (y1 - ry1) / 2 - rD / 2):
        x = x0 + 40
        while x + rL < endx - 15:
            eq(x, yy, H, rL, rD, rH, "RSC", pid, "RF"); eq(x + rL + 1, yy + 1.5, H, sL, sD, sH, "STACK", pid, "RF"); x += 26.0

    def mond(tag, face, a, b):
        zs = [(0.42 * H, 0.90 * H, M_RED, 0.0, 0.62), (0.92 * H, 0.97 * H, M_YEL, 0.0, 0.62),
              (0.42 * H, 0.60 * H, M_BLUE, 0.66, 1.0), (0.30 * H, 0.38 * H, M_YEL, 0.0, 0.45)]
        for j, (z0, z1, col, f0, f1) in enumerate(zs):
            p0 = a + (b - a) * f0; p1 = a + (b - a) * f1
            if face == "W": bx = [x0 - 0.6, p0, z0, x0 - 0.2, p1, z1]
            elif face == "E": bx = [x1 + 0.2, p0, z0, x1 + 0.6, p1, z1]
            else: bx = [p0, y0 - 0.6, z0, p1, y0 - 0.2, z1]
            add(f"{pid}-mond-{tag}-{j}", f"{name} 몬드리안 그래픽 패널", "외장 그래픽", bx, col, "C", ["YT", "YT_RE", "PRESS_TOUR"],
                "공식·부동산 채널 드론 영상의 원색 패널을 단순화(정확한 분할·위치는 근사)", **S)
    mond("w", "W", y0 + 4, y0 + 90); mond("s", "S", x0 + 4, x0 + 70); mond("e", "E", y0 + 4, y0 + 70)

    ix0, ix1, iy0, iy1 = x0 + t, x1 - t, y0 + t, y1 - t
    add(f"{pid}-slab-B", f"{name} 기초/1F 바닥", "층 슬래브", [ix0, iy0, -1.0, ix1, iy1, 0.0], "#8a8f96", "C", ["GEN"], "", fl="1F", **S)
    cxa, cxb = x0 + 26, endx - 20
    cya, cyb = y0 + SUP, y1 - SUP
    core = 24.0; cm = (cxa + cxb) / 2
    halves = [("W", cxa, cm - core / 2), ("E", cm + core / 2, cxb)]
    NOTE = "층별 용도는 공개자료(지상 8층·3층 시창투어·2개 층 4개 클린룸·FAB+CSF+FSF 구조)를 결합한 추정. 층고는 가정. 장비 배치는 개념도."
    for fl, z0, z1, role, role_ko, what in LEVELS:
        if role == "ROOF": continue
        if z0 > 0 and role != "PLN":   # plenum floor = the FFU ceiling grid itself
            thick = 1.2 if role == "FAB" else 0.8
            add(f"{pid}-slab-{fl}", f"{name} {fl} 바닥 슬래브" + (" (와플 슬래브: 공기가 아래로 빠지는 격자 구조)" if role == "FAB" else ""), "층 슬래브",
                [ix0, iy0, z0 - thick, ix1, iy1, z0], "#9aa0a8", "C", ["P2_FLOORS", "GEN"], "층 구성은 공개자료 기반 추정, 층고는 가정값." + (" NFPA 318 개정 제안문은 FSF를 클린룸 기류와 내화 구획으로 분리된 층으로 정의 → 이 슬래브를 내화 구획 경계로 표시(개념)." if role == "CSF" else ""), fl=fl, **S)
        for hk, hx0, hx1 in halves:
            side_ko = "서" if hk == "W" else "동"
            zid = f"{pid}-{fl}-{hk}"
            ph = PHASE.get(pid, {}).get((hk, fl))
            if role == "FAB":
                zname = f"{name} {fl} {side_ko}측 · {role_ko}" + (f" · {ph[0]}" if ph else "")
                add(zid, zname, "클린룸 구역", [hx0, cya, z0, hx1, cyb, z0 + 0.9], ZONE_COL[role], "A" if ph and "추정" not in ph[1] else "C",
                    (["PHASE"] if ph else []) + ["CR4", "TOUR_3F", "GEN"],
                    (f"페이즈 위치: {ph[1]}. " if ph else "이 팹의 페이즈 명칭·위치는 공개 자료에서 확인하지 못함. ") + NOTE + " 바닥은 액세스 플로어(0.9 m 가정).", fl=fl, **S)
                add(zid + "-ffu", f"{zname} · FFU 천장면", "FFU 천장", [hx0, cya, z0 + 6.6, hx1, cyb, z0 + 7.0], "#dfe7ee", "D", ["GEN", "AMHS_H"],
                    "클린룸 천장고 약 6.6 m는 일반적 300mm 팹 수치", opacity=0.22, fl=fl, **S)
                cleanroom(pid, fl, hx0, hx1, cya, cyb, z0)
                sxs = []; xx = x0 + 60
                while xx < endx - 40: sxs.append(xx + 4.5); xx += 70
                egress(pid, fl, hx0, hx1, cya, cyb, z0, sxs, hx1 if hk == "W" else hx0)
            elif role == "CSF":
                add(zid, f"{name} {fl} {side_ko}측 · {role_ko}", "서브팹 구역", [hx0, cya, z0, hx1, cyb, z0 + 0.3], ZONE_COL[role], "C", ["CSF_FSF", "GEN"], NOTE, fl=fl, **S)
                csf(pid, fl, hx0, hx1, cya, cyb, z0 + 0.3)
            elif role == "FSF":
                add(zid, f"{name} {fl} {side_ko}측 · {role_ko}", "서브팹 구역", [hx0, cya, z0, hx1, cyb, z0 + 0.3], ZONE_COL[role], "C", ["CSF_FSF", "GEN"], NOTE, fl=fl, **S)
                fsf(pid, fl, hx0, hx1, cya, cyb, z0 + 0.3)
            elif role == "PLN":
                add(zid, f"{name} {fl} {side_ko}측 · {role_ko}", "플레넘 구역", [hx0, cya, z0, hx1, cyb, z0 + 0.3], ZONE_COL[role], "C", ["GEN", "SKECO"], NOTE + " 플레넘 바닥은 FFU 천장 격자 자체.", opacity=0.12, fl=fl, **S)
                plenum(pid, fl, hx0, hx1, cya, cyb, z0)
        add(f"{pid}-{fl}-core", f"{name} {fl} 중앙 코어(수직 동선·샤프트 추정)", "코어", [cm - core / 2 + 1, cya, z0, cm + core / 2 - 1, cyb, z1 - 1.3],
            "#5b6570", "C", ["GEN"], "위치·크기 가정", opacity=0.5, fl=fl, **S)
        # ---- support strips (north / south), per floor
        for sk, ya, yb in (("S", iy0, cya), ("N", cyb, iy1)):
            sko = "남측" if sk == "S" else "북측"
            add(f"{pid}-{fl}-sup-{sk}", f"{name} {fl} {sko} 서포트 구역(추정)", "서포트 구역", [ix0, ya, z0, endx - 0.5, yb, z0 + 0.25], "#6b7a52", "C", ["NAMU", "SKECO", "GEN"],
                "공개 위키: 건물이 북측 서포트·FAB동·남측 서포트로 나뉨(신뢰도 낮음). 폭 25 m는 증권사 리포트의 클린룸 면적에 맞춘 보정값", opacity=0.7, fl=fl, **S)
            # return-air shaft band next to the cleanroom, with DCC
            if role in ("CSF", "FAB", "PLN"):
                ra0, ra1 = (cya - 5, cya) if sk == "S" else (cyb, cyb + 5)
                add(f"{pid}-{fl}-ra-{sk}", f"{name} {fl} {sko} 리턴 에어 샤프트", "공조", [cxa, ra0, z0 + 0.3, cxb, ra1, z1 - 1.3], "#59b6c7", "D", ["GEN", "SKECO", "DCC"],
                    "클린룸 바닥 아래로 빠진 공기가 양옆 샤프트로 올라가 플레넘으로 되돌아가는 순환을 개념적으로 표현", opacity=0.25, fl=fl, **S)
            if role == "PLN":
                dL, dD, dH = TYPES[TI["DCC"]]["size"]; mL, mD, mH = TYPES[TI["MAU"]]["size"]
                yy = cya - 3 if sk == "S" else cyb + 2
                x = cxa + 6
                while x + dL < cxb:
                    eq(x, yy, z0 + 0.5, dL, dD, dH, "DCC", pid, fl); x += 14.0
                ym = ya + 6 if sk == "S" else yb - 6 - mD
                x = cxa + 10
                while x + mL < cxb:
                    eq(x, ym, z0 + 0.5, mL, mD, mH, "MAU", pid, fl); x += 46.0
            if role == "FSF":
                key = "CDS" if sk == "S" else "ELEC"
                L, D, Hh = TYPES[TI[key]]["size"]
                ym = ya + 8
                x = cxa + 8
                while x + L < cxb:
                    eq(x, ym, z0 + 0.3, L, D, Hh, key, pid, fl); eq(x, ym + D + 3, z0 + 0.3, L, D, Hh, key, pid, fl); x += 22.0
            if role == "FAB" and sk == "S":
                add(f"{pid}-{fl}-smock", f"{name} {fl} 스막룸·에어샤워(추정)", "서포트 시설", [x0 + 40, ya + 4, z0, x0 + 80, ya + 19, z0 + 4.5], "#d9d4c3", "D", ["SMOCK"],
                    "방진복 갈아입는 스막룸과 에어샤워를 거쳐 클린룸에 들어감(일반). 위치·크기 가정", fl=fl, **S)
                if pid == "P1" and fl == "3F":
                    add("P1-3F-window", "P1 3F 시창 투어 통로", "서포트 시설", [x0 + 100, cya - 9, z0, x0 + 190, cya - 5.2, z0 + 4.0], "#f2cc3a", "A", ["TOUR_3F", "PRESS_TOUR"],
                        "보도: P1 3층에 마련된 공간에서 시창(유리창) 너머로 클린룸을 봄. 통로의 정확한 위치·길이는 가정", fl=fl, **S)
        # stair / elevator cores in the support strips (full height, emitted per floor for floor isolation)
        k = 0; x = x0 + 60
        while x < endx - 40:
            for sk, yy in (("S", iy0 + 3), ("N", iy1 - 3 - 12)):
                add(f"{pid}-{fl}-stair-{sk}-{k}", f"{name} 계단·승강기 코어(추정)", "서포트 시설", [x, yy, z0, x + 9, yy + 12, z1 - 0.9], "#55606b", "D", ["GEN"],
                    "피난 계단·승강기 코어를 약 70 m 간격으로 가정. EHS 피난 보행거리 계산의 출구로 사용", fl=fl, **S)
            x += 70; k += 1
        # equipment move-in hall in the east end block
        add(f"{pid}-{fl}-movein", f"{name} {fl} 장비 반입 홀·화물 승강기(추정)", "서포트 시설", [endx + 2, y0 + 60, z0, x1 - 3, y1 - 60, z1 - 1.3], "#8a7f6a", "D", ["SKECO", "ESRI"],
            "FAB 단면 양쪽에 장비 반입 공간이 있다는 일반 설명과 위성영상의 동측 단부 블록을 결합한 추정", opacity=0.6, fl=fl, **S)
        if role == "FAB":
            ymid = (y0 + y1) / 2
            add(f"{pid}-{fl}-moveopen", f"{name} {fl} 외벽 장비 반입구(개념 · 위치 임의)", "참조 설계(반입구)", [x1 - 0.6, ymid - 6, z0 + 0.4, x1 + 0.2, ymid + 6, z0 + 6.4], "#e0a43a", "D", ["MOVEIN_COMM", "SKECO"],
                "지상보다 높은 클린룸 층에는 외벽 반입구와 반입 스테이지를 두고 크레인으로 장비를 올려 넣는 것이 팹의 일반적 방식. 평택 현장 종사자 커뮤니티 글에도 2층 이상은 기중기로 반입구에 넣는다는 서술이 있음(비공식·신뢰도 낮음). 어느 면·몇 곳인지는 공개 자료로 확인하지 못해 동측 단부 중앙에 1곳만 개념 표시", fl=fl, **S)
            add(f"{pid}-{fl}-movestage", f"{name} {fl} 반입 스테이지(개념)", "참조 설계(반입구)", [x1 + 0.2, ymid - 7, z0 - 0.3, x1 + 7.2, ymid + 7, z0 + 0.1], "#c9c2ae", "D", ["MOVEIN_COMM", "SKECO"],
                "크레인으로 올린 장비를 내려놓는 외부 돌출 데크의 일반 형태. 치수 임의", fl=fl, **S)
    # ---- v6 interior detail: columns / plenum trusses / CSF lateral racks (generic concept), exit doors, inter-floor lifters, docks
    for fl, z0, z1, role, role_ko, what in LEVELS:
        if role == "ROOF": continue
        for hk, hx0, hx1 in halves:
            n, centres, xoff = bays(hx0, hx1)
            xs = [xoff + i * PITCH for i in range(n + 1)]
            if role in ("FSF", "CSF", "FAB"):
                step = 12.5 if role != "FAB" else 25.0; w = 1.1 if role == "FSF" else 0.9 if role == "CSF" else 0.8
                zb, zt = (z0 + 0.3, z1 - (1.2 if role == "CSF" else 0.8)) if role != "FAB" else (z0 + 0.9, z0 + 6.6)
                for x in xs:
                    y = cya + step / 2
                    while y < cyb:
                        if abs(y - (cya + cyb) / 2) > 4.6: STRUCT.append([round(x - w / 2, 2), round(y - w / 2, 2), zb, w, w, round(zt - zb, 2), 0, pid, fl])
                        y += step
            if role == "PLN":
                for x in xs: STRUCT.append([round(x - 0.35, 2), cya, z0 + 4.0, 0.7, round(cyb - cya, 2), 3.6, 1, pid, fl])
            if role == "CSF":
                for bx in centres:
                    for dx in (-4.2, 3.4): STRUCT.append([round(bx + dx, 2), cya + 4, z1 - 2.6, 0.8, round(cyb - cya - 8, 2), 0.35, 2, pid, fl])
        if role in ("FAB", "CSF", "FSF"):
            xx = x0 + 60
            while xx < endx - 40:
                SAFETY.append([xx + 4.5, cya + 0.4, z0 + (0.9 if role == "FAB" else 0.3), 2, pid, fl]); SAFETY.append([xx + 4.5, cyb - 0.4, z0 + (0.9 if role == "FAB" else 0.3), 2, pid, fl])
                SAFETY.append([xx + 10.5, iy0 + 9, z0 + 0.3, 1, pid, fl]); SAFETY.append([xx + 10.5, iy1 - 9, z0 + 0.3, 1, pid, fl]); xx += 70
    for k, yy in enumerate((cya + 30, cyb - 34)):
        for j, xx in enumerate((cm - 9.5, cm + 5.5)):
            add(f"{pid}-lifter-{k}{j}", f"{name} 층간 FOUP 반송 리프터(개념)", "서포트 시설", [xx, yy, 16.5, xx + 4, yy + 4, 55.0], "#e8eef5", "D", ["LIFTER", "CR4", "GEN"],
                "2개 층 클린룸 사이에서 FOUP을 옮기려면 층간 반송 장치가 필요하다는 일반 원리를 표시(특허 문헌: 리프팅 타워가 층 사이에서 용기를 올리고 내림). 대수·위치는 개념이며 실제와 무관", fab=pid, fl="")
    for k in range(5):
        dx0 = x0 + 22 + k * 15
        add(f"{pid}-dock-{k}", f"{name} 지상층 반입 도크(영상 확인 · 위치 개략)", "외장 그래픽", [dx0, y0 - 0.5, 0.0, dx0 + 9, y0 - 0.1, 6.5], "#4a5058", "C", ["YT"],
            "공식 영상(2026-06)에서 몬드리안 패널 아래 지상층에 셔터가 달린 반입 도크가 줄지어 있는 모습을 확인. 어느 팹의 어느 면인지는 특정하지 못해 위치·개수는 개략", **S)
    return dict(id=pid, x0=x0, x1=x1, y0=y0, y1=y1, endx=endx, H=H, L=round(x1 - x0), W=round(y1 - y0), Lmain=round(endx - x0),
                cr=[cxa, cxb, cya, cyb], core=[cm - core / 2, cm + core / 2],
                cr_area=round(2 * (cxb - cxa - core) * (cyb - cya)))

SRC_FAB = ["ESRI", "OSM"]
HN = " 높이는 미공개. 서쪽에서 찍은 드론 사진에서 4개 팹 높이가 비슷해 보여 P1(83 m)과 같게 가정."
FABS = []
FABS.append(fab("P1", -498, 51, 1941, 2142, 21, 83.0, [(-435, -21, 1989, 2095)],
    "공식·보도 수치: 길이 518~520 m, 폭 200~201 m, 높이 83 m. 위성 실측: 본체 519 m(단부 블록 포함 549 m) × 201 m → 일치", SRC_FAB + ["P1_DIM"]))
FABS.append(fab("P2", -309, 243, 1544, 1748, 212, 83.0, [(-243, 160, 1599, 1696)],
    "위성 실측: 본체 521 m(단부 포함 552 m) × 204 m. 보도의 '400 m대'와 불일치(실측값 채택). 지하1층~지상8층, 연면적 592,077㎡(감리사 공개)." + HN, SRC_FAB + ["P2_FLOORS", "P2_400", "YT_RE"]))
FABS.append(fab("P3", -306, 345, 1281, 1489, 317, 83.0, [(-240, -35, 1332, 1437), (80, 270, 1332, 1437)],
    "보도 수치: 길이 700 m, 건축허가면적 70만㎡, 연면적 약 99만㎡. 위성 실측: 본체 623 m(단부 포함 651 m) × 208 m. 보도 700 m와 차이 있음." + HN, SRC_FAB + ["P3_DIM", "YT_RE"]))
FABS.append(fab("P4", -307, 347, 862, 1070, 310, 83.0, [(-185, 10, 915, 1017), (20, 212, 915, 1017)],
    "위성 실측: 본체 617 m(단부 포함 654 m) × 208 m. Ph1(하서)·Ph2(하동)·Ph3(상서)·Ph4(상동). 2025-12 위성영상에서 동측 일부 공사 중." + HN, SRC_FAB + ["P4_PH", "PHASE", "CR4", "YT_RE"]))

# OHT vehicles: spacing chosen so that P1 carries about 1,850 (press figure); the same spacing is applied to P2-P4 (their counts are not public)
_p1 = sum(max(r[3], r[4]) for r in RAILS if r[6] == "P1"); OHT_SP = _p1 / 1850.0
for r in list(RAILS):
    x, y, z, dx, dy, dz, fb, fl = r; Ln = max(dx, dy); t = OHT_SP / 2
    while t < Ln:
        if dx > dy: eq(x + t - 0.45, y + dy / 2 - 0.3, z - 0.75, 0.9, 0.6, 0.7, "OHTV", fb, fl)
        else: eq(x + dx / 2 - 0.3, y + t - 0.45, z - 0.75, 0.6, 0.9, 0.7, "OHTV", fb, fl)
        t += OHT_SP

# ---------------------------------------------------------------- auxiliary buildings
def aux(id, name, box2, H, color="#aab1b9", conf="B", src=None, note="", rot=0, layer="부속동", z0=0):
    x0, x1, y0, y1 = box2
    add(id, name, layer, [x0, y0, z0, x1, y1, z0 + H], color, conf, src or ["ESRI", "OSM"],
        ("평면은 위성영상 실측, 높이·용도는 추정. " + note).strip(), rot=rot)

aux("V2", "EUV 전용동(V2 라인)", (-522, -350, 1585, 1767), 70, "#aeb6c0", note="삼성물산 공시 공사명 '평택 V2L 상층/하층 FAB동'으로 2개 층 구조 확인. 분석가(SemiWiki)도 'P1~P3가 EUV 2개 층의 V2에 연결'이라고 언급. 드론 사진상 팹보다 약간 낮음", src=["ESRI", "OSM", "V2", "V2L", "YT_RE"])
aux("UT-12", "유틸리티동(P1·P2 사이, UT동 추정)", (-314, -2, 1806, 1889), 42, "#9fa7b0", note="삼성E&A 프로젝트 소개: P2 UT동 — 냉수·스팀·압축공기·공업용수를 생산 라인에 공급, 냉수 일 최대 약 24만 냉동톤, 'UT동과 CT동'을 블록 단위로 배치. 이 건물이 해당 동인지는 미확인", src=["ESRI", "OSM", "P2_UT"])
aux("UT-12E", "유틸리티동 동측부(P1·P2 사이)", (-2, 212, 1806, 1889), 58, "#9fa7b0", src=["ESRI", "OSM"])
aux("UT-34", "유틸리티동(P3·P4 사이, UT동 추정)", (-307, 357, 1117, 1232), 45, "#9fa7b0", note="위성영상에서 냉각탑 수증기 확인", src=["ESRI", "P3_UT"])
aux("UT-34E", "유틸리티동 단부(P3·P4 사이)", (357, 390, 1120, 1230), 60, "#a9b0b8")
aux("CUB-N", "북측 유틸리티/냉각탑 구역(추정)", (-150, 139, 2167, 2283), 35, "#9aa3ad", note="수증기 확인")
aux("OFF-T", "기술동(구글 지도 표기 · 대장의 기술동-2와 같은 건물인지는 미확정)", (-420, -339, 2206, 2248), 45, "#8fa3b8", rot=38, note="위성영상(Esri World Imagery, 줌 18, 약 0.48 m/px, 2026-11-12 재취득)에서 모서리를 읽어 평면·방향을 다시 잡음(판독 오차 약 ±5 m). v7.12까지는 방향이 반대(−30°)였고 평면도 동쪽의 어두운 부속 부분까지 합친 86 × 80 m였음 — 태양광 지붕이 보이는 본체만 약 81 × 42 m, 북동 방향 38°로 수정. 구글 지도의 장소 '삼성전자 평택캠퍼스 기술동' 좌표(37.04006, 127.05605 → 모델 약 (-351, 2231))가 이 박스 안에 있음. 카카오맵은 북쪽 약 240 m 지점을 '기술동 입구', 동쪽 건물을 '기술동 주차타워'로 표기. 건축물대장에는 '기술동-2'(건축면적 6,412.72㎡, 높이 67.90 m, 지상 11층)만 공개되어 있는데, '기술동'과 '기술2동'이 공공데이터에 따로 등록되어 있고 이 박스 평면(약 3,400㎡)이 훨씬 작아 같은 건물인지 정하지 않음. 보도: P1 담당 사무1동은 9층, P2 담당 사무2동은 11층이며 사무동과 생산동은 분리 배치", src=["ESRI", "OFFICE", "PRESS_TOUR", "GOOGLE", "BLDG_REG", "DISINF"], conf="M")
aux("OFF-2", "기술동 주차타워(카카오맵 표기)", (-280, -194, 2211, 2281), 52, "#a7b4c2", rot=48, note="위성영상(Esri World Imagery, 줌 18, 약 0.48 m/px, 2026-11-12 재취득)에서 모서리를 읽어 평면·방향을 다시 잡음(판독 오차 약 ±5 m). 옥상에 차량이 보이는 주차 구조물 약 86 × 71 m, 방향 48°(v7.12까지는 회전 없는 123 × 118 m). 사무2동(11층) 후보. 대응 관계 미확인", src=["ESRI", "OFFICE"])
aux("OFF-3", "자재1동(카카오맵 표기)", (-249, -106, 2363, 2410), 26, "#a7b4c2", rot=39, note="위성영상(Esri World Imagery, 줌 18, 약 0.48 m/px, 2026-11-12 재취득)에서 모서리를 읽어 평면·방향을 다시 잡음(판독 오차 약 ±5 m). 옥상에 덕트·설비가 빽빽한 약 143 × 47 m 건물, 방향 39°(v7.12까지는 −30°로 반대 방향)", src=["ESRI", "KAKAO"])
aux("GATE-W", "사무1동(카카오맵 표기 · 보도상 9층)", (-656, -520, 1942, 1986), 40, "#5d86c9")
aux("E1", "동측 부속동 1(GCS동 후보 — 위치 미확인)", (73, 150, 1950, 2132), 25, note="보도(뉴시스 2022-09): 캠퍼스에 가스·화학물질을 보관하는 대형 GCS(Gas Chemical System)동이 있고 연결 브리지로 생산 라인에 공급. 어느 건물인지는 기사에 없어 이 건물은 후보일 뿐", src=["ESRI", "OSM", "TOUR_3F"])
aux("E2", "동측 부속동 2", (196, 237, 1956, 2126), 15)
aux("E3", "동측 부속동 3", (319, 349, 1950, 2115), 12)
aux("E4", "동측 부속동 4", (388, 418, 1950, 2018), 12)
for i, (a, b, c, d) in enumerate([(235, 344, 1856, 1897), (353, 462, 1856, 1897), (235, 344, 1797, 1838), (353, 462, 1797, 1838)]):
    aux(f"CT-{i+1}", f"냉각탑 뱅크 {i+1}(CT동 추정)", (a, b, c, d), 18, "#c5ccd3", note="위성영상에서 팬 셀 배열 확인. 삼성E&A 소개 자료에 'CT동'이라는 동 명칭이 나옴 — 이 뱅크가 그 동인지는 추정", src=["ESRI", "P2_UT"])
aux("M1", "동측 부속동 M1", (264, 350, 1530, 1752), 30)
aux("M2", "동측 부속동 M2", (388, 470, 1540, 1790), 30)
aux("M3", "동측 부속동 M3", (500, 602, 1610, 1717), 20, note="그림자 길이(2025-12-22 영상)로 약 20 m 추정")
aux("M4", "동측 부속동 M4(P3 쪽 154동 후보)", (386, 470, 1285, 1492), 35, note="P4에서는 채널 주석상 팹 남동쪽 별동이 154동(변전소), 팹 동측 단부가 복합동. 같은 구성을 P3에 적용하면 이 건물이 154동 후보이나 확인하지 못함", src=["ESRI", "OSM", "NAMU"])
aux("M5", "동측 부속동 M5", (497, 600, 1315, 1427), 30)
aux("S1", "남동측 대형 부속동 S1(그린동·수처리 추정)", (484, 645, 1057, 1232), 18, note="보도: P4는 FAB동·복합동·변전소·그린동(폐수처리시설) 4개 시설로 구성, 그린동은 삼성엔지니어링 시공. 삼성E&A 공시 공사명에 그린동 포함, 한성크린텍은 P4 그린동 내 기계·배관 설치 공사 수주 공시. 그린동의 존재·용도는 확인, 이 건물과의 대응은 미확인. 참고(2021 공식 공개): 평택 그린동의 지하 수처리 시설 단면적 약 3만 4천㎡, 하루 약 7만 t 정화, 폐수는 성분별 6가지로 구분, 약품 배관에 스크린도어, 중앙통제실(CCR), 자동화율 97%. 이 박스의 평면은 약 2만 8천㎡", src=["ESRI", "P4_SITE", "P4_4FAC", "EA_P4", "HSCT", "GREEN21"])
aux("S2", "남동측 대형 부속동 S2(그린동·수처리 추정)", (484, 650, 877, 1032), 18, src=["ESRI", "P4_SITE"])
aux("SM1", "남동측 부속동 SM1", (377, 435, 987, 1092), 35)
aux("SM2", "남동측 부속동 SM2(154동·변전소 추정 — 현장 관찰 채널 주석)", (377, 435, 865, 967), 35, note="현장 관찰 유튜브 채널의 남쪽 드론 주석 사진: P4 팹 남동쪽의 낮은 별동을 '154동(변전소)'로, 팹 동측 단부의 높은 블록을 '복합동'으로 표기. 공시의 공사명('FAB동/복합동 마감공사')과도 부합. 보도: P4는 FAB동·복합동(삼성물산)과 변전소·그린동(삼성엔지니어링)의 4개 시설로 구성, 변전소 PC 공사 약 180억 원. 이 박스(SM2)와 주석 건물의 대응은 사진 판독에 의한 추정", src=["ESRI", "YT_DAL2", "YT_DAL1", "P4_SITE", "P4_4FAC", "EA_P4"])
aux("WA", "사무2동(카카오맵 표기 · 보도상 지상 11층)", (-494, -353, 1502, 1552), 50, note="보도(2024-02): 사무1동은 지상 9층(P1 라인 쪽), 사무2동은 지상 11층(P2 라인 쪽), 사무3동은 P3 라인 서쪽, 사무6동은 P6 라인 북쪽에 계획", src=["ESRI", "KAKAO", "OFFICE"])
aux("WB", "서측 지원동 WB", (-481, -409, 1464, 1499), 45)
aux("WC", "서측 지원동 WC", (-500, -350, 1408, 1446), 30)
aux("WD", "사무3동(카카오맵 표기 지점 인접)", (-500, -380, 1245, 1400), 40, "#b9ad98", note="부동산 채널 드론 사진에서 P3 서쪽에 대형 사무동이 공사 중인 모습 확인('2조 사무동'으로 소개). 2025-12 위성영상에서도 공사 중. 범위·높이 개략", src=["ESRI", "YT_RE"])
aux("PR-W", "서측 배관 랙/유틸리티 스트립", (-366, -319, 1180, 1405), 20, "#c9d0d7")
aux("W1", "사무복합동(카카오맵 표기, 주차타워 포함)", (-675, -600, 1252, 1574), 45, "#9fb0c2", note="KCC건설 공개: 사무3동은 지상 9층·연면적 7.8만 평, P3·P4와 연결. 도로를 건너는 브리지로 캠퍼스와 이어진 이 건물로 추정(높이는 9층 기준 가정)", src=["ESRI", "KCC"])
aux("W2", "도로 서측 건물 W2", (-637, -581, 1149, 1236), 15)
aux("W3", "도로 서측 건물 W3", (-634, -578, 1111, 1139), 10, "#5d86c9")
aux("W4", "도로 서측 건물 W4", (-637, -581, 1005, 1096), 15)
# KEPCO Godeok substation site: boundary and three buildings from OpenStreetMap (way 720447745), checked against the 2025-12 satellite image
add("KEPCO-PAD", "한전 고덕변전소 부지(OSM 경계)", "지반", [-476, 595, -1.0, 68, 782, -0.1], "#4a4350", "A", ["BLDG_REG", "OSM", "PWR_GD24", "PWR_GD2", "PWR_GD3B", "YT_DAL2"],
    "건축물대장: 대지면적 102,076㎡, 건축면적 합 20,081.47㎡, 연면적 합 48,546.62㎡(이 OSM 경계의 면적 약 101,700㎡와 0.4% 차이). 보도: 캠퍼스와 도로 하나를 사이에 둔 맞은편, 부지는 삼성이 제공(보도의 '연면적 약 10만㎡'는 대장상 대지면적에 해당). 경계는 OpenStreetMap '고덕변전소' 폴리곤. 추가 계획(보도 2024-08): 345 kV 고덕3 변전소를 고덕국제화계획지구 내 변전소 부지에 2031-09 완공 목표로 추진 — 이 부지와 같은 곳인지는 확인하지 못함. 현장 관찰 채널 사진(2026)에는 '한전변전소 증설공사 중' 주석")
SSN = "보도: 지하 1층~지상 4층, 345 kV, 1변전소 2016년·2변전소 2022년 운영 시작, 2018년에는 변전소와 HVDC 변환소 두 건물. 이 건물이 그중 어느 것인지는 확인하지 못함. 높이는 지상 4층 기준 가정"
REGN = "건축물대장(고덕동 1730, 삼성1로 160 — 건물명 '고덕변환소, 고덕변전소#1, 고덕변전소#2'): 대지 102,076㎡, 주건축물 3동·부속 6동, 허가 2014-12-24, 착공 2015-04-13, 사용승인 2024-10-02. "
aux("SS-A", "고덕 변환소(건축물대장 · 건물 대응은 면적 비교 추정)", (-317, -214, 733, 767), 23.8, "#c9ced4", conf="M", note=REGN + "고덕 변환소: 건축면적 7,745.67㎡, 연면적 9,350.77㎡, 높이 23.80 m, 지상 3층. 위성영상 재판독(v7.13): 북쪽 넓은 블록(약 103 × 34 m)과 남쪽 좁은 블록(약 64 × 78 m)의 합이 약 8,500㎡로 대장 건축면적과 9% 차이. 남쪽 블록 양옆의 칸막이 구획(변압기 베이로 보임)을 빼면 맞아떨어져 이 건물을 변환소로 판단", src=["BLDG_REG", "OSM", "ESRI", "PWR_GD24", "PWR_GD", "PWR_GD2"])
aux("SS-A2", "고덕 변환소 남쪽 블록(위성 판독)", (-300, -236, 655, 733), 23.8, "#c9ced4", conf="M", note=REGN + "변환소 본체의 남쪽 부분. 높이는 대장값을 그대로 적용(블록별 높이 차이는 미확인)", src=["BLDG_REG", "ESRI"])
aux("SS-A3", "변환소 옆 칸막이 구획(서) — 변압기 베이로 보임(위성 판독)", (-317, -300, 655, 733), 9, "#8a939c", note="위성영상에서 방화벽으로 나뉜 칸이 줄지어 보임. 용도는 형상에 따른 추정, 높이 임의", src=["ESRI"])
aux("SS-A4", "변환소 옆 칸막이 구획(동) — 변압기 베이로 보임(위성 판독)", (-236, -214, 655, 733), 9, "#8a939c", note="위성영상 판독. 용도 추정, 높이 임의", src=["ESRI"])
aux("SS-SP", "예비품창고 후보(대장 1,166㎡ · 위성의 파란 지붕 약 1,300㎡)", (-355, -290, 601, 621), 15.0, "#5b8fd6", conf="C", note=REGN + "대장: 예비품창고동 건축면적 1,166.17㎡, 높이 15.00 m, 지상 1층, PC구조. 부지 남서쪽의 파란 지붕 건물(약 65 × 20 m)이 면적 11% 차이로 가장 가까워 후보로 표시. 대응은 면적 비교에 의한 추정", src=["BLDG_REG", "ESRI"])
aux("SS-OF", "사무동 후보(대장 410㎡ · 높이 9.9 m)", (-290, -262, 605, 625), 9.9, "#d9dde2", conf="C", note=REGN + "대장: 사무동 건축면적 409.70㎡, 연면적 706.38㎡, 높이 9.90 m, 지상 2층. 파란 지붕 건물 동쪽의 흰 건물을 후보로 표시(위성 판독 평면은 약 600㎡로 대장보다 큼 — 대응 불확실)", src=["BLDG_REG", "ESRI"])
aux("SS-ST", "STATCOM 후보(대장 978㎡ · 높이 17.5 m)", (-21, 1, 607, 634), 17.5, "#d9dde2", conf="C", note=REGN + "대장: STATCOM 건축면적 978.12㎡, 연면적 1,307.06㎡, 높이 17.50 m, 지상 2층. 부지 남동쪽에 양옆으로 옥외 기기가 붙은 흰 건물이 있어 후보로 표시(위성 판독 건물 평면은 약 600㎡ — 대장보다 작아 대응 불확실)", src=["BLDG_REG", "ESRI"])
aux("SS-B", "고덕 변전소(#1 또는 #2 — 건축물대장)", (-61, -17, 651, 763), 32.85, "#b9c0c7", conf="M", note=REGN + "변전소: 건축면적 4,861.36㎡, 연면적 17,921.59㎡, 높이 32.85 m, 지상 4층·지하 1층. 변전소-2: 건축면적 4,671.44㎡, 연면적 17,853.72㎡, 높이 33.45 m, 지상 4층·지하 1층. 이 박스의 평면은 약 4,930㎡로 대장값과 1~6% 차이. 두 변전소 중 어느 쪽인지는 구분하지 못해 높이는 #1 값을 넣음", src=["BLDG_REG", "OSM", "ESRI", "PWR_GD24", "PWR_GD", "PWR_GD2"])
aux("SS-C", "고덕 변전소(#1 또는 #2 — 건축물대장)", (10, 57, 654, 762), 33.45, "#b9c0c7", conf="M", note=REGN + "이 박스의 평면은 약 5,080㎡(대장의 변전소 4,861㎡·변전소-2 4,671㎡와 4~9% 차이). 높이는 변전소-2 값(33.45 m)을 넣었고 #1·#2 대응은 미확인. 같은 대지의 부속 건물(대장): STATCOM 978㎡·높이 17.5 m·2층, 예비품창고 1,166㎡·15 m, 사무동 410㎡·9.9 m, 소내변압기동 173㎡·7.4 m — 위치를 알 수 없어 모델에 넣지 않음", src=["BLDG_REG", "OSM", "ESRI", "PWR_GD24", "PWR_GD", "PWR_GD2"])
aux("SS-Y1", "옥외 철구·기기 구역 1(위성 확인)", (-460, -340, 625, 778), 9, "#7d8791", note="위성영상에서 철구(갠트리)와 기기 열을 확인. 용도 세부는 미확인", src=["ESRI", "PWR_GD"])
aux("SS-Y2", "옥외 철구·기기 구역 2(위성 확인)", (-195, -70, 690, 780), 9, "#7d8791", note="위성영상에서 철구(갠트리)와 기기 열을 확인. 용도 세부는 미확인", src=["ESRI", "PWR_GD"])
BR = [("BR-V2a", (-350, -309, 1712, 1728)), ("BR-V2b", (-350, -309, 1644, 1660)), ("BR-12a", (-303, -279, 1889, 1941)),
      ("BR-12b", (-232, -206, 1889, 1941)), ("BR-12c", (-300, -280, 1748, 1806)), ("BR-12d", (100, 124, 1748, 1806)),
      ("BR-23a", (11, 28, 1489, 1544)), ("BR-23b", (133, 146, 1489, 1544)), ("BR-34a", (5, 35, 1232, 1281)),
      ("BR-34b", (-50, -30, 1070, 1117)), ("BR-34c", (80, 105, 1070, 1117)), ("BR-W", (-600, -481, 1483, 1497))]
for bid, b, nm in [("BR-12e", (-74, -45, 1748, 1806), "연결 브리지(오버 브리지 · v7.16 위성 판독 추가)"), ("BR-12f", (-39, -13, 1748, 1806), "연결 브리지(오버 브리지 · v7.16 위성 판독 추가)"),
                   ("BR-W2", (-353, -309, 1546, 1558), "서측 지원동–P2 연결 브리지(v7.16 위성 판독 추가)"),
                   ("BR-PR1", (395, 473, 1224, 1236), "배관 랙 브리지(트러스 구조 · v7.16 위성 판독 추가)"), ("BR-PR2", (409, 421, 1236, 1279), "배관 랙 브리지(트러스 구조 · v7.16 위성 판독 추가)")]:
    aux(bid, nm, b, 16, "#4f9dff", note="위성영상(줌 18, 약 0.48 m/px)에서 건물 사이를 잇는 구조물로 판독해 추가. 평면은 위성영상 실측(오차 약 ±5 m), 높이·층수·용도는 가정", src=["ESRI", "PRESS_TOUR"], layer="연결 브리지", z0=16)
for bid, b in BR:
    aux(bid, "연결 브리지(오버 브리지)", b, 16, "#4f9dff", note="보도: 건물 사이를 오버 브리지로 연결(인원·웨이퍼·가스·케미컬 이동). 개별 위치는 위성영상 판독, 층수·높이 가정",
        src=["ESRI", "PRESS_TOUR"], layer="연결 브리지", z0=16)

# V2 interior: two EUV levels (filing title 'V2L 상층/하층'), with drive-laser/aux level below each — grade D
for fl, zf, ko in (("V2-L", 16.5, "하층"), ("V2-U", 48.5, "상층")):
    add(f"V2-{fl}-zone", f"V2 {ko} EUV 클린룸(개념)", "클린룸 구역", [-510, 1597, zf, -362, 1755, zf + 0.9], "#f3efe2", "C", ["V2L", "V2", "GEN"],
        "상층·하층 2개 층은 공시 공사명으로 확인. 대수·배치는 개념이며 실제와 무관", fab="V2", fl=fl)
    add(f"V2-{fl}-sub", f"V2 {ko} 아래 서브팹(EUV 구동 레이저·보조 설비, 개념)", "서브팹 구역", [-510, 1597, zf - 7.5, -362, 1755, zf - 7.2], "#4d6072", "D", ["EUV", "GEN"],
        "EUV 장비는 구동 레이저 등 보조 설비를 아래층에 둠(ASML 공개 자료의 서브팹 풋프린트 언급)", fab="V2", fl=fl)
    L, D, Hh = TYPES[TI["EUV"]]["size"]; aL, aD, aH = TYPES[TI["EUVAUX"]]["size"]
    for yy in (1615, 1650, 1690, 1725):
        x = -500
        while x + L < -372:
            eq(x, yy, zf + 0.9, L - 4, D, Hh, "EUV", "V2", fl); eq(x + L - 4, yy + 0.3, zf + 0.9, 4, D - 0.6, 3.5, "EUV", "V2", fl)
            eq(x + 1, yy + 0.8, zf - 7.2, aL, aD, aH, "EUVAUX", "V2", fl); x += L + 6

# ---------------------------------------------------------------- utility-system concept layers (v4)
import utility
USYS, UGROUPS, UTIL = utility.build_utilities(FABS, add, bays)

KAKAO_NOTE = {"OFF-T": "이전 판에서는 사무1동으로 추정했으나, 카카오맵의 '사무1동' 표기 지점은 서측 건물 쪽이어서 추정을 철회", "GATE-W": "카카오맵 장소 '삼성전자 평택캠퍼스 사무1동' 표기 지점이 이 건물 안쪽. 높이는 9층 기준 가정", "OFF-2": "카카오맵 장소 '기술동주차타워' 표기 지점이 이 건물 안", "OFF-3": "카카오맵 장소 '자재1동' 표기 지점이 이 건물 안. 북쪽에 '기술동 입구'·'게스트룸' 표기", "WA": "카카오맵 장소 '사무2동' 표기 지점이 이 건물 안", "W1": "카카오맵 장소 '사무복합동'·'사무복합동 주차타워' 표기 지점이 이 건물 안", "WD": "카카오맵 '사무3동' 표기 지점이 이 건물 남쪽 약 35 m. KCC건설 공개: 사무3동은 지상 9층, P3·P4와 연결"}
for e in ELEMS:
    if e["id"] in KAKAO_NOTE:
        e["note"] = (KAKAO_NOTE[e["id"]] + ". " + e["note"]).strip(); e["src"] = ["KAKAO"] + [k for k in e["src"] if k != "KAKAO"]; e["conf"] = "M"
    if e["id"] == "V2": e["note"] += " 카카오맵에는 'EUV동' 표기 지점이 이 건물 서쪽 도로변에 있음."; e["src"].append("KAKAO")
# map-labelled points (Kakao Map place search, 2026-11): gates and facilities not modelled as buildings
for mid, nm, x, y in [("MK-G1", "GATE1", -611, 1702), ("MK-G3", "GATE3·북서게이트", -524, 2153), ("MK-G4", "GATE4", -478, 1454), ("MK-G2", "2번게이트", -508, 951), ("MK-G5", "5번게이트", 494, 828),
                      ("MK-G7", "7번게이트", 712, 1146), ("MK-GE", "동측게이트", 684, 1488), ("MK-QC", "검품장 입구", 578, 1918), ("MK-WF", "복지동", -717, 1965), ("MK-ER", "방제센터", -360, 1893),
                      ("MK-P2", "2단지 주차동", -858, 1715), ("MK-TB", "기술동 입구", -387, 2472), ("MK-P2P", "P2 주차타워·야외주차장(구글 지도 표기)", -1042, 1275), ("MK-G5G", "GATE5(구글 지도 표기 — 카카오맵 5번게이트와 약 235 m 차이)", 306, 686)]:
    add(mid, nm + " (카카오맵 표기)", "지도 표기 지점", [x - 7, y - 7, 0.0, x + 7, y + 7, 0.8], "#f2cc3a", "M", ["KAKAO"], "카카오맵 장소 검색에 등록된 지점. 좌표는 표기 지점이며 건물 외곽이 아님")

REG_M = "위치: 카카오맵 장소·주소 검색 좌표(2026-11-12). 규모: 국토교통부 건축물대장. 상자의 형상·배치는 건축면적 합에 맞춘 단순 표현이며 실제 동 배치가 아님. "
aux("PUB-WWTP", "평택고덕공공폐수처리시설 A동(위성 판독 · 건축물대장)", (-1286, -1181, 712, 744), 12, "#7d6a4f", conf="M", note=REG_M + "고덕동 1721, 삼성1로 60. 대장: 주용도 자원순환관련시설(하수등처리시설), 대지 150,297.2㎡, 건축면적 8,429.26㎡, 연면적 21,840.49㎡, 주건축물 3동, 사용승인 2022-07-15. 카카오맵 장소명이 같은 지번에 '평택고덕공공폐수처리시설'로 표기되어 대장의 시설과 같은 곳으로 확인. 캠퍼스 그린동에서 1차 처리된 물이 이 시설을 거쳐 서정리천으로 방류(보도). 높이는 임의", src=["KAKAO", "BLDG_REG", "WW_PATH_B"])
aux("PUB-WWTP-B", "평택고덕공공폐수처리시설 B동(위성 판독)", (-1162, -1105, 688, 724), 12, "#7d6a4f", conf="M", note="위성영상 판독 평면. 높이 임의. 대장상 주건축물 3동 중 하나로 봄", src=["ESRI", "BLDG_REG", "KAKAO"])
aux("PUB-WWTP-C", "평택고덕공공폐수처리시설 C동(위성 판독 · 지붕 태양광)", (-1098, -995, 698, 721), 10, "#7d6a4f", conf="M", note="위성영상 판독 평면. 지붕에 태양광 패널이 보임. 높이 임의", src=["ESRI", "BLDG_REG", "KAKAO"])
aux("PUB-WWTP-T", "처리조 구역(잔디 격자 — 복개 구조로 보임, 위성 판독)", (-1286, -943, 598, 688), 1.0, "#5f7a4d", note="위성영상에서 격자 모양 잔디 구획과 점검구 열이 보임. 지하·복개 처리조로 보이나 용도는 형상에 따른 추정", src=["ESRI"])
aux("LINDE-BLD", "린데코리아 평택공장 서측 건물군(위성 판독 · 건축물대장)", (-914, -871, 590, 788), 12, "#8fa7b5", conf="M", note=REG_M + "고덕동 1722. 대장: 공장, 대지 78,833.4㎡, 건축면적 27,316.3㎡, 연면적 22,665.15㎡, 주건축물 6동, 착공 2018-11-20, 사용승인 2023-04-27. v7.13: 위성영상으로 부지(약 369 × 219 m = 약 80,800㎡, 대장 대지 78,833㎡와 2.5% 차이)와 건물·탱크를 다시 배치. 서측의 파란 지붕 건물 여러 동을 한 상자로 묶음. 높이 임의", src=["KAKAO", "BLDG_REG", "GAS_LINDE_B"])
aux("LINDE-PAD", "린데코리아 평택공장 부지(위성 판독)", (-929, -560, 583, 802), 0.3, "#4a5560", note="가스 전문지(2019): 1단계 ASU 공장을 완공해 가동했고 여러 기의 ASU와 수소 공장, 정제기, 파이프라인 시스템으로 구성. 회사 보도자료(2025): 8번째 온사이트 공기분리장치를 건설. 부지 외곽. 대장 대지면적과 2.5% 차이. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG", "INT_LINDE25", "GAS_LINDE19"])
aux("LINDE-NE", "린데코리아 북동측 건물(파란 지붕, 위성 판독)", (-626, -574, 726, 779), 20, "#3f7fc4", note="약 52 × 53 m. 용도 미확인, 높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-M1", "린데코리아 중앙 건물 1(위성 판독)", (-802, -726, 657, 679), 12, "#3f7fc4", note="파란 지붕 3연동. 높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-M2", "린데코리아 중앙 건물 2(위성 판독)", (-681, -645, 655, 683), 14, "#3f7fc4", note="높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-S", "린데코리아 남측 건물(지붕 태양광, 위성 판독)", (-726, -655, 602, 629), 10, "#5b6f8a", note="지붕에 태양광 패널이 보임. 높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-CT", "린데코리아 냉각탑(팬 5셀, 위성 판독)", (-595, -569, 621, 683), 12, "#c5ccd3", note="원형 팬 5개가 보임. 높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-TK1", "린데코리아 저장탱크 1(돔 지붕, 위성 판독)", (-814, -776, 743, 781), 32, "#eef1f4", note="지름 약 38 m의 돔 지붕 탱크. 내용물·높이 미확인(높이 임의). 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-TK2", "린데코리아 저장탱크 2(위성 판독)", (-850, -812, 719, 757), 32, "#eef1f4", note="지름 약 38 m. 높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-TK3", "린데코리아 저장탱크 3(위성 판독)", (-814, -776, 702, 740), 32, "#eef1f4", note="지름 약 38 m. 높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("LINDE-TK4", "린데코리아 저장탱크 4(위성 판독)", (-759, -721, 719, 757), 32, "#eef1f4", note="지름 약 38 m. 높이 임의. 원통형 탱크도 상자로 단순화", src=["ESRI", "BLDG_REG"])
aux("NGATE-BLD", "북문동(건축물대장)", (-630, -606, 2196, 2220), 10.32, "#9aa5b1", conf="M", note=REG_M + "고덕동 1695, 삼성1로 457. 대장: 건축면적 572.85㎡, 연면적 934.22㎡, 높이 10.32 m, 지상 2층, 일반철골구조, 사용승인 2026-04-27. 평면은 정사각형으로 가정", src=["KAKAO", "BLDG_REG"])

aux("PARK-2", "2단지 주차동(건축물대장 · 평면은 위성 판독)", (-938, -764, 1572, 1818), 20.99, "#e4e6e8", conf="M", rot=43, note="위성영상 재판독(v7.13): 흰 지붕의 대형 구조물 — 모서리 서(-997, 1727)·북(-869, 1845)·동(-704, 1662), 약 174 × 246 m, 방향 43°. 남쪽 모서리는 실제로는 잘려 있으나(모따기) 직사각형으로 단순화해 평면이 약 42,800㎡(대장 42,286㎡와 1% 차이). " + REG_M + "고덕동 1696, 삼성로 117, 건물명 '삼성전자(주) 평택캠퍼스 2단지'. 대장: 주차동 — 건축면적 42,285.72㎡, 연면적 161,032.54㎡, 높이 20.99 m, 지상 4층·지하 1층, 철골철근콘크리트구조, 옥내 자주식 4,858대(149,513㎡)·옥외 248대, 허가 2018-05-29, 사용승인 2026-01-05, 대지 804,237.8㎡. 높이·층수·면적은 대장값. 평면은 건축면적에 맞춘 150 × 282 m 직사각형 가정이며 중심은 카카오맵 '2단지 주차동' 지점. 구글 지도의 'P2 주차타워·야외주차장' 지점은 남서쪽 약 480 m로 같은 대지의 다른 구역일 수 있음", src=["BLDG_REG", "KAKAO", "GOOGLE"])

# ---------------------------------------------------------------- v7.17 surrounding facilities (public map labels + satellite imagery)
def cbox(cx, cy, L, Wd): return (cx - L / 2, cx + L / 2, cy - Wd / 2, cy + Wd / 2)
EXT_N = "평면은 위성영상(Esri World Imagery 줌 18, 약 0.48 m/px, 2026-11-13 재취득) 판독이며 오차 약 ±5 m. 높이·용도는 추정. 원통형 탱크와 공정 설비는 상자로 단순화. "
APX = ". 회사 공식 발표: 2015년 평택 신규 팹의 산업용 벌크가스와 벌크 특수가스 공급 시스템 계약을 수주, 2018-01 두 번째 초고순도 질소 플랜트 가동과 질소 플랜트 2기 추가 건설 발표"
AP_N = EXT_N + "카카오맵과 구글 지도가 같은 부지를 '에어프로덕츠코리아 평택공장'으로 표기(장당동 627, 경기대로 1029). 캠퍼스 북동쪽 경계 밖, 철도와 도로 사이의 삼각형 부지. Air Products 보도자료: 평택에서 질소·산소·아르곤·수소 생산 설비와 벌크 특수가스 공급 시스템을 건설·소유·운영. 해외 전문지: 1단계에 초고순도 질소 플랜트, 수소 발생기, 액화기, 벌크 특수가스 공급 시스템을 지었고 질소 플랜트 2기를 추가. 개별 건물·설비의 용도는 형태로 본 추정" + APX
AP_S = ["ESRI", "KAKAO2", "GOOGLE2", "AP_OFF18", "AP_OFF15", "INT_AP26", "INT_AP_P1", "GAS_AP"]
aux("AP-PAD", "에어프로덕츠코리아 평택공장 부지(지도 표기 · 위성 판독)", cbox(622, 2150, 255, 118), 0.3, "#4a5560", conf="M", note=AP_N, src=AP_S, rot=-45)
for i, (cx, cy) in enumerate([(563, 2205), (544, 2185), (580, 2182)]):
    aux(f"AP-TK{i+1}", f"에어프로덕츠 저장탱크 {i+1}(돔 지붕, 위성 판독)", cbox(cx, cy, 27, 27), 28, "#eef1f4", note=AP_N + ". 지름 약 27 m, 높이 임의", src=AP_S)
aux("AP-B1", "에어프로덕츠 남서측 건물(지붕 태양광, 위성 판독)", cbox(549, 2140, 55, 22), 12, "#3b4654", note=AP_N, src=AP_S, rot=-44)
aux("AP-B2", "에어프로덕츠 북동측 건물(파란 지붕, 위성 판독)", cbox(640, 2233, 76, 16), 12, "#3f6fd0", note=AP_N, src=AP_S, rot=-35)
aux("AP-B3", "에어프로덕츠 동측 건물(파란 지붕, 위성 판독)", cbox(663, 2188, 24, 18), 10, "#3f6fd0", note=AP_N, src=AP_S, rot=-45)
aux("AP-B4", "에어프로덕츠 남측 건물(파란 지붕, 위성 판독)", cbox(635, 2057, 26, 20), 10, "#3f6fd0", note=AP_N, src=AP_S, rot=-45)
aux("AP-PROC", "에어프로덕츠 공정 설비 구역(콜드박스·압축 설비로 보임, 위성 판독)", cbox(647, 2100, 84, 58), 30, "#dfe4e8", note=AP_N + ". 흰색 탑·박스가 밀집한 구역을 한 상자로 묶음, 높이 임의", src=AP_S, rot=-45)
aux("AP-CT1", "에어프로덕츠 냉각탑(위성 판독)", cbox(590, 2088, 26, 12), 10, "#aab1b9", note=AP_N, src=AP_S, rot=-45)
aux("AP-CT2", "에어프로덕츠 냉각탑(위성 판독)", cbox(661, 2019, 30, 12), 10, "#aab1b9", note=AP_N, src=AP_S, rot=-45)
AFX = ". 회사 공식 발표(2021-07): 평택캠퍼스 세 번째 반도체 공장의 산업용 가스 공급사로 선정돼 방축리·지제동 일대 100,000㎡ 부지에 공장을 건설(도시계획시설 실시계획 인가 2021-06-28). 보도(2021): P3 가스 공급사는 에어퍼스트와 린데, P4 물량 일부도 에어퍼스트. 보도(2026-05): 평택공장이 회사 가스 생산량의 약 40%를 맡고, 건물 지붕에 약 729.6 kW 자가소비형 태양광이 있으며, 캠퍼스 증설에 맞춰 공급 시설을 추가로 짓는 중. 이 모델의 부지 상자(약 330 × 175 m)는 공식 부지 면적보다 작음 — 서쪽 공사 구역을 빼고 그렸기 때문"
AF_N = EXT_N + "카카오맵이 '에어퍼스트 평택공장'(고덕면 방축리 151-1)으로 표기한 부지. 캠퍼스 남쪽 약 1 km. 보도: 산소·질소·아르곤·수소를 지하 배관으로 공급, P3·P4 담당. 회사 채용 공고의 평택공장 직무에 ASU(공기분리장치)와 SMR(수증기 메탄 개질, 수소 생산) 운전이 적혀 있어 두 설비가 있는 것으로 보임. 개별 건물·설비의 용도는 형태로 본 추정. 서쪽의 흰색 가설 건물군(공사용으로 보임)은 넣지 않음" + AFX
AF_S = ["ESRI", "KAKAO2", "AF_OFF", "GAS_AF", "AF_SIG", "AF_JOB", "GAS_PARK", "GAS_PARK2"]
aux("AF-PAD", "에어퍼스트 평택공장 부지(지도 표기 · 위성 판독)", cbox(-465, -295, 330, 175), 0.3, "#4a5560", conf="M", note=AF_N, src=AF_S, rot=-50)
aux("AF-TK1", "에어퍼스트 저장탱크 1(돔 지붕, 위성 판독)", cbox(-384, -208, 40, 40), 34, "#eef1f4", note=AF_N + ". 지름 약 40 m, 높이 임의", src=AF_S)
aux("AF-TK2", "에어퍼스트 저장탱크 2(돔 지붕, 위성 판독)", cbox(-376, -248, 40, 40), 34, "#eef1f4", note=AF_N + ". 지름 약 40 m, 높이 임의", src=AF_S)
aux("AF-B1", "에어퍼스트 북측 건물군(파란 지붕, 위성 판독)", cbox(-501, -168, 140, 26), 12, "#3f6fd0", note=AF_N + ". 줄지어 선 건물 여러 동을 한 상자로 묶음", src=AF_S, rot=-50)
aux("AF-B2", "에어퍼스트 중앙 건물(파란 지붕, 위성 판독)", cbox(-418, -272, 46, 40), 14, "#3f6fd0", note=AF_N, src=AF_S, rot=-50)
aux("AF-B3", "에어퍼스트 남측 대형 건물(파란 지붕, 위성 판독)", cbox(-477, -390, 136, 36), 16, "#3f6fd0", note=AF_N, src=AF_S, rot=-48)
aux("AF-PROC", "에어퍼스트 공정 설비 구역(위성 판독)", cbox(-432, -350, 110, 70), 30, "#dfe4e8", note=AF_N + ". 흰색 탑·박스가 밀집한 구역을 한 상자로 묶음, 높이 임의", src=AF_S, rot=-48)
LGX = " 추가 확인(2020 보도): 삼성전자 평택 종합물류센터(CDC)는 2018년 완공됐고 TV·냉장고·에어컨 등 삼성전자 가전제품 대부분의 물류를 맡으며 자회사 삼성전자로지텍이 관리. 2025-12 다른 매체도 P6 예정 부지의 CDC 물류센터 철거 계획과 건축허가 확보를 보도. 포승 센터는 국내 생산 가전과 평택항으로 들어오는 해외 생산 제품을 전국으로 보내는 거점이 될 전망(2026-09 보도). 2026년 보도: P5 다음 공장은 P5와 구조가 같은 쌍둥이 팹(P5-2)으로 짓는다는 계획과, 현장에서 터파기에 들어갔다는 작업자 전언이 있음 — 다만 이 건물이 철거됐다는 직접 확인은 아님. 유튜브(부동산 채널, 2026-09, 음소거 시청)의 자체 제작 배치도는 P5 팹2를 P5 팹1 바로 북쪽에 그렸고, 이 창고는 그 북서쪽 자리에 해당 — 공식 도면이 아니므로 참고로만 씀. 이에 따라 이 모델은 건물을 이전 예정으로 표기"
LG_N = EXT_N + "카카오맵이 '삼성전자 물류창고'(물류센터, 고덕동 1696-1)로 표기한 건물. 2025-12-22 위성영상에서 약 177 × 320 m(약 56,600㎡)의 단일 지붕 건물이며 동·서 양쪽에 하역 도크가 줄지어 있음. 높이는 그림자 길이(약 37 m)로 본 약 21 m 추정. 건축물대장 표제부는 조회되지 않음. 보도(2025-12): P6 공사 예정 부지에 있는 CDC 물류센터를 2026년 5월까지 철거할 계획이며 철거용 건축허가가 나온 상태. CDC(Central Distribution Center)는 제품의 입출고·보관·분류·배송을 통합 관리하는 중앙물류센터를 뜻하고, 삼성전자는 평택 포승지구에 약 11만㎡ 규모의 가전제품 CDC를 2025-03 착공해 2027-06 준공 목표로 짓는 중(투자협약 보도 2026-09). 즉 보도대로라면 팹 자재 창고가 아니라 제품 물류센터이며, 없애는 것이 아니라 포승으로 옮기는 흐름으로 읽힘. 다만 카카오맵의 이 건물이 보도의 CDC 물류센터와 같은 건물인지, 포승 센터가 그 대체 시설인지는 어느 자료도 직접 적지 않아 추정이며, 현재 철거 여부도 확인하지 못함." + LGX
LG_S = ["ESRI", "KAKAO2", "CDC_DEMO", "CDC_DEMO2", "CDC_2018", "CDC_POSEUNG", "CDC_POSEUNG2", "P52_SE", "P52_IN", "YT_P6"]
aux("LOG-WH", "삼성전자 물류창고 — 이전 예정(카카오맵 표기 · 위성 판독 · CDC 물류센터 추정, 포승 신축 CDC로 이전 보도)", (-1567, -1390, 1248, 1568), 21, "#c9d2dc", conf="M", note=LG_N, src=LG_S)
aux("LOG-E", "물류창고 동측 부속 건물(위성 판독)", (-1360, -1338, 1263, 1358), 10, "#3b4654", note=LG_N, src=LG_S)
aux("LOG-SW1", "물류창고 남서측 부속 건물 1(위성 판독)", (-1625, -1605, 1292, 1319), 8, "#aab1b9", note=LG_N, src=LG_S)
aux("LOG-SW2", "물류창고 남서측 부속 건물 2(위성 판독)", (-1640, -1602, 1237, 1268), 8, "#aab1b9", note=LG_N, src=LG_S)
# v7.24: rooftop detail of the utility building between P3 and P4, read from imagery
CT34N = "위성영상(2025-12-22 촬영분)에서 유틸리티동 옥상에 원형 팬이 줄지어 있고 수증기 기둥이 올라오는 구역. 냉각탑으로 추정. 열의 평면 범위는 판독(약 0.5 m/px), 팬은 약 13 m 간격으로 배치한 근사이며 실제 개수·제조사·용량은 확인하지 못함. 높이는 임의"
BL34N = "위성영상(2025-12-22 촬영분)에서 유틸리티동 옥상에 청색 상판 모듈이 줄지어 보이는 구역. 평면 범위는 판독, 용도는 확인하지 못함. 높이는 임의"
EN34N = "위성영상(2025-12-22 촬영분)에서 유틸리티동 끝에 따로 보이는 건물. 평면은 판독, 높이·용도는 추정"
for _i, (_x0, _x1, _y0, _y1) in enumerate([(-285, -25, 1215, 1232), (-285, -25, 1190, 1208), (-285, -25, 1132, 1150), (25, 275, 1215, 1232), (25, 275, 1192, 1208)], 1):
    aux(f"CT34-R{_i}", f"P3·P4 사이 유틸리티동 옥상 냉각탑 열 {_i}(추정, 위성 판독)", (_x0, _x1, _y0, _y1), 6, "#8f9aa6", conf="B", src=["ESRI"], note=CT34N, z0=45)
    _n = int((_x1 - _x0) // 13)
    for _k in range(_n):
        _cx = _x0 + 6.5 + _k * 13; _cy = (_y0 + _y1) / 2
        aux(f"CT34-F{_i}-{_k + 1:02d}", f"냉각탑 팬(추정) 열 {_i}-{_k + 1:02d}", (_cx - 5, _cx + 5, _cy - 5, _cy + 5), 3, "#c9d2da", conf="C", src=["ESRI"], note=CT34N, z0=51)
for _i, (_x0, _x1, _y0, _y1) in enumerate([(45, 275, 1165, 1178), (45, 275, 1138, 1150)], 1):
    aux(f"UT34-BL{_i}", f"P3·P4 사이 유틸리티동 옥상 청색 모듈 열 {_i}(용도 미확인, 위성 판독)", (_x0, _x1, _y0, _y1), 4, "#3f6fb5", conf="B", src=["ESRI"], note=BL34N, z0=45)
MKN = "카카오맵 장소 검색에 등록된 지점. 좌표는 표기 지점이며 건물 외곽이 아님. "
for mid, mname, mx, my, mnote, msrc in [
    ("MK-EAC1", "삼성E&A 평택캠프(공사 현장 사무소, 카카오맵 표기)", -1249, 1707, "삼성E&A(옛 삼성엔지니어링)는 공시상 평택에서 그린동·변전소·복합동, 대기방지, UT동, 옥상 배기, UPW 마감공사와 수처리 시설을 맡음", ["KAKAO2", "EA_P4", "P3_UT", "WTR_EA"]),
    ("MK-EAC2", "삼성E&A 평택2캠프(공사 현장 사무소, 카카오맵 표기)", -237, 2550, "삼성E&A(옛 삼성엔지니어링)는 공시상 평택에서 그린동·변전소·복합동, 대기방지, UT동, 옥상 배기, UPW 마감공사와 수처리 시설을 맡음", ["KAKAO2", "EA_P4", "P3_UT", "WTR_EA"]),
    ("MK-SEMES", "세메스 평택사무소(카카오맵 표기)", -702, 2317, "세메스는 삼성전자 자회사인 반도체 장비 회사. 평택 P1의 천장 반송(OHT) 장비가 세메스 제품이라는 것이 공식 영상과 견학 보도로 확인됨. 세정·트랙 등은 업계 대표 공급사로만 표기", ["KAKAO2", "YT", "TOOLS", "TOUR_3F"]),
    ("MK-AFG", "에어퍼스트 평택공장 정문(카카오맵 표기)", -726, -174, "에어퍼스트는 산업용 가스 회사. 보도: 평택캠퍼스 P3·P4에 산소·질소·아르곤·수소를 지하 배관으로 공급", ["KAKAO2", "GAS_AF"]),
    ("MK-WIPS", "원익IPS 평택사업장(카카오맵 표기)", 1625, 588, "원익IPS는 증착 장비 회사(PECVD, ALD, 확산·열처리 장비). 회사 소개: 삼성 등에 공급. 해외판 전자신문(2020): 평택 2라인 10나노급 D램 팹용 장비 수주로 알려짐. 이 사업장에서 무엇을 하는지는 확인하지 못함. 증권사 추정(2025-11): 2025년 상반기 삼성전자향 매출 비중 약 58%, 범용 CVD·ALD 장비가 D램·낸드·파운드리 투자 모두에 쓰임. 본사는 평택 진위산단", ["KAKAO2", "WIPS_CO", "WIPS_ET", "WIPS_MZ"]),
    ("MK-HYE", "한양이엔지(카카오맵 표기)", 1723, 644, "한양이엔지는 배관·케미컬 공급 장치 회사. 공시: P4 1단계 일반배관 4공구(최종 약 1,513억 원), P5 일반배관 1공구(약 1,481억 원) — 삼성물산과 계약. 보도: P4 페이즈3 훅업·CCSS 설치. 기업분석 보고서(2023): 반도체·디스플레이·산업플랜트의 배관 설비와 CCSS(화학물질 중앙공급장치)에 특화된 업체", ["KAKAO2", "HYENG", "HYENG2", "HYENG_IR"]),
    # v7.23: more supplier locations registered on Kakao Map (queried 2026-11-14)
    ("MK-AMAT", "어플라이드 머티어리얼즈코리아(카카오맵 표기)", 1018, 2234, "미국 반도체 장비 회사(증착·식각·CMP·이온주입·계측). 견학 보도에서 P1 장비 공급사로 언급됨. 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2", "TOOLS"]),
    ("MK-KLA", "KLA 평택(카카오맵 표기)", -447, 2628, "미국 반도체 검사·계측 장비 회사. 견학 보도에서 P1 장비 공급사로 언급됨. 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2", "TOOLS"]),
    ("MK-LAM", "램리서치코리아 평택사무실(카카오맵 표기)", -494, 327, "미국 반도체 장비 회사(식각·증착). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-TEL", "도쿄일렉트론코리아 평택사무소(카카오맵 표기)", -561, 2739, "일본 반도체 장비 회사(도포·현상 트랙, 식각, 증착, 세정). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-KCT", "케이씨텍 평택사무소(카카오맵 표기)", -622, 2858, "국내 반도체 장비·소재 회사(CMP 장비, 세정 장비, 슬러리). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-UNI", "유니셈 평택CS센터(카카오맵 표기)", -635, 123, "국내 반도체 부대 장비 회사(가스 스크러버, 칠러). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-PSK", "피에스케이 평택 제조공장(카카오맵 표기)", 937, 2052, "국내 반도체 장비 회사(감광액 제거 드라이 스트립 장비). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-PSKH", "피에스케이홀딩스 평택제조공장(카카오맵 표기)", 946, 2302, "국내 반도체 후공정 장비 회사(디스컴, 리플로우). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-STI", "에스티아이 평택사무소(카카오맵 표기)", 451, 231, "국내 케미컬 중앙 공급 장치(CCSS)·세정 장비 회사. 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-HSC", "한성크린텍(카카오맵 표기)", 464, -123, "국내 초순수·수처리 설비 시공 회사. 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-MERCK", "머크(카카오맵 표기)", 1871, 1652, "독일 머크의 전자재료 사업장(반도체용 소재·특수가스). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-VSM", "버슘머트리얼즈에스피씨코리아(카카오맵 표기)", 1800, 1680, "반도체용 특수가스·소재 회사(버슘머트리얼즈는 2019년 머크에 인수됨). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-FST", "에프에스티 평택사업장(카카오맵 표기)", -891, 2161, "국내 반도체 부품·장비 회사(펠리클, 칠러). 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-WIPS2", "원익아이피에스(모곡동)(카카오맵 표기)", 1001, 1200, "증착 장비 회사 원익IPS의 또 다른 등록 지점. 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2", "WIPS_CO"]),
    ("MK-KCENC", "케이씨이앤씨(카카오맵 표기)", -811, 151, "국내 가스·케미컬 공급 설비 시공 회사. 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2"]),
    ("MK-CNTC", "삼성물산 평택캠프(공사 현장 사무소)(카카오맵 표기)", -1246, 1641, "삼성물산 건설부문은 공시상 평택 팹의 골조와 FAB동·복합동 마감공사를 맡음. 역할은 회사가 공개한 주력 사업 기준의 일반 설명이며 이 프로젝트에서 개별 문서로 대조하지 않음. 이 지점에서 하는 일과 평택캠퍼스 납품 내역은 확인하지 못함", ["KAKAO2", "P4_4FAC"]),
]:
    add(mid, mname, "지도 표기 지점", [mx - 7, my - 7, 0.0, mx + 7, my + 7, 1.2], "#ffd21f", "M", msrc, MKN + mnote)
add("GROUND", "주변 지반", "지반", [-1950, -650, -2.0, 1950, 2900, -1.0], "#2a3138", "C", ["ESRI"], "평탄 단순화")
add("PAD-1", "평택캠퍼스 1단지 부지(개략)", "지반", [-720, 690, -1.0, 700, 2330, -0.2], "#3a434c", "C", ["ESRI", "SITE_AREA"], "부지 경계는 개략. 캠퍼스 총 부지 약 289만㎡(보도)")
add("PAD-P5", "P5 건설 부지(2단지, 공사 중)", "지반", [-1560, 880, -1.0, -800, 1620, -0.2], "#5a4b3a", "C", ["ESRI", "P5", "P5_HK", "GG_2026_189"],
    "2025-12 위성영상에서 기초공사 확인. 보도: P5는 약 650 m × 195 m, 3개 층 6개 클린룸. 범위는 개략. 상충 보도(한국일보 2026-10-30, 현장 르포): 팹1 바닥은 남북 211 m × 동서 638 m, 트리플 팹, 완공 시 높이 약 100 m, 연면적 145만㎡, 2028년 가동 목표. 두 보도의 치수가 달라 모델은 부지 범위만 개략으로 그리고 건물 형상은 넣지 않음. 경기도 고시 제2026-189호(2026-07-30, 산업단지계획 변경 승인)에서 A1-1 구역의 기준용적률은 350% 이하로 변경이 없음(Astra가 고시문 26쪽을 대조). 490% 상향을 승인한 고시는 확인되지 않아, 트리플 팹과 클린룸 6개는 보도상 계획으로만 표기하고 승인된 구조로 쓰지 않음")

SOURCES = {
 "ESRI": ("Esri World Imagery (Vantor/WorldView-2, 촬영 2025-12-22, 0.5 m) — 평면 치수 실측", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer"),
 "OSM": ("OpenStreetMap 건물 폴리곤(ODbL) — 교차 확인용", "https://www.openstreetmap.org/#map=16/37.0350/127.0600"),
 "YT": ("삼성전자 반도체 뉴스룸 공식 영상 '삼성전자 평택캠퍼스' — 외관·지붕·클린룸(포토 베이)·SEMES OHT", "https://www.youtube.com/watch?v=6if4eP8fn_U"),
 "YT_RE": ("평택 부동산 채널(이지티비) 드론 사진 — 서쪽에서 본 P1~P4·V2·신축 사무동 현장", "https://www.youtube.com/watch?v=2OaCpiqyLGE"),
 "P1_DIM": ("ZDNet Korea 2022-08-25: 생산라인 길이 518 m·폭 201 m·높이 83 m / 이투데이: P1 길이 520 m·폭 200 m", "https://zdnet.co.kr/view/?no=20220825080050"),
 "PRESS_TOUR": ("이투데이 2022-09 르포: 사무동·생산동 분리, 오버 브리지", "https://www.etoday.co.kr/news/view/2171028"),
 "OFFICE": ("헬로티 2021-09: 사무1동(9층, P1 담당)·사무2동(11층, P2 담당), 통합사무동 계획", "https://www.hellot.net/news/article.html?no=62184"),
 "P2_FLOORS": ("한방유비스 감리 실적: 평택 P2 B1F~8F, 연면적 592,077㎡", "https://kfubis.co.kr/board/af_supervision/46"),
 "P2_400": ("전자신문 2020-06: 'P2 길이 400 m대, P3 700 m'", "https://m.etnews.com/20200619000158"),
 "P2_UT": ("삼성E&A 프로젝트 소개: 평택 고덕 P2 UT동", "https://www.samsungena.com/kr/business/project-template?idx=73"),
 "P3_DIM": ("디일렉 2022-09: P3 건축허가면적 70만㎡·길이 700 m / 전자신문: 면적 99.1만㎡", "https://www.thelec.kr/news/articleView.html?idxno=17958"),
 "P3_UT": ("딜사이트: 삼성엔지니어링 P3 그린동·UT동·옥상배기·UPW 담당", "https://dealsite.co.kr/articles/114320"),
 "PHASE": ("페이즈 위치(공시 공사명): P3L Ph2 상층서편·Ph3 하층동편·Ph4 상층동편(삼성중공업) / P3 Ph4 상부동편, P4 Ph1 하서(삼성물산) / P4 Ph3 상서(삼성물산) / P4 상동 Ph4·하동 Ph2(보도)", "https://www.koreaittimes.com/news/articleView.html?idxno=117613"),
 "P4_PH": ("이데일리 2025-09: P4는 4개 Ph, Ph1 낸드·D램 하이브리드 / 딜사이트: Ph3 '300 m 규모 클린룸'", "https://v.daum.net/v/20250929151553763"),
 "P4_SITE": ("블로터 2023-06: P4 복합동·팹·변전소·그린동, 시공 삼성물산·설계 삼우", "https://www.bloter.net/news/articleView.html?idxno=603212"),
 "CR4": ("Cleanroom Technology / BusinessKorea: P1~P4는 2개 층·4개 클린룸, P5는 3개 층·6개", "https://cleanroomtechnology.com/samsung-speeds-up-construction-of-p5-cleanroom-for"),
 "TOUR_3F": ("뉴시스 2022-09: P1 3층 시창 투어, OHT 1,850여 대", "https://mobile.newsis.com/view.html?ar_id=NISX20220907_0002006194"),
 "TOOLS": ("시사저널e 2022-09: P1 OHT 약 1,850대·설비 2,000여 대 / 디지털데일리: SEMES OHT, AMAT·KLA 장비", "https://www.sisajournal-e.com/news/articleView.html?idxno=289581"),
 "V2": ("SemiWiki 포럼(Scotten Jones): P1~P3 2개 층 클린룸, V2(EUV 2개 층) 연결", "https://semiwiki.com/forum/threads/nand-flash-fab-shell-designs.17710/"),
 "V2L": ("한국경제 2022-03 수주공시: '평택 V2L 상층Ph3/하층 FAB동 마감공사'(삼성물산)", "https://www.hankyung.com/article/202203249155L"),
 "P5": ("TechTimes 2026-09: P5 650 m × 195 m, 3개 층 6개 클린룸, 한양이엔지 배관 계약", "https://www.techtimes.com/articles/326838/20260907/samsung-p5-cleanroom-piping-starts-contract-confirms-phase-one-under-active-construction.htm"),
 "SITE_AREA": ("삼성 반도체 뉴스룸: 단일 팹 건축면적 약 12만㎡·연면적 약 99만㎡, 캠퍼스 약 289만㎡", "https://news.samsungsemiconductor.com/global/a-scale-beyond-imagination-inside-samsungs-massive-semiconductor-fabs/"),
 "KCC": ("KCC 웹진: 평택캠퍼스 사무3동(지상 9층, P3·P4와 연결), 사무2동·상생협력동·기술2동", "https://webzine.kccworld.co.kr/synergy/the-built/"),
 "NAMU": ("나무위키 '고덕국제신도시': 그린동·복합동·154kV·사무동, 북측 서포트/FAB동/남측 서포트 (비공식·신뢰도 낮음)", "https://namu.wiki/w/%EA%B3%A0%EB%8D%95%EA%B5%AD%EC%A0%9C%EC%8B%A0%EB%8F%84%EC%8B%9C"),
 "CSF_FSF": ("한국산업보건학회지(KoreaScience) 2015: 300mm 라인은 FAB + CSF + FSF 3층 구조, 스크러버·펌프·칠러는 FSF", "https://www.koreascience.or.kr/article/JAKO201524848647870.pdf"),
 "SMOCK": ("반도체 입문 강의 요약: CSF에 제너레이터·가스 캐비닛, FSF에 펌프·스크러버, 스막룸·에어샤워·FFU", "https://winspec.co.kr/community/study-log/129513752"),
 "SKECO": ("SK에코플랜트 뉴스룸: FAB 단면(위 공급층·가운데 클린룸·아래 회수·배관층·양옆 장비 반입 공간)", "https://news.skecoplant.com/board/19231"),
 "DCC": ("산업의역군 공사DB 소개 글: 평택 P4 'Ph4 DCC 1공구', 'Ph4 S-GAS 1공구' 공사명", "https://www.sankun.com/blog/detail/1306_%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90_%ED%8F%89%ED%83%9D_P5_%EA%B3%B5%EC%82%AC_%EC%9E%AC%EA%B0%9C_%EC%86%8C%EC%8B%9D__%EC%8B%9C%EA%B3%B5%EC%82%AC__%ED%98%84%EC%9E%A5%EC%A0%95%EB%B3%B4__%EC%B0%A9%EA%B3%B5%ED%98%84%ED%99%A9_%EC%95%8C%EC%95%84%EB%B3%B4%EA%B8%B0"),
 "EUV": ("Laser Focus World: EUV 장비(NXE:3400B) 약 180 t·1 MW 이상 / ASML 공개 발표: 서브팹 풋프린트", "https://www.laserfocusworld.com/blogs/article/14039015/how-does-the-laser-technology-in-euv-lithography-work"),
 "LAYOUT": ("Semiconductor Digest: 300mm 팹은 중앙 스파인(인터베이 AMHS)과 베이, 베이 끝 스토커", "https://sst.semiconductor-digest.com/?p=43610"),
 "AMHS_H": ("'From 200 to 300 mm fabs' 발표자료: 클린룸 천장고·OHT 높이·액세스 플로어 치수", "https://www.slideshare.net/slideshow/from-200-to-300-mm-fabs-presentation/806908"),
 "FFU_SRC": ("뉴스프라임 2023-07: 신성이엔지, 평택 P1~4 클린룸 장비 공급 / 페로타임즈: 삼성물산과 평택 클린룸 천정 공사 계약", "https://www.newsprime.co.kr/news/article/?no=605356"),
 "CR_AREA": ("신성이엔지 기업브리프(2023-07, 증권사): 평택 클린룸 면적 P1 약 135,300㎡·P2 약 148,500㎡·P3·P4 약 181,500㎡", "https://ssl.pstatic.net/imgstock/upload/research/company/1689724899976.pdf"),
 "STI": ("데일리인베스트 2023-08: 에스티아이 CCSS, 평택 3기 Ph3·Ph4 및 4기 Ph1·Ph2 공급(증권사 인용)", "http://www.dailyinvest.kr/news/articleView.html?idxno=53701"),
 "SEBO": ("세보엠이씨 2026-09 공시 요약: 삼성물산과 평택 설비공사 계약", "https://www.chickstockfi.com/disclosures/20260904900182"),
 "LAW34": ("건축법 시행령 제34조: 직통계단까지 보행거리 30 m, 내화구조 50 m, 자동화 생산시설+자동식 소화설비 공장 75 m(무인화 공장 100 m)", "https://www.law.go.kr/법령/건축법시행령/제34조"),
 "IBC_H5": ("ICC/Koffel H-5 Timed Egress Study(2021): IBC Table 1017.2의 H-5 보행거리 200 ft(61 m), 300 ft 상향 제안", "https://www.iccsafe.org/wp-content/uploads/E86-21-Koffel-RPT_Generic-H5-Timed-Egress-Study_Final.pdf"),
 "NFPA318": ("NFPA 318 개정 제안문(CI-21, 2022): 클린 서브팹·퍼실리티 서브팹 정의, 대형 팹 보행거리 295 ft(90 m) 제안", "https://docinfofiles.nfpa.org/files/AboutTheCodes/318/318_A2024_SCR_AAA_FD_CIReport.pdf"),
 "GEN": ("Construction Physics: 일반적 팹 단면(서브팹 2개 층 + 클린룸 + 팬·필터 층)", "https://www.construction-physics.com/p/how-to-build-a-20-billion-semiconductor"),
}

SOURCES.update(utility.USRC)
SOURCES["LIFTER"] = ("미국 특허 출원 US 2013/0230375: 팹의 층간 반송 — 리프팅 타워가 층 사이에서 웨이퍼 용기를 올리고 내림, OHT 대차 리프터", "https://patents.google.com/patent/US20130230375")
SOURCES["LOADPORT"] = ("미국 특허 US 7,100,340: 300mm EFEM은 SEMI E15.1 로드 포트 2~4개, 로드 포트 폭 약 505 mm·높이 1,386 mm까지", "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7100340")
SOURCES["Z358"] = ("Lab Manager: ANSI/ISEA Z358.1 — 비상 샤워·세안 설비는 위험원에서 10초 이내(통상 약 55 ft), 같은 층·장애물 없는 경로", "https://www.labmanager.com/a-guide-to-safety-showers-eye-washes-20580")
SOURCES["KAKAO"] = ("카카오맵 장소 검색(2026-11 조회): 사무1·2·3동, 사무복합동, 기술동 주차타워, 자재1동, 복지동, 방제센터, 게이트, 가스 3사 평택공장의 표기 위치", "https://map.kakao.com/")
SOURCES["YT_DRONE"] = ("삼성전자 반도체 공식 유튜브 2021-08 드론 영상(평택 포함 5개 캠퍼스) — 외관·몬드리안 패널·주변 배치 확인", "https://www.youtube.com/watch?v=IUO-qeB_Pa4")

SOURCES["P4_4FAC"] = ("대한경제 2021-12: P4 PC 발주 — FAB동·복합동(생산지원, 삼성물산) + 변전소·그린동(폐수처리, 삼성엔지니어링) 4개 시설", "https://m.dnews.co.kr/m_home/view.jsp?idxno=202112142259545330101")
SOURCES["EA_P4"] = ("삼성엔지니어링(삼성E&A) 공시 보도: P4 Ph1·Ph2(하동)·Ph3(상서) '그린동, 변전소 및 복합동, 대기방지, UPW 마감공사'", "https://www.businesspost.co.kr/BP?command=article_view&num=357012")
SOURCES["EA_P4B"] = ("포쓰저널 2022-12: 삼성엔지니어링 P4 Ph1 7,938억 원 수주 공시", "https://www.4th.kr/news/articleView.html?idxno=2031078")
SOURCES["EA_P4C"] = ("한국경제 2023-12: 삼성엔지니어링 평택 P4 Ph2 1조 1,000억 원 공시", "https://www.hankyung.com/article/2023121463256")
SOURCES["CT_P4PH4"] = ("포쓰저널 2025-07: 삼성물산 P4 페이즈4(상동) 약 1조 4,630억 원 공시", "https://www.4th.kr/news/articleView.html?idxno=2090886")
SOURCES["EA_P3"] = ("한국경제 2022-11: 삼성엔지니어링 [P3 Ph4] 그린동 및 UT동, 옥상배기, UPW 마감 공사 5,500억 원 공시", "https://www.hankyung.com/article/202211241150L")
SOURCES["HSCT"] = ("뉴스토마토 2025-11: 한성크린텍 — 초순수 설비가 구축되는 복합동 공사(약 112억 원), P4 그린동 내 기계·배관 설치(약 68억 원)", "https://www.newstomato.com/ReadNews.aspx?no=1280628")
SOURCES["OFFICE"] = ("인베스트조선 2024-02: 사무1동 지상 9층(P1), 사무2동 지상 11층(P2), 사무3동은 P3 서쪽, 사무6동은 P6 북쪽", "https://www.investchosun.com/site/data/html_dir/2024/02/01/2024020180225.html")
SOURCES["CT_P4PH1"] = ("스마트투데이 2023-02: 삼성물산 P4 Ph1(하서) 1조 7,600억 원, P3 Ph4(상부동편) 1조 2,650억 원 FAB동/복합동 마감공사 공시", "https://www.smarttoday.co.kr/ko-kr/articles/27502")
SOURCES["CT_P4PH3"] = ("비즈니스포스트 2024-06: 삼성물산 P4 Ph3(상서) FAB동, 복합동 마감공사 1조 8,656억 원 공시", "https://www.businesspost.co.kr/BP?command=article_view&num=355599")
SOURCES["SHI_P4PH4"] = ("디지털투데이 2025-07: 삼성중공업 P4 Ph4(상동) 마감공사 약 3,926억 원 공시", "https://www.digitaltoday.co.kr/news/articleView.html?idxno=578667")
SOURCES["HYENG"] = ("이포커스 2026-09: 한양이엔지 P4 1단계 일반배관 4공구(1,067억→1,513억 원), P5 일반배관 1공구 1,481억 원 — 삼성물산과 계약", "https://www.e-focus.co.kr/news/articleView.html?idxno=3002831")
SOURCES["HYENG2"] = ("시사저널e 2026-05: 한양이엔지 P4 페이즈3 훅업·CCSS 설치, 신성이엔지 클린환경 수주", "https://www.sisajournal-e.com/news/articleView.html?idxno=420948")
SOURCES["SSENG"] = ("페로타임즈 2021: 신성이엔지 — 삼성물산과 평택공장 클린룸 시스템 천정 공사 약 276억 원 계약", "https://www.ferrotimes.com/news/articleView.html?idxno=19432")
SOURCES["PWR_GD3B"] = ("평택시민신문 2024-08: 345 kV 고덕3 변전소 — 고덕국제화계획지구 내 변전소 부지, 2031-09 완공 목표, 송전선로 지중화", "https://www.pttimes.com/news/articleView.html?idxno=72936")
SOURCES["GREEN21"] = ("이투데이 2021-03: 평택캠퍼스 그린동 첫 공개 — 지하 수처리 시설 약 3만 4천㎡, 하루 약 7만 t, 스크린도어, CCR, 자동화율 97%", "https://www.etoday.co.kr/news/view/2006423")
SOURCES["GREEN21B"] = ("한국경제 2021-03: 그린동 — 폐수 6가지 구분, 활성탄 필터링, 복합 유기탄소원", "https://www.hankyung.com/article/202103216018Y")
SOURCES["EA_P2WT"] = ("삼성E&A 프로젝트 소개: 평택 P2 Phase 1 수처리 — 폐수처리 86,000 m³/d, 대기오염방지시설·정수장·초순수·폐수처리·재이용 시설", "https://samsungena.com/kr/business/project-template?idx=80")
SOURCES["EA_P3PH3"] = ("이데일리 2022-06: 삼성엔지니어링 [P3 Ph3 PJT] 그린동 및 UT동, 옥상배기, UPW 마감 공사 6,600억 원", "https://edaily.co.kr/News/Read?mediaCodeNo=257&newsId=02974966632364344")
SOURCES["EA_P1GR"] = ("이투데이 2015-12: 삼성엔지니어링 평택 P-PJT 그린동 1기 공사 2,387억 원", "https://www.etoday.co.kr/news/view/1260134")
SOURCES["AREA"] = ("ZDNet Korea 2022-09: 평택 1라인 연면적 24만 평, 2라인 25만 평, 3라인 100만㎡(약 30만 평), 부지 289만㎡", "https://zdnet.co.kr/view/?no=20220907135616")
SOURCES["OFF_SE_P2"] = ("삼성전자 뉴스룸 2020-08: 평택 2라인 가동 — 연면적 12만 8,900㎡, 부지 289만㎡", "https://news.samsung.com/kr/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%EC%84%B8%EA%B3%84-%EC%B5%9C%EB%8C%80%EA%B7%9C%EB%AA%A8-%ED%8F%89%ED%83%9D-2%EB%9D%BC%EC%9D%B8-%EA%B0%80%EB%8F%99")
SOURCES["OFF_CT_PJT"] = ("삼성물산 건설부문 포트폴리오: 평택 단지(평택 P-PJT) — 연면적 3,967,000㎡", "https://www.secc.co.kr/ko/business/portfolio/building/7")
SOURCES["OFF_EA_P2EN"] = ("Samsung E&A: Pyeongtaek P2 Utility Project — gross area 128,999㎡, UT and CT buildings", "https://www.samsungena.com/en/business/project-template?idx=73")
SOURCES["OFF_SE_SITE"] = ("삼성전자 반도체 뉴스룸 2026-06: 평택캠퍼스 총 283만㎡(약 86만 평)", "https://news.samsungsemiconductor.com/kr/tag/%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90-%ED%8F%89%ED%83%9D%EC%BA%A0%ED%8D%BC%EC%8A%A4/")
SOURCES["OFF_EA_SR21"] = ("삼성엔지니어링 지속가능경영보고서 2021: P3 그린동 프로젝트 — 고덕사업장 폐수 처리 시설 총 용량 81,600 m³", "https://www.samsungena.com/resources/kr/file/2021_Samsung_Engineering_Sustainability_Report_Kr.pdf")
SOURCES["OFF_CT_SMART"] = ("삼성물산 건설부문 스마트기술: Access Floor Grating 시공 로봇(평택 P3 PH2·PH3), 건설용 앵커 로봇(평택 P3 복합동), 스마트 드릴링 로봇(평택 P3 PH1·PH4)", "https://www.secc.co.kr/ko/library/tech/smart")
SOURCES["OFF_CT_STRUCT"] = ("삼성물산 건설부문 보유 기술: 미진동 제어 구조설계 — PC 격자보 최적화(하이테크 FAB 골조)", "https://www.secc.co.kr/ko/library/tech/building-structure")
SOURCES["OFF_CT_P3PH1"] = ("Samsung C&T IR: Pyeongtaek P3-PJT FAB Building Lower West (Ph1) Finishing Work — KRW 1,815 billion", "https://www.samsungcnt.com/eng/ir/disclosure/view.do?seq=520")
SOURCES["SR2026"] = ("삼성전자 지속가능경영보고서 2026: 기흥·화성·평택 폐열 사용률 51%→55%, 평택은 인근 소각장 폐열 등 외부 열에너지 활용 계획, 국내 5개 사업장 태양광 누적 7.6 MW, 하수 재이용 2030년 도입 계획, RCS 전사 55대", "https://www.samsung.com/sec/sustainability/media/pdf/Samsung_Electronics_Sustainability_Report_2026_KOR.pdf")
SOURCES["BLDG_REG"] = ("국토교통부 건축HUB 건축물대장(공공데이터포털, 2026-11-12 조회): 평택시 고덕동 1730(고덕변환소·변전소), 1722(린데코리아 평택공장), 1721(하수등처리시설)", "https://www.data.go.kr/")
SOURCES["WW_PATH_B"] = ("이투데이 2026-10: 그린동 → 고덕 공공폐수처리시설 → 서정리천", "https://www.etoday.co.kr/news/view/2632115")
SOURCES["GAS_LINDE_B"] = ("카카오맵 장소 검색: 린데코리아 평택공장, 평택고덕공공폐수처리시설, 삼성전자 평택캠퍼스 사무2동·사무3동·사무복합동 주차타워·기술동 입구", "https://map.kakao.com/")
SOURCES["DISINF"] = ("전국 소독 의무 대상 시설 지도(공공데이터 기반): 삼성전자(주) 평택캠퍼스 기술동 1층, 기술2동 지하 1층~3층", "https://dfi.purpleo.co.kr/view/7511")
SOURCES["ILSUNG"] = ("뉴시스 2026-07: 일성건설 — 평택2단지 부대동 그룹2 건축 및 통신공사 451억 원, 3개동 연면적 2,774평(자원순환센터·유수분리기·방재센터), 2027-10-31까지", "https://news.nate.com/view/20260706n26076")
SOURCES["GOOGLE"] = ("구글 지도 장소 검색(2026-11-12): 삼성전자 평택캠퍼스 기술동, 사무복합동, GATE2, Gate3 좌표", "https://www.google.com/maps")
SOURCES["YT_DAL1"] = ("유튜브 '달팽이의 반도체 현장' — P4 Ph2 공시 화면, P4 클린룸 구획 주석 사진, Ph3 일정표(비공식 현장 관찰 채널)", "https://www.youtube.com/watch?v=tAFdsr6iP94")
SOURCES["YT_DAL2"] = ("유튜브 '달팽이의 반도체 현장' — P5 착공·그린동·154동·P4 Ph2/Ph4: 남쪽 드론 주석 사진(한전변전소 증설, 복합동, 154동(변전소), 옥상 대기방지 시설), 턴오버 일정표(비공식)", "https://www.youtube.com/watch?v=IDYu0nR1TxI")
SOURCES["MOVEIN_COMM"] = ("알바몬 커뮤니티 글(평택 P3 현장 종사자 서술: 2층 이상 장비는 기중기로 반입구 반입, 외벽 호이스트) — 비공식·신뢰도 낮음", "https://community.albamon.com/post/detail/911656")
META = dict(
    title="Samsung Pyeongtaek Campus P1–P4 open model", version="7",
    origin=dict(lat=37.02, lon=127.06, note="local tangent plane, X east / Y north / Z up, metres"),
    imagery_date="2025-12-22",
    floor_area=dict(rule="면적 수치는 삼성전자·삼성물산·삼성E&A·삼성중공업의 공식 자료를 우선하고, 보도 수치는 참고로만 둔다",
        official={"캠퍼스 부지": "289만㎡(삼성전자 뉴스룸 2015·2020) / 283만㎡(삼성전자 뉴스룸 2014, 반도체 뉴스룸 2026-06)",
                  "평택 단지 전체 연면적": "3,967,000㎡(삼성물산 건설부문 포트폴리오 '평택 단지(평택 P-PJT)')",
                  "P2": "연면적 12만 8,900㎡(삼성전자 뉴스룸 2020-08, 삼성E&A 프로젝트 소개 국문. 삼성E&A 영문 페이지는 128,999㎡)",
                  "P1·P3·P4": "네 회사 공식 자료에서 동별 면적을 찾지 못함",
                  "P3 그린동": "폐수 처리 시설 총 용량 81,600 m³/d(삼성엔지니어링 지속가능경영보고서 2021, 보고서 본문에서 단위 확인. 면적·층수는 기재 없음)"},
        verified="2026-11-12 직접 열람: 삼성물산 건설부문 포트폴리오에는 단지 전체 연면적만 있고 층수·공사기간·동별 면적은 없음. 삼성엔지니어링 2021 보고서에는 P3 그린동 용량만 있고 면적 수치는 없음(문서 앞 약 3분의 2 범위 열람)",
        gov_register="건축물대장(국토교통부)으로 확인한 인접 시설: 고덕변환소·변전소(고덕동 1730) 대지 102,076㎡·연면적 48,546.62㎡, 린데코리아 평택공장(고덕동 1722) 대지 78,833.4㎡·건축면적 27,316.3㎡·연면적 22,665.15㎡·6동·사용승인 2023-04-27, 하수등처리시설(고덕동 1721, 삼성1로 60) 대지 150,297.2㎡·건축면적 8,429.26㎡·연면적 21,840.49㎡·사용승인 2022-07-15. 삼성전자 평택캠퍼스는 고덕동 1695번지(외 37필지, 도로명주소 안내 사이트로 지번 확인)",
        gov_register_campus="건축물대장 표제부(고덕동 1695)에 공개된 동은 2건뿐: (1) 기술동-2 — 삼성로 114, 건축면적 6,412.72㎡, 연면적 51,410.10㎡, 높이 67.90 m, 지상 11층·지하 1층, 철골철근콘크리트구조, 승강기 16대, 허가 2015-02-27, 사용승인 2026-09-21 (2) 북문동 — 삼성1로 457, 건축면적 572.85㎡, 연면적 934.22㎡, 높이 10.32 m, 지상 2층, 사용승인 2026-04-27. 대지면적 1,833,839.5㎡. 주차(대장 기재): 옥내 자주식 약 4,000대·128,907㎡, 옥외 자주식 약 6,437대·172,590㎡. FAB동·복합동·그린동 등 생산 시설은 이 공개 조회 결과에 없음. 건축인허가 동별개요는 316건이나 조회한 100건은 모두 가설건축물(컨테이너 등)이었음. 기술동-2가 모델의 어느 박스인지는 확정하지 못함. 위성영상 재판독(v7.13) 결과 기술동 본체는 약 81 × 42 m(약 3,400㎡)로 대장의 기술동-2 건축면적의 절반 수준이라 같은 건물로 보기 어려움. 공공데이터(소독 의무 대상 시설)에 '기술동'과 '기술2동(지하 1층~3층 식당)'이 따로 있고, 카카오맵 '기술동 입구'는 P1 북서쪽 (-387, 2472).  카카오맵 '사무2동' 좌표는 사무2동 박스 안에 있어 사무2동과 기술동-2는 다른 건물로 판단",
        gov_register_parcels="고덕동 지번별 대장 조회 결과: 1695(캠퍼스 본 필지) 2동 공개, 1696(2단지) 주차동 1동 공개, 1697·1698·1699·1725·1727·1728 결과 없음. 사무1동·사무2동·사무3동·사무복합동·복지동과 FAB동은 공개 조회 결과에 없음",
        map_crosscheck="구글 지도와 카카오맵 비교(2026-11-12): 사무복합동·GATE2·GATE3는 15 m 안에서 일치. GATE5는 카카오맵 (494, 828)과 구글 (306, 686)이 약 235 m 달라 두 지점을 모두 표지로 둠(어느 쪽이 맞는지 미확인). 구글에만 있는 장소: 기술동, P2 주차타워·야외주차장(고덕동 1696). 공공데이터(소독 의무 대상 시설): T1카페테리아 = 기술동 1층, T2카페테리아 = 기술2동 지하 1층~3층 — 기술동과 기술2동은 서로 인접한 별개 건물로 등록. 네이버 지도는 접속 차단으로 확인하지 못함",
        planned="공시(2026-07): 평택2단지 부대동 그룹2 — 자원순환센터·유수분리기·방재센터 3개동, 연면적 2,774평, 2027-10-31까지. 위치를 알 수 없어 모델에 넣지 않음",
        verified2="2026-11-12 추가 열람: 삼성전자 지속가능경영보고서 2026(전문) — 사업장별 부지·건물 면적 표 없음, 평택 단독 수치 없음(국내 5개 사업장 합계만). 삼성E&A P1 Utility Project 페이지 — 제목과 연도(2018)만 있음. 삼성물산 분기보고서 PDF — 본문을 읽지 못함(바이너리로 반환)",
        reference_press={"P1": "약 24만 평", "P2": "약 25만 평, 감리사 공개 592,077㎡(지하 1층~지상 8층)", "P3": "약 100만㎡"},
        check="P2 공식값 12만 8,900㎡ ÷ 모델 평면(552 × 204 m = 약 11만 2,600㎡) = 1.14. 공식 표현은 '연면적'이지만 8개 층 바닥면적 합(감리사 59만㎡)보다 훨씬 작아 한 층 평면에 가까운 값. 모델 평면이 약 13% 작거나 공식값에 부속 부분이 포함됐을 수 있음(미확인)"),
    p4_phases=dict(src="YT_DAL1·YT_DAL2 (비공식 현장 관찰 채널의 주석·일정표, 공시 화면 포함)", quadrants={"상층 서측": "Ph3 — 공시 'P4 페이즈3(상서)', '평택 4기 상층서편' (A)", "상층 동측": "Ph4 — 공시 'P4 페이즈4(상동)': 삼성물산 약 1조 4,630억 원·삼성E&A 약 9,096억 원, 2027-07-31까지 (A)", "하층 동측": "Ph2 — 공시 'P4 Ph2(하동)', 계약기간 2023-07-15~2027-12-31로 정정(2026-08) (A)", "하층 서측": "Ph1 — 삼성물산 공시 'P4 Ph1(하서) FAB동/복합동 마감공사' 약 1조 7,600억 원 (A). 채널 주석은 P4F→P4H로 표기(비공식)"},
        scope="삼성E&A 공시 공사명: P4 = 그린동, 변전소 및 복합동, 대기방지, UPW 마감공사 / P3 = 그린동, UT동, 옥상배기, UPW 마감 공사",
        ph2_filing="공시 화면: [P4 Ph2(하동)] FAB동/복합동 마감공사, 1조 3,791.7억 원, 2023-07-15~",
        filings_latest="삼성물산 단일판매·공급계약 공시의 최신 정정본(2026-11-14 Codex·Astra가 DART 원문을 대조, 이 모델 작성 과정에서는 원문을 직접 열지 못함): Ph1 하층서편 2023-03-01~2025-12-31, 2조 9,635.1억 원(부가세 포함) / Ph2 하층동편 2023-07-15~2027-12-31, 1조 6,997.1억 원(부가세 제외) / Ph3 상층서편 2024-06-17~2026-03-31, 2조 3,343.65억 원(부가세 포함) / Ph4 상층동편 2025-07-18~2027-04-30, 2조 6,301.55억 원(부가세 포함). 기간은 공시상 마감공사 공사기간이며 실제 착공·준공·가동일이 아님. 하층·상층은 수직 구분, 동·서는 방위이며 평면 사분면이 아님. 위 표의 금액은 최초 공시 시점 값이라 정정 전 수치임. 금액은 형상 근거로 쓰지 않음",
        turnover="채널 일정표(계획 일정이며 실적 여부는 확인하지 못함): Ph4 FFU T/O 2026-08-01 · GCS T/O 2026-09-30, Ph2 AFC 2026-03-15 · FFU T/O 2026-12-15 · GCS T/O 2027-01-30. 공사 순서는 AFC(시공도면 승인) → FFU 턴오버 → GCS(가스 공급) 턴오버"),
    disclaimer="공개된 자료만으로 제작. 내부 층 구성·장비 배치는 개념도이며 실제 삼성전자 설비 배치가 아님.",
    grades={"A": "공식·보도·공시 확인", "B": "공개 위성영상 기반 치수 추정(해상도 0.5 m, 오차 수 m)", "M": "공개 지도 표기 확인(카카오맵·OSM — 좌표는 입구·대표 지점일 수 있음)", "C": "추정·가정", "D": "일반 개념(현장 고유 정보 아님)"},
)

# ---------------------------------------------------------------- products by line (official material and press only)
SOURCES["PROD_P1"] = ("디지털데일리 2022-09-07: P1 시창 투어 — 첨단 D램·낸드 제작, P2에 파운드리 라인 포함, P3는 낸드부터 투입", "https://www.ddaily.co.kr/page/view/2022090716533610184")
SOURCES["PROD_P1N"] = ("DIGITIMES 2025-11-24: 평택 P1·화성은 낸드·D램 혼합 라인, 낸드 일부를 D램으로 전환 검토", "https://apps.digitimes.com/news/a20251124PD215.html")
SOURCES["PROD_P2F"] = ("삼성전자 뉴스룸 2020-05-21: 평택에 EUV 파운드리 생산라인 구축", "https://news.samsung.com/kr/%ec%82%bc%ec%84%b1%ec%a0%84%ec%9e%90-%ed%8f%89%ed%83%9d%ec%97%90-euv-%ed%8c%8c%ec%9a%b4%eb%93%9c%eb%a6%ac-%ec%83%9d%ec%82%b0%eb%9d%bc%ec%9d%b8-%ea%b5%ac%ec%b6%95")
SOURCES["PROD_P3"] = ("디지털데일리 2022-09-08: P3 낸드 양산 시설, 2022-07 웨이퍼 투입, 이후 D램·파운드리 순차", "https://www.ddaily.co.kr/page/view/2022090718280766169")
SOURCES["PROD_FDRY"] = ("파이낸셜뉴스 2026-03-02: 평택 P2·P3에 4·5·7나노 파운드리 라인 가동", "https://www.fnnews.com/news/202603020606549650")
SOURCES["PROD_P4A"] = ("디지털데일리 2026-02-24: P4는 4개 페이즈 — Ph1 낸드·D램 복합, Ph3 D램 전용, Ph4·Ph2 D램", "https://m.ddaily.co.kr/page/view/2026022415344369085")
SOURCES["PROD_P4B"] = ("딜사이트: P4 PH1은 낸드·1c D램 절반씩, PH3는 1c D램 전용, PH2는 하이브리드 계획에서 1c D램으로 전환, PH4는 1c D램", "https://dealsite.co.kr/articles/154190")
SOURCES["PROD_P4C"] = ("딜사이트: P4 PH1은 낸드 절반·1a D램 절반의 하이브리드로 설계 변경, PH3의 300 m 클린룸을 두세 칸으로 나누는 방안 논의", "https://dealsite.co.kr/articles/139534")
SOURCES["PROD_P4D"] = ("다음 뉴스 게재 단독 기사 2025-12-11: P4 Ph2를 HBM4용 1c D램 라인으로 운용 결정, 본공사 2026년 2분기·가동 준비 2027년 상반기 목표", "https://v.daum.net/v/20251211104113749")
SOURCES["PROD_BR"] = ("딜사이트: P4 PH2와 파운드리 라인인 P3 PH2를 잇는 브리지 설치, OHT 설치 추정", "https://dealsite.co.kr/articles/140556")
SOURCES["PROD_P5"] = ("아시아경제(영문) 2026-02-05: P1~P4는 2개 층 '더블 팹', P5는 3개 층 '트리플 팹' 계획, 제품 구성 미확정", "https://www.asiae.co.kr/en/article/2026020509440178925")
SOURCES["INT_RTR_P5"] = ("Reuters 2025-11-16: 삼성전자, 평택에 생산 라인(P5) 추가 — 세계 최대 반도체 단지의 일부, 2023년 말부터 지연(삼성물산 공시 인용), 메모리 생산", "https://www.thestar.com.my/tech/tech-news/2025/11/16/samsung-electronics-to-add-chip-production-line-as-demand-rises")
SOURCES["INT_RTR_BIDEN"] = ("Reuters 2022-05-20: 바이든 대통령의 평택 방문 — 세계 최대 반도체 공장으로 서술", "https://newgelora.thejakartapost.com/world/2022/05/20/samsung-boss-lee-hosts-biden-yoon-in-tour-of-south-korea-chip-plant")
SOURCES["INT_SE_P2"] = ("Samsung Newsroom U.S. 2020-08-31: 평택 2라인에서 EUV 1z 16Gb LPDDR5 양산, 이후 V낸드·파운드리 생산", "https://news.samsung.com/us/16gb-lpddr5-dram-largest-semiconductor")
SOURCES["INT_TF_P4"] = ("TrendForce 2025-09-12: P4는 4개 페이즈 — ph1 낸드·D램 하이브리드, ph3 D램 전용, ph4 D램 작업 중, ph2도 D램 예상(용도 미확정)", "https://www.trendforce.com/news/2025/09/12/news-samsung-reportedly-expands-1c-dram-capacity-for-hbm4-targeting-60k-wafers-monthly-in-2025/")
SOURCES["INT_TF_P4B"] = ("TrendForce 2024-08-13: P4는 4개 페이즈의 종합 생산 시설, 낸드 장비 반입 후 1c D램 투자 확정 보도", "https://www.trendforce.com/news/?p=13064")
SOURCES["INT_TF_DBL"] = ("TrendForce 2026: P4는 한 건물에 클린룸 4개인 더블 팹 구조", "https://www.trendforce.com/news/?p=62922")
SOURCES["INT_DT_P4"] = ("DIGITIMES 2026-02-26: P4는 당초 D램·낸드·파운드리 하이브리드로 설계됐으나 D램 중심으로 전환", "https://www.digitimes.com/news/a20260226PD226.html")
SOURCES["INT_DT_P3"] = ("DIGITIMES 2023-12-08: P3는 2020년 착공, 낸드 라인 2022-05 장비 반입·07 양산, 이후 D램·파운드리 라인", "https://apps.digitimes.com/news/a20231208PD208.html")
SOURCES["INT_LINDE25"] = ("Linde 보도자료 2025-04-29: 평택 단지의 주 공급사, 8번째 온사이트 공기분리장치(질소·산소·아르곤) 건설·소유·운영, 기존 온사이트 수소 설비에서 수소 공급, 2026년 중반 공급 개시 예정", "https://www.linde.com/news-and-media/2025/linde-to-expand-supply-of-industrial-gases-to-samsung-in-south-korea")
SOURCES["INT_LINDE20"] = ("Linde 보도자료 2020-10-28: 평택 최신 반도체 시설용 초고순도 산업가스 장기 공급 계약, 공기분리 설비 건설·소유·운영", "https://linde-engineering.com/en/news_and_media/press_releases/news-20201028")
SOURCES["INT_AP26"] = ("Air Products 보도자료 2026-04-29(PR Newswire): 평택 신규 팹용 질소·산소·아르곤·수소 생산 설비와 벌크 특수가스 공급 시스템 건설·소유·운영, 2028~2030년 단계별 가동", "https://www.prnewswire.com/news-releases/air-products-to-expand-industrial-gas-supply-for-samsung-electronics-next-generation-semiconductor-fab-in-south-korea-302757497.html")
SOURCES["INT_AP_P1"] = ("Process Worldwide: Air Products, 평택 1단계에 초고순도 질소 플랜트·수소 발생기·액화기·벌크 특수가스 공급 시스템 구축, 질소 플랜트 2기 추가", "https://www.process-worldwide.com/air-products-to-build-tow-more-nitrogen-plants-at-samsung-electronics-giga-fab-a-674628/")
SOURCES["INT_GE_HVDC"] = ("GE Vernova 사례 자료: 북당진–고덕 HVDC(LCC) — 당진 발전 전력을 고덕 산업단지의 삼성전자 공장으로 송전, 1단계 2014년 수주·2단계 2018년 수주", "https://www.gevernova.com/electrification/sites/default/files/case_studies_pdfs/case-study-buk-dangjin-godeok-hvdc.pdf")
SOURCES["INT_KJD_345"] = ("Korea JoongAng Daily 2023-09-12: 한전, 23.5 km 345 kV 송전선 준공식 — 삼성전자 평택 공장이 있는 경기 남부 전력 공급용", "https://v.daum.net/v/20230912170932100")
SOURCES["INT_SS_WATER"] = ("Samsung Semiconductor Global Newsroom: 경기권역 반도체 사업장 재이용수 사업(1단계) 양해각서 — 화성·오산 하수를 재생해 하루 12만 t 공급", "https://news.samsungsemiconductor.com/global/samsung-semiconductor-signs-mou-with-ministry-of-environment-and-local-governments-for-reclaimed-water-collaboration/")
SOURCES["INT_KT_WATER"] = ("The Korea Times 2022-11-30: 하수처리수 재이용 협약 — 기흥·화성·평택 사업장에 하루 약 47만 4천 t, 연 1억 7,300만 t", "https://www.koreatimes.co.kr/amp/business/companies/20221130/samsung-electronics-secures-stable-water-supply-for-chip-production")
SOURCES["KAKAO2"] = ("카카오맵 장소 검색(2026-11-13 조회): 삼성전자 물류창고(고덕동 1696-1), 에어프로덕츠코리아 평택공장(장당동 627), 에어퍼스트 평택공장(고덕면 방축리 151-1), 삼성E&A 평택캠프, 세메스 평택사무소, 원익IPS 평택사업장, 한양이엔지", "https://map.kakao.com/")
SOURCES["GOOGLE2"] = ("구글 지도 장소 검색(2026-11-13 조회): 에어프로덕츠코리아(주) 평택공장 — 경기대로 1029", "https://www.google.com/maps")
SOURCES["CDC_DEMO"] = ("딜사이트 2025-12-31: P6 부지에 있는 CDC 물류센터는 2026년 5월까지 철거 예정", "https://dealsite.co.kr/articles/154190")
SOURCES["CDC_POSEUNG"] = ("산업일보·SBS Biz 2026-09-29: 삼성전자 CDC 물류센터 투자협약 — 평택 포승(BIX)지구 약 11만㎡, 가전제품 첨단자동화 물류센터, 2025-03 착공, 2027-06 준공 목표", "https://kidd.co.kr/news/247560")
SOURCES["AF_JOB"] = ("에어퍼스트 채용 공고(링커리어 게재): 평택공장 프로세스 엔지니어(ASU) — ASU·SMR 운전 경험 우대", "https://linkareer.com/activity/328524")
SOURCES["WIPS_CO"] = ("Wonik 그룹 공식 사이트: 원익IPS — 1991년 가스 캐비닛 생산으로 시작, 1996년 ALD 장비 상용화, 삼성 등에 공급", "https://wonik.com/en/business/semiconductor?tab=semi0")
SOURCES["WIPS_ET"] = ("ETNews(영문) 2020-02-21: 원익IPS, 삼성전자에서 몰딩 장비 수주 — 평택 2라인 10나노급 D램 팹용 장비도 수주한 것으로 알려짐", "https://english.etnews.com/20200221200001")
SOURCES["CDC_2018"] = ("아이뉴스24 2020-01: 삼성전자 평택 종합물류센터(CDC) — 2018년 완공, 가전제품 대부분의 물류 담당, 삼성전자로지텍 관리", "https://www.inews24.com/view/1340732")
SOURCES["CDC_DEMO2"] = ("투데이신문 2025-12-31: P6 예정 부지의 CDC 물류센터 철거 계획, 건축허가 확보, 2026년 5월까지 철거", "https://www.ntoday.co.kr/news/articleView.html?idxno=123645")
SOURCES["CDC_POSEUNG2"] = ("이데일리 2026-09-29: 포승 CDC는 국내 생산 가전과 평택항으로 반입되는 해외 생산 제품을 전국으로 배송하는 거점", "https://edaily.co.kr/News/Read?mediaCodeNo=257&newsId=04706806645585040")
SOURCES["AF_OFF"] = ("에어퍼스트 공식 보도자료 2021-07-23: 평택캠퍼스 세 번째 반도체 공장 가스 공급사 선정, 방축리 일대 100,000㎡ 부지 공장 건설 인허가 완료", "https://www.airfst.com/kr/sub/pr/press.asp?mode=view&bid=2&idx=147&page=1")
SOURCES["AF_SIG"] = ("서울경제 시그널 2021-04: P3 가스 공급사로 에어퍼스트와 린데 선정, P4 물량 일부도 에어퍼스트", "https://signalm.sedaily.com/NewsView/264N276OS4/GX11")
SOURCES["AP_OFF18"] = ("Air Products 공식 발표 2018-01-03: 평택 기가 팹용 두 번째 초고순도 질소 플랜트 가동, 질소 플랜트 2기 추가 건설", "https://www.airproducts.com/company/news-center/2018/01/0103-air-products-expansion-to-support-samsung-giga-fab-in-korea")
SOURCES["AP_OFF15"] = ("Air Products 보도자료 2015-06-10(PR Newswire): 평택 신규 팹의 산업용 벌크가스·벌크 특수가스 공급 시스템 계약 수주", "https://prnewswire.com/news-releases/air-products-to-supply-industrial-gases-to-new-giga-fab-campus-in-korea-300097145.html")
SOURCES["GAS_LINDE19"] = ("가스신문 2019: 린데코리아 평택 프로젝트 1단계 ASU 공장 완공·가동, 여러 기의 ASU와 수소 공장, 정제기와 파이프라인 시스템", "http://www.gasnews.com/news/articleView.html?idxno=91198")
SOURCES["WIPS_MZ"] = ("메리츠증권 2025-11: 원익IPS 삼성전자향 매출 비중 추정, CVD·ALD 장비", "https://home.imeritz.com/include/resource/research/WorkFlow/20251116182831976K_02.pdf")
SOURCES["HYENG_IR"] = ("한국IR협의회 기업분석 2023-03: 한양이엔지 — 배관 및 CCSS 선도업체", "https://file.alphasquare.co.kr/media/pdfs/company-report/IR20230317한양이엔지.pdf")
SOURCES["P52_SE"] = ("서울경제 2026-04-23(다음 게재): P5 이후 신규 공장을 P5와 구조가 같은 'P5 2'로 건설할 계획", "https://v.daum.net/v/UVoAWRXSTG")
SOURCES["P52_IN"] = ("아이뉴스24 2026: 현장 작업자 전언 — 내부에서는 P5-2라 부르며 터파기 작업에 들어감", "https://inews24.com/view/1965929")
SOURCES["YT_P6"] = ("유튜브 달팽이의 반도체 현장(고덕달팽이부동산) 2026-09-17: 평택캠퍼스 P6 건설 현장 — 채널 자체 제작 P5 팹1·팹2 배치도(비공식)", "https://www.youtube.com/watch?v=xtWACaaWlgc")
SOURCES["P5_HK"] = ("한국일보 2026-10-30(현장 르포): P5 팹1 바닥 남북 211 m × 동서 638 m, 트리플 팹, 완공 시 높이 약 100 m, 연면적 145만㎡, 생산층 한 세트 30여 m", "https://www.hankookilbo.com/news/article/A2026102911560004232")
SOURCES["GG_2026_189"] = ("경기도 고시 제2026-189호(2026-07-30) 평택 고덕국제화계획지구 일반산업단지계획 변경 승인 고시(토지이음): 산업단지 3,905,709.9㎡, 제조시설용지 2,861,212.4㎡, A1-1 기준용적률 350% 이하", "https://www.eum.go.kr/web/gs/gv/gvGosiDet.jsp?seq=639228")
META["source_policy"] = "출처 우선순위: (1) 삼성전자·시공사의 공식 자료와 공시, 공공 대장 (2) 국제 통신사·해외 전문 매체(Reuters, TrendForce, DIGITIMES 등) (3) 국내 언론. 같은 사실에 여러 출처가 있으면 앞 순위를 먼저 적는다. 해외 매체가 국내 보도를 인용한 경우가 많으므로 원 보도도 함께 남긴다"
META["products"] = dict(
    rule="삼성전자 공식 발표와 보도에 나온 내용만 적는다. 건물 안 어느 구역인지는 공개된 경우에만 적고, 나머지는 '구역 미공개'로 둔다. 제품 구성은 수요에 따라 자주 바뀌므로 보도 시점을 함께 본다",
    rows=[
        ["P1", "건물 전체(구역 미공개)", "D램 · 낸드", "P1 투어 보도(2022-09): 첨단 D램과 낸드 제작. 2025-11 보도: 낸드·D램 혼합 라인이며 낸드 일부를 D램으로 전환 검토", "A", ["PROD_P1N", "INT_RTR_BIDEN", "PROD_P1"]],
        ["P2", "건물 전체(구역 미공개)", "EUV D램 · V낸드 · 파운드리", "삼성전자 공식(2020-08): EUV 1z LPDDR5 D램으로 가동을 시작하고 V낸드·파운드리까지 만드는 복합 라인. 파운드리 라인 2020-05 착공, 낸드 라인 2020-06 착공. 2026-03 보도: P2·P3에서 4·5·7나노 파운드리 가동", "A", ["INT_SE_P2", "OFF_SE_P2", "PROD_P2F", "PROD_FDRY"]],
        ["P3", "건물 전체(구역 미공개)", "낸드 · D램 · 파운드리", "삼성전자 발표 보도(2022-09): 낸드부터 2022-07 웨이퍼 투입, 이어 D램·파운드리 순차 가동", "A", ["INT_DT_P3", "PROD_P3", "PROD_P1"]],
        ["P3", "Ph2 (상층 서)", "파운드리", "보도: '기존 파운드리 라인인 P3의 PH2'. P4 PH2와 잇는 브리지가 설치됐다는 보도", "A", ["PROD_BR"]],
        ["P4", "Ph1 (하층 서)", "낸드 + D램 하이브리드", "보도: 클린룸을 절반씩 나눠 낸드와 D램을 생산. D램 세대는 1a로 적은 보도와 1c로 적은 보도가 있음", "A", ["INT_TF_P4", "INT_TF_P4B", "PROD_P4A", "PROD_P4B", "PROD_P4C"]],
        ["P4", "Ph3 (상층 서)", "1c D램 전용", "보도: 1c D램 전용 라인. 300 m 규모 클린룸을 두세 칸으로 나눠 다른 제품 라인으로 쓰는 방안이 논의됐다는 보도도 있음", "A", ["INT_TF_P4", "INT_TF_DBL", "PROD_P4A", "PROD_P4B", "PROD_P4C"]],
        ["P4", "Ph4 (상층 동)", "D램(1c)", "보도: D램 전용 공간으로 구축", "A", ["INT_TF_P4", "INT_DT_P4", "PROD_P4A", "PROD_P4B"]],
        ["P4", "Ph2 (하층 동)", "1c D램(HBM4용)", "보도: 당초 파운드리·메모리 하이브리드 계획에서 1c D램 라인으로 전환 결정(2025-12). 본공사 2026년 2분기, 가동 준비 2027년 상반기 목표(계획)", "A", ["INT_TF_P4", "INT_DT_P4", "PROD_P1N", "PROD_P4D", "PROD_P4B"]],
        ["P5", "건물 전체(공사 중)", "HBM·D램 중심(구성 미확정)", "보도(2026-02): 3개 층에 HBM·D램·파운드리를 층별로 나눌 수 있는 구조로 계획, 제품 구성은 미확정", "A", ["INT_RTR_P5", "PROD_P5"]],
    ],
)

if __name__ == "__main__":
    r = lambda e: [round(v, 2) if isinstance(v, float) else v for v in e]
    # v7.21: storage tanks are exported as cylinders (diameter = shorter plan side of the box)
    CYL_OLD = ("원통형 탱크도 상자로 단순화", "원통형 탱크·공정 설비는 상자로 단순화")
    for e in ELEMS:
        if e["id"] == "LINDE-NE":
            e["box"][5] = 22.55; e["conf"] = "M"; e["note"] += " 높이 갱신(v7.21): 건축물대장(고덕동 1722) 주건축물 제38동이 건축면적 2,796.08㎡·높이 22.55 m로, 이 박스 평면(약 2,756㎡)과 1.4% 차이여서 같은 건물로 보고 높이를 22.55 m로 적용. 대응은 면적 비교에 따른 추정"
            if "BLDG_REG" not in e["src"]: e["src"].append("BLDG_REG")
        if e["id"] == "PUB-WWTP": e["note"] += " 대장(고덕동 1721)의 주건축물 높이: 1단계 관리 및 설비동 30.2 m(지상 7층, 건축면적 1,865.66㎡), 2단계 설비동 13.2 m(1,368.31㎡), 3단계 관리 및 설비동 18.1 m(5,195.29㎡). 어느 박스가 어느 동인지 정하지 못해 모델 높이는 임의값을 유지"
        if e["id"].startswith("CT34-F"): e["shape"] = "cyl"
        if re.search(r"-TK\d+$", e["id"]):
            e["shape"] = "cyl"
            for o in CYL_OLD: e["note"] = e["note"].replace(o, "저장탱크는 원통으로 표현(지름은 위성 판독, 돔 지붕은 평평하게 단순화)")
    data = dict(meta=META, fabs=FABS, levels=LEVELS, types=TYPES, phase={k: {f"{a}|{b}": v for (a, b), v in d.items()} for k, d in PHASE.items()},
                elems=ELEMS, equip=[r(e) for e in EQUIP], rails=[r(e) for e in RAILS], struct=STRUCT, safety=SAFETY, pipes=[r(e) for e in PIPES], dets=[r(e) for e in DETS], egress=EGRESS,
                usys=USYS, ugroups=UGROUPS, util=UTIL,
                cr_report={"P1": 135300, "P2": 148500, "P3": 181500, "P4": 181500}, sources=SOURCES)
    json.dump(data, open("campus.json", "w"), ensure_ascii=False, separators=(",", ":"))
    from collections import Counter
    print("elems", len(ELEMS), "equip boxes", len(EQUIP), "rails", len(RAILS))
    c = Counter((e[7], e[8], TYPES[e[6]]["key"]) for e in EQUIP)
    for f in ("P1", "P4"):
        for fl in [l[0] for l in LEVELS]:
            print(f, fl, {k: v for (ff, l, k), v in sorted(c.items()) if ff == f and l == fl})
    for f in FABS:
        d = [e[5] for e in EGRESS if e[6] == f["id"] and e[7] == "3F"]
        print(f["id"], "cleanroom area model", f["cr_area"], "| egress tiles", len(d), "max", max(d), "<=61m %.0f%%" % (100 * sum(v <= 61 for v in d) / len(d)), "<=75m %.0f%%" % (100 * sum(v <= 75 for v in d) / len(d)), "<=100m %.0f%%" % (100 * sum(v <= 100 for v in d) / len(d)))
    print("util segments", len(UTIL), "systems", len(USYS))
    print("struct", len(STRUCT), "safety", len(SAFETY), "OHT spacing %.1f m" % OHT_SP, "OHTV", {f["id"]: sum(1 for e in EQUIP if e[6] == TI["OHTV"] and e[7] == f["id"]) for f in FABS})
    print("pipes", len(PIPES), "dets", len(DETS), "egress", len(EGRESS))
    bad = [s for e in ELEMS for s in e["src"] if s not in SOURCES]; print("missing src keys:", set(bad))
