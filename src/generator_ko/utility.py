# -*- coding: utf-8 -*-
"""
Utility-system concept layers (v4): thermal (CHW / CW / heat recovery), PCW, bulk & specialty gas incl. transfer /
exchange points, segregated exhaust, wastewater, chemical supply, UPW / reclaim, power (HV -> MV -> LV, UPS, emergency).

EVERY route here is a GENERIC REFERENCE DESIGN (grade D): it shows supply -> use -> return/treatment relationships,
not the real pipe / duct / cable routes of the Pyeongtaek campus, which are not public.
Only the facts listed in UFACTS are site-specific, and each one carries a press / official source key.
"""

USYS = [  # key, ko, color, group
 ("CHW.S", "냉수 공급 (냉동기 증발기 → MAU·DCC·PCW 열교환기)", "#2f7fff", "열관리"),
 ("CHW.R", "냉수 환수", "#8dbbff", "열관리"),
 ("CW.S", "냉각수 공급 (냉각탑 → 냉동기 응축기)", "#12b8a6", "열관리"),
 ("CW.R", "냉각수 환수 (응축기 → 냉각탑)", "#86e0d6", "열관리"),
 ("HR", "폐열 회수 온수 (선택 계통: 응축열 → MAU 재열·예열)", "#ff7ab8", "열관리"),
 ("PCW.S", "공정 냉각수 공급 (열교환기 → 장비·펌프·스크러버)", "#a35cff", "PCW"),
 ("PCW.R", "공정 냉각수 환수", "#d3b0ff", "PCW"),
 ("GAS.BULK", "벌크가스 (N2·O2·Ar·H2 등: 외부 플랜트 배관 → 정제 → CSF 헤더)", "#ffd21f", "가스 공급·충전"),
 ("GAS.SPEC", "특수가스 (가스 캐비닛·BSGS → VMB → 장비)", "#b8e000", "가스 공급·충전"),
 ("EXH.ACID", "산 배기 (→ 중앙 습식 스크러버 → 스택)", "#ff7a1a", "유해물질 배기"),
 ("EXH.ALK", "알칼리(암모니아) 배기 (→ 전용 습식 스크러버)", "#ffb98a", "유해물질 배기"),
 ("EXH.VOC", "유기(VOC·용제) 배기 (→ 제올라이트 농축 로터 + 산화기)", "#ff4d6d", "유해물질 배기"),
 ("EXH.HEAT", "열·일반 배기 (별도 계통)", "#c7ccd1", "유해물질 배기"),
 ("WW.F", "불소계 폐수", "#8b5a2b", "폐수"),
 ("WW.AA", "산·알칼리계 폐수", "#b88655", "폐수"),
 ("WW.ORG", "유기계 폐수", "#6b4a1e", "폐수"),
 ("WW.OUT", "처리수 방류 (그린동 → 공공폐수처리시설 → 하천)", "#4fb3a5", "폐수"),
 ("CHEM", "케미컬 공급 (탱크로리 하역·ACQC → 저장 → CCSS → VMB)", "#39d98a", "케미컬"),
 ("UPW.S", "초순수 공급 루프", "#9be7ff", "초순수·재이용"),
 ("UPW.R", "초순수 환수 루프", "#d4f3ff", "초순수·재이용"),
 ("RCL", "재이용수 회수 (저농도 린스 배수 → 회수 설비)", "#5fa8a0", "초순수·재이용"),
 ("WTR.RAW", "공업용수 인입 (광역상수도·팔당 계통, 보도)", "#3aa0ff", "초순수·재이용"),
 ("WTR.REUSE", "하수처리 재이용수 인입 (수원·화성·오산, 2030년경 계획·보도)", "#7ad0c0", "초순수·재이용"),
 ("ELEC.HV", "초고압 수전 (345 kV·154 kV, 보도)", "#ff2fa0", "전력"),
 ("ELEC.MV", "특고압 배전 (22.9 kV 가정, A·B 이중 피더)", "#ff86cf", "전력"),
 ("ELEC.LV", "저압 버스덕트 (전기실 변압기 → CSF 전원 랙)", "#ffc2e6", "전력"),
 ("ELEC.UPS", "UPS·순간전압강하 보상 전원 (선정된 중요 부하)", "#f2e6ff", "전력"),
 ("ELEC.EMERG", "비상전원 (비상발전기 → 선정된 비상 부하)", "#ff3030", "전력"),
 ("ELEC.PV", "주차장 태양광 (사업장 내 사용, 생산 라인용 아님 — 보도)", "#ffe45c", "전력"),
]
SI = {s[0]: i for i, s in enumerate(USYS)}

