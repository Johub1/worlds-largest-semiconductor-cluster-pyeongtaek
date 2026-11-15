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
      vendors_site="신성이엔지 (평택 P1~4 클린룸 공급 보도, 삼성물산과 평택 클린룸 시스템 천정 공사 약 276억 원 계약 공시 2021) / 케이엔솔 공시(2026 반기): 삼성물산 발주 '평택 P3-PJT PH4 모듈 S/C 공사', 'P4-PJT PH2·PH3 모듈 S/C 공사'(별도 수익 주석에는 'P4-PJT PH4 모듈 S/C 공사' 행도 있음) — 계약표에 S/C의 정의는 없음. 같은 보고서가 시스템실링 모듈화 공법을 '2020년 삼성전자의 평택공장을 시작으로' 적용 중이라고 적음. 대수·면적·층·위치는 공시에 없음", vendors="신성이엔지, 에이펙스(APEX)"),
 dict(key="MAU", role="PLN", ko="외조기(MAU)", color="#7fa6c9", size=(14.0, 6.0, 5.0), shape="대형 공조기 박스",
      vendors_site="신성엔지니어링(신성이엔지와 다른 회사) 공식 실적표: 평택 'P PJT Ph2 OAC 납품설치'(2017), 'P2L Ph1 2공구 공조기 납품·설치'(2019·2021), 'P2L Ph2·Ph4 AHU'(2021~2022), 'EUV V2 AHU'·'V2-Ph2 EUV동 OAC'(2021), 'P4 Ph1 2공구 AHU 납품 설치'(2023) 등 — 연도는 계약년도, 대수·모델·용량·위치는 표에 없음. 원문 ITEM은 AHU·OAC이며 이 모델의 MAU 상자와 같은 장비인지는 확인되지 않음. 케이엔솔 공시(2026 반기): 삼성물산 발주 '평택 P4-PJT Ph1 Module OAC 제작납품'과 'P4-PJT PH3 OAC 제작납품' — 보고서가 OAC를 외조기(Outdoor Air Conditioner)로 적음. 대수·모델·풍량·설치 층은 공시에 없고, 회사 전체 생산 실적(OAC 58대 등)은 평택 납품 수가 아님", vendors="삼성E&A(시공)"),
 dict(key="DCC", role="PLN", ko="DCC(건식 냉각 코일)", color="#59b6c7", size=(8.0, 1.0, 3.0), shape="리턴 에어 샤프트 안의 코일 벽",
      vendors_site="P4 'Ph4 DCC 공구' 공사명 공개. 신성엔지니어링(신성이엔지와 다른 회사) 공식 실적표: 평택 'P2L Ph1 DCC'(2019), 'P2L Ph2 DCC'·'EUV 하부마감 DCC'·'P1L V2L DCC'(2021~2022), 'P3L Ph1 1공구·Ph2·Ph3·Ph4 DCC'(2021~2023), ITEM 드라이코일 — 연도는 계약년도, 같은 문구의 반복 행은 대수가 아님, 대수·모델·위치는 표에 없음. 2017·2018 'P-PJT Ph-4 DCC'는 옛 프로젝트 단계 명칭이며 P4 팹이 아님", vendors="미확인(v7.34에서 출처 없는 회사명 삭제)"),
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
    add(f"{pid}-endblk", f"{name} 동측 띠의 경계선(띠가 비친 벽면인지 단부 블록인지 미확정 — v7.27 재판독은 벽면 쪽, v7.32 비교까지 판정 없음. 이전 판은 단부 블록·복합동 추정)", "외피", [endx - 0.5, y0 + t, 0, endx + 0.5, y1 - t, H], FACADE, "B", src + ["P4_4FAC", "EA_P4", "HSCT", "OFF_CT_SMART"],
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
    add(f"{pid}-rack-S", f"{name} 옥상 대기방지시설·배관 랙(남)", "옥상 랙", [(-238 if pid == "P1" else x0 + 30), y0 + 6, H, endx - 10, ry0 - 6, H + 6], RACK, "C", ["ESRI", "YT", "YT_DAL2", "EA_P4", "EA_P3"],
        "위성·드론 영상에 보이는 옥상 철골 랙을 단순 박스로 표현. 삼성E&A 공시의 공사명에 P4는 '대기방지', P3는 '옥상배기'가 들어 있음(공사 범위 명칭 — 랙 전체의 기능을 뜻하지는 않음). 현장 관찰 유튜브 채널의 P4 주석 사진은 옥상 구조물을 '대기방지 시설'로 표기(비공식 주석)", opacity=0.3, fl="RF", **S)
    add(f"{pid}-rack-N", f"{name} 옥상 대기방지시설·배관 랙(북)", "옥상 랙", [(-238 if pid == "P1" else x0 + 30), ry1 + 6, H, endx - 10, y1 - 6, H + 6], RACK, "C", ["ESRI", "YT"], "", opacity=0.3, fl="RF", **S)
    if pid == "P1":  # v7.24: west half — rack only on the inner strip (read from imagery)
        add("P1-rack-S2", "P1 FAB 옥상 배관 랙(남, 서쪽 절반 안쪽 띠 — 위성 판독)", "옥상 랙", [x0 + 30, ry0 - 21, H, -238, ry0 - 3, H + 6], RACK, "B", ["ESRI"], "위성영상(2025-12-22 촬영분)에서 P1 서쪽 절반은 옥상 외곽대의 바깥 띠가 지붕면으로 보이고 안쪽 띠에만 철골 격자와 배관이 보임. 그래서 서쪽 절반의 랙은 안쪽 띠로만 그림. 평면 범위는 판독, 높이는 임의", opacity=0.3, fl="RF", **S)
        add("P1-rack-N2", "P1 FAB 옥상 배관 랙(북, 서쪽 절반 안쪽 띠 — 위성 판독)", "옥상 랙", [x0 + 30, ry1 + 3, H, -238, ry1 + 21, H + 6], RACK, "B", ["ESRI"], "위성영상(2025-12-22 촬영분)에서 P1 서쪽 절반은 옥상 외곽대의 바깥 띠가 지붕면으로 보이고 안쪽 띠에만 철골 격자와 배관이 보임. 그래서 서쪽 절반의 랙은 안쪽 띠로만 그림. 평면 범위는 판독, 높이는 임의", opacity=0.3, fl="RF", **S)
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
HN = " 높이는 미공개. 서쪽에서 찍은 드론 사진에서 4개 팹 높이가 비슷해 보여 P1 모델과 같은 83 m를 개념 가정으로 둠(83 m 자체도 대상이 확정되지 않은 보도값)."
FABS = []
FABS.append(fab("P1", -498, 51, 1941, 2142, 21, 83.0, [(-435, -21, 1989, 2095)],
    "보도 수치: P1 길이 약 520 m·폭 약 200 m(이투데이 2022-09-07, 관계자 인용). ZDNet(2022-08-25)의 518 × 201 × 83 m는 대상이 '평택캠퍼스 생산라인'으로만 적혀 있어 P1 단독의 치수인지 확정되지 않음. 위성 실측: 본체 519 m(단부 블록 포함 549 m) × 201 m로 평면은 보도값과 부합. 높이 83 m는 대상 미확정 보도값을 쓴 모델 가정이며 측정 경계·법정 높이·층고는 확인하지 못함", SRC_FAB + ["P1_DIM"]))
FABS.append(fab("P2", -309, 243, 1544, 1748, 212, 83.0, [(-243, 160, 1599, 1696)],
    "위성 실측: 본체 521 m(단부 포함 552 m) × 204 m. 보도의 '400 m대'와 불일치(실측값 채택). 감리사 실적 페이지 '삼성전자 평택 P2': 지하 1층~지상 8층, 연면적 592,077㎡ — FAB 단독 범위인지는 적혀 있지 않음." + HN, SRC_FAB + ["P2_FLOORS", "P2_400", "YT_RE"]))
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
aux("UT-12", "유틸리티동(P1·P2 사이, UT동 추정)", (-314, -2, 1806, 1889), 42, "#9fa7b0", note="삼성E&A 프로젝트 소개: P2 UT동 — 냉수·스팀·압축공기·공업용수를 생산 라인에 공급, 냉수 일 최대 약 24만 냉동톤, 'UT동과 CT동'을 블록 단위로 배치. 이 건물이 해당 동인지는 미확인. '24만 냉동톤'은 회사가 쓴 냉각 규모 표현을 그대로 옮긴 것으로, 하루 냉수량·가동 부하·설비 대수로 환산하지 않음. 'CT'가 무엇의 약어인지와 회사 페이지 면적 표기의 대상 범위는 확정하지 못함. P2에 대한 설명이며 P3·P4 유틸리티동에 옮겨 쓰지 않음", src=["ESRI", "OSM", "P2_UT"])
aux("UT-12E", "유틸리티동 동측부(P1·P2 사이)", (-2, 212, 1806, 1889), 58, "#9fa7b0", src=["ESRI", "OSM"])
aux("UT-34", "P3·P4 사이 건물(인허가상 복합동 또는 UT동 후보 — 미확정)", (-307, 357, 1117, 1232), 45, "#9fa7b0", note="위성영상에서 냉각탑 수증기 확인. 삼성엔지니어링 공시(KRX 2022-11-24)의 공사명에 '[P3 Ph4] 그린동 및 UT동, 옥상배기, UPW 마감공사'가 있어 P3에 'UT동'이라는 명칭이 쓰인 것은 확인됨(Astra 원문 대조). 이 상자가 그 UT동인지, 층수·높이·동 수, 복합동과 같은 건물인지는 확인하지 못함", src=["ESRI", "P3_UT", "KRX_P3PH4"])
aux("UT-34E", "유틸리티동 단부(P3·P4 사이)", (357, 390, 1120, 1230), 60, "#a9b0b8")
aux("CUB-N", "북측 유틸리티/냉각탑 구역(추정)", (-150, 139, 2167, 2283), 35, "#9aa3ad", note="수증기 확인")
aux("OFF-T", "기술동(구글 지도 표기 · 대장의 기술동-2와 같은 건물인지는 미확정)", (-420, -339, 2206, 2248), 45, "#8fa3b8", rot=38, note="위성영상(Esri World Imagery, 줌 18, 약 0.48 m/px, 2026-11-12 재취득)에서 모서리를 읽어 평면·방향을 다시 잡음(판독 오차 약 ±5 m). v7.12까지는 방향이 반대(−30°)였고 평면도 동쪽의 어두운 부속 부분까지 합친 86 × 80 m였음 — 태양광 지붕이 보이는 본체만 약 81 × 42 m, 북동 방향 38°로 수정. 구글 지도의 장소 '삼성전자 평택캠퍼스 기술동' 좌표(37.04006, 127.05605 → 모델 약 (-351, 2231))가 이 박스 안에 있음. 카카오맵은 북쪽 약 240 m 지점을 '기술동 입구', 동쪽 건물을 '기술동 주차타워'로 표기. 건축물대장에는 '기술동-2'(건축면적 6,412.72㎡, 높이 67.90 m, 지상 11층)만 공개되어 있는데, '기술동'과 '기술2동'이 공공데이터에 따로 등록되어 있고 이 박스 평면(약 3,400㎡)이 훨씬 작아 같은 건물인지 정하지 않음. 보도: P1 담당 사무1동은 9층, P2 담당 사무2동은 11층이며 사무동과 생산동은 분리 배치", src=["ESRI", "OFFICE", "PRESS_TOUR", "GOOGLE", "BLDG_REG", "DISINF"], conf="M")
aux("OFF-2", "기술동 주차타워(카카오맵 표기)", (-280, -194, 2211, 2281), 52, "#a7b4c2", rot=48, note="위성영상(Esri World Imagery, 줌 18, 약 0.48 m/px, 2026-11-12 재취득)에서 모서리를 읽어 평면·방향을 다시 잡음(판독 오차 약 ±5 m). 옥상에 차량이 보이는 주차 구조물 약 86 × 71 m, 방향 48°(v7.12까지는 회전 없는 123 × 118 m). 대장의 기술동-2(건축면적 6,412.72㎡)와는 평면이 약 6% 작음 — 같은 건물인지는 미확인", src=["ESRI", "OFFICE"])
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
aux("S1", "남동측 대형 부속동 S1(그린동·수처리 추정)", (484, 645, 1057, 1232), 18, note="보도: P4는 FAB동·복합동·변전소·그린동(폐수처리시설) 4종 시설로 구성(보도상 분류이며 독립 건물 수가 아님), 그린동은 삼성엔지니어링 시공. 삼성E&A 공시 공사명에 그린동 포함, 한성크린텍은 P4 그린동 내 기계·배관 설치 공사 수주 공시. 그린동의 존재·용도는 확인, 이 건물과의 대응은 미확인. 참고(2021 공식 공개): 평택 그린동의 지하 수처리 시설 단면적 약 3만 4천㎡, 하루 약 7만 t 정화, 폐수는 성분별 6가지로 구분, 약품 배관에 스크린도어, 중앙통제실(CCR), 자동화율 97%. 이 박스의 평면은 약 2만 8천㎡", src=["ESRI", "P4_SITE", "P4_4FAC", "EA_P4", "HSCT", "GREEN21"])
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
    "건축물대장 총괄표제부(Codex가 2026-11-15 공식 화면에서 전체 열로 내려받아 확인): 대지면적 102,076㎡, 건축면적 20,081.47㎡, 연면적 48,546.62㎡(대지면적은 이 OSM 경계의 면적 약 101,700㎡와 0.4% 차이). 같은 기준월의 동별 표제부 9행을 더하면 건축면적 20,081.46㎡, 연면적 48,558.01㎡로 총괄보다 연면적이 11.39㎡ 큼 — 원인 미확정이며 이 차이로 건물이나 설비를 만들지 않음. 보도: 캠퍼스와 도로 하나를 사이에 둔 맞은편, 부지는 삼성이 제공(보도에는 '연면적 약 10만㎡'로 나옴 — 대장의 대지면적 102,076㎡·연면적 합 48,546.62㎡와 나란히 적어 두며, 보도 수치가 어느 값·어느 시점을 가리키는지는 확정하지 못함). 경계는 OpenStreetMap '고덕변전소' 폴리곤. 추가 계획(보도 2024-08): 345 kV 고덕3 변전소를 고덕국제화계획지구 내 변전소 부지에 2031-09 완공 목표로 추진 — 이 부지와 같은 곳인지는 확인하지 못함. 현장 관찰 채널 사진(2026)에는 '한전변전소 증설공사 중' 주석")
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
# v7.26: rooftop reading of the building between P1 and P2 (plan extents only; type and height unknown)
UT12N = '위성영상(Esri World Imagery 줌 18, 약 0.5 m/화소)에서 읽은 옥상의 평면 범위(±3 m). 설비 종류·대수·높이는 확인하지 못했고 높이 값은 표시용 임의값. 건물 안에 둔 개념 설비 요소와는 별개'
aux('UT12-RF-N1', 'P1·P2 사이 유틸리티동 옥상 설비군 N1(위성 판독, 종류 미확인)', (-273, -243, 1867, 1885), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-N2', 'P1·P2 사이 유틸리티동 옥상 설비군 N2(위성 판독, 종류 미확인)', (-205, -193, 1866, 1883), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-N3', 'P1·P2 사이 유틸리티동 옥상 설비군 N3(위성 판독, 종류 미확인)', (-190, -158, 1867, 1885), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-N4', 'P1·P2 사이 유틸리티동 옥상 설비군 N4(위성 판독, 종류 미확인)', (-110, -83, 1866, 1881), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-N5', 'P1·P2 사이 유틸리티동 옥상 설비군 N5(위성 판독, 종류 미확인)', (-78, -56, 1865, 1881), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-N6', 'P1·P2 사이 유틸리티동 옥상 설비군 N6(위성 판독, 종류 미확인)', (-32, -8, 1867, 1884), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-S1', 'P1·P2 사이 유틸리티동 옥상 철골 격자 구조물 S1(위성 판독, 종류 미확인)', (-265, -232, 1826, 1838), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-S2', 'P1·P2 사이 유틸리티동 옥상 철골 격자 구조물 S2(위성 판독, 종류 미확인)', (-185, -166, 1827, 1837), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-S3', 'P1·P2 사이 유틸리티동 옥상 철골 격자 구조물 S3(위성 판독, 종류 미확인)', (-108, -57, 1826, 1836), 3, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")
aux('UT12-RF-SP', 'P1·P2 사이 유틸리티동 옥상 중앙 길이방향 띠(배관 랙 또는 통로로 보임)(위성 판독, 종류 미확인)', (-285, -5, 1845, 1853), 1.5, "#8f9aa6", conf="B", src=["ESRI"], note=UT12N, z0=42, layer="옥상 랙")

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
# v7.28: public roads and railway at ground level (read from imagery)
add('ROAD-W', '캠퍼스 1단지 서측 남북 공공도로(직선 구간, 위성 판독)', "지반", [-547, 650, -0.2, -510, 1480, 0.05], '#565c63', "B", ['ESRI', 'ESRI_META', 'BLDG_REG'], "위성영상(Esri World Imagery 줌 18, 촬영일 2025-12-22)에서 읽은 차도 범위(±5 m). 지면 높이라 사각 촬영에 따른 치우침은 작음. 절대 위치 정확도는 확인되지 않음. 두께는 표시용. 출입구·검문 시설·보안 동선은 그리지 않음. 대장의 도로명주소가 이 도로 동쪽(1단지)은 '삼성로 114', 서쪽(2단지 주차동)은 '삼성로 117'이어서 '삼성로'로 추정 — 지도 표기로 확인하지는 않음. Y 1480 북쪽은 북서로 휘며 ROAD-W2·ROAD-W3로 이어짐.")
add('ROAD-S', '캠퍼스 남측 동서 공공도로(직선 구간, 위성 판독)', "지반", [-1150, 808, -0.2, 720, 838, 0.05], '#565c63', "B", ['ESRI', 'ESRI_META'], '위성영상(Esri World Imagery 줌 18, 촬영일 2025-12-22)에서 읽은 차도 범위(±5 m). 지면 높이라 사각 촬영에 따른 치우침은 작음. 절대 위치 정확도는 확인되지 않음. 두께는 표시용. 출입구·검문 시설·보안 동선은 그리지 않음. 도로 이름은 확인하지 않음. X 720 부근에서 북쪽으로 꺾이는 구간은 그리지 않음.')
add('RAIL-E', '캠퍼스 동측 철도(복선, 남측 직선 구간 — 위성 판독)', "지반", [762, 650, -0.2, 798, 900, 0.05], '#6b5f52', "B", ['ESRI', 'ESRI_META'], '위성영상(Esri World Imagery 줌 18, 촬영일 2025-12-22)에서 읽은 선로 범위(±5 m). 지면 높이라 사각 촬영에 따른 치우침은 작음. 절대 위치 정확도는 확인되지 않음. 두께는 표시용. 출입구·검문 시설·보안 동선은 그리지 않음. 전차선 지지물이 보이는 복선 철도. 노선 이름은 확인하지 않음. 북쪽은 캠퍼스 동쪽을 따라 곡선으로 이어지며 그리지 않음.')
# v7.29: north-west continuation of the west public road (rotated rectangles)
add('ROAD-W2', '캠퍼스 1단지 서측 공공도로 굴곡 구간(위성 판독)', "지반", [-583, 1472.5, -0.2, -547, 1647.5, 0.05], "#565c63", "B", ["ESRI","ESRI_META"], '위성영상(Esri World Imagery 줌 18, 촬영일 2025-12-22)에서 읽은 차도 범위를 회전한 직사각형으로 단순화(±10 m, 실제는 완만한 곡선). 지면 높이라 사각 촬영에 따른 치우침은 작음. 절대 위치 정확도는 확인되지 않음. 두께는 표시용. 출입구·검문 시설·보안 동선·도로 위 보행 연결통로는 그리지 않음. ROAD-W의 북쪽 연장.', rot=24)
add('ROAD-W3', '1단지와 2단지 사이 북서 방향 공공도로(직선 구간, 위성 판독)', "지반", [-793, 1576.5, -0.2, -757, 2123.5, 0.05], "#565c63", "B", ["ESRI","ESRI_META"], '위성영상(Esri World Imagery 줌 18, 촬영일 2025-12-22)에서 읽은 차도 범위를 회전한 직사각형으로 단순화(±10 m, 실제는 완만한 곡선). 지면 높이라 사각 촬영에 따른 치우침은 작음. 절대 위치 정확도는 확인되지 않음. 두께는 표시용. 출입구·검문 시설·보안 동선·도로 위 보행 연결통로는 그리지 않음. 2단지 주차동의 북동쪽 변과 나란함. 북서쪽 끝은 교차로이며 그 너머는 그리지 않음. 도로 이름은 ROAD-W와 같은 도로로 추정할 뿐 확인하지 않음.', rot=40)
# v7.30: public cross road north-west of the campus
add("ROAD-NW", '캠퍼스 북서측 시가지 공공도로(북동–남서 방향 직선 구간, 위성 판독)', "지반", [-1118.5, 2111.5, -0.2, -618.5, 2151.5, 0.05], "#565c63", "B", ["ESRI","ESRI_META"], '위성영상(Esri World Imagery 줌 18, 촬영일 2025-12-22)에서 읽은 차도 범위를 회전한 직사각형으로 단순화(±10 m는 영상 위 판독의 추정 정밀도이며 검측 오차 한계가 아님). 지면 높이라 사각 촬영에 따른 치우침은 작음. 절대 위치 정확도는 확인되지 않음. 두께는 표시용. 캠퍼스 북서쪽 시가지의 공공도로로, ROAD-W3의 북서쪽 끝 교차로를 지남. 도로 이름은 확인하지 않음. 양 끝 너머는 그리지 않음.', rot=39)
add("PAD-1", "평택캠퍼스 1단지 부지(개략)", "지반", [-720, 690, -1.0, 700, 2330, -0.2], "#3a434c", "C", ["ESRI", "SITE_AREA"], "부지 경계는 개략. 캠퍼스 총 부지 약 289만㎡(보도)")
add("PAD-P5", "P5 건설 부지(2단지, 공사 중)", "지반", [-1560, 880, -1.0, -800, 1620, -0.2], "#5a4b3a", "C", ["ESRI", "P5", "P5_HK", "GG_2026_189", "POSCOANC_P5"],
    "2025-12 위성영상에서 기초공사 확인. 보도: P5는 약 650 m × 195 m, 3개 층 6개 클린룸. 범위는 개략. 상충 보도(한국일보 2026-10-30, 현장 르포): 팹1 바닥은 남북 211 m × 동서 638 m, 트리플 팹, 완공 시 높이 약 100 m, 연면적 145만㎡, 2028년 가동 목표. 두 보도의 치수가 달라 모델은 부지 범위만 개략으로 그리고 건물 형상은 넣지 않음. 경기도 고시 제2026-189호(2026-07-30, 산업단지계획 변경 승인)에서 A1-1 구역의 기준용적률은 350% 이하로 변경이 없음(Astra가 고시문 26쪽을 대조). 490% 상향을 승인한 고시는 확인되지 않아, 트리플 팹과 클린룸 6개는 보도상 계획으로만 표기하고 승인된 구조로 쓰지 않음. 설계·사업관리 회사 실적(v7.33): 포스코A&C 공식 실적 페이지(959번, Codex가 원문 확인)는 'Pyeongtaek P5 Ph1 Semi-Production Facility CM/CS', 서비스 CM, 발주처 Samsung Electronics, Year 2028로 표기 — 미래 연도의 표기이며 준공·가동의 근거가 아님. 면적·층수 칸은 값이 없는 자리표시이고, 형상에는 쓰지 않음")

SOURCES = {
 "ESRI": ("Esri World Imagery (Vantor/WorldView-2, 촬영 2025-12-22, 0.5 m) — 평면 치수 실측", "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer"),
 "OSM": ("OpenStreetMap 건물 폴리곤(ODbL) — 교차 확인용", "https://www.openstreetmap.org/#map=16/37.0350/127.0600"),
 "YT": ("삼성전자 반도체 뉴스룸 공식 영상 '삼성전자 평택캠퍼스' — 외관·지붕·클린룸(포토 베이)·SEMES OHT", "https://www.youtube.com/watch?v=6if4eP8fn_U"),
 "YT_RE": ("평택 부동산 채널(이지티비) 드론 사진 — 서쪽에서 본 P1~P4·V2·신축 사무동 현장", "https://www.youtube.com/watch?v=2OaCpiqyLGE"),
 "P1_DIM": ("이투데이 2022-09-07: P1 길이 약 520 m·폭 약 200 m(관계자 인용, 높이 없음) / ZDNet Korea 2022-08-25: 평택캠퍼스 생산라인 길이 518 m·폭 201 m·높이 83 m(P1이라고 특정하지 않음)", "https://zdnet.co.kr/view/?no=20220825080050"),
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
SOURCES["DEALSITE_BR"] = ('딜사이트 2025-06-24(수정 2025-08-25): 평택 P4 후속 공사 보도 — 사진 설명에 P3 PH2·P4 PH2 브리지 4개와 중간 복합동, 세메스 OHT 설치 예상', "https://dealsite.co.kr/articles/143484")
REG_SFX = {'P1-wall-S': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P1-wall-N': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P1-wall-W': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P1-wall-E': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P1-endblk': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P2-wall-S': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P2-wall-N': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P2-wall-W': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P2-wall-E': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P2-endblk': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동'(건축면적 107,653.47㎡, 지상 1~9·지하 1 표시)과 'FAB동-2'(111,791.28㎡, 지상 1~8·지하 1 표시)가 면적상 후보. 모델 평면은 P1 110,349㎡, P2 112,608㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P1이고 어느 동이 P2인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P3-wall-S': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P3-wall-N': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P3-wall-W': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P3-wall-E': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P3-endblk': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P4-wall-S': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P4-wall-N': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P4-wall-W': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P4-wall-E': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'P4-endblk': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'FAB동-3'(건축면적 138,388.36㎡, 지상 1~8·지하 1 표시)과 'FAB동-4'(134,164.30㎡, 지상 1~8 표시, 지하 행 없음 — 지하가 없다는 확정은 아님)가 면적상 후보. 모델 평면은 P3 135,408㎡, P4 136,032㎡로 두 동 모두와 5% 안에서 맞아, 면적만으로는 어느 동이 P3이고 어느 동이 P4인지 가리지 못함. 모델의 8개 층 단면과 83 m는 개념 가정 그대로임. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'V2': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'EUV동'(건축면적 31,623.49㎡, 지상 1~9·지하 1 표시)이 면적상 후보(모델 평면 31,304㎡, −1.0%). 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'UT-34': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '복합동'(건축면적 87,013.82㎡, 지상 1~9·지하 1 표시)이 면적상 후보 — 이 건물의 두 상자 합 79,990㎡(−8.1%). 딜사이트 사진 설명이 P3·P4 사이 건물을 복합동으로 적은 것과 방향이 같으나, 현장 관찰 채널 주석은 팹 동측 단부 블록을 복합동으로 표기해 서로 다르므로 미확정. 인허가상 'UT동'(16,348.93㎡)·'UT동-2'(19,153.67㎡)는 이 건물보다 훨씬 작음. 그래서 v7.26에서 이름의 'UT동 추정'을 '복합동 또는 UT동 후보'로 바꿈. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'UT-34E': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '복합동'(건축면적 87,013.82㎡, 지상 1~9·지하 1 표시)이 면적상 후보 — 이 건물의 두 상자 합 79,990㎡(−8.1%). 딜사이트 사진 설명이 P3·P4 사이 건물을 복합동으로 적은 것과 방향이 같으나, 현장 관찰 채널 주석은 팹 동측 단부 블록을 복합동으로 표기해 서로 다르므로 미확정. 인허가상 'UT동'(16,348.93㎡)·'UT동-2'(19,153.67㎡)는 이 건물보다 훨씬 작음. 그래서 v7.26에서 이름의 'UT동 추정'을 '복합동 또는 UT동 후보'로 바꿈. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'UT-12': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'UT동'(건축면적 16,348.93㎡)·'UT동-2'(19,153.67㎡, 둘 다 지상 1~5·지하 1 표시)와 비교하면 서측 상자 25,896㎡, 동측 상자 17,762㎡, 합 43,658㎡ — 동측 상자만 15% 안(UT동 대비 +8.6%, UT동-2 대비 −7.3%)이고 서측 상자와 합계는 맞지 않음. 대응 미확정. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'UT-12E': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'UT동'(건축면적 16,348.93㎡)·'UT동-2'(19,153.67㎡, 둘 다 지상 1~5·지하 1 표시)와 비교하면 서측 상자 25,896㎡, 동측 상자 17,762㎡, 합 43,658㎡ — 동측 상자만 15% 안(UT동 대비 +8.6%, UT동-2 대비 −7.3%)이고 서측 상자와 합계는 맞지 않음. 대응 미확정. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'S1': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '그린동-3'(건축면적 25,583.41㎡, 지상 1~6 표시)과 '그린동-4'(24,741.09㎡, 지상 1~5 표시)가 면적상 후보 — 모델 평면 S1 28,175㎡, S2 25,730㎡. 어느 상자가 어느 동인지는 가리지 못함. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'S2': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '그린동-3'(건축면적 25,583.41㎡, 지상 1~6 표시)과 '그린동-4'(24,741.09㎡, 지상 1~5 표시)가 면적상 후보 — 모델 평면 S1 28,175㎡, S2 25,730㎡. 어느 상자가 어느 동인지는 가리지 못함. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'CT-1': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'CT동'·'CT동-2'는 지상 건축면적이 645.92㎡·517.23㎡로 작고 지하 1층 면적이 17,157.64㎡·20,739.91㎡로 큼. 이 뱅크 4개의 평면 합은 17,876㎡로 수치가 비슷하다는 것 외에 관계는 확인하지 못함. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'CT-2': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'CT동'·'CT동-2'는 지상 건축면적이 645.92㎡·517.23㎡로 작고 지하 1층 면적이 17,157.64㎡·20,739.91㎡로 큼. 이 뱅크 4개의 평면 합은 17,876㎡로 수치가 비슷하다는 것 외에 관계는 확인하지 못함. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'CT-3': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'CT동'·'CT동-2'는 지상 건축면적이 645.92㎡·517.23㎡로 작고 지하 1층 면적이 17,157.64㎡·20,739.91㎡로 큼. 이 뱅크 4개의 평면 합은 17,876㎡로 수치가 비슷하다는 것 외에 관계는 확인하지 못함. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'CT-4': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'CT동'·'CT동-2'는 지상 건축면적이 645.92㎡·517.23㎡로 작고 지하 1층 면적이 17,157.64㎡·20,739.91㎡로 큼. 이 뱅크 4개의 평면 합은 17,876㎡로 수치가 비슷하다는 것 외에 관계는 확인하지 못함. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'E1': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): 'GCS동' 건축면적은 43,199.47㎡(지상 1~6·지하 1 표시)로 이 상자(14,014㎡)와 맞지 않음. 동측 부속동 M1·M2의 합(39,592㎡, −8.4%)이 면적상 더 가까우나 대응 미확정. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'OFF-2': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '기술동 주차타워' 건축면적은 8,160.30㎡(지상 1~6 표시)로 이 상자(6,020㎡)가 약 26% 작음. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'OFF-T': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '기술동' 건축면적은 4,552.02㎡(지상 1~5·지하 1 표시)로 이 상자(3,402㎡)가 약 25% 작음. 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'GATE-W': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '사무동' 건축면적은 8,964.21㎡, 표시 층번호 지상 1~10·지하 1 — 이 상자(5,984㎡)가 약 33% 작고, 보도의 9층과 표시 층번호가 다름(계수 방식 미확인). 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음.", 'WA': " [인허가 대조 v7.26] 건축HUB 건축인허가 동별개요 316행·층별개요 701행(고덕동 1695, 2026-09 기준 — Codex가 공식 화면에서 전체 열로 내려받은 웹 내보내기, API 원응답 아님. 허가PK·동PK로 결합): '사무동-2' 건축면적은 10,861.63㎡, 표시 층번호 지상 1~12·지하 1 — 이 상자(7,050㎡)가 약 35% 작고, 보도의 11층과 표시 층번호가 다름(계수 방식 미확인). 표시 층번호는 인허가 스냅샷의 번호이며 높이·층고·가동 여부가 아님. 대응은 후보이며 상자의 위치·크기·높이는 바꾸지 않음."}
SOURCES["HUB_FLR_1695"] = ("건축HUB 건축인허가 동별개요·층별개요(국토교통부) — 평택시 고덕동 1695, 2026-09 기준. Codex가 2026-11-15 공식 화면에서 전체 열로 내려받은 웹 내보내기: 동별 316행·29열, 층별 701행·24열(API 원응답 아님). 입수 이력: 2026-11-14에는 선택 8열 701행과 동별 전사 28행으로 먼저 결합했고, 28개 동의 건축면적·연면적은 전체 열 자료와 모두 일치", "https://www.hub.go.kr/portal/opn/tyb/idx-acpmslg-flrcb.do")
SOURCES["R7_2026_15"] = ("한강유역환경청고시 제2026-15호 공공폐수처리시설 기본계획 통합 고시(2026-01-13) 제36항 — 고덕 처리능력 340,000 m³/일(120,000 + 67,500 + 92,500 + 60,000)", "https://www.law.go.kr/LSW/admRulLsInfoP.do?admRulSeq=2100000272784")
SOURCES["ESRI_META"] = ('Esri World Imagery 메타데이터 레이어(MapServer 10, 줌 18 대응) — 2026-11-15 Astra 조회: 캠퍼스 7개 지점·범위 모두 촬영일 2025-12-22, 원자료 해상도 0.5 m, WV02, Vantor. 촬영각 항목 없음', "https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/10")
SOURCES["NGII_ORTHO_2025"] = ('국토지리정보원 국토정보플랫폼 정사영상 2025(도엽 37713083, 사업코드 202511A0012, 25 cm) — 공개 미리보기를 Codex가 열람, 메타데이터는 Astra가 조회. 영상은 재배포하지 않음', "https://map.ngii.go.kr/ms/map/NlipMap.do")
SOURCES["SSEC_20251023"] = ('삼성증권 리서치 보고서 「2026년이 아니라 2029년까지 봐야합니다」(2025-10-23) 12쪽 팹 위치 표기 — 증권사 자체 표기', "https://www.samsungpop.com/common.do?cmd=down&contentType=application%2Fpdf&fileName=2020%2F2025102309010017K_02_02.pdf&inlineYn=Y&saveKey=research.pdf")
SOURCES["KRX_P3PH4"] = ("삼성엔지니어링 단일판매·공급계약 공시(KRX KIND 2022-11-24): [P3 Ph4] 그린동 및 UT동, 옥상배기, UPW 마감공사", "https://kind.krx.co.kr/external/2022/11/24/000282/20221123000578/91370.htm")
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
                  "삼성물산 '평택 단지(평택 P-PJT)' 포트폴리오의 프로젝트 연면적(범위·기준일 미표시)": "3,967,000㎡ — 회사 포트폴리오가 제시한 프로젝트 수치. 포함 건물·단계·기준일·공사기간이 적혀 있지 않아 현재 캠퍼스 전체의 합계로 확정하지 않으며, 모델 요소 면적을 여기에 맞추거나 팹별로 나누지 않음",
                  "P2": "'연면적 12만 8,900㎡'라는 표기가 삼성전자 뉴스룸(2020-08)과 삼성E&A P2 유틸리티 프로젝트 소개(국문)에 있음(삼성E&A 영문 페이지는 128,999㎡). 이 수치가 가리키는 대상 범위(P2 FAB 전체인지, 유틸리티 프로젝트 범위인지, 한 층 평면인지)는 확정하지 못해 P2 FAB의 연면적으로 쓰지 않음",
                  "P1·P3·P4": "네 회사 공식 자료에서 동별 면적을 찾지 못함",
                  "P3 그린동": "폐수 처리 시설 총 용량 81,600 m³/d(삼성엔지니어링 지속가능경영보고서 2021, 보고서 본문에서 단위 확인. 면적·층수는 기재 없음)"},
        verified="2026-11-12 직접 열람: 삼성물산 건설부문 포트폴리오에는 '평택 단지(평택 P-PJT)'의 프로젝트 연면적 수치만 있고(범위·기준일 미표시) 층수·공사기간·동별 면적은 없음. 삼성엔지니어링 2021 보고서에는 P3 그린동 용량만 있고 면적 수치는 없음(문서 앞 약 3분의 2 범위 열람)",
        gov_register="건축물대장(국토교통부) 조회 도구가 표시한 값을 옮겨 적은 인접 시설(요청 URL·원응답 파일은 보유하지 않음): 고덕변환소·변전소(고덕동 1730) 대지 102,076㎡·연면적 48,546.62㎡, 린데코리아 평택공장(고덕동 1722) 대지 78,833.4㎡·건축면적 27,316.3㎡·연면적 22,665.15㎡·6동·사용승인 2023-04-27, 하수등처리시설(고덕동 1721, 삼성1로 60) 대지 150,297.2㎡·건축면적 8,429.26㎡·연면적 21,840.49㎡·총괄표제부 사용승인 2022-07-15(동별 사용승인일은 단계마다 다름: 1단계 2017-06-22, 2단계 2022-07-15, 3단계 2025-01-23 — 역산분석 방 전사본 기준). 삼성전자 평택캠퍼스는 고덕동 1695번지(외 37필지, 도로명주소 안내 사이트로 지번 확인)",
        gov_register_campus="건축물대장 표제부(고덕동 1695) 조회 결과에 나온 행은 2건(조회 범위의 결과이며 이 필지의 실제 건물 수가 아님): (1) 기술동-2 — 삼성로 114, 건축면적 6,412.72㎡, 연면적 51,410.10㎡, 높이 67.90 m, 지상 11층·지하 1층, 철골철근콘크리트구조, 승강기 16대, 허가 2015-02-27, 사용승인 2026-09-21 (2) 북문동 — 삼성1로 457, 건축면적 572.85㎡, 연면적 934.22㎡, 높이 10.32 m, 지상 2층, 사용승인 2026-04-27. 대지면적 1,833,839.5㎡. 주차(대장 기재): 옥내 자주식 약 4,000대·128,907㎡, 옥외 자주식 약 6,437대·172,590㎡. FAB동·복합동·그린동 등 생산 시설은 이 표제부 조회 결과에 나오지 않음(공개 자료에 없다는 뜻이 아님). 건축인허가 동별개요(316건): 2026-11-12 이 방이 본 100건은 모두 가설건축물이었음. 2026-11-14 역산분석 방이 1~40행·201~316행 156건을 조회해 주 건축허가에 묶인 연면적 1만㎡ 이상 28행을 전사(당시 41~200행 미조회 — 2026-11-15 Codex의 전체 열 내보내기로 해소, 아래 참조). 그 가운데 건축면적 8.7만~13.8만㎡·연면적 53만~72만㎡의 행이 5개 있음. 2026-11-14 Codex가 공식 화면에서 층별개요 701행(선택 8열, 2026-09 기준, 층별PK 열 없음)을 내려받아 허가PK·동PK로 결합한 결과 28행 모두 동 이름이 붙음: 대형 5행은 FAB동-3·FAB동-4·FAB동·FAB동-2·복합동(FAB 5개가 아님)이고 그 밖에 EUV동, UT동·UT동-2, CT동·CT동-2, 그린동 4개, 154kV동 4개, GCS동, 정수장, 사무동 3개, 기술동·기술동-2·기술동 주차타워, 일반창고1, 창고동. 표시 층번호는 FAB동 지상 1~9·지하 1, FAB동-2·-3 지상 1~8·지하 1, FAB동-4 지상 1~8(지하 행 없음 — 무지하 확정 아님), 복합동·EUV동 지상 1~9·지하 1, UT동·UT동-2 지상 1~5·지하 1. 높이·층고·표고는 없음. 이 방은 701행과 28행 표를 스크립트로 전부 읽어 모델 상자와 건축면적을 비교함(data/register_vs_model.csv): 팹 4개와 EUV동은 5% 안에서 맞지만 FAB동/FAB동-2와 P1/P2, FAB동-3/FAB동-4와 P3/P4는 면적만으로 서로 가려지지 않음. 2026-11-15 Codex가 같은 공식 화면에서 동별개요 316행·29열과 층별개요 701행·24열을 전체 열로 다시 내려받음(공식 웹 내보내기, API 원응답 아님): 층별PK 701개가 모두 고유해 전날 '같은 8열 행 19개'는 중복이 아니며, 주 허가에는 70개 동이 있고 연면적 1만㎡ 이상은 28개 동으로 전날 표에 누락이 없음. 주 허가 70개 동의 동별 연면적 합은 4,713,467.42㎡(28개 대형 동 4,669,137.36㎡ + 나머지 42개 동 44,330.06㎡)이고, 층별 행의 단순 합과의 차 256.65㎡는 사무동·방재센터-2의 옥탑 행과 같음(산술 대조이며 법적 산입 규칙 검증이 아님). 이 합은 한 필지 한 허가의 인허가 기록 합계로, 캠퍼스 전체·다른 필지·현재 준공 면적이 아님. 전체 열에도 높이·좌표·표고 열은 없음. 이 방은 316행 결합표를 스크립트로 읽어 28개 동의 건축면적이 비교표와 모두 같음을 확인함. 동명 접미사를 P번호·모델 상자·좌표에 그대로 대응시키지 않으며, 행 수를 층수로 세지 않고, 면적으로 층수·높이를 역산하지 않음. 한 행(6,412.72 / 51,410.10㎡)은 표제부의 기술동-2와 수치가 같음. 기술동-2가 모델의 어느 박스인지는 확정하지 못함. 위성영상 재판독(v7.13) 결과 기술동 본체는 약 81 × 42 m(약 3,400㎡)로 대장의 기술동-2 건축면적의 절반 수준임(같은 건물인지 여부는 정하지 않음). 공공데이터(소독 의무 대상 시설)에 '기술동'과 '기술2동(지하 1층~3층 식당)'이 따로 있고, 카카오맵 '기술동 입구'는 P1 북서쪽 (-387, 2472).  카카오맵 '사무2동' 좌표는 사무2동 박스 안에 있음. 기술동-2가 사무2동·기술동 주차타워·기술동 가운데 어느 것인지, 또는 그 밖의 건물인지는 정하지 않음(건축면적 비교: 대장 6,412.72㎡ / 모델 상자 OFF-T 약 3,400㎡, OFF-2 약 6,020㎡, WA 약 7,050㎡). 11층·67.90 m는 이 동의 값이며 P2 FAB의 층수·높이로 쓰지 않음. 2단지(고덕동 1696) 대지면적은 804,237.8㎡이고 두 지번 표시값의 합은 2,638,077.3㎡ — 외필지 37개의 범위와 캠퍼스 경계는 확인하지 못했으며, 공식 289만㎡나 고시의 산업시설용지 2,861,212.4㎡에 맞춰 모델 경계를 바꾸지 않음. 2026-11-14 이 방의 건축HUB 연결 도구로 1695·1696 표제부를 다시 조회해 위 수치가 그대로임을 확인(요청 URL·원응답 파일은 보유하지 않음). 사용승인일은 가동일이 아니며, 허가·착공일(2015)은 이 동의 착공일로 쓰지 않음 층별개요 전체 열의 구조·용도(Codex 검토 2026-11-15): FAB 4개 동의 층 기록은 주로 철골철근콘크리트구조이고 FAB동-2에는 철골콘크리트구조 기록도 있음. CT동은 지상 1층(645.92㎡)이 일반철골구조, 지하 1층(17,157.64㎡)이 철골철근콘크리트구조. CT동-2는 지상 1층(187.93 + 329.30㎡)과 지하 1층(9,666.11 + 11,073.80㎡) 기록이 모두 철골철근콘크리트구조(v7.30은 두 동을 한 문장으로 묶어 CT동-2의 지상을 일반철골이라고 잘못 요약했음 — 공식 자료가 아니라 이 모델 요약의 오류, v7.31 정정). 층별 주용도는 모두 '기타공장'이라 옥탑·지하의 세부 용도는 구분되지 않음. 층 기록 면적은 FAB동 지하 364.72㎡·지상 596,083.41㎡, FAB동-2 지하 23,919.66㎡·지상 560,307.25㎡·옥탑 6,925.11㎡, FAB동-3 지하 35,052.29㎡·지상 674,755.13㎡·옥탑 9,166.75㎡, FAB동-4 지상 700,171.00㎡·옥탑 11,261.11㎡(지하 기록 없음 — 지하가 없다는 뜻이 아님), CT동 지하 17,157.64㎡·지상 645.92㎡, CT동-2 지하 20,739.91㎡·지상 517.23㎡. 구조 명칭은 부재 단면·기둥 간격·층고를 주지 않으며, 모델의 구조 부재는 개념 요소 그대로임.",
        gov_register_parcels="고덕동 지번별 대장 조회 결과: 1695(캠퍼스 본 필지) 표제부 2행, 1696(2단지) 표제부 1행(주차동) — 조회 결과의 행 수이며 필지의 건물 수가 아님, 1697·1698·1699·1725·1727·1728 결과 없음. 사무1동·사무2동·사무3동·사무복합동·복지동과 FAB동은 표제부 조회 결과에 나오지 않음(건축인허가 동별개요에는 대형 동 행이 있음 — gov_register_campus 참조)",
        map_crosscheck="구글 지도와 카카오맵 비교(2026-11-12): 사무복합동·GATE2·GATE3는 15 m 안에서 일치. GATE5는 카카오맵 (494, 828)과 구글 (306, 686)이 약 235 m 달라 두 지점을 모두 표지로 둠(어느 쪽이 맞는지 미확인). 구글에만 있는 장소: 기술동, P2 주차타워·야외주차장(고덕동 1696). 공공데이터(소독 의무 대상 시설): T1카페테리아 = 기술동 1층, T2카페테리아 = 기술2동 지하 1층~3층 — 기술동과 기술2동은 서로 인접한 별개 건물로 등록. 네이버 지도는 접속 차단으로 확인하지 못함",
        planned="공시(2026-07): 평택2단지 부대동 그룹2 — 자원순환센터·유수분리기·방재센터 3개동, 연면적 2,774평, 2027-10-31까지. 위치를 알 수 없어 모델에 넣지 않음",
        verified2="2026-11-12 추가 열람: 삼성전자 지속가능경영보고서 2026(전문) — 사업장별 부지·건물 면적 표 없음, 평택 단독 수치 없음(국내 5개 사업장 합계만). 삼성E&A P1 Utility Project 페이지 — 제목과 연도(2018)만 있음. 삼성물산 분기보고서 PDF — 본문을 읽지 못함(바이너리로 반환)",
        reference_press={"P1": "약 24만 평", "P2": "약 25만 평, 감리사(한방유비스) 실적 페이지 '삼성전자 평택 P2' 592,077㎡·지하 1층~지상 8층(2023-11-14 게시, Astra가 원문 확인) — FAB·복합동·UT의 구분과 단일 동 범위가 적혀 있지 않아 P2 FAB 단독의 법정 층수·연면적으로 확정하지 않음", "P3": "약 100만㎡"},
        check="철회(v7.25): 이전 판은 12만 8,900㎡를 모델 평면(552 × 204 m = 약 11만 2,600㎡)으로 나눠 '모델 평면이 약 13% 작을 수 있음'이라고 적었음. 12만 8,900㎡의 대상 범위가 확정되지 않았으므로 이 비율은 치수 검증에 쓰지 않음. 모델 평면은 위성영상 판독값 그대로임"),
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
META["infra_plan"] = "산업단지 계획값(경기도 고시 제2026-189호, 2026-07-30, 10~12쪽 — Codex가 고시문을 대조, 이 모델 작성 과정에서는 직접 열지 못함). 전력수요량 3,324,190 kVA(유효전력 MW가 아님) / 용수공급계획 478,950 m³/일 = 공업용수 473,485 + 생활용수 5,465 / 오·폐수 449,211 m³/일(산단 밖 시설분 8,997 포함) / 공공폐수처리시설 규모 450,000 m³/일(산업단지 지원 계획의 값) / 통합 처리 후 서정리천 방류 계획. 모두 산업단지 전체의 계획값이며 특정 팹의 실제 소비량·가동 능력·준공 용량이 아님. 관경·설비 대수·위치로 바꿔 쓰지 않음. 정수(공정용수), 초순수, 사내 그린동 전처리, 산업단지 공공폐수처리시설은 서로 다른 단계임. 삼성E&A 실적 페이지의 평택 정수장 130,000 m³/일(1단계 증설 뒤 145,000 m³/일)은 공정용수 처리 규모이며 초순수 생산 능력이 아님(Codex와 역산분석 방이 페이지를 확인)"
META["infra_plan"] += ' 별도 문서인 공공폐수처리시설 기본계획 통합 고시(한강유역환경청고시 제2026-15호, 제36항 — Astra가 국가법령정보센터 본문과 첨부 PDF 45쪽을 대조): 고덕 처리능력 340,000 m³/일 = 1단계 120,000 + 2단계 67,500 + 3단계 92,500 + 4단계 60,000, 공동처리구역 3,905,709.9㎡, 오·폐수 배출량 예측 337,390 m³/일. 기본계획에 실린 처리능력이며 준공량·실가동량이 아님. 같은 배분은 제2025-370호(2025-09-25) 본문에도 실려 있고, 제2024-380호(2024-09-27)까지의 판에는 102,000 / 67,500 / 67,500 / 103,000으로 실려 있었음. 고덕의 이 배분이 처음 승인된 날짜는 확정하지 못함. 제2026-15호의 개정 이유는 다른 산업단지 건이므로 2026-01-13을 고덕 변경일로 쓰지 않음. 340,000과 450,000은 서로 다른 문서의 값으로 나란히 두며, 한쪽이 다른 쪽을 대체·승인했다는 관계는 확인되지 않음. 건물의 형태·동 수·배치 근거로 쓰지 않음'  # v7.26
SOURCES["GG_2023_181"] = ("경기도 고시 제2023-181호(2023-06-30) 평택 고덕국제화계획지구 일반산업단지계획 변경승인 — PDF 10쪽 오·폐수 처리계획, 11쪽 제8항 지원계획(폐수종말처리시설 345천 → 450천 m³/일)", "https://www.eum.go.kr/web/gs/gv/gvGosiDet.jsp?seq=570591")  # v7.37
META["infra_plan"] += " 산업단지 지원계획의 450,000 m³/일 연혁(v7.37 — Astra가 경기도 고시 4건의 공식 첨부를 받아 대조, Codex가 2022-168·2023-181의 해당 쪽 렌더를 직접 확인, 이 방은 두 검토문만 읽음): 제2022-168호(2022-07-29, PDF 11쪽 제8항 지원 대상시설) 폐수종말처리시설 345천 m³/일 → 제2023-181호(2023-06-30, PDF 11쪽 제8항) '기정 345천 → 변경 450천 m³/일'로 변경을 직접 표기 → 제2024-1호(2024-01-05)·제2025-121호(2025-03-14) 450천 m³/일(지원계획 변경 없음) → 제2026-189호 450천. 따라서 450,000은 늦어도 2023-06-30 고시에 나타남(그 이전 문서 전체를 본 것은 아니므로 '최초'로 단정하지 않음). 같은 2023-181호 PDF 10쪽 오·폐수 처리계획: 계획 발생량 445,939 m³/일 = 생활오수 4,503 + 산단 내 산업폐수 435,711 + 산단 밖 평택 에코센터 5,725(기정 324,395) — 산단 밖 시설분이 들어 있어 삼성 단독 발생량이 아니며 실측 유입량도 아님. 위 2026-189호의 449,211 m³/일(산단 밖 8,997 포함)과는 고시 시점이 다른 계획값임. 산단 고시의 직전 값은 345,000이며 기본계획의 340,000과 다름 — 두 값을 같은 것으로 보거나 차이를 오기로 고치지 않음. 이 고시들은 450,000의 단계별 구성(1~4단계 용량)을 주지 않으며, 기본계획 340,000을 대체한 승인인지, 실제 준공·처리 능력인지도 확인되지 않음. 시설 동 수·배치·설비 수에는 쓰지 않음."  # v7.37
SOURCES["MCEE_WWTP_2024"] = ("기후에너지환경부 '2024년 말 공공폐수처리시설 운영현황'(정책자료 8527, XLSX) — 평택고덕국제화 33행: 시설용량·공법·2024 유입·방류·재이용량", "https://mcee.go.kr/home/web/policy_data/read.do?menuId=10260&seq=8527")  # v7.40
SOURCES["SUVIOL_REF"] = ("수비올 공식 사업실적 — '평택시 고덕일반산업단지 공공폐수관리 용역', 용량 187,500, 하이브리드 MSBR/CSBR", "https://suviol.com/m221.php?pg=4")  # v7.40
META["wwtp_operations_2024"] = "평택고덕국제화 공공폐수처리시설 2024 운영 통계(v7.40, 형상 변경 없음). 출처: 기후에너지환경부 '2024년 말 공공폐수처리시설 운영현황' XLSX(정책자료 8527, SHA-256 6a8f8671…; Codex가 받아 검토하고 Sol이 독립 검산, 이 방이 같은 파일을 열어 아래 셀을 직접 확인). 공개 시트 '운영현황(2024년 기준)' 33행(F33 평택시, G33 평택고덕국제화). 대상: 2024-01-01~12-31(B3), 2023-12-31까지 준공보고된 시설. 시설용량 187,500 m³/일(AI33), 주처리 공법 하이브리드 MSBR(AK33), 총인처리 공법 Actiflo(AM33), 연간 총유입량 56,362,100 m³(AQ33, 일평균 153,994.81 m³/일 = 366일로 나눈 값), 일최대·최소 유입 187,285·84,362 m³/일(AS33·AT33), 연간 총방류량 53,711,408 m³(AU33, 일평균 146,752.48), 일최대·최소 방류 195,189·79,252 m³/일(AW33·AX33), 평균·최대 가동률 82.1%·99.9%(AO33·AP33), 연간 재이용량 1,308,848 m³(AZ33, 재이용률 2.3% — AY33). 셀에는 수식이 없는 저장값이며, 일평균·가동률은 재산술로 일치함. 읽는 법: 외부 공공처리시설의 그 해 보고값이며 삼성전자 사내 그린동 처리량, 팹별 배분, 2026년 현재 용량이 아님. 기본계획 340,000·산단 지원계획 450,000 m³/일은 계획값으로, 187,500과의 차이를 미시공 용량이나 단계 수로 해석하지 않음(시점·범위가 대응되지 않음). 공급사 자료: 수비올 실적표는 같은 용량 187,500과 '하이브리드 MSBR/CSBR'를 적음(표기를 각각 보존), DL 2013 수주문은 1단계 계획 102,000 m³/일·하이브리드 MSBR, Actiflo는 Veolia의 일반 공법 설명(미세모래 가중 응집·침전)일 뿐 고덕의 장비·대수·크기는 확인되지 않음. 모델 연결: 시설 단위 값이므로 A동(PUB-WWTP) 주석에만 이 항목을 가리키고, B·C동과 처리조 구역에 용량을 나누거나 같은 값을 넣지 않음. 같은 시트의 수질 열은 머리글(BQ7)이 '2023년도 연간 유입 및 방류수질 현황'이라 제목·대상기간(2024)과 연도 표기가 달라 귀속 연도가 확인될 때까지 수질 값을 쓰지 않음(오류로 판정하지 않음, 역산 담당과 공동 검토 중)."  # v7.40
META["wwtp_operations_2024"] += " 단계별 설치 현황(v7.41 — 같은 부처의 2023년도 운영현황 XLSX, 정책자료 8332, SHA-256 7e310030…; 이 방이 Sheet1 28행 '평택고덕국제화'를 직접 읽음): 1단계 착공 2013.12.26·준공 2018.12.31·설치용량 120,000 m³/일·하이브리드 MSBR(AT28~AW28), 2단계 착공 2021.03.01·준공 '2023.1.15'(원문 표기)·설치용량 67,500 m³/일·공법 'A2O+SBR'(BB28~BE28), 단계별 설치용량 합계 187,500 m³/일(AS28). 2단계 공법이 시설 대표 공법(하이브리드 MSBR)과 다르게 적혀 있음 — 원문대로 둠. 준공일은 시설 공사 단계의 준공이며 삼성 팹 가동과 무관. 같은 행의 사업비·위탁 계약비·연락처·수질 값은 넣지 않음(비용을 물량·삼성 부담금으로 읽지 않는 원칙). 2023년 연간 총유입량 53,276,717 m³(DG28, 일평균 145,963.61 m³/일)도 같은 시설 단위 보고값임."  # v7.41
SOURCES["MCEE_WWTP_2023"] = ("기후에너지환경부 '2023년도 공공폐수처리시설 운영현황'(정책자료 8332, XLSX) — 평택고덕국제화 28행: 단계별 착공·준공·설치용량·공법", "https://mcee.go.kr/home/web/policy_data/read.do?menuId=10260&seq=8332")  # v7.41
META["imagery_geometry"] = "공개 위성영상(Esri World Imagery, 줌 18)은 수직 촬영이 아님(v7.27 판독). 근거: 팹 동측의 폭 29~37 m 띠에 벽면 외장 그래픽이 보임. 대장 높이 32.85 m·33.45 m인 고덕 변전소 두 동(표제부 공식 원본으로 Codex가 확인 — 어느 상자가 어느 동인지는 미확정이고 대장 PK는 인허가 동 PK와 직접 이어지지 않음)에서 옥상 동쪽에 벽면이 약 10~12 m 폭으로 보여 '비침 폭 ÷ 높이'가 약 0.30~0.36 — 이를 팹 띠(28~37 m)에 적용하면 약 80~120 m가 나오지만, 변전소 상자와 대장 건물의 대응이 확정되지 않았고 촬영 기하도 알 수 없으므로 이 값은 탐색치일 뿐 팹 높이의 독립 근거나 83 m의 검증이 아님. 영향: 영상의 옥상 윤곽으로 그린 상자는 서쪽 가장자리가 높이의 약 0.3배만큼 서쪽으로(남북으로는 약 0.1배) 치우쳐 있을 수 있음 — 83 m 팹은 약 28 m, 35 m 건물은 약 11 m, 낮은 건물·도로·지반은 영향이 작음. 동쪽 가장자리를 벽 밑동으로 읽은 상자는 동서 폭이 같은 만큼 넓게 그려졌을 수 있음. 이 판에서는 좌표를 고치지 않음. 영상 메타데이터(2026-11-15 Astra가 Esri 공식 메타데이터 레이어를 P1~P4·주차동·변전소 2동의 7개 지점과 캠퍼스 범위로 조회): 모두 같은 레코드로 촬영일 2025-12-22, 원자료 해상도 0.5 m, 원자료 코드 WV02, 제공자 Vantor. 촬영각(off-nadir)·방위·정사 보정 방식은 공개 메타데이터에 없음. 위치 정확도 항목 8.47 m는 신뢰수준 정의를 확인하지 못해 보정량으로 쓰지 않음. 2단지 주차동도 같은 레코드이므로 v7.27에 적었던 '타일마다 촬영일이 다를 수 있음'은 이 자료로 뒷받침되지 않음(주차동은 높이 약 21 m라 비침 폭이 작아 이 방이 판독하지 못한 것일 수 있음). 이 방의 모자이크는 2026-11-12~13에 내려받은 줌 18 타일 990장(행 101992~102021, 열 223578~223610)이며 Astra 조사점 7개가 모두 이 범위 안에 있음 — Astra가 이 7개 지점의 타일을 현재 공식 서비스 타일과 대조해 바이트 수와 SHA-256이 모두 같음을 확인함(나머지 983장, 재압축한 모자이크 전체, 촬영각·정사 보정은 확인한 것이 아님). 평면 판독 ±3 m는 영상 위의 판독 정밀도이며 절대 위치 정확도가 아님. 동쪽 28 m·북쪽 8 m 같은 임의 보정은 하지 않음. 다른 공식 영상과의 비교(v7.31): 국토지리정보원 2025년 정사영상(도엽 37713083, 사업 '수도권남부1권역 25cm', DEM 사용 — 촬영일은 공개 메타데이터에 없음)의 공개 미리보기를 Codex가 공식 화면에서 열어 캡처했고, 이 방이 그 캡처에서 P1 지붕 가장자리를 화면 픽셀로 읽음. 화면 축척을 Esri 판독 폭 201 m로 잡으면 P1 동서 길이는 약 530 m(±9 m)로, 옥상 본체 519 m와 띠 포함 549 m의 사이여서 어느 쪽인지 가르지 못함. 이 값은 Esri 판독 폭에 기댄 것이므로 독립 길이 검증이 아님. 미리보기의 P1 동쪽 끝에는 Esri의 밝은 띠에 해당하는 면이 보이지 않고 어두운 띠가 보이나 그림자·벽면·지면 가운데 무엇인지 판정하지 못함. 정사영상의 지붕 윤곽을 지상 외곽으로 쓰지 않으며, 캡처 영상은 싣지 않음. 축척이 기록된 두 번째 캡처(v7.32): Astra가 같은 공개 미리보기에서 지도 상태를 함께 기록해 캡처(1.2021 투영 m/화면픽셀, EPSG:5179, 회전 0). 북쪽 팹(모델 P1) 지붕의 밝은 테두리 사이 동서 거리는 Codex 531.3~547.0 m, Astra 526.5~543.4 m(수동 선택 범위이며 오차 구간이 아님), 이 방의 밝기 단면 판독 약 539 m(가장자리 ±1.5 px). Esri 영상의 같은 밝은 테두리 기준 거리는 옥상 본체 약 522 m, 띠 포함 약 549 m. 남북은 이 방 판독으로 정사영상 약 210 m, Esri 약 203 m. 길이÷폭은 정사영상 약 2.57, Esri 옥상 본체 약 2.57, Esri 띠 포함 약 2.70 — 축척에 무관한 이 비는 옥상 본체 쪽과 맞지만, 같은 캡처 한 장을 읽은 값이고 남쪽 가장자리에 밝은 선이 여러 개여서 어느 선이 같은 가장자리인지 독립 확인이 필요함. 항공 정사영상은 지표 DEM으로 보정되면 높은 지붕이 약간 확대되어 보일 수 있어(정사영상의 길이·폭이 Esri보다 각각 약 3% 큼) 길이 하나만으로는 어느 쪽인지 판정하지 못함. 지붕 테두리는 지상 벽선이 아니므로 이 비교로 띠를 지우거나 상자를 옮기지 않음."  # v7.27
META["permit_basic_summary"] = "건축HUB 건축인허가 기본개요(Codex가 2026-11-15 공식 화면에서 전체 열로 내려받은 웹 내보내기, 2026-09 기준, API 원응답 아님 — 이 방은 Codex 검토 문서로 읽음): 고덕동 1695 122행·1696 126행. 1695 주 허가: 대지면적 1,833,839.50㎡, 건축면적 935,346.60㎡, 연면적 4,713,467.42㎡, 주건축물 52·부속 18, 허가 2015-02-27, 착공 2015-03-11, 표시 사용승인일 2026-09-21. 동별개요 70개 동 합과 연면적은 같고 건축면적은 304.96㎡ 다름(원인 미확정). 1696 주 허가: 대지면적 937,899.70㎡, 건축면적 503,106.23㎡, 연면적 2,160,822.49㎡, 주건축물 14·부속 5(19개 동), 허가 2018-05-29, 착공 2018-08-07, 표시 사용승인일 2026-01-05. 1696은 동별개요가 20개 동·연면적 합 2,321,855.03㎡로 기본개요와 다름 — 건축면적·연면적의 차는 주차동 값과 같지만 용적률 산정 연면적의 차는 주차동 값과 달라 '주차동을 빼면 맞는다'고 할 수 없음. 어느 쪽도 현재 완공 총량·동 수로 쓰지 않음. 날짜는 허가 단위의 현재 스냅샷이며 개별 동의 준공·가동일이나 변경 차수별 날짜가 아님. 같은 대지면적이 여러 허가에 반복되므로 허가 간 대지면적을 더하지 않음. 이전 판 대장 표제부의 1696 대지면적 804,237.8㎡와 다른 값이며 경계·시점 차이는 확인하지 못함."  # v7.28
META["imagery_geometry"] += " 지상 외곽의 다음 공개 경로(v7.36): 국토교통부 GIS건물통합정보 — 공식 컬럼정의서(Astra 확인)상 SHP 파일(AL_D010)에 건물 도형, 높이(m), 건물명·건물동명, 지상·지하 층수, 건축물ID·참조체계연계키 필드가 있고, 원천 설명은 수치지형도 2.0 건물 레이어와 건축물대장 속성의 통합임. 고덕동 1695·1696의 실제 레코드는 아직 받지 않아(정상 로그인 후 다운로드 또는 발급 키가 필요한 단계) 수록 여부·값·도화 기준(외벽선인지 지붕선인지)은 확인되지 않았고, 이 모델은 그 자료로 아무것도 바꾸지 않았음."  # v7.36
META["imagery_geometry"] += " 국토지리정보원 국가기본도 건물 대조(v7.39, 형상 변경 없음 — Codex가 사용자 기존 VWorld 로그인으로 정상 다운로드: '국가기본도_건물_경기.zip', 기준 2026-07, SHA-256 750d3472…, 12개 멤버 CRC 통과, EPSG:5179, 3,328,154 도형; 공식 테이블정의서로 필드 확인; 모델 좌표식으로 변환해 718개 후보 중 각 팹 사각형과 IoU가 가장 큰 도형을 고르고 Astra가 같은 4개를 독립 재현; 이 방은 두 검토문과 원좌표를 뺀 검산 JSON을 읽음, 원 파일은 열지 않음). 모델 P1~P4 자리의 후보 도형: 방향 기준 긴 변 × 짧은 변 521.92 × 204.68 / 530.65 × 204.58 / 640.92 × 204.38 / 647.71 × 203.40 m, IoU 0.86 / 0.90 / 0.90 / 0.88(둘째 후보는 모두 0.003 미만), 긴 변 방향은 동서에서 0.1° 이내. 모델 사각형(549×201 / 552×204 / 651×208 / 654×208 m)과 비교하면 길이 차는 주로 서쪽 끝에서 생김(후보 서쪽 변이 모델보다 동쪽으로 31.4 / 19.4 / 16.2 / 17.1 m), 동쪽 변 차이는 +4.4 / −1.9 / +6.1 / +11.0 m(+는 동쪽), 남·북 변은 모두 북쪽으로 5.7~11.2 m 치우침. 모델 동측 띠(-endblk 동쪽 구간)는 후보 도형에 91.0~96.3% 덮임 — 즉 이 지도 도형은 동측 띠 자리를 건물 안으로 그림. 읽는 법과 한계: 수정측량방법 코드 P=사진측량이며, 이 정의만으로 도형이 지상 외벽선인지 지붕선인지 정해지지 않음. 객체변동 일시는 P1·P2 후보 2022-11-10, P3·P4 후보 2024-04-13이고, P4 후보의 건물 구분은 BDC007(공사중건물)이라 2026년 현재 상태가 아님. 건물층수 필드(P1 후보 5, 나머지 1)와 높이 필드 없음 — 팹의 층수·높이를 바꾸지 않음. 도형에는 P번호·동 이름이 없어 위치로만 대응시킨 것. 모델 국지 좌표는 근사 아핀 변환이므로 수 m의 차이는 좌표식 자체의 오차일 수 있음. 따라서 이 결과는 '동측 띠가 벽면 비침이라 지워야 한다'는 쪽을 뒷받침하지 않으며(지도 도형이 그 자리를 덮음), 서쪽 끝·북쪽 치우침의 원인(영상 사각 촬영, 좌표 변환, 도화 기준, 시점 차)도 정해지지 않음. 상자는 옮기거나 줄이지 않음. 이용 조건이 목록에 '지정 없음'으로 표시돼 원 도형·비교 그림은 공개 패키지에 넣지 않고, 여기에는 원좌표 없는 비교 수치만 적음."  # v7.39
SOURCES["NGII_BASEMAP_BLDG"] = ("국토지리정보원 국가기본도 건물(경기, 기준 2026-07, VWorld 공식 다운로드 — 원 도형은 이용 조건 미지정으로 재배포하지 않음, 비교 수치만 사용)", "https://www.vworld.kr/dtmk/dtmk_ntads_s002.do?svcCde=MK&dsId=20250121DS00011")  # v7.39
META["p_number_layout"] = 'P번호 배치의 교차 확인(v7.32): 삼성증권 리서치 보고서(2025-10-23, 12쪽 — Codex가 PDF를 렌더해 확인)의 위성사진 표기는 북에서 남으로 P1·P2·P3·P4이고 P5·P6을 그 서쪽에 표시해, 이 모델의 북→남 P1~P4 배치와 같음. 증권사 자체 표기이며 삼성전자의 공식 배치도가 아니고 사진 촬영일도 적혀 있지 않음. OSM 이름 태그(PS-1~PS-4)는 이 배치와 맞지 않으며 채택하지 않음. 인허가 동 이름(FAB동~FAB동-4)과 P번호의 대응은 여전히 면적 유사 후보일 뿐임.'  # v7.32
SOURCES["SAMOO_P2"] = ("삼우종합건축사사무소 공식 실적 'P2-Project': 평택시, Industrial, 연면적 828,992㎡, 지상 8층·지하 1층, Project Completion 2021 — 대상 동 범위는 적혀 있지 않음(2026-11-15 이 방과 Codex가 각각 열람)", "https://samoo.com/home/works/view.do?cntntsSn=41603")  # v7.33
SOURCES["POSCOANC_P5"] = ("포스코A&C 공식 실적 959번 'Pyeongtaek P5 Ph1 Semi-Production Facility CM/CS': 서비스 CM, 발주처 Samsung Electronics, Year 2028(미래 연도 표기) — Codex가 원문 확인", "https://poscoanc.com/en/project/portfolio_view.do?num=959")  # v7.33
SOURCES["EA_SR2018"] = ("삼성엔지니어링 2018 지속가능경영보고서(인쇄 30쪽): '삼성전자 평택 P1 초순수 프로젝트'에 전기적 탈이온법(CEDI) 적용 — Codex가 원문 확인", "https://www.samsungena.com/filesview/2018%20Samsung%20Engineering%20Sustainability%20Report_Korean.pdf?folder=%2Fupload%2Fpublishing%2F&storedfile=9913c016cac9490d96d7b1645da90ee1.pdf")  # v7.33
SOURCES["SAMOO_INSIGHT"] = ("삼우종합건축사사무소 공식 Insight 'High-Tech Industrial Facility Design Services'(2025-08-07): Samsung Electronics Pyeongtaek Campus를 마스터플래닝 사례로 명시 — Astra가 원문 확인", "https://samoo.com/home/about/insightview.do?bbsSn=49635")  # v7.33
SOURCES["SHINSUNG_2105"] = ("신성엔지니어링 공식 실적표 '2015 - 2019'(ishinsung.com 2105): 평택 P2L Ph1 2공구 공조기 납품·설치(AHU), P2L Ph1 DCC(드라이코일), P-PJT Ph-4 DCC, P PJT Ph2 OAC — 계약년도 표", "https://ishinsung.com/product/partner/2105?lang=ko")  # v7.34
SOURCES["SHINSUNG_2111"] = ("신성엔지니어링 공식 실적표 '2020 - 2022'(중앙공조, ishinsung.com 2111): 평택 P2L Ph2·Ph4 AHU, EUV V2 AHU, V2-Ph2 EUV동 OAC, EUV 하부마감 DCC, P1L V2L DCC, P3L Ph1~Ph3 DCC, P3L 그린동 AHU, P3L 인프라복합동 ph3 DHC — 계약년도 표", "https://ishinsung.com/product/partner/2111")  # v7.34
SOURCES["SHINSUNG_2119"] = ("신성엔지니어링 공식 실적표 '2023'(중앙공조, ishinsung.com 2119, 게시 2024-07-08): 평택 P4 Ph1 2공구 항온항습기·AHU 납품 설치, P3L Ph2·Ph4 DCC, P3L 그린동 Ph4 AHU 설치공사 — 계약년도 표", "https://ishinsung.com/product/partner/2119")  # v7.34
SOURCES["KENSOL_H1_2026"] = ("케이엔솔 제38기 반기보고서(2026-08-14, 기준일 2026-06-30) — 주요 수주계약 현황(전기 매출액 5% 이상 계약만), 수익 주석(연결 17·별도 16), 사업의 내용(OAC=외조기, 시스템실링 모듈화 공법의 평택 적용)", "https://dart.fss.or.kr/dsaf001/main.do?rcpNo=20260814003241")  # v7.35
SOURCES["KENSOL_Q1_2026"] = ("케이엔솔 2026년 1분기보고서(KIND 공시) — 주요 수주계약 현황과 수익 주석(평택 P3·P4 모듈 S/C·OAC 계약)", "https://kind.krx.co.kr/external/2026/05/15/002134/20260515004740/11013.htm")  # v7.35
SOURCES["KENSOL_ICR"] = ("케이엔솔 공식 ICR(산업용 클린룸) 브로슈어 PDF — Suspended Ceiling System 연결 위계, 모듈 설치 공법, OAC 구성(일반 제품 설명, 평택 제원 아님)", "https://k-ensol.com/wp-content/uploads/2024/11/KE_ICR_k-web.pdf")  # v7.36
SOURCES["ANSEN_PC"] = ("안센 공식 'PC 공법·PP SHEET' 페이지 — 평택 사업장 P3 WWT·UPW(Acid water, DI water) PCPL 공법 적용 완료, 2023 삼성전자 평택 고덕 P3 UPW 복합 수조동 PP방수시트 ST2 신축공사(삼성물산 건설부문) 등 실적 표", "https://www.ansenpp.com/pc-%EA%B3%B5%EB%B2%95/")  # v7.38
SOURCES["ARMACELL_CL1"] = ("Armacell ArmaFlex Class 1 제품 브로슈어(한국어 PDF) — 31쪽 납품 실적에 평택 삼성 P2·평택 삼성전자 P3, 5~8쪽 일반 재료 정보(NBR계 고무발포 단열재)", "https://www.armacell.com/sites/default/files/2025/01/24/ArmaFlex%20Class%201%20-%20Product%20Brochure%20-%20ko-KR.pdf")  # v7.38
META["construction_material_records"] = "시공 자재 공급사 실적(v7.38 신설, v7.41 갱신, 형상 변경 없음). 시공 방법 근거 22건·자재·장비 근거 31건(main f8aceb2 기준 — v7.39 데크플레이트 계약 공시 3건 M20~M22, P5 근거 4건 M23~M26: 덕신이피씨 P5 데크플레이트, 제일테크노스 P5 FAB 데크 설치 2공구, 삼일씨엔에스 P5 FAB2 PC 부재 제작·납품, 광명전기 P5 전동기제어반(MCC), 이어서 M27~M31: 삼일벤드 배관 자재 납품 실적, 아이에스동서 P3·P4 154kV PC 제작·납품, 대양이앤에이 P1·P3·P4 내화·단열 포트폴리오, 삼성물산·에스와이 외장패널 공동연구(평택 미지정), 삼화 P2 UT 내부 바닥 비노출 우레탄 방수, 공종 CM-S16 MFR 2022-08 평택 내화뿜칠·볼팅 로봇 시연, CM-S17 삼일벤드 일반 맞대기용접 관이음쇠 제작 공정)의 영문 안내와 출처 목록은 저장소 docs/construction_methods.md·docs/construction_materials.md(각 sources.json)에 있으며(Codex 작성, Astra 독립 검토), 배포본 docs 폴더에 함께 넣음. 이 모델 데이터에서는 두 건을 meta에 적고, 그중 안센 1건만 이름이 맞는 요소 1개(UT-34-UPW)의 주석·출처에 연결함 — Armacell은 연결할 요소가 없어 meta에만 있음(v7.42 표현 정정: 이전 문구 '두 건만 연결'은 실제와 달랐음). (1) 안센(ansenpp.com, Astra가 본문을 읽고 Codex가 표 행을 다시 추출 — 이 방은 그 추출 결과를 읽음, 페이지는 열지 못함): '평택 사업장 P3. WWT, UPW – Acid water, DI water – PCPL 공법 적용 – 완료', '삼성전자 평택 고덕 P3 복합 수조동 콘크리트 일체형 PP시트(삼성물산 건설부문)', '2023 삼성전자 평택 고덕 P3 UPW 복합 수조동 PP방수시트 ST2 신축공사(삼성물산 건설부문)'. PCPL은 PP 시트를 PC 콘크리트와 일체로 만드는 라이닝 공법(회사 설명). ST2는 원문의 프로젝트 표기이며 재료 등급이나 단계로 읽지 않음. 시트 두께·수지 등급·접합 조건은 실적표에 없고, 같은 회사 일반 제품 비교표의 두께는 P3 설치 두께가 아님. 'P3 UPW 복합 수조동'이 이 모델의 어느 건물인지 확인되지 않아, P3 초순수 개념 상자(UT-34-UPW)에 공급 사실만 적고 위치·크기는 그대로 둠. 같은 페이지의 기흥·화성 수조 사진·도면은 평택 자료로 쓰지 않음. (2) Armacell(공식 PDF, Astra가 HTTP로 받아 31쪽 납품 목록과 5~8쪽 재료 정보를 추출 — 이 방은 그 기록을 읽음): 납품 목록에 '평택 삼성 P2'·'평택 삼성전자 P3'. 같은 문서의 NBR계 고무발포 단열재 설명은 일반 제품 정보이며, 각 현장에 설치된 제품·두께·배관 대상과 대응되지 않음. 이 모델에는 배관 단열 요소가 없어 요소에 연결하지 않음. 단열재는 구조 내화 피복과 다름. 쓰지 않은 것: 일반 카탈로그 값(두께·강도·열전도율 등)을 평택 설계값으로 넣지 않음. 문서 쪽 표기: docs/construction_methods.md 영상 단락의 'high-elasticity'는 77b5c67에서 자재 안내 M10과 같은 'high-modulus'로 통일됨. 데크플레이트 계약(제일테크노스·덕신 — 'FAB 2기' 2건, 'P4 신축공사 1공구' 1건, 모두 삼성물산 상대)은 docs에만 두고 모델 바닥 요소의 종류·두께·면적에 쓰지 않음. 'FAB 2기'는 계약명 표기이며 모델 P2로 확정하지 않음. P5 근거 4건은 계약 범위·기간의 근거일 뿐 데크 종류·두께·면적, PC 부재 종류·강도·수량, MCC 반 수·위치를 주지 않으며, 모델의 P5는 부지 패드(PAD-P5)뿐이라 요소에 연결하지 않음. v7.41 추가분(M27~M31·CM-S16·S17)도 모델 요소에 연결하지 않음: 154kV 변전 관련 동과 PC 실적의 대응, P2 UT 바닥 방수의 층·면적, 내화·단열의 팹별 공종이 원문에 없음. 같은 판에서 docs/campus_systems.md(삼성 공식 평택 무선랜 사례, 초기 한 라인 시점의 일반 통신 항목만, 보안 구성요소 제외)가 README에서 연결되며, 모델에는 통신 장비·위치·배선을 만들지 않음. 말뚝 시험 용역·SB TECH 이중마루 자료는 별도 docs 후보로 남아 이 집계에 들어 있지 않음."  # v7.38
META["permit_link_corridors"] = "인허가상 연결통로 기록(v7.36, 형상 변경 없음). 건축HUB 인허가 동별·층별개요(2026-09 기준, 전체 열 웹 내보내기 — Codex가 원 JSON 4개를 허가 PK·동 PK로 다시 결합해 확인, 이 방은 결합 CSV와 Codex의 원 JSON 대조 결과를 읽음)의 두 주 허가에 이름이 '연결통로' 계열인 부속건축물(용도 공장) 6동이 있음: 고덕동 1695 — '연결통로'(트러스구조, 건축면적 248.31㎡, 연면적 259.79㎡, 기록된 지상층 1·3), '연결통로-2'(일반철골구조, 515.39㎡/515.39㎡, 지상 3), '연결통로-3'(일반철골구조, 2,751.79㎡/3,431.43㎡, 지상 1·2·3); 고덕동 1696 — '연결통로'(트러스구조, 188.53㎡/1,153.20㎡, 지상 3), '연결통로-2'(일반철골구조, 1.83㎡/295.32㎡, 지상 3), '연결통로-3'(일반철골구조, 1,581.59㎡/2,234.86㎡, 지상 1·2·3). 층별 원 행은 19개이고 동마다 층별 면적 합이 연면적과 같음. 읽는 법: 층 번호는 '해당 연결통로 기록에 지상 3층 행이 있음'이라는 뜻일 뿐, 어느 팹의 몇 층에 접속하는지를 뜻하지 않음. 6개 기록이 6개의 서로 다른 실물 구조물인지 확인되지 않았고, 모델의 브리지 상자(BR-…)와의 대응도 없음. 1695·1696 두 지번의 '연결통로-2'(층 면적 293.49㎡)와 '연결통로-3'(1층 323.20㎡·2층 42.24㎡·3층 443.94㎡)에 같은 값이 반복되며, 원인(같은 구조물의 이관·표준 설계 등)은 확인되지 않았고 오류나 중복으로 보지 않음. 건축면적과 연면적의 차이를 교각·상공 점유 면적으로 해석하지 않음. 같은 허가에 '보행자통로' 계열 4동도 있으나 출입 동선이므로 위치·구성은 다루지 않음. 이 기록으로 브리지의 높이·층·위치·용도를 바꾸지 않음."  # v7.36
META["module_oac_records"] = "모듈 공법·외조기 공급사 공시(v7.35, 형상 변경 없음). 케이엔솔(클린룸 OAC·시스템실링 업체) 제38기 반기보고서(DART 20260814003241, 기준일 2026-06-30)를 Astra가 원 HTML로 읽고 Codex가 보존된 HTML 3개 절을 확인한 뒤 별도 수익 주석을 독립적으로 다시 받았으며(v7.36 표현 정정), 이 방은 두 검토문, 선택 행 JSON 7개, 사업의 내용 본문 텍스트를 읽음(DART 화면은 열지 않음). 주요 수주계약 표(전기 매출액 5% 이상인 주요 계약만이므로 전체 공급 목록이 아님)의 평택 5행, 모두 삼성물산 발주: 'P3-PJT PH4 모듈 S/C 공사', 'P4-PJT Ph1 Module OAC 제작납품', 'P4-PJT PH2 모듈 S/C 공사', 'P4-PJT PH3 모듈 S/C 공사', 'P4-PJT PH3 OAC 제작납품'. 별도 수익 주석에는 'P4-PJT PH4 모듈 S/C 공사' 행도 있으나 주요 계약 표에 없어 발주처·계약 총액은 확인되지 않음. 비교 기간 표에는 'P3-PJT PH2 모듈 S/C 공사'도 있음. 용어: 보고서가 OAC를 외조기(Outdoor Air Conditioner)로 직접 적음. S/C는 계약표에 정의가 없어 원 표기를 유지함 — 다만 같은 보고서의 원재료 표는 품목을 '외조기, System Ceiling 등'으로, 매출 표는 'S/C, OAC 외'로 적어 S/C가 System Ceiling(시스템 천장)의 약칭일 가능성이 높다는 것은 이 방의 읽기임. 사업의 내용은 시스템실링 모듈화 장비를 2019년 말 개발해 '2020년 삼성전자의 평택공장을 시작으로' 현장에 적용 중이라고 적음 — 평택에 모듈 공법이 쓰였다는 회사 직접 근거이나, 어느 팹·층에 썼는지는 적혀 있지 않음. 모델에 연결한 범위: FFU·MAU 장비 종류 설명, P3·P4 FFU 천장면 8개 요소의 주석·출처(P3는 PH4 행, P4는 PH2~PH4 행). 상자의 위치·크기·등급(D)은 그대로. 넣지 않은 것: 계약 금액·진행률(대수·물량·가동률이 아님), 회사 전체 생산 실적(OAC 58대·FFU 16,748대는 회사 전체 실적이며 평택 납품 수가 아님), 모듈 크기·OAC 풍량(공시에 없음; 회사 연구개발 목록의 일반 제품 설명은 평택 납품 모델이 아님), P5(이번에 읽은 범위에서 확인되지 않음 — 공급 부재의 근거가 아님). PH는 프로젝트 단계이며 층 번호가 아님. 일정 주의: 'P4-PJT PH3 모듈 S/C 공사'의 공사기한이 주요 계약 표·연결 주석에서는 2026-12-31, 별도 주석에서는 2026-05-31이고(PT-F008), 'P4-PJT PH3 OAC 제작납품'의 계약일이 1분기 주요 계약 표에서는 2024-09-27, 수익 주석에서는 2023-09-27임(PT-F009) — 두 차이 모두 원인 미확인이며 이 모델은 어느 날짜도 준공·가동일로 쓰지 않음. 진행률 100%는 수익 인식 진행률이며 팹 준공이나 장비 가동의 증거가 아님. 회사 브로슈어(v7.36): 케이엔솔 공식 ICR 브로슈어(PDF 16쪽 — Codex가 4·5·10·13쪽을 렌더해 확인, 이 방은 10·13쪽 렌더를 열어 봄, 이미지는 싣지 않음)는 일반 제품·공법을 설명함. 10쪽 'Suspended Ceiling System': 데크 매립형 인서트 → 1차 행어 볼트 → SQ-Pipe → 2차 행어 볼트 → Mould Bar 격자·연결재(브래킷·다이캐스팅) → FFU·블라인드 패널·조명의 연결 위계. 같은 쪽의 설계 허용치(처짐 2.0 mm 또는 L/240, 행어 볼트 응력 80 MPa)는 회사 제품의 일반 기준이며 평택 설계값으로 쓰지 않음. 4·5쪽: 낮은 작업 높이에서 조립한 뒤 리프트로 올려 설치하는 모듈 공법(그림의 리프트 높이·연동 대수는 장비 능력이며 평택 층고·투입 대수가 아님; 공기 단축 비율은 'S사' 실적 기준이라는 단서가 붙어 특정 팹·계약에 배정하지 않음). 13쪽: OAC의 일반 구성(케이싱·팬·코일·가습·여과)과 Built-up·Module 두 방식 — 계약명이 'OAC'뿐인 행은 어느 방식인지 정하지 않고, 'Module OAC'로 적힌 행만 모듈 방식의 제작·납품 범위로 읽음(치수·설치 위치는 미확인). 이 연결 위계는 모델의 FFU 천장면이 바닥 구조(와플 슬래브)와 다른 매달린 구조임을 설명하는 데 쓰며, 천장면의 높이·범위는 바꾸지 않음."  # v7.35
META["hvac_supplier_records"] = "공조 장비 공급사 실적(v7.34, 형상 변경 없음). 신성엔지니어링(ishinsung.com — 클린룸 FFU 자료의 '신성이엔지'와 회사명이 다르며 같은 회사로 합치지 않음)의 공식 실적표 5쪽(중앙공조 2105·2111·2119, 산업공조 2113·2120 — 출처 키는 평택 삼성 행이 있는 3쪽에만 둠)를 Codex·Astra가 원 HTML로 읽었고 이 방은 선택 행 JSON과 두 검토문을 읽음(원 HTML은 열지 않음). 표의 열은 계약년도·계약처·프로젝트명·ITEM·현장뿐이며, 모델명·풍량·냉동능력·대수·층·위치는 없음. 확인된 것: (1) DCC(드라이코일) — P2L Ph1(2019, 삼성물산), P2L Ph2(2021~2022), EUV 하부마감(2021~2022), P1L V2L(2021), P3L Ph1 1공구(2021)·Ph2(2022~2023)·Ph3(2022)·Ph4(2023), 계약처는 모두 삼성물산. (2) AHU·OAC(외조기) — P PJT Ph2 OAC 납품설치(2017, 삼성전자), P2L Ph1 2공구 공조기 납품(삼성전자)·설치(삼성물산)(2019·2021), P2L Ph2·Ph4 AHU(2021~2022), EUV V2 AHU 납품·설치와 V2-Ph2 EUV동 OAC 납품(2021), EUV Retrofit OAC 케이싱 보수(2022), P3L 그린동 AHU 제작·설치(2022~2023, 삼성엔지니어링), P4 Ph1 2공구 AHU 납품 설치(2023, 삼성물산). (3) P4 Ph1 2공구 항온항습기 납품 설치(2023, 삼성물산). (4) P3L 인프라복합동 ph3 DHC 납품 설치(2022, ITEM '기타') — DHC가 무엇의 약칭인지 표에 정의가 없음. 모델에 연결한 범위: DCC·MAU 장비 종류 설명(vendors_site)과 P2·P3 리턴 에어 샤프트(P2·P3 각 12개 요소), V2 주석. 이 장비 종류가 해당 프로젝트에 공급된 사실의 근거일 뿐이며, 상자의 위치·수·크기는 그대로 개념(D)이고 등급을 올리지 않음. 넣지 않은 것과 이유: 항온항습기 — 이 모델의 장비 종류 26개에 항온항습기(정밀 공조기)가 없음. 표에 대수·용량·설치 층·실 이름이 없고, 클린룸 본 공조인지 전기실·제어실 같은 보조 실의 공조인지 알 수 없어 새 장비 종류나 상자를 만들지 않음(만들면 위치와 수를 지어내게 됨). P3L 그린동 AHU — 그린동의 존재는 확인되나 이 모델의 어느 상자가 P3의 그린동인지 정해지지 않아 특정 상자에 붙이지 않음(S1·S2는 P4 쪽 그린동 후보). DHC·인프라복합동 — 정의와 모델 건물 대응이 확인되지 않아 보류. 제조사 카탈로그의 일반 제원은 이 현장 장비의 제원이 아니므로 쓰지 않음. 주의: 계약년도는 납품·설치 완료나 가동 연도가 아님. 같은 문구의 반복 행(예: P2L Ph1 DCC 6행, P3L Ph2 DCC 4행)은 계약 분할·변경 등 이유가 불명하므로 대수·구역 수로 세지 않음. 납품 행과 설치 행을 서로 다른 장비로 이중 계산하지 않음. 2017·2018 'P-PJT Ph-4 DCC'의 Ph-4는 옛 프로젝트 단계 명칭으로, 팹 번호 P4로 읽지 않음(2023 행은 원문에 'P4 Ph1'이라고 적혀 있어 P4로 읽음). 'UHP P3_HVAC SYSTEM 직팽식 공조'(2022, 계약처 에이에프이엔씨) 행은 삼성전자·평택 P3L을 직접 적지 않아 연결하지 않음. 산업공조 표 2개(2113·2120)에는 평택 삼성 행이 없음(그 두 표의 범위일 뿐). 자체 정정: v7.33까지 MAU·DCC의 '업계 대표 공급사'에 '신성이엔지'(두 종류)와 '한양이엔지'(DCC)를 출처 없이 적어 두었음 — 공급사 실적이 확인된 회사는 이름이 다른 신성엔지니어링이므로 출처 없는 이름을 지우고 확인된 실적을 현장 근거 칸에 옮김."  # v7.34
META["design_firm_records"] = "설계·건설사업관리 회사의 공식 실적 대조(v7.33, 형상 변경 없음). (1) 삼우종합건축사사무소 'P2-Project'(이 방이 2026-11-15 페이지를 직접 열어 확인, Codex도 원문 보존): 위치 평택시, 용도 Industrial, 연면적 828,992㎡, 지상 8층·지하 1층, Project Completion 2021. 페이지에 설명문·동 이름·허가번호·높이·좌표가 없어 이 면적이 어느 동들을 포함하는지 알 수 없음. 감리사(한방유비스) 실적 592,077㎡, 인허가 'FAB동-2' 591,152.02㎡와 값이 다르지만 대상 범위와 기준 시점이 확정되지 않아 차이를 오류로 보지 않으며, 어느 동에도 이 값을 넣지 않고 동 면적을 조합해 맞추지도 않음. 2021은 설계사 실적의 표기이며 사용승인일·가동일이 아님. 지상 8층·지하 1층은 감리사 실적의 B1F~8F와 같아 'P2' 프로젝트의 층수 표기가 회사 실적 두 곳에서 일치하나, 인허가 층별개요의 층 번호와 같은 기준인지는 확인되지 않음. (2) 같은 페이지의 조감도 1장(Codex가 내려받아 내부 검토용으로만 보관, 이 방이 열어 봄 — 싣지 않음): 설계 단계의 그림이며 실측도·준공 사진이 아니고 제작 시점이 적혀 있지 않음. 그림에서 읽은 것(정성): 긴 장방형 대형 동 2개가 나란히 있고 한 동이 길이 방향으로 어긋나 있음; 두 동 사이에 더 낮은 긴 건물이 있고 양쪽 대형 동과 공중 연결부로 이어짐; 어긋난 동의 가까운 끝에 대형 동과 비슷한 높이의, 정방형에 가까운 건물이 붙어 있음; 대형 동의 지붕은 가운데가 낮고 둘레가 높음; 모서리에 색 패널 외장; 가까운 끝 쪽에 중·고층 건물이 있음. 그림을 서쪽에서 본 것으로 읽으면(방향은 그림에 적혀 있지 않은 이 방의 해석) 이 배치는 모델의 P1·P2(P2가 동쪽으로 약 190 m 어긋남), UT-12·UT-12E, BR-12a~f, V2, 옥상 외곽대, 몬드리안 패널, GATE-W·WA의 상대 배치와 어긋나지 않음. 조감도는 팹의 서쪽 끝을 보여 주므로 동측 띠가 벽면 비침인지 단부 블록인지에는 정보를 주지 않음. 조감도에서 치수·높이·층고를 읽지 않았고 어떤 상자도 바꾸지 않음. 조감도의 보행 연결 통로와 주차 시설 세부는 모델에 넣지 않음(출입 동선은 모델 범위 밖). 조감도와 모델이 어긋나지 않는다는 것은 설계 단계 그림과의 정성 비교일 뿐 모델 등급을 올리는 근거가 아님. (3) 포스코A&C 'Pyeongtaek P5 Ph1 Semi-Production Facility CM/CS'(실적 959번, Codex가 원문 확인 — 이 방은 페이지를 열지 못함): 서비스 CM, 발주처 Samsung Electronics, 위치 Pyeongtaek, Year 2028. 2028은 미래 연도의 표기로 준공·가동의 근거가 아님. 면적·층수 칸은 값이 제공되지 않은 자리표시이며 0으로 읽지 않음. D램·낸드·파운드리 라인을 수용할 수 있다는 소개문은 설치·양산의 확정이 아님. 참여 회사와 업무의 근거로만 쓰고 형상·금액에는 쓰지 않음. (4) 국토지리정보원 일반지도(Astra 조회): 북쪽 팹 후보 자리에 장방형 건물 윤곽이 표시되나 타일 배경 그림이며, 개별 도형·취득일·지상선인지 지붕선인지의 정의를 공개 화면에서 읽을 수 없어 지상 벽선의 근거로 쓰지 않음. (5) 삼우의 공식 Insight 글(2025-08-07, Astra가 원문 확인)은 Samsung Electronics Pyeongtaek Campus를 마스터플래닝 업무의 사례로 명시하나, P2-Project 면적에 포함된 동의 목록이나 동별 면적·높이는 주지 않음. 삼우의 지도형 프로젝트 목록에는 P2 항목이 없으며, 이는 목록의 범위일 뿐 자료가 없다는 뜻이 아님."  # v7.33
SOURCES["OFF_SS_FAB101"] = ("삼성전자 반도체 공식 용어 설명 '팹(FAB)의 모든 것': 천장 고성능 필터와 바닥 격자 구멍으로 공기가 위에서 아래로 순환, FOUP을 천장 레일의 OHT가 설비로 자동 운송(특정 공장 지칭 없음)", "https://semiconductor.samsung.com/kr/support/tools-resources/dictionary/semiconductors-101-part-7-all-about-the-fab-the-birthplace-of-semiconductor-chips/")
SOURCES["OFF_SS_OHT"] = ("삼성 반도체 글로벌 뉴스룸 2025-09-04: 천장 레일의 OHT가 FOUP을 운반, 차량 1대가 하루 약 100 km 주행(특정 팹 지칭 없음)", "https://news.samsungsemiconductor.com/global/the-invisible-highways-tracing-the-journey-inside-a-semiconductor-fab/")
SOURCES["OFF_SS_LEGO"] = ("삼성전자 반도체 공식 페이지: 평택캠퍼스 1라인을 1:520, 약 15,000피스 블록 모형으로 재현 — 에어 샤워, 드라이 쿨링 코일, ULPA 필터 표현(홍보용 모형이며 실제 도면이 아님)", "https://semiconductor.samsung.com/support/tools-resources/fabrication-process/a-lego-model-of-the-worlds-largest-semiconductor-production-line-fab-on-the-block/")
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

# Dated company account; no model-building assignment or geometry change.
SOURCES['OFF_SS_PT_GREEN_2026'] = ('삼성전자 평택 소통협의회 2026년 6월 16일 회의 소개: 그린동 4개 동 가동, 유기 처리 단계의 생물학적 질소 제거, 방류수 수온 저감 시설 연말 완공 목표(회사 기사 설명, 운영 동수의 정확한 기준일 미명시)', 'https://semiconductor.samsung.com/kr/sustainability/people/community-communication/pyeongtaek-story/20260707/')
META["green_building_official_context"] = {'source_keys': ['OFF_SS_PT_GREEN_2026'], 'meeting_date': '2026-06-16', 'reported_operating_green_buildings': 4, 'visit_label': '그린1동', 'treatment_description': '유기 처리 단계에서 미생물을 활용한 생물학적 처리로 질소 오염물질을 제거한다는 회사 설명', 'temperature_reduction_completion_target': '2026-12', 'limits': '6월 회의를 소개하는 회사 기사에 네 동이 가동 중이라고 적혀 있으나 이 운영 동수의 정확한 기준일은 명시되지 않았다. 2026년 11월 현재 운영현황이나 처리용량을 확정하지 않는다. 네 동의 개별 명칭·위치·팹 대응은 제시되지 않았다. 그린1동 방문이라는 원문 표기는 유지하되 나머지를 그린2~4동이라고 새로 명명하지 않는다. S1/S2 상자 및 개념 처리단계와의 개별 대응은 미확인이다. 수온 저감 시설의 2026년 12월은 당시 완공 목표이며 준공·가동 확인이 아니다. URL 경로의 숫자를 게시일로 확정하지 않는다. 상자·장비·배관·수량·물성·등급은 바꾸지 않는다.', 'operating_count_reference_date': 'not specified in the article'}

if __name__ == "__main__":
    r = lambda e: [round(v, 2) if isinstance(v, float) else v for v in e]
    # v7.21: storage tanks are exported as cylinders (diameter = shorter plan side of the box)
    CYL_OLD = ("원통형 탱크도 상자로 단순화", "원통형 탱크·공정 설비는 상자로 단순화")
    for e in ELEMS:
        # v7.24: official Samsung descriptions attached to existing concept layers (kind and principle only; grades unchanged)
        if e["layer"] == "FFU 천장": e["src"] += [k for k in ("OFF_SS_FAB101", "OFF_SS_LEGO") if k not in e["src"]]
        if e["layer"] == "플레넘 구역": e["src"] += [k for k in ("OFF_SS_LEGO",) if k not in e["src"]]
        if e["layer"] == "공정 구역" and "OHT" in e["name"]: e["src"] += [k for k in ("OFF_SS_FAB101", "OFF_SS_OHT") if k not in e["src"]]
        if e["id"] == "LINDE-NE":
            e["box"][5] = 22.55; e["conf"] = "M"; e["note"] += " 높이 갱신(v7.21): 건축물대장(고덕동 1722) 주건축물 제38동이 건축면적 2,796.08㎡·높이 22.55 m로, 이 박스 평면(약 2,756㎡)과 1.4% 차이여서 같은 건물로 보고 높이를 22.55 m로 적용. 대응은 면적 비교에 따른 추정"
            if "BLDG_REG" not in e["src"]: e["src"].append("BLDG_REG")
        if e["id"] == "PUB-WWTP": e["note"] += " 대장(고덕동 1721)의 주건축물 높이: 1단계 관리 및 설비동 30.2 m(지상 7층, 건축면적 1,865.66㎡), 2단계 설비동 13.2 m(1,368.31㎡), 3단계 관리 및 설비동 18.1 m(5,195.29㎡). 어느 박스가 어느 동인지 정하지 못해 모델 높이는 임의값을 유지"
        if e["id"].startswith("CT34-F"): e["shape"] = "cyl"
        if e["id"] in ("BR-34a", "BR-34b", "BR-34c"):  # v7.25: press caption recorded as a concept note; geometry unchanged
            e["note"] += " 보도 사진 설명(딜사이트, 공개 2025-06-24 · 수정 2025-08-25): P4 PH2와 P3 PH2에 브리지가 모두 4개 있고 그 사이에 복합동이 놓인다고 설명. 개별 접속점·층·좌표는 공개되지 않았고, 세메스 OHT는 '설치 예상'으로만 적혀 있음. 이 주석은 개념 설명이며 상자의 위치·높이는 바꾸지 않음(원문 대조는 Codex·Astra, 이 저장소 작업자는 원문을 다시 열지 못함)"
            if "DEALSITE_BR" not in e["src"]: e["src"].append("DEALSITE_BR")
        if e["id"].endswith("-endblk"): e["note"] += " [v7.27 재판독] 공개 위성영상(Esri World Imagery)은 수직 촬영이 아님: P1·P3·P4의 이 띠에서 건물 동측 벽면의 외장 그래픽(빨강·노랑 패널)이 그대로 보이므로, 이 경계선 동쪽의 폭 29~37 m 띠는 별도의 단부 블록이 아니라 옥상 가장자리와 벽 밑동 사이에 비친 벽면일 가능성이 높음(P2 띠는 그래픽을 확인하지 못해 유추). 이 경우 팹 평면 길이는 '본체' 길이(P1 519 m — P1을 명시한 보도의 약 520 m와 같음)이고, 옥상에서 읽은 서쪽 가장자리는 실제보다 높이의 약 0.3배만큼 서쪽으로 치우쳐 있음. 이번 판은 상자를 고치지 않고 이 사실만 기록함 — 정사 보정된 건물 외곽 자료로 확인한 뒤 평면을 고칠 예정."  # v7.27
        if e["id"] == "UT-34E": e["note"] += ''  # v7.27 (appended after the permit note below)
        if e["id"] in REG_SFX:  # v7.26: permit comparison recorded as candidates; geometry unchanged
            e["note"] += REG_SFX[e["id"]]
            if "HUB_FLR_1695" not in e["src"]: e["src"].append("HUB_FLR_1695")
        if e["id"] == "UT-34E": e["note"] += ' [v7.27 재판독] 이 상자(폭 33 m)는 영상에서 무늬 없는 회색 면으로 보이며, 위와 같은 사각 촬영 효과로 비친 동측 벽면일 가능성이 있음 — 그렇다면 별도의 단부 건물이 아님. 미확정, 상자 변경 없음.'  # v7.27
        if e["id"] == "PUB-WWTP": e["note"] += ' 대장의 사용승인일은 가동 개시일이나 처리 능력을 뜻하지 않음.'
        if e["id"] == "PUB-WWTP":  # v7.40
            e["note"] += " 2024 운영 통계(v7.40): 시설 단위 값은 meta.wwtp_operations_2024 참조 — 시설용량 187,500 m³/일, 2024 일평균 유입 153,994.81 m³/일(기후에너지환경부 운영현황). 이 동 하나의 값이 아니며 B·C동에 나누지 않음."; e["src"] += ["MCEE_WWTP_2024"]
        if e["id"].endswith("-endblk"): e["note"] += " [v7.33 판정 상태] 위 v7.27 재판독의 '벽면일 가능성이 높음'은 한 영상의 판독이며 확정이 아님. 국토지리정보원 정사영상과의 비교(v7.31~v7.32)로도 띠가 비친 벽면인지 낮은 단부 블록인지 판정하지 못했고, 지면 높이의 벽선 근거가 확보되기 전에는 이 선과 상자를 옮기거나 지우지 않음."  # v7.33
        if e["id"] == "UT-34-UPW":  # v7.38
            e["note"] += " 공급사 실적(v7.38): 안센 공식 실적표에 '평택 사업장 P3. WWT, UPW – PCPL 공법 적용 – 완료'와 '2023 P3 UPW 복합 수조동 PP방수시트 ST2 신축공사'(삼성물산 건설부문)가 있음 — P3 초순수 계통에 PP 시트 라이닝 수조가 쓰였다는 근거이나, 그 수조동이 이 상자와 같은 건물인지는 확인되지 않았고 이 상자의 위치·크기·설비 수는 그대로 개념."; e["src"] += ["ANSEN_PC"]
        if e["layer"] == "연결 브리지" and not e["id"].startswith("BR-PR"):  # v7.36
            e["note"] += " 인허가 기록(v7.36): 두 주 허가에 '연결통로' 계열 부속건축물 6동의 구조·층 번호가 있음(meta.permit_link_corridors) — 이 상자와의 대응은 확인되지 않았고 높이·층은 그대로 가정."; e["src"] += ["HUB_FLR_1695"] if "HUB_FLR_1695" not in e["src"] else []
        if e["id"].endswith("-ffu") and e["id"].startswith("P3-"):  # v7.35
            e["note"] += " 공급사 공시(v7.35): 케이엔솔 반기보고서(2026)의 주요 계약 표에 삼성물산 발주 '평택 P3-PJT PH4 모듈 S/C 공사'가 있음(비교 기간 표에 PH2 행도 있음). S/C의 정의는 계약표에 없고, 같은 보고서는 시스템실링 모듈화 공법을 2020년 평택공장부터 적용했다고 적음 — 이 천장면의 높이·범위·모듈 수의 근거는 아니며 상자는 개념 그대로."; e["src"] += ["KENSOL_H1_2026"]
        if e["id"].endswith("-ffu") and e["id"].startswith("P4-"):  # v7.35
            e["note"] += " 공급사 공시(v7.35): 케이엔솔 반기보고서(2026)의 주요 계약 표에 삼성물산 발주 '평택 P4-PJT PH2 모듈 S/C 공사'·'PH3 모듈 S/C 공사'가 있고, 별도 수익 주석에 'PH4 모듈 S/C 공사' 행이 있음(발주처·총액은 미확인). S/C의 정의는 계약표에 없고, 같은 보고서는 시스템실링 모듈화 공법을 2020년 평택공장부터 적용했다고 적음 — 이 천장면의 높이·범위·모듈 수의 근거는 아니며 상자는 개념 그대로. PH3 S/C의 공사기한은 표마다 다름(PT-F008)."; e["src"] += ["KENSOL_H1_2026"]
        if "-ra-" in e["id"] and e["id"].startswith("P2-"):  # v7.34
            e["note"] += " 공급사 실적(v7.34): 신성엔지니어링 공식 실적표에 'P2L Ph1 DCC'(2019)와 'P2L Ph2 DCC'(2021~2022, 계약처 삼성물산, ITEM 드라이코일)가 있음 — P2에 DCC가 공급된 근거이며, 이 샤프트의 위치·크기·DCC 대수의 근거는 아님(계약년도 표, 대수 없음)."; e["src"] += ["SHINSUNG_2105", "SHINSUNG_2111"]
        if "-ra-" in e["id"] and e["id"].startswith("P3-"):  # v7.34
            e["note"] += " 공급사 실적(v7.34): 신성엔지니어링 공식 실적표에 'P3L Ph1 1공구 DCC'(2021), 'P3L Ph2 DCC'(2022~2023), 'P3L Ph3 DCC'(2022), 'P3L Ph4 DCC'(2023)가 있음(계약처 삼성물산, ITEM 드라이코일) — P3에 DCC가 공급된 근거이며, 이 샤프트의 위치·크기·DCC 대수의 근거는 아님(계약년도 표, 대수 없음)."; e["src"] += ["SHINSUNG_2111", "SHINSUNG_2119"]
        if e["id"] == "V2":  # v7.34
            e["note"] += " 공조 공급사 실적(v7.34): 신성엔지니어링 공식 실적표에 'EUV V2 AHU 납품·설치'와 'V2-Ph2 EUV동 OAC 납품'(2021), 'EUV 하부마감 DCC'(2021~2022), 'EUV Retrofit OAC Casing 보수공사'(2022)가 있음 — 계약년도 표이며 대수·위치·모델은 없음. 표의 'EUV V2'·'EUV동'과 이 상자의 대응은 이름 일치에 따른 것."; e["src"] += ["SHINSUNG_2111"]
        if e["id"] == "UT-12-UPW":  # v7.33
            e["note"] += " 회사 공식 공정 근거(v7.33): 삼성엔지니어링 2018 지속가능경영보고서(인쇄 30쪽 — Codex가 PDF 원문과 렌더를 확인, 이 방은 열지 않음)는 '삼성전자 평택 P1 초순수 프로젝트' 사례에 전기적 탈이온법(CEDI)을 적용했다고 적고, 이온 제거 단계를 종전 '역삼투압 → Mixed-Bed' 대신 '역삼투압 → CEDI'로 비교함. 하루 2만 ton은 재생 약품을 쓰지 않는 효과를 계산한 기준값이며 P1의 설계 용량·운전량이 아님. 모듈의 제조사·대수·위치·치수는 공개되지 않아 이 상자의 위치·수·크기는 그대로 개념이며, P1의 초순수 설비가 이 건물에 있다는 근거도 아님."
            if "EA_SR2018" not in e["src"]: e["src"].append("EA_SR2018")
        if re.search(r"-TK\d+$", e["id"]):
            e["shape"] = "cyl"
            for o in CYL_OLD: e["note"] = e["note"].replace(o, "저장탱크는 원통으로 표현(지름은 위성 판독, 돔 지붕은 평평하게 단순화)")
    data = dict(meta=META, fabs=FABS, levels=LEVELS, types=TYPES, phase={k: {f"{a}|{b}": v for (a, b), v in d.items()} for k, d in PHASE.items()},
                elems=ELEMS, equip=[r(e) for e in EQUIP], rails=[r(e) for e in RAILS], struct=STRUCT, safety=SAFETY, pipes=[r(e) for e in PIPES], dets=[r(e) for e in DETS], egress=EGRESS,
                usys=USYS, ugroups=UGROUPS, util=UTIL,
                cr_report={"P1": 135300, "P2": 148500, "P3": 181500, "P4": 181500}, sources=SOURCES)
    json.dump(data, open("campus.json", "w", encoding='utf-8', newline='\n'), ensure_ascii=False, separators=(",", ":"))
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