# group -> flow order, typical ranges (public literature), what is publicly reported for Pyeongtaek, sources, limits
UGROUPS = [
 dict(key="열관리", title="열관리: 냉동기 · 냉각탑 · 냉수 · 외조기 · DCC · 폐열 회수",
  flow=["냉동기 증발기 ↔ 냉수(CHW) 공급·환수 ↔ 외조기(MAU) 냉각·제습 코일 / DCC(현열 제거) / PCW 열교환기 1차측",
        "냉동기 응축기 ↔ 냉각수(CW) 공급·환수 ↔ 냉각탑(대기로 방열)",
        "공기: 외기 → MAU(예열·가습·냉각 제습·재열) → 플레넘 → FFU → 클린룸 → 바닥 아래 → 리턴 샤프트의 DCC → 플레넘",
        "선택: 응축열·환수열 → 열회수 냉동기/열교환기 → MAU 재열·겨울철 예열용 온수"],
  values=["MAU 냉각 코일용 냉수 약 5–7 °C(논문), 이중 온도 냉수 계통에서는 저온 약 6–7 °C(MAU)·고온 약 15–18 °C(DCC)(기업 기술 글)",
          "문헌의 MAU 구성 순서: 팬 → 예열 코일 → 예냉 코일 → 가습(에어 와셔) → 냉각 코일 → 재열 코일",
          "DCC는 결로가 생기지 않도록 코일 표면을 리턴 공기 이슬점보다 높게 운전(그래서 '건식')"],
  site=["위성영상에서 P1·P2 동측 냉각탑 뱅크 4개의 팬 셀 배열, P3·P4 사이 유틸리티동과 북측 유틸리티 구역의 수증기를 확인(등급 B·C)",
        "삼성E&A가 평택 P2 UT동, P3 그린동·UT동·옥상 배기·UPW를 수행했다고 공개·보도(등급 A: 존재 사실)",
        "공시 공사명에 'P4 Ph4 DCC 1공구'가 등장(등급 A: DCC 공사의 존재)",
        "삼성전자 지속가능경영보고서(2023): 기흥·화성·평택에서 설비 냉각수와 폐수 방류수의 폐열을 회수해 공정용수·공조 열원으로 재사용(등급 A: 폐열 회수의 존재)",
        "평택사업장 지열 냉난방 설비 200 RT(2021·2022 보고서) → 738 RT(2023 보고서). 화성·평택 일부 건물 하부에 설치(보도). 위치는 공개되지 않음"],
  src=["HVAC_OUP", "HVAC_CKY", "HVAC_BENCH", "PCW_PAT", "P2_UT", "P3_UT", "DCC", "ESRI", "SR2023", "SR2021", "PV_NEWS"],
  limit="냉동기 형식·대수·용량, 냉수 온도 설정, 폐열 회수 적용 여부, 실제 배관 경로는 공개되지 않았습니다. 냉동기를 유틸리티동에 둔 것과 팹 연결 위치는 가정입니다. 냉수 헤더는 리턴 샤프트 띠와 중앙 코어 안에 두었고 FFU 천장 위는 지나지 않게 했습니다(수배관 누수가 클린룸으로 떨어지는 위험을 줄이는 배치인지는 검토 가설)."),
 dict(key="PCW", title="PCW: 공정 냉각수 폐회로",
  flow=["PCW 열교환기(2차측) → 순환 펌프 → 공급 헤더 → 베이 분기 → 장비·드라이 펌프·스크러버·RF 전원 → 환수 헤더 → 열교환기",
        "열교환기 1차측은 냉수(CHW) 또는 냉각탑수. PCW는 장비 전용 폐회로이며 정상 운전 중 소모·배출되는 물이 아님"],
  values=["문헌상 요구 온도 약 13–20 °C(논문)",
          "실측 벤치마크 사례(대만 팹): 공급 17.8 °C·환수 21 °C·유량 1,121.9 ㎥/h·냉각 용량 1,187 RT",
          "검산: Q = ρ·V·cp·ΔT = 1000 × (1121.9/3600) × 4.186 × 3.2 ≈ 4,175 kW ≈ 1,187 RT(3.517 kW/RT) → 문헌 수치와 일치"],
  site=["평택 P1~P4의 PCW 온도·유량·이중화 구성은 공개 자료에서 확인하지 못했습니다."],
  src=["HVAC_BENCH", "HVAC_OUP", "PCW_PAT"],
  limit="열교환기 위치(1F·5F FSF 서포트 구역), 헤더·분기 위치는 모두 개념입니다. 관경·유량 계산을 한 수리 해석 결과가 아닙니다."),
 dict(key="가스 공급·충전", title="가스: 벌크가스 · 특수가스 · 충전(이송)·교체 지점",
  flow=["벌크가스: 인근 가스사 플랜트(공기분리장치) → 지하 배관 → 캠퍼스 인입 → (백업 액체 저장·기화) → 정제 → 팹 CSF 헤더 → 장비",
        "특수가스: 실린더·대용량 용기 반입 → 가스 캐비닛 또는 BSGS → 분배(VMB) → 장비 가스 박스. 퍼지·캐비닛 배기는 별도 계통",
        "작업 구분: 벌크 저장설비는 '이송·충전 접속점', 실린더는 '교체 작업 구역'(현장에서 실린더를 충전하지 않음)"],
  values=["압력·순도·저장량 등 수치는 공급사·공정마다 달라 이 모델에 넣지 않았습니다(근거 없는 수치 배제)."],
  site=["뉴시스 2022-09 현장 기사: 캠퍼스에 생산에 쓰는 가스와 화학물질을 보관하는 대형 GCS(Gas Chemical System)동이 있고, 안전을 위해 필요한 때에만 연결 브리지를 통해 생산 라인으로 공급(등급 A: GCS동과 공급 브리지의 존재. 어느 건물인지는 기사에 없음)",
        "P1~P4 가스 공급은 에어프로덕츠·린데·에어퍼스트가 나눠 수주(보도). P1은 에어프로덕츠코리아(보도), P3 벌크가스 공급자는 에어퍼스트(보도)",
        "에어퍼스트 평택공장(약 20만㎡)은 캠퍼스에서 직선 약 1 km, 지하 배관으로 산소·질소·아르곤·수소 공급(2026-05 보도)",
        "린데는 평택에 8번째 공기분리장치를 지어 초고순도 가스·수소를 추가 공급한다고 발표(보도)",
        "공시 공사명에 'P4 Ph4 S-GAS 1공구'가 등장(특수가스 공사의 존재)",
        "가스 3사 공장 위치(카카오맵): 에어프로덕츠코리아는 캠퍼스 북동쪽 바로 옆, 린데코리아는 남서쪽, 에어퍼스트는 남쪽 약 1 km → 세 방향의 인입을 표시",
        "캠퍼스 남쪽 고덕면 방축리 일원 46만㎡의 평택 첨단복합 일반산업단지에도 린데코리아·에어퍼스트·에어프로덕츠코리아 3사가 입주 예정(보도)",
        "평택시가 고덕 공공하수처리장 처리수를 이 가스 3사에 냉각용 공업용수로 공급: 3.23 km·지름 50 cm 관로, 하루 2만 4,400 t 계획(2026-10 보도)"],
  src=["INT_LINDE25", "INT_LINDE20", "INT_AP26", "INT_AP_P1", "TOUR_3F", "KAKAO", "GAS_SUP", "GAS_AF", "GAS_AP", "GAS_LINDE", "GAS_PARK", "GAS_PARK2", "DCC", "NFPA318", "CSF_FSF"],
  limit="캠퍼스 안 저장 위치·인입 지점·배관 경로·가스실 위치는 공개되지 않았습니다. 야드·가스실·간선은 임의 위치의 개념 표시입니다."),
 dict(key="유해물질 배기", title="유해물질 배출(대기): 배기 계통 분리와 처리",
  flow=["공정 장비 → (필요 시) 드라이 펌프·POU 처리 → 성상이 맞는 전용 배기 헤더 → 중앙 처리설비 → 팬 → 스택(처리 후 배출가스)",
        "계통 분리: 산 / 알칼리(암모니아) / 유기(VOC·용제) / 열·일반. 섞이면 반응·고형물이 생기므로 따로 모음",
        "POU → 옥상 스크러버 → 스택은 여러 구성 중 하나이며 공정에 따라 POU의 종류·유무가 다름"],
  values=["문헌의 배기 분류: 열·일반 / 산 / (선택) 암모니아 / VOC. 열 배기는 처리 없이 배출하는 경우가 많음(특허 문헌)",
          "VOC: 제올라이트 농축 로터 + 열 산화기 조합, 산·알칼리: 중앙 습식 스크러버(논문)",
          "산성 가스는 중화 수용액과 접촉시키는 습식 스크러버로 처리(장비사 기술 자료)"],
  site=["삼성엔지니어링이 P3 '옥상 배기'를 담당했다는 보도(등급 A: 옥상 배기 설비의 존재)",
        "위성·드론 영상에서 팹 옥상 외곽대의 철골 랙과 설비 열을 확인(등급 B·C)",
        "삼성전자 지속가능경영보고서(2023): 반도체 사업장의 공정가스(F-gas) 저감에 POU 스크러버와 옥상의 RCS(재생 촉매 시스템)를 운영(등급 A: 설비 종류의 존재, 평택 대수·위치는 미공개)"],
  src=["EXH_PAT", "EXH_AAQR", "EXH_MKS", "P3_UT", "CSF_FSF", "ESRI", "SR2023"],
  limit="어느 랙에 어떤 계통이 있는지, 처리설비 종류·대수·처리 효율은 공개되지 않았습니다. 남측=산·알칼리, 북측=유기·열 배치는 설명용 가정입니다(동·서 분산 배치가 경로상 유리할 수 있다는 검토 의견이 있으나 근거 미확인)."),
 dict(key="폐수", title="유해물질 배출(수질): 폐수 분리 수집과 처리",
  flow=["발생원(세정·CMP·스크러버 배수) → 성상별 분리 집수(불소계 / 산·알칼리계 / 유기계 …) → 계통별 이송 → 그린동의 해당 처리 단계",
        "처리수 → 공공폐수처리시설 → 하천 방류. 일부는 사내 재이용"],
  values=["처리 공정 수치(약품·체류 시간 등)는 넣지 않았습니다."],
  site=["삼성전자 반도체 공식 영상(내일도 애쓰지 Ep.5) 소개 글: 평택캠퍼스 폐수처리장에 '2.6 km 길이의 지하 통로'와 누출을 막는 스크린도어, 24시간 상황실(등급 A: 지하 통로의 존재. 경로는 미공개)",
        "평택캠퍼스 그린동은 2곳, 지하 수처리 시설 면적 약 3.4만㎡, 하루 평균 약 7만 t 정화, 업무의 약 97% 자동화(2021 보도)",
        "2020년 기준 평택캠퍼스 하루 평균 약 6.7만 t 사용, 약 5.4만 t이 평택시 폐수종말처리장을 거쳐 서정리천으로 방류(보도)",
        "2024년 삼성전자 전사 수자원 흐름(천 t): 지표수 187,626 → 사내 처리 59,569·사외 처리 92,540, 재이용 125,463(지속가능경영 자료)"],
  src=["WW_TUNNEL", "GREEN", "WTR_FLOW", "P3_UT", "P4_SITE"],
  limit="그린동이 어느 건물인지(S1·S2는 추정), 계통 구분·처리 공정·이송 경로는 공개되지 않았습니다. 지하 트렌치는 보이도록 지면 위에 그렸습니다."),
 dict(key="케미컬", title="케미컬 공급: 하역 · 저장 · 중앙 공급(CCSS)",
  flow=["탱크로리 하역 베이(품질 확인) → 저장 탱크 → 중앙 공급 장치(CCSS) → 이중 배관 → 팹 FSF의 공급 유닛 → 분배(VMB) → 세정·트랙 장비",
        "CMP 슬러리는 침전을 막기 위해 공급실에서 장비 근처까지 계속 순환시키는 루프로 공급"],
  values=["압력·유속·순도 수치는 넣지 않았습니다."],
  site=["에스티아이 CCSS가 평택 3기 Ph3·Ph4와 4기 Ph1·Ph2에 공급된 것으로 증권사 리포트 인용 보도",
        "한양이엔지가 P5 배관 계약을 공시(2026-09 보도)"],
  src=["STI", "P5", "CSF_FSF"],
  limit="하역 베이·저장 위치·배관 경로는 공개되지 않았습니다. 유틸리티동 서쪽 끝에 둔 것은 임의 위치입니다."),
 dict(key="초순수·재이용", title="초순수(UPW)와 재이용수",
  flow=["공업용수 → 전처리 → 역삼투·이온교환·탈기 → 초순수 저장 → 폴리싱 → 팹 순환 루프(공급·환수) → 장비",
        "저농도 린스 배수는 따로 모아 회수 설비를 거쳐 재이용(초순수로 바로 되돌리는 것이 아니라 원수·유틸리티 용수 쪽으로 환원)"],
  values=["수질·회수율 수치는 넣지 않았습니다."],
  site=["평택캠퍼스(1·2공장 가동 시점)는 하루 22만 t의 공업용수를 공급받고, 6공장까지 가동하면 하루 25만 t이 더 필요(2020·2024 보도). 원수는 한강 팔당 계통(기흥·화성·평택 합계 하루 약 30만 t을 팔당에서 취수한다는 2022 보도)",
        "추가 용수 대안(2020 보도): 한국수자원공사 추가 공급(팔당댐·충주댐, 1조 원 이상·10년 이상) 또는 평택시 자체 수원(안성천) 개발(3,348억 원·7년)",
        "하수 재이용 계획(2022 보도): 수원 28만 t·화성 동탄2 4.2만 t·오산 5만 t = 하루 37.2만 t을 고덕(평택)사업장에, 전용 관로 약 60 km·약 6,000억 원, 2030년부터",
        "2026-09 보도: 화성·오산 하루 약 12만 t, 수원 하루 약 21만 t 규모 재이용 사업을 준비 중(합계 약 33만 t)",
        "평택캠퍼스 공업용수 사용량: 2022년 11월 기준 하루 약 12만 t(지역지 보도)",
        "2022-11 협약: 수원·화성·오산 하수처리수 하루 37.2만 t을 평택캠퍼스에, 10.2만 t을 기흥·화성에 공급하는 계획(총 47.4만 t)",
        "삼성엔지니어링이 P3 UPW를 담당했다는 보도(등급 A: 존재 사실)"],
  src=["INT_SS_WATER", "INT_KT_WATER", "WTR_22", "WTR_22B", "WTR_REUSE", "WTR_33", "WTR_30", "WTR_USE", "WTR_FLOW", "P3_UT"],
  limit="초순수 설비의 위치·용량·루프 구성은 공개되지 않았습니다. 유틸리티동에 둔 것은 가정입니다. 공업용수·재이용수가 캠퍼스로 들어오는 지점과 관로 경로도 공개되지 않아 북측 경계에 임의로 표시했습니다. 보도 수치(22만 t·12만 t)는 시점과 기준(공급량·사용량)이 서로 다릅니다."),
 dict(key="전력", title="전력: 수전 · 변전 · 배전 · UPS · 비상전원",
  flow=["한전 송전망(345 kV·154 kV) → 수전·변전 설비(GIS·주변압기) → 특고압 배전(이중 피더) → 팹 전기실 변압기 → 저압 배전반·버스덕트 → 부하",
        "선정된 중요 부하 ← UPS·순간전압강하 보상 설비 / 선정된 비상 부하 ← 절체 설비 ← 비상발전기",
        "UPS·비상발전기가 팹 전체 공정 부하를 감당하는 것은 아님"],
  values=["캠퍼스 내 배전 전압(22.9 kV)은 국내 일반 특고압 배전 전압을 가정한 것이며 현장 값은 확인하지 못했습니다."],
  site=["한전 고덕변전소는 캠퍼스와 도로 하나를 사이에 둔 맞은편에 있고, 지하 1층~지상 4층·연면적 약 10만㎡, 345 kV 공급, 1변전소 2016년·2변전소 2022년 운영 시작, 부지는 삼성이 제공(2024-12 서울경제). OpenStreetMap에도 P4 남쪽에 '고덕변전소' 부지와 건물 3동이 등록돼 있어 이 모델의 위치를 그 경계로 고쳤습니다(등급 A·B)",
        "345 kV 고덕#2 변전소: 평택시 지제동 302, 대지 102,076㎡, 연면적 17,853.72㎡, 변전소 1개 동(지하 1층·지상 4층)·전력구·환기구, 2022-11 준공(시공사 동양 실적 자료)",
        "2018년 현장 기사: 고덕변전소와 HVDC 변환소 두 건물이 나란히 있고, 내부에 345 kV 변압기실과 154 kV GIS실",
        "345 kV 고덕–서안성: 가공 10.2 km(철탑 35기) + 지중 13.3 km = 23.5 km. 500 kV 북당진–고덕 HVDC 34.2 km 지중(1단계 1.5 GW 2020-12, 2단계 1.5 GW)",
        "삼성전자가 발주한 '평택 345 kV 변전소 신축공사'(HL디앤아이한라, 1,429억 원, 고덕국제화계획지구 일반산업단지 A4-1블록, 2023-12~2026-08 계약 공시)",
        "2단지(5·6라인): 한전·삼성 협약(2022-09) — 345 kV 변전소 2곳을 새로 짓고 공장까지는 154 kV 선로로 공급, 1조 1,971억 원",
        "한전 주민설명회(2024-08): 평택 현재 공급 2,300 MW, 2034년까지 삼성 평택캠퍼스 2,000 MW 등 3,637 MW 추가 필요 → 345 kV 신평택·고덕3 변전소(2031-09 목표, 고덕3는 고덕지구 내 한전 부지)",
        "공식 영상(2026-06)에서 팹 옆 저층 건물 옥상의 청색 태양광 패널을 확인(어느 건물인지는 특정하지 못함)",
        "주차장 태양광: 평택사업장 0.4 MW(2021·2022 보고서) + 0.2 MW(2022년 추가) → 0.7 MW(2024 보고서). 주차장 패널 전력은 생산 라인에 쓰지 않는다는 보도",
        "345 kV 고덕–서안성 송전선로(23.5 km) 2023-09-12 준공 → P1~P4 전력 공급 능력 2 GW(전력 전문지 보도)",
        "이 선로 공사비 약 3,900억 원을 삼성전자가 부담, 그 전까지 평택캠퍼스로 오는 송전선은 154 kV(보도)",
        "2공장은 154 kV 고덕–평택·송탄–진위 선로로 공급 가능, 3·4공장은 345 kV 선로가 선행돼야 한다는 2018년 보도",
        "고덕변전소에는 345 kV 변압기실과 154 kV GIS실이 있음(2018 전력 전문지 현장 기사)",
        "500 kV 북당진–고덕 HVDC(34.2 km 지중, 3 GW)가 평택 일대에 전력 공급(보도)"],
  src=["INT_GE_HVDC", "INT_KJD_345", "PWR_GD24", "PWR_GD2", "PWR_GD", "PWR_345B", "PWR_345", "PWR_HK", "PWR_154", "PWR_HVDC", "PWR_HL", "PWR_P5", "PWR_GD3", "SR2024", "SR2021", "PV_NEWS", "PV_KT", "OSM", "P4_SITE", "NAMU"],
  limit="수전 설비의 정확한 위치, 이중화 구성, 변압기·UPS·발전기 용량과 공급 범위는 공개되지 않았습니다. 변전소 건물 3동 가운데 어느 것이 1변전소·2변전소·HVDC 변환소인지, 캠퍼스가 받는 전압(154 kV인지 345 kV인지)과 캠퍼스 안 수전 설비 위치는 확인하지 못했습니다. 간선 경로는 개념입니다. 태양광 캐노피 위치는 위성영상의 청회색 지붕을 근거로 한 추정입니다. 전기실을 북측 서포트 구역에만 둔 것은 단순화이며, 긴 팹에서는 저압 전압강하 때문에 분산 배치를 검토해야 한다는 의견이 있습니다(검토 가설)."),
]

UTIL = []   # [x, y, z, dx, dy, dz, sysIdx, fab]

def _seg(sys, a, b, w, fab):
    x0, x1 = sorted((a[0], b[0])); y0, y1 = sorted((a[1], b[1])); z0, z1 = sorted((a[2], b[2]))
    h = w / 2
    UTIL.append([round(x0 - h, 2), round(y0 - h, 2), round(z0 - h, 2), round(x1 - x0 + w, 2), round(y1 - y0 + w, 2), round(z1 - z0 + w, 2), SI[sys], fab])

def route(sys, pts, w=0.8, fab="", off=(0, 0, 0)):
    """axis-aligned polyline; legs that change several coordinates are split x -> y -> z."""
    p = [tuple(c + o for c, o in zip(q, off)) for q in pts]
    for a, b in zip(p, p[1:]):
        cur = list(a)
        for ax in (0, 1, 2):
            if abs(b[ax] - cur[ax]) > 1e-6:
                nxt = list(cur); nxt[ax] = b[ax]; _seg(sys, cur, nxt, w, fab); cur = nxt

def pair(base, pts, w=0.8, fab="", d=(1.3, 1.3, 1.0)):
    route(base + ".S", pts, w, fab); route(base + ".R", pts, w, fab, off=d)

def build_utilities(FABS, add, bays):
    U = "유틸리티 설비"; T = "충전·교체 지점"
    D_NOTE = "일반 참조 설계(개념). 실제 평택캠퍼스의 설비 위치·대수·용량이 아닙니다. "
    F = {f["id"]: f for f in FABS}
    # ------------------------------------------------------------ plants in the utility buildings (assumed location)
    UT = {"UT-12": dict(x0=-314, x1=-2, y0=1806, y1=1889, serves=("P1", "P2")), "UT-34": dict(x0=-307, x1=357, y0=1117, y1=1232, serves=("P3", "P4"))}
    for uid, u in UT.items():
        ym = (u["y0"] + u["y1"]) / 2
        for k in range(6):
            x = u["x0"] + 60 + k * 22
            add(f"{uid}-CH{k+1}", "냉동기(터보 냉동기, 개념)", U, [x, ym - 14, 0.3, x + 14, ym - 8, 5.3], "#2f7fff", "D", ["HVAC_BENCH", "HVAC_OUP", "P2_UT"],
                D_NOTE + "증발기 쪽은 냉수(CHW), 응축기 쪽은 냉각수(CW)에 연결. 유틸리티동에 둔 것은 가정", fab="UT", fl="")
        add(f"{uid}-PMP", "냉수·냉각수 순환 펌프 스키드(개념)", U, [u["x0"] + 60, ym - 4, 0.3, u["x0"] + 190, ym - 1, 3.0], "#5c8fd6", "D", ["HVAC_BENCH"], D_NOTE, fab="UT")
        add(f"{uid}-HRC", "열회수 냉동기·열교환기(선택 계통, 개념)", U, [u["x0"] + 200, ym - 14, 0.3, u["x0"] + 216, ym - 8, 5.3], "#ff7ab8", "D", ["PCW_PAT", "HVAC_CKY"],
            D_NOTE + "응축열·환수열을 MAU 재열·예열용 온수로 돌려 쓰는 선택 계통. 평택 적용 여부는 확인하지 못함", fab="UT")
        add(f"{uid}-UPW", "초순수(UPW) 제조 설비(개념)", U, [u["x0"] + 60, ym + 6, 0.3, u["x0"] + 150, ym + 30, 9.0], "#9be7ff", "D", ["P3_UT", "WTR_USE"],
            D_NOTE + "전처리 → 역삼투·이온교환·탈기 → 저장 → 폴리싱. 삼성엔지니어링이 P3 UPW를 담당했다는 보도는 있으나 위치는 미확인", fab="UT")
        add(f"{uid}-RCL", "재이용수 회수 설비(개념)", U, [u["x0"] + 156, ym + 6, 0.3, u["x0"] + 196, ym + 30, 7.0], "#5fa8a0", "D", ["WTR_FLOW", "WTR_USE"], D_NOTE, fab="UT")
        add(f"{uid}-CHEM", "케미컬 저장·중앙 공급(CCSS) 설비(개념 · 시공사 보도: 한양이엔지)", U, [u["x0"] + 4, u["y0"] + 8, 0.3, u["x0"] + 30, u["y1"] - 8, 8.0], "#39d98a", "D", ["STI", "CSF_FSF", "HYENG", "HYENG2"],
            D_NOTE + "현장 관련 보도: 에스티아이 CCSS(평택 3기 Ph3·Ph4, 4기 Ph1·Ph2). 위치는 임의", fab="UT")
        add(f"{uid}-CHEM-DOCK", "케미컬 탱크로리 하역 베이(품질 확인 후 이송) — 충전 지점(개념)", T, [u["x0"] - 14, ym - 12, 0.0, u["x0"] - 1, ym + 12, 0.6], "#39d98a", "D", ["STI", "CSF_FSF"],
            "탱크로리에서 저장 탱크로 케미컬을 옮기는 접속점. 방류턱·누액 감지·품질 확인을 두는 것이 일반적. 위치는 임의의 개념 표시", fab="UT")
    add("UT-34-CT", "UT동 옥상 냉각탑 구역(추정)", U, [150, 1130, 45.0, 350, 1220, 53.0], "#c5ccd3", "C", ["ESRI", "P3_UT"],
        "위성영상에서 P3·P4 사이 유틸리티동 위로 수증기를 확인. 셀 수·범위는 가정", fab="UT", opacity=0.85)
    # cooling-water loops: chillers <-> towers
    pair("CW", [(-150, 1834, 6), (-150, 1834, 46), (-150, 1800, 46), (250, 1800, 46), (250, 1876, 46), (250, 1876, 19)], 1.2, "UT-12", d=(1.8, 1.8, 1.4))
    pair("CW", [(250, 1818, 46), (250, 1818, 19)], 1.2, "UT-12", d=(1.8, 0, 0))
    pair("CW", [(400, 1800, 46), (400, 1876, 46), (400, 1876, 19)], 1.2, "UT-12", d=(1.8, 1.8, 1.4))
    pair("CW", [(250, 1800, 46), (400, 1800, 46), (400, 1818, 46), (400, 1818, 19)], 1.2, "UT-12", d=(1.8, 1.8, 1.4))
    pair("CW", [(-150, 1161, 6), (-150, 1161, 49), (250, 1161, 49), (250, 1175, 49)], 1.2, "UT-34", d=(1.8, 1.8, 1.4))

    # ------------------------------------------------------------ campus trunks (concept corridor west of P2-P4 and south of P1)
    SPX, SPY = -316.0, 1925.0
    add("GAS-YARD", "벌크가스 수급·백업 야드(개념, 위치 임의)", U, [440, 1950, 0.0, 520, 2010, 0.4], "#6b6f3a", "D", ["GAS_SUP", "GAS_AF"],
        "보도: 벌크가스는 남측 가스사 플랜트에서 지하 배관으로 공급. 캠퍼스 안의 백업 저장 위치는 공개되지 않아 임의 위치에 개념만 표시")
    for k in range(4):
        add(f"GAS-TK{k+1}", "액화가스 저장 탱크(백업, 개념)", U, [448 + k * 9, 1988, 0.4, 453 + k * 9, 1993, 16.0], "#f4f4f0", "D", ["GAS_AF", "GAS_LINDE"], D_NOTE + "벌크가스 공급이 끊길 때를 대비한 액체 저장·기화 설비의 일반 구성")
    add("GAS-VAP", "기화기(개념)", U, [448, 1972, 0.4, 470, 1980, 7.0], "#d9dde0", "D", ["GAS_AF"], D_NOTE)
    add("GAS-PUR", "가스 정제 설비(개념)", U, [476, 1958, 0.4, 500, 1970, 6.0], "#ffd21f", "D", ["GAS_AF"], D_NOTE + "공정에 들어가기 전 불순물을 제거")
    add("GAS-FILL", "벌크가스 탱크로리 이송 접속점 — 충전 지점(개념)", T, [490, 1984, 0.0, 518, 1998, 0.6], "#ffd21f", "D", ["GAS_AF", "NFPA318"],
        "액화가스 탱크로리가 저장 탱크에 가스를 옮겨 넣는 접속점. 실린더 교체 구역과 구분되는 작업. 위치는 임의의 개념 표시")
    add("GAS-EDGE", "에어퍼스트 평택공장 방향(남쪽 약 1 km · P3·P4 공급 보도) — 인입 지점 개념", T, [185, 690, 0.0, 215, 706, 0.6], "#ffd21f", "M", ["KAKAO", "GAS_AF", "GAS_PARK", "GAS_PARK2", "GAS_SUP"],
        "카카오맵의 에어퍼스트 평택공장 위치는 이 모델 좌표로 약 (-413, -278), 캠퍼스 남쪽. 보도: 캠퍼스에서 직선 약 1 km, 지하 배관으로 산소·질소·아르곤·수소 공급, P3·P4 담당. 인입 지점·경로는 공개되지 않음")
    add("GAS-EDGE-AP", "에어프로덕츠코리아 평택공장 방향(북동쪽 인접 · P1 공급 보도) — 인입 지점 개념", T, [640, 2204, 0.0, 670, 2220, 0.6], "#ffd21f", "M", ["KAKAO", "GAS_AP", "GAS_SUP"],
        "카카오맵의 에어프로덕츠코리아 평택공장 위치는 약 (624, 2220), 캠퍼스 북동쪽 바로 옆('에어프로덕츠사거리' 지명도 있음). 보도: 평택캠퍼스 1공장에 산업용 가스 공급. 배관 경로는 공개되지 않음")
    add("GAS-EDGE-LD", "린데코리아 평택공장 방향(남서쪽 · 보도) — 인입 지점 개념", T, [-700, 790, 0.0, -670, 806, 0.6], "#ffd21f", "M", ["KAKAO", "GAS_LINDE", "GAS_SUP", "BLDG_REG"],
        "카카오맵의 린데코리아 평택공장 위치는 약 (-906, 776), 캠퍼스 남서쪽. 건축물대장(고덕동 1722): 대지 78,833.4㎡, 건축면적 27,316.3㎡, 연면적 22,665.15㎡, 주건축물 6동, 착공 2018-11-20, 사용승인 2023-04-27. 보도: 평택캠퍼스와 초창기부터 협력, 평택은 린데의 전자 산업용 단일 최대 사이트. 배관 경로는 공개되지 않음")
    route("GAS.BULK", [(640, 2212, 1.0), (505, 2212, 1.0), (505, 1998, 1.0)], 1.0); route("GAS.BULK", [(-670, 798, 1.0), (SPX, 798, 1.0), (SPX, 845, 1.0), (SPX, 845, 12.0)], 1.0)
    route("GAS.BULK", [(200, 706, 1.0), (200, 845, 1.0), (200, 845, 12.0), (SPX, 845, 12.0), (SPX, 880, 12.0)], 1.0)
    route("GAS.BULK", [(476, 1964, 3.0), (430, 1964, 3.0), (430, SPY, 12), (SPX, SPY, 12), (SPX, 880, 12)], 1.0)
    add("PWR-EDGE-E", "345 kV 고덕–서안성 송전선로 방향(동쪽, 23.5 km · 보도) — 지점 개념", T, [80, 660, 0.0, 110, 676, 0.6], "#ff2fa0", "A", ["PWR_345B", "PWR_345", "PWR_HK", "OSM"],
        "보도: 가공 10.2 km(철탑 35기) + 지중 13.3 km, 2023-09-12 준공, P1~P4 공급 능력 2 GW, 공사비 약 3,900억 원 삼성전자 부담. OSM에는 동쪽에서 오는 345 kV 지중 케이블이 등록. 변전소 인입 지점은 개념 표시")
    add("PWR-EDGE-W", "500 kV 북당진–고덕 HVDC 방향(서쪽, 34.2 km 지중 · 보도) — 지점 개념", T, [-520, 660, 0.0, -490, 676, 0.6], "#ff2fa0", "A", ["PWR_HVDC", "PWR_GD"],
        "보도: 당진 쪽 발전력 3 GW를 평택 등 수도권 남부로 보내는 초고압 직류 송전(1단계 1.5 GW 2020-12). 고덕에 변환소. 인입 지점은 개념 표시")
    add("PWR-RCV", "캠퍼스 수전·주변압 설비(154동 추정 위치 · 설비는 개념)", U, [394, 880, 0.3, 418, 902, 9.0], "#ff2fa0", "C", ["PWR_GD24", "NAMU", "P4_SITE", "YT_DAL2"],
        D_NOTE + "한전 변전소에서 받은 전력을 캠퍼스 배전 전압으로 낮추는 설비. 캠퍼스 수전 전압은 공개 자료에서 확인하지 못함. 위치는 현장 관찰 채널 주석 사진의 '154동(변전소)'(P4 팹 남동쪽 별동)에 맞춰 v7에서 옮김. 내부 설비 형태·한전 변전소와의 연결 경로는 개념")
    route("ELEC.HV", [(80, 668, 2.0), (34, 668, 2.0), (34, 700, 2.0)], 1.4); route("ELEC.HV", [(-490, 668, 2.0), (-266, 668, 2.0), (-266, 700, 2.0)], 1.4)
    route("ELEC.HV", [(-266, 768, 2.0), (-266, 812, 2.0), (34, 812, 2.0)], 1.4); route("ELEC.HV", [(34, 762, 2.0), (34, 812, 2.0), (406, 812, 2.0), (406, 880, 2.0)], 1.4)
    # parking-lot PV canopy (official: Pyeongtaek 0.4 MW + 0.2 MW -> 0.7 MW); location = bluish canopy seen on the satellite image (estimate)
    add("PARK-NW", "임직원주차장(카카오맵 표기 · OSM 경계)", U, [-769, 2043, -0.1, -557, 2247, 0.12], "#39424c", "B", ["OSM", "ESRI"], "OpenStreetMap 주차장 경계와 위성영상의 주차 차량으로 확인", opacity=0.9)
    add("PV-CANOPY", "주차장 태양광 캐노피(존재: 공식 자료 · 위치: 추정)", U, [-760, 2058, 4.2, -695, 2102, 4.8], "#3b5fae", "C", ["SR2024", "SR2021", "PV_NEWS", "PV_KT", "ESRI"],
        "지속가능경영보고서: 평택사업장 태양광 0.4 MW(2021·2022 보고서), 2022년 0.2 MW 추가, 0.7 MW(2024 보고서). 보도: 반도체 사업장 주차장에 패널 설치, 생산 라인에는 쓰지 않음. 이 위치는 위성영상에서 주차장 남서쪽의 청회색 지붕(약 65 × 44 m)을 본 추정이며 태양광인지 확인하지 못함")
    route("ELEC.PV", [(-727, 2080, 4.2), (-727, 2080, 0.8), (-727, 2150, 0.8)], 0.6)
    # water intake markers (source = press; entry point = arbitrary)
    add("WTR-EDGE", "공업용수 인입(광역상수도·팔당 계통, 보도) — 지점 임의", T, [48, 2300, 0.0, 76, 2316, 0.6], "#3aa0ff", "C", ["WTR_22", "WTR_30", "WTR_USE", "WTR_EA"],
        "보도: 평택캠퍼스는 하루 22만 t의 공업용수를 공급받음(1·2공장 가동 기준, 2020·2024 보도). 기흥·화성·평택 공급수는 한강 팔당에서 취수(2022 보도). 캠퍼스로 들어오는 지점·관로는 공개되지 않음")
    add("WTR-REUSE-EDGE", "하수처리 재이용수 인입(수원·화성·오산, 2030년경 계획) — 지점 임의", T, [84, 2300, 0.0, 112, 2316, 0.6], "#7ad0c0", "C", ["WTR_REUSE", "WTR_33", "WTR_USE"],
        "보도: 수원 28만 t·화성 동탄2 4.2만 t·오산 5만 t = 하루 37.2만 t을 고덕(평택)사업장에 공급하는 계획, 전용 관로 약 60 km. 2026-09 보도 기준 화성·오산 약 12만 t, 수원 약 21만 t 사업 준비 중. 아직 공급 전인 계획")
    for sysn, o in (("WTR.RAW", 0.0), ("WTR.REUSE", 1.4)):
        route(sysn, [(62 + o, 2300, 1.4), (62 + o, 1933 + o, 1.4), (-209 + o, 1933 + o, 1.4), (-209 + o, 1866, 1.4)], 0.8)
        route(sysn, [(-209 + o, 1933 + o, 1.4), (-325 - o, 1933 + o, 1.4), (-325 - o, 1192 + o, 1.4), (-202, 1192 + o, 1.4)], 0.8)
    for k, dx in enumerate((-1.8, -3.6)):
        route("ELEC.MV", [(394, 886 + k * 1.8, 9), (362, 886 + k * 1.8, 9), (362, 852 + k * 1.8, 9), (SPX + dx, 852 + k * 1.8, 9), (SPX + dx, SPY + 4 + k * 1.8, 9), (-506 - k * 1.8, SPY + 4 + k * 1.8, 9), (-506 - k * 1.8, 2128, 9)], 0.9)

    # ------------------------------------------------------------ per fab
    NEAR = {"P1": ("S", "UT-12"), "P2": ("N", "UT-12"), "P3": ("S", "UT-34"), "P4": ("N", "UT-34")}
    LV = [("1F", 0.0, 9.0), ("2F", 9.0, 16.5), ("3F", 16.5, 24.0), ("4F", 24.0, 33.0), ("5F", 33.0, 41.0), ("6F", 41.0, 48.5), ("7F", 48.5, 56.0), ("8F", 56.0, 66.0)]
    for pid, f in F.items():
        side, uid = NEAR[pid]; u = UT[uid]
        x0, x1, y0, y1, endx, H = f["x0"], f["x1"], f["y0"], f["y1"], f["endx"], f["H"]
        cxa, cxb, cya, cyb = f["cr"]; cm = (f["core"][0] + f["core"][1]) / 2; ymid = (cya + cyb) / 2
        iy0, iy1 = y0 + 1.5, y1 - 1.5
        ns = (lambda d: iy0 + d) if side == "S" else (lambda d: iy1 - d)     # y inside the near support strip
        fs = (lambda d: iy1 - d) if side == "S" else (lambda d: iy0 + d)     # y inside the far support strip
        ra_n = (cya - 2.5) if side == "S" else (cyb + 2.5); ra_f = (cyb + 2.5) if side == "S" else (cya - 2.5)
        uy = (u["y0"] + u["y1"]) / 2
        # --- thermal: CHW riser in the near strip, headers at the two plenum levels (MAU + DCC), branch to PCW heat exchangers
        rx = cm
        pair("CHW", [(rx, uy - 10, 6), (rx, uy - 10, 20), (rx, ns(6), 20), (rx, ns(6), 3), ], 1.2, pid)
        pair("CHW", [(rx, ns(6), 20), (rx, ns(6), 61)], 1.2, pid)
        for zf in (24.0, 56.0):
            z = zf + 4.6
            pair("CHW", [(rx, ns(6), z), (rx, ra_n, z)], 1.0, pid)
            pair("CHW", [(cxa + 4, ra_n, z), (cxb - 4, ra_n, z)], 1.0, pid)
            pair("CHW", [(rx, ra_n, z), (rx, ra_f, z)], 1.0, pid)
            pair("CHW", [(cxa + 4, ra_f, z), (cxb - 4, ra_f, z)], 1.0, pid)
            route("HR", [(rx + 5, ns(9), z + 2.2), (cxa + 10, ns(9), z + 2.2)], 0.7, pid); route("HR", [(rx + 5, ns(9), z + 2.2), (cxb - 10, ns(9), z + 2.2)], 0.7, pid)
        route("HR", [(u["x0"] + 208, uy - 11, 6), (rx + 5, uy - 11, 22), (rx + 5, ns(9), 22), (rx + 5, ns(9), 62.8)], 0.7, pid)
        # --- PCW: heat-exchanger skid in each FSF (1F, 5F), mains under the cleanroom, bay branches, drops to tools
        n, centres, _ = bays(cxa, cxb)
        for fl, zf in (("1F", 0.0), ("5F", 33.0)):
            hx = [rx + 14, min(ns(8), ns(15)), zf + 0.3, rx + 30, max(ns(8), ns(15)), zf + 3.6]
            add(f"{pid}-{fl}-PCW-HX", f"{pid} {fl} PCW 열교환기·순환 펌프(개념)", U, hx, "#a35cff", "D", ["HVAC_BENCH", "HVAC_OUP", "PCW_PAT"],
                D_NOTE + "1차측은 냉수(CHW), 2차측은 장비 전용 폐회로(PCW). 문헌 사례: 공급 17.8 °C·환수 21 °C", fab=pid, fl=fl)
            pair("CHW", [(rx, ns(6), zf + 3.0), (rx + 14, ns(6), zf + 3.0), (rx + 14, ns(10), zf + 3.0)], 0.8, pid, d=(0, 1.2, 0.9))
            z = zf + 5.3
            pair("PCW", [(rx + 22, ns(11), zf + 3.6), (rx + 22, ns(11), z), (rx + 22, ymid - 3, z)], 0.8, pid, d=(1.2, 0, 0.9))
            pair("PCW", [(cxa + 4, ymid - 3, z), (cxb - 4, ymid - 3, z)], 0.8, pid, d=(0, 1.4, 0.9))
            for bi, bx in enumerate(centres):
                if bi % 2: continue
                pair("PCW", [(bx + 1.7, cya + 6, z), (bx + 1.7, cyb - 6, z)], 0.45, pid, d=(0.8, 0, 0.9))
                pair("PCW", [(bx + 1.7, cya + 32, z), (bx + 1.7, cya + 32, zf + 17.6)], 0.45, pid, d=(0.8, 0, 0))
        # --- gases: bulk header + specialty-gas room -> CSF headers that meet the existing VMB->tool risers
        gy = ns(12)
        if pid == "P1": route("GAS.BULK", [(rx - 9, SPY, 12), (rx - 9, gy, 12)], 0.8, pid)
        else: route("GAS.BULK", [(SPX, gy, 12), (rx - 9, gy, 12)], 0.8, pid)
        route("GAS.BULK", [(rx - 9, gy, 12), (rx - 9, gy, 46.4)], 0.8, pid)
        gr = [cxa + 10, min(ns(5), ns(19)), 0.3, cxa + 44, max(ns(5), ns(19)), 5.0]
        add(f"{pid}-GASROOM", f"{pid} 특수가스 공급실(가스 캐비닛·BSGS, 개념)", U, gr, "#b8e000", "D", ["NFPA318", "CSF_FSF", "DCC"],
            D_NOTE + "실린더·대용량 용기를 가스 캐비닛·BSGS에 물려 VMB로 보내는 방. 공시 공사명 'P4 Ph4 S-GAS 1공구'로 특수가스 공사의 존재만 확인", fab=pid, fl="1F")
        wall = y0 if side == "S" else y1; sgn = -1 if side == "S" else 1
        dk = sorted((wall + sgn * 1.0, wall + sgn * 13.0))
        add(f"{pid}-CYL-DOCK", f"{pid} 실린더·BSGS 반입·교체 구역(개념)", T, [cxa + 14, dk[0], 0.0, cxa + 40, dk[1], 0.6], "#b8e000", "D", ["NFPA318", "CSF_FSF"],
            "빈 용기를 떼고 새 용기를 물리는 '교체' 작업 구역. 현장에서 실린더를 충전하지 않음. 위치는 임의의 개념 표시", fab=pid, fl="1F")
        for fl, zc in (("2F", 9.0), ("6F", 41.0)):
            zb = zc + 5.4; zsg = zc + 2.2
            route("GAS.BULK", [(rx - 9, gy, zb), (rx - 9, ymid, zb)], 0.7, pid); route("GAS.BULK", [(cxa + 4, ymid, zb), (cxb - 4, ymid, zb)], 0.7, pid)
            route("GAS.SPEC", [(cxa + 6, ns(12), 5.0), (cxa + 6, ns(12), zsg), (cxa + 6, cya + 20, zsg)], 0.6, pid)
            route("GAS.SPEC", [(cxa + 6, cya + 20, zsg), (cxa + 6, cyb - 20, zsg)], 0.6, pid)
            for yy in (cya + 20, cyb - 20): route("GAS.SPEC", [(cxa + 6, yy, zsg), (cxb - 4, yy, zsg)], 0.6, pid)
        # --- exhaust: segregated collectors in each FSF, risers in the support strips, headers + treatment on the roof racks
        xs = [x for x in (x0 + 95, x0 + 235, x0 + 375, x0 + 515) if x < endx - 25]
        for sysn, yb, strip_y, dz in (("EXH.ACID", cya - 1.2, iy0 + 20, 0.0), ("EXH.ALK", cya - 2.6, iy0 + 22.2, 0.9), ("EXH.VOC", cyb + 1.2, iy1 - 20, 0.0), ("EXH.HEAT", cyb + 2.6, iy1 - 22.2, 0.9)):
            south = sysn in ("EXH.ACID", "EXH.ALK"); yr = (y0 + 8.0 + dz * 2.4) if south else (y1 - 8.0 - dz * 2.4)
            for zf in (0.0, 33.0):
                route(sysn, [(cxa + 2, yb, zf + 7.0 + dz * 0.5), (cxb - 2, yb, zf + 7.0 + dz * 0.5)], 0.8, pid)
                for x in xs: route(sysn, [(x + dz * 2, yb, zf + 7.0 + dz * 0.5), (x + dz * 2, yr, zf + 7.0 + dz * 0.5)], 0.8, pid)
            for x in xs: route(sysn, [(x + dz * 2, yr, 7.0), (x + dz * 2, yr, H + 1.4 + dz)], 0.9, pid)
            route(sysn, [(x0 + 40, yr, H + 1.4 + dz), (endx - 15, yr, H + 1.4 + dz)], 1.1, pid)
        for k, x in enumerate(xs[::2] or xs[:1]):
            add(f"{pid}-RTO-{k+1}", f"{pid} 옥상 VOC 농축 로터 + 산화기(개념)", U, [x + 14, y1 - 22, H, x + 30, y1 - 13, H + 7.0], "#ff4d6d", "D", ["EXH_AAQR", "P3_UT"],
                D_NOTE + "저농도·대풍량 유기 배기를 제올라이트 로터로 농축한 뒤 산화 처리하는 일반 구성. 평택 적용 설비는 확인하지 못함", fab=pid, fl="RF")
            add(f"{pid}-RCS-{k+1}", f"{pid} 옥상 RCS(재생 촉매 시스템 — 공정가스 저감, 보고서 명시 · 위치 개념)", U, [x + 32, y0 + 13, H, x + 46, y0 + 21, H + 7.0], "#c084fc", "C", ["SR2023", "P3_UT"],
                "삼성전자 지속가능경영보고서(2023): 반도체 사업장의 공정가스(F-gas) 저감에 POU 스크러버와 옥상에 설치한 RCS를 운영. 평택의 대수·위치는 공개되지 않아 개념 표시", fab=pid, fl="RF")
            add(f"{pid}-ALKSCR-{k+1}", f"{pid} 옥상 알칼리 전용 습식 스크러버(개념)", U, [x + 14, y0 + 13, H, x + 26, y0 + 20, H + 6.0], "#ffb98a", "D", ["EXH_AAQR", "EXH_PAT"],
                D_NOTE + "암모니아 계열 배기를 산 배기와 분리해 처리하는 일반 구성", fab=pid, fl="RF")
        # --- wastewater: three segregated headers in 1F, concept trench (drawn on grade) to the green building (assumed S1 / S2)
        ex_y = {"P1": 1930.0, "P2": 1516.0, "P3": 1256.0, "P4": 1094.0}[pid]; tgt = (500.0, 1150.0) if pid != "P4" else (500.0, 960.0)
        for k, sysn in enumerate(("WW.F", "WW.AA", "WW.ORG")):
            o = k * 1.1; yh = (cya + 4 + o) if ex_y < y0 else (cyb - 4 - o)
            route(sysn, [(cxa + 4, yh, 0.9), (cxb - 4, yh, 0.9)], 0.6, pid)
            route(sysn, [(cm + 4 + o, yh, 0.9), (cm + 4 + o, ex_y + o, 0.9), (478 + o, ex_y + o, 0.9), (478 + o, tgt[1] + o, 0.9), (tgt[0], tgt[1] + o, 0.9)], 0.6, pid)
        # --- chemicals: dock/CCSS in the utility building -> CDS units in the south strip of each FSF
        cx = cm - 16; cy_s = iy0 + 6.0
        route("CHEM", [(u["x0"] + 17, uy, 8.0), (u["x0"] + 17, uy, 18.0), (cx, uy, 18.0), (cx, ns(14), 18.0), (cx, ns(14), 37.6)], 0.6, pid)
        route("CHEM", [(cx, ns(14), 18.0), (cx, ns(14), 4.6)], 0.6, pid)
        for zf in (0.0, 33.0):
            z = zf + 4.6
            if side == "S": route("CHEM", [(cx, ns(14), z), (cx, cy_s, z)], 0.6, pid)
            else: route("CHEM", [(cx, ns(14), z), (cx, cy_s, z)], 0.6, pid)
            route("CHEM", [(cxa + 8, cy_s, z), (cxb - 4, cy_s, z)], 0.6, pid)
        # --- UPW loop + reclaim
        ux = cm + 8
        pair("UPW", [(u["x0"] + 105, uy + 18, 9.0), (u["x0"] + 105, uy + 18, 24.0), (ux, uy + 18, 24.0), (ux, ns(17), 24.0), (ux, ns(17), 12.0)], 0.7, pid, d=(1.1, 1.1, 0.8))
        pair("UPW", [(ux, ns(17), 24.0), (ux, ns(17), 46.6)], 0.7, pid, d=(1.1, 1.1, 0))
        for zc in (9.0, 41.0):
            z = zc + 3.6; yl = cyb - 8 if side == "S" else cya + 8
            pair("UPW", [(ux, ns(17), z), (ux, yl, z)], 0.6, pid, d=(1.1, 0, 0.8)); pair("UPW", [(cxa + 4, yl, z), (cxb - 4, yl, z)], 0.6, pid, d=(0, 1.1, 0.8))
        route("RCL", [(cm + 12, cya + 9 if side == "S" else cyb - 9, 1.8), (cm + 12, ns(20), 1.8), (cm + 12, uy + 18, 1.8), (u["x0"] + 176, uy + 18, 1.8), (u["x0"] + 176, uy + 18, 7.0)], 0.6, pid)
        # --- power: MV feeders -> electrical rooms in the north strip (1F, 5F), LV bus ducts up to the CSF, UPS, emergency generator
        ey = cyb + 6.0
        for k, dxs in enumerate((-1.8, -3.6)):
            yb = ey + 2 + k * 1.6
            if pid == "P1": route("ELEC.MV", [(-506 - k * 1.8, yb, 9), (x0 + 24, yb, 9)], 0.9, pid)
            else: route("ELEC.MV", [(SPX + dxs, yb, 9), (x0 + 24, yb, 9)], 0.9, pid)
            route("ELEC.MV", [(x0 + 24, yb, 7.6), (x0 + 24, yb, 40.6)], 0.9, pid)
            for zf in (0.0, 33.0): route("ELEC.MV", [(x0 + 24, yb, zf + 7.6), (cxb - 6, yb, zf + 7.6)], 0.8, pid)
        for fl, zf in (("1F", 0.0), ("5F", 33.0)):
            add(f"{pid}-{fl}-UPS", f"{pid} {fl} UPS·순간전압강하 보상 설비(개념)", U, [x0 + 30, cyb + 9, zf + 0.3, x0 + 52, cyb + 20, zf + 3.4], "#f2e6ff", "D", ["PWR_345"],
                D_NOTE + "선정된 중요 부하만 공급. 팹 전체 공정 부하를 감당하는 것이 아님. 용량·공급 범위는 공개되지 않음", fab=pid, fl=fl)
            route("ELEC.UPS", [(x0 + 52, cyb + 14, zf + 6.2), (cxb - 6, cyb + 14, zf + 6.2)], 0.6, pid)
            xb = cxa + 30
            while xb < cxb - 10:
                route("ELEC.LV", [(xb, ey + 2, zf + 7.6), (xb, ey + 2, zf + 14.6), (xb, cya + 6, zf + 14.6)], 0.6, pid); xb += 130.0
        add(f"{pid}-GEN", f"{pid} 비상발전기(개념)", U, [x0 + 4, cyb + 8, 0.3, x0 + 22, cyb + 21, 4.6], "#ff3030", "D", ["PWR_345"],
            D_NOTE + "정전 시 선정된 비상 부하(배기·감지·피난·소방 설비 등)를 절체 설비를 거쳐 공급. 연료·배기·냉각 계통이 따로 필요", fab=pid, fl="1F")
        route("ELEC.EMERG", [(x0 + 22, cyb + 17, 5.4), (cxb - 6, cyb + 17, 5.4)], 0.6, pid); route("ELEC.EMERG", [(x0 + 26, cyb + 17, 5.4), (x0 + 26, cyb + 17, 38.4), (cxb - 6, cyb + 17, 38.4)], 0.6, pid)
    # wastewater treatment stages inside the assumed green buildings + treated discharge to the campus edge
    for gid, (gx0, gy0, gy1) in {"S1": (484, 1057, 1232), "S2": (484, 877, 1032)}.items():
        ym = (gy0 + gy1) / 2
        add(f"{gid}-WW-F", "불소계 폐수 처리 단계(개념)", U, [gx0 + 12, ym + 20, 0.3, gx0 + 60, ym + 60, 6.0], "#8b5a2b", "D", ["GREEN", "GREEN21B", "EA_P2WT"], D_NOTE + "공식 공개(2021): 폐수는 성분별 6가지로 구분해 처리, 알칼리성 폐수는 활성탄 필터링, 질소 제거(유기 처리)에는 복합 유기탄소원 사용. 이 모델은 3계통으로만 단순화했고 6가지의 구체 명칭·배치는 확인하지 못함. P2 수처리 설비 규모는 폐수처리 86,000 m³/d(삼성E&A)", fab="UT")
        add(f"{gid}-WW-AA", "산·알칼리계 폐수 중화 단계(개념)", U, [gx0 + 12, ym - 25, 0.3, gx0 + 60, ym + 12, 6.0], "#b88655", "D", ["GREEN"], D_NOTE, fab="UT")
        add(f"{gid}-WW-ORG", "유기계 폐수 처리 단계(개념)", U, [gx0 + 12, ym - 70, 0.3, gx0 + 60, ym - 33, 6.0], "#6b4a1e", "D", ["GREEN"], D_NOTE, fab="UT")
        for k in range(6):
            add(f"{gid}-SD-{k}", "스크린도어형 유리 격벽 설비 열(공식 영상 확인 · 위치 개념)", U, [gx0 + 70 + k * 11, ym - 3.0, 0.3, gx0 + 80 + k * 11, ym - 2.5, 3.4], "#9fd8c8", "C", ["YT", "WW_TUNNEL"],
                "공식 영상(2026-06, 약 1분 24초)에 SAMSUNG 로고가 붙은 유리문이 줄지어 선 밀폐 설비와 바닥의 녹색 띠가 나옴. 공식 소개 글은 폐수처리장에 누출을 막는 '스크린도어'가 있다고 설명. 영상의 장면이 폐수처리장인지는 자막으로 확인하지 못했고 위치는 개념", fab="UT", opacity=0.75)
        route("WW.OUT", [(gx0 + 60, ym, 1.2), (gx0 + 150, ym, 1.2), (700, ym, 1.2), (700, 1045, 1.2), (728, 1045, 1.2)], 0.8)
    add("P4-UPW-CPX", "P4 복합동 초순수(UPW) 설비(존재: 공시 · 위치·형상: 개념)", U, [314, 905, 0.3, 343, 1025, 12.0], "#4aa8ff", "C", ["HSCT", "EA_P4", "P4_4FAC"],
        "한성크린텍 공시 보도: '초순수 설비가 구축되는 복합동 공사'. 삼성E&A 공시 공사명에도 '복합동, …, UPW 마감공사'. 복합동 안의 실제 위치·규모는 공개되지 않아 팹 동측 단부 블록(복합동 추정) 안에 개념 박스로 표시. 기존 UT동 안의 UPW 개념 설비와 배관 경로는 그대로 두었으며 P4의 실제 공급 경로는 확인하지 못함", fab="P4")
    add("WW-EDGE", "처리수 방류 경계(보도: 평택시 공공폐수처리시설 → 서정리천)", T, [728, 1035, 0.0, 756, 1055, 0.6], "#4fb3a5", "A", ["GREEN", "WTR_FLOW", "WW_PFAS", "WW_PFAS2", "WW_PATH", "WW_TEMP", "WW_PFAS3", "BLDG_REG"],
        "보도(2020년 기준): 평택캠퍼스 하루 평균 약 6.7만 t 사용, 약 5.4만 t이 평택시 폐수종말처리장을 거쳐 서정리천으로 방류. 건축물대장: 고덕동 1721(삼성1로 60)에 '하수등처리시설' — 대지 150,297.2㎡, 건축면적 8,429.26㎡, 연면적 21,840.49㎡, 사용승인 2022-07-15. 보도의 고덕 공공폐수처리시설과 같은 시설인지는 대장만으로 확정하지 못함. 경로(2026-10 경기도 점검 보도): 사내 수처리시설 그린동(1차 처리) → 고덕 공공폐수처리시설 → 서정리천 → 진위천 → 안성천 → 평택호. 2026-10 시민단체 발표의 PFAS 17종은 고덕산단 공공폐수처리시설 최종 방류구(고덕동 2745번지 서정리천)에서 채취한 시료의 결과이며, 이 시설에는 삼성전자 외 다른 시설의 처리수도 들어오므로 전량을 삼성전자 배출로 단정할 수 없다는 보도가 있음. 삼성전자 계획(보도): PFAS 분리·농축 후 전기화학 처리 기술 실증설비 2026-12 설치, 2027-08 적용. 방류수 수온저감시설은 냉각탑이 아닌 열에너지 활용 방식으로 약 30 ℃ → 17 ℃ 이하 목표, 2026-12~2027-02 시운전. 수온저감시설·실증설비의 위치는 공개되지 않아 모델에 넣지 않음. 이 박스의 위치는 개념 표시이며 실제 방류구 좌표가 아님")
    return USYS, UGROUPS, UTIL

USRC = {
 "WW_PATH": ("이투데이 2026-10: 경기도 점검 — P5 현장·P4 라인·그린동·고덕 공공폐수처리시설·서정리천 방류 지점", "https://www.etoday.co.kr/news/view/2632115"),
 "WW_TEMP": ("이투데이 2026-11: 방류수 30도→17도 이하, 열에너지 활용 수온저감, 12월~2027-02 시운전", "https://www.etoday.co.kr/news/view/2647008"),
 "WW_PFAS3": ("이투데이 2026-11: 고덕산단 공공폐수처리시설 최종 방류수 PFAS 17종 — 다른 시설 처리수도 유입, 삼성은 분리·농축+전기화학 처리 기술", "https://www.etoday.co.kr/news/view/2642674"),
 "WTR_EA": ("삼성E&A 프로젝트 소개: 평택 P 공정용수처리 Phase 1 — 팔당댐 원수 여과, 13만 m³/d, 1단계(P1·P2)+증설(P3 Ph1) 14.5만 m³/d 공급, 2단계(P3·P4) 진행", "https://samsungena.com/kr/business/project-template?idx=79"),
 "WW_PFAS": ("프레시안 2026-10-19: 평택캠퍼스 방류수 PFAS 분석 발표 — 채수 지점 고덕동 2745번지 서정천 종단 방류구", "https://www.pressian.com/pages/articles/2026101913350826763"),
 "WW_PFAS2": ("아시아경제 2026-11-11: 평택사업장 PFAS 저감 실증설비 12월 설치, 방류수 냉각시설 시운전(민·관·산·학 협의체 4차)", "https://view.asiae.co.kr/article/2026111117142786508"),
 "WW_TUNNEL": ("삼성전자 반도체 뉴스룸 [내일도 애쓰지 Ep.5]: 평택캠퍼스 폐수처리장 하루 7만 t, 2.6 km 지하 통로, 스크린도어", "https://news.samsungsemiconductor.com/kr/?p=12802"),
 "PWR_GD24": ("서울경제 2024-12 [우리동네 변전소] 고덕변전소: 캠퍼스와 도로 하나 사이, 지하 1층~지상 4층, 연면적 10만㎡, 1변전소 2016·2변전소 2022", "https://www.sedaily.com/article/14000160"),
 "PWR_GD2": ("동양 건설 실적: 345kV 고덕#2 변전소 토건공사 — 지제동 302, 대지 102,076㎡, 연면적 17,853.72㎡, 2022-11 준공", "https://tongyanginc.co.kr/portfolio-item/345kv-%EA%B3%A0%EB%8D%952-%EB%B3%80%EC%A0%84%EC%86%8C-%ED%86%A0%EA%B1%B4%EA%B3%B5%EC%82%AC/"),
 "PWR_345B": ("전기에너지뉴스 2023-09: 고덕–서안성 가공 10.2 km·철탑 35기·지중 13.3 km, 기존 154 kV 고덕–평택·송탄–진위", "https://www.elec-inews.co.kr/news/articleView.html?idxno=9655"),
 "PWR_HL": ("비즈니스포스트 2024-10: HL디앤아이한라, 삼성전자 '평택 345kV 변전소 신축공사' 1,429억 원(A4-1블록)", "https://www.businesspost.co.kr/BP?command=article_view&num=368586"),
 "PWR_P5": ("이투뉴스 2022-09: 한전·삼성 평택캠퍼스 2단지 전력공급협약 — 345 kV 변전소 2곳, 공장까지 154 kV, 1조 1,971억 원", "http://www.e2news.com/news/articleView.html?idxno=245573"),
 "PWR_GD3": ("평택시민신문 2024-08: 345 kV 신평택·고덕3 변전소 추진, 평택 2,300 MW 공급·3,637 MW 추가 필요", "https://www.pttimes.com/news/articleView.html?idxno=72936"),
 "SR2024": ("삼성전자 지속가능경영보고서 2024: 기흥 1.5 MW·평택 0.7 MW 등 국내 2.8 MW 태양광, 지열 냉난방 1,372 RT", "https://csr.samsung.com/data/Sustainability_report_2024_kr.pdf"),
 "SR2023": ("Samsung Electronics Sustainability Report 2023: Pyeongtaek 0.4 MW PV + 738 RT geothermal, 0.2 MW added in 2022, waste-heat recovery, POU scrubbers + rooftop RCS", "https://download.semiconductor.samsung.com/resources/others/Samsung_Electronics_Sustainability_Report_2023_ENG.pdf"),
 "SR2021": ("삼성전자 지속가능경영보고서 2021: 평택사업장 태양광 0.4 MW·지열 200 RT", "https://images.samsung.com/kdp/aboutsamsung/overview/sustainability_report_kr_2021_01.pdf"),
 "PV_NEWS": ("이투데이 2021-04: 기흥·화성·평택·온양 주차장 태양광(연 2,847 MWh), 화성·평택 건물 하부 지열", "https://www.etoday.co.kr/news/view/2011039"),
 "PV_KT": ("The Korea Times 2021-04: parking-lot solar panels at four chip sites; power not used for production lines", "http://m.koreatimes.co.kr/pages/article.asp?newsIdx=306527"),
 "WTR_22": ("경기일보 2020-07: 평택공장 하루 22만 t 공급, 6공장까지 25만 t 추가 필요, 팔당·충주댐 또는 안성천 대안", "https://www.kyeonggi.com/news/articleView.html?idxno=2306223"),
 "WTR_22B": ("경기일보 2024-10 의정단상: 평택캠퍼스 하루 22만 t, 수원 하수처리수 29만 t 재이용 구상, 2030년 공급 전망", "https://www.kyeonggi.com/article/20241031580413"),
 "WTR_REUSE": ("서울경제 2022-11: 수원 28만·동탄2 4.2만·오산 5만 t → 고덕, 관로 약 60 km·약 6,000억 원, 2030년부터", "https://www.sedaily.com/article/13526484"),
 "WTR_33": ("아주경제 2026-09: 화성·오산 하루 약 12만 t, 수원 약 21만 t 하수처리수 재이용 사업 준비", "https://www.ajunews.com/view/20260911085511428"),
 "WTR_30": ("경향신문 2022-11: 기흥·화성·평택 공급수 하루 약 30만 t, 모두 팔당댐에서 취수", "https://www.khan.co.kr/article/202211302212005"),
 "GAS_PARK": ("전자신문 2024-08: 고덕캠퍼스 남쪽 방축리 46만㎡ 첨단복합산단에 가스 3사 입주, 하수처리수 하루 2만 4,000 t 공급 계획", "https://www.etnews.com/20240817000023"),
 "GAS_PARK2": ("SBS(연합) 2026-10: 고덕 공공하수처리장 → 첨단복합산단 3.23 km·지름 50 cm 관로 착공, 린데·에어퍼스트·에어프로덕츠", "https://news.sbs.co.kr/news/endPage.do?news_id=N1008792606"),
 "PWR_345": ("전기신문 2023-09: 345 kV 고덕–서안성 송전선로 준공, 평택 P1~P4 전력 공급 능력 2 GW", "https://www.electimes.com/news/articleView.html?idxno=325868"),
 "PWR_HK": ("한국경제 생글생글 2023-09: 고덕–서안성 23.5 km, 공사비 3,900억 원 삼성전자 부담, 기존 송전선은 154 kV", "https://sgsg.hankyung.com/article/2023091515061"),
 "PWR_154": ("서울파이낸스 2018: 2공장은 154 kV 고덕–평택·송탄–진위, 3·4공장은 345 kV 선로 필요", "https://www.seoulfn.com/news/articleView.html?idxno=336324"),
 "PWR_GD": ("전기신문 2018: 고덕변전소 — 345 kV 변압기실과 154 kV GIS실", "https://www.electimes.com/news/articleView.html?idxno=152094"),
 "PWR_HVDC": ("세계일보 2023-08: 500 kV 북당진–고덕 HVDC(34.2 km 지중, 3 GW)", "https://www.segye.com/newsView/20230802514964"),
 "WTR_USE": ("평택시민신문 2022-12: 평택캠퍼스 공업용수 하루 12만 t, 하수처리수 37.2만 t 공급 협약", "https://www.pttimes.com/news/articleView.html?idxno=67117"),
 "GREEN": ("평택시사신문 2021: 그린동 2곳, 하루 약 7만 t 정화, 97% 자동화, 2020년 6.7만 t 사용·5.4만 t 서정리천 방류", "https://www.ptsisa.com/news/articleView.html?idxno=32595"),
 "WTR_FLOW": ("삼성전자 지속가능경영: 수자원 흐름도(2024년, 전사)", "https://www.samsung.com/sec/sustainability/popup/popup_doc/AYStMpdqB1cAIyC3"),
 "GAS_SUP": ("인베스트조선 2024-08: 평택 P1~P4 가스 공급은 에어프로덕츠·린데·에어퍼스트 분담", "https://www.investchosun.com/site/data/html_dir/2024/08/19/2024081980260.html"),
 "GAS_AF": ("머니투데이 2026-05: 에어퍼스트 평택공장 — 캠퍼스에서 약 1 km, 지하 배관, P3·P4 공급", "https://www.mt.co.kr/living/2026/05/27/2026052714124088732"),
 "GAS_AP": ("월간수소경제 2024-08: 에어프로덕츠코리아가 평택캠퍼스 1공장에 산업용 가스 공급", "https://www.h2news.kr/news/articleView.html?idxno=12828"),
 "GAS_LINDE": ("더구루 2025-04: 린데, 평택에 8번째 공기분리장치 — 초고순도 가스·수소 공급 확대", "https://www.theguru.co.kr/news/article.html?no=86537"),
 "HVAC_OUP": ("Int. J. Low-Carbon Technologies 14(4) 2019: MAU 구성, MAU 냉수 5–7 °C, PCW 약 13–20 °C, DCC·FFU 순환", "https://academic.oup.com/ijlct/article/14/4/508/5547016"),
 "HVAC_BENCH": ("Energy and Buildings 2008 'Power consumption benchmark for a semiconductor cleanroom facility system': PCW 17.8→21 °C, 1,121.9 ㎥/h, 1,187 RT", "https://www.sciencedirect.com/science/article/abs/pii/S0378778808000662"),
 "HVAC_CKY": ("CKY 기술 글(기업 자료): 저온 냉수 약 6–7 °C(MAU)·고온 냉수 약 15–18 °C(DCC), 열회수", "https://www.cky.com.tw/en/insights/semiconductor-fab-hvac"),
 "PCW_PAT": ("미국 특허 US 11,644,218: 팹의 PCW는 장비 전용 폐회로, 환수열 회수", "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11644218"),
 "EXH_PAT": ("미국 특허 US 7,857,880: 팹 배기 분류(열·일반 / 산 / 암모니아 / VOC), 옥상 습식 스크러버", "https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7857880"),
 "EXH_AAQR": ("Aerosol and Air Quality Research 2023: 제올라이트 농축 로터 + 산화기(VOC), 중앙 습식 스크러버(산·알칼리)", "https://aaqr.org/articles/aaqr-23-02-oa-0034.pdf"),
 "EXH_MKS": ("MKS 기술 자료: 진공 펌프 뒤 배기는 성상별 중앙 처리설비(스크러버)로 보냄", "https://www.mks.com/n/exhaust-gas-treatment/"),
}
