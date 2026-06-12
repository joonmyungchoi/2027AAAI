# GT 합성 규칙(gt_design_v1)의 sanity 검증용 프로토타입 — 샘플 10 instance × 4 persona GT 시퀀스 생성
"""
규칙 출처: design/gt_design_v1.md, design/personas_v1.md, design/template_matrix_v1.md
실행: python3 synth_sanity.py > sanity_output.md
"""

from dataclasses import dataclass, field

# ---------------- 상수 (초기값 — sanity 대상) ----------------
BAND = 7.5          # 발사 band ±분
GRID = 15           # 그리드 간격 분
PREP = 10           # 준비시간 분
B_EARLY, B_LATE = 30, 10  # lead buffer

# S2 이동 구성: (총 소요, 도보 구간, 대중교통 leg 존재)
TRANSPORT = {
    "근거리도보": (15, 15, False),
    "지하철":    (30, 10, True),
    "KTX":      (60, 10, True),
}

# 채널맵 (상황층): state -> 가용 채널
CHANNELS = {
    "default": {"visual": 1, "sound": 1, "vibe": 1},
    "통화":     {"visual": 1, "sound": 0, "vibe": 1},
    "회의":     {"visual": 1, "sound": 0, "vibe": 1},
    "운전":     {"visual": 0, "sound": 1, "vibe": 1},
}

PERSONAS = {  # (빈번도 많은가, 정도 강한가, lead 미리인가)
    "P_A 윤서": (False, False, True),
    "P_B 도현": (False, True, False),
    "P_C 하은": (True, False, False),
    "P_D 지훈": (True, True, True),
}


def fmt(m):  # 분 -> HH:MM
    return f"{int(m) // 60:02d}:{int(m) % 60:02d}"


@dataclass
class Event:
    time: int            # 분 (절대)
    kind: str            # weather_rain / weather_severe / cp_delay / cp_cancel / cp_move / transit_delay / state
    d_appt: int = 0      # ΔT_appt
    d_travel: int = 0    # Δtravel
    forced: bool = False # 1층 강제 공지 여부
    state: str = ""      # state 이벤트용
    dur: int = 0


@dataclass
class Instance:
    iid: str
    desc: str
    transport: str
    familiar: bool
    appt: int = 17 * 60         # T_appt 절대 분
    has_appt: bool = True       # no-op 용
    events: list = field(default_factory=list)


def rain_delta(transport):
    walk = TRANSPORT[transport][1]
    return 10 if walk >= 15 else 5  # 도보 비중 큰 구성만 승격 후보


def synth(inst: Instance, persona):
    """instance × persona -> trigger 별 GT 결정 리스트"""
    freq_high, depth_high, lead_early = persona
    buffer = B_EARLY if lead_early else B_LATE
    rows, checks = [], []

    if not inst.has_appt:
        win_start = inst.appt - 90
        grids = list(range(win_start, inst.appt + 1, GRID))
        for t in grids:
            rows.append((fmt(t), "grid", "silent", "no-op (약속 없음/완료)"))
        return rows, checks

    travel0 = TRANSPORT[inst.transport][0]
    # 창 길이: 90분, 단 travel+buffer+prep 이 넘치면 확장 (finding 후보)
    need = travel0 + buffer + PREP + BAND
    win = 90 if need <= 90 else (int((need + GRID - 1) // GRID) * GRID)
    win_start = inst.appt - win
    grids = list(range(win_start, inst.appt + 1, GRID))

    # 상태 변수
    appt, travel = inst.appt, travel0
    cancelled, fired_plan = False, None  # fired_plan = 마지막 안내한 출발시각
    state_now = "default"
    state_until = -1

    def fire_time():
        return appt - travel - PREP - buffer

    def depart_time():
        return appt - travel - PREP

    # R4: 관찰 창은 T_appt 갱신을 따라 연장 (이벤트로 약속이 밀리면 grid도 연장)
    final_appt = inst.appt + sum(e.d_appt for e in inst.events)
    grids = list(range(win_start, final_appt + 1, GRID))

    # 트리거 목록 = 그리드 + 이벤트 즉시
    triggers = sorted(set(grids + [e.time for e in inst.events]))
    ev_by_time = {e.time: e for e in inst.events}

    for t in triggers:
        kind = "event" if t in ev_by_time and t not in grids else (
            "grid+event" if t in ev_by_time else "grid")
        ev = ev_by_time.get(t)
        note, decision, content = "", "silent", []

        # state 갱신
        if ev and ev.kind == "state":
            state_now, state_until = ev.state, t + ev.dur
            note = f"state→{ev.state}({ev.dur}분)"
        if state_until >= 0 and t > state_until:
            state_now = "default"

        # R3: 이동 판정은 '안내한' 출발시각 기준 (user는 안내를 따름)
        moving = fired_plan is not None and t >= fired_plan

        if ev and ev.kind != "state":
            old_ft = fire_time()
            appt += ev.d_appt
            travel += ev.d_travel
            new_ft = fire_time()
            if ev.kind == "cp_cancel":
                cancelled = True
                decision, content = "fire", ["취소 공지"]
                note = "override1: 취소 — 이후 전부 silent"
            elif cancelled:
                decision, note = "silent", "취소 후 무효"
            elif ev.forced:
                decision = "fire"
                # R5: 이동 중이면 출발시각 대신 도착 영향 공지 (도착예정 = 출발시각 + 갱신된 travel)
                impact = (f"새 출발 {fmt(depart_time())}" if not moving
                          else f"도착예정 {fmt(fired_plan + travel)} vs 약속 {fmt(appt)}")
                content = [f"{ev.kind} 변경공지", impact]
                note = "override3: 1층 강제"
                if not moving:
                    fired_plan = depart_time()
            elif fired_plan is None:
                # R1: 첫 알림 미발사 상태 — 빈번도 필터 미적용, band 시작 도달 시 즉시 fire
                if t >= new_ft - BAND:
                    decision = "fire"
                    content = ["약속명/시각", f"출발 {fmt(depart_time())}"]
                    note = "첫 알림 (이벤트 trigger에서 창 도달)"
                    fired_plan = depart_time()
                else:
                    decision, note = "silent", "이르다 (첫 알림 전, 이벤트 흡수)"
            else:
                delta = abs(new_ft - old_ft)
                if delta > BAND:
                    decision = "fire"
                    impact = (f"새 출발 {fmt(depart_time())}" if not moving
                              else f"도착예정 {fmt(fired_plan + travel)} vs 약속 {fmt(appt)}")
                    content = [f"{ev.kind} 갱신", impact]
                    note = f"승격(Δ{delta:.0f}>7.5) — persona 무관"
                    if not moving:
                        fired_plan = depart_time()
                elif moving:
                    decision, note = "silent", f"미세(Δ{delta:.0f}) + 이동 중"
                elif freq_high:
                    decision = "fire"
                    content = [f"{ev.kind} 업데이트", f"출발 {fmt(depart_time())}"]
                    note = f"미세(Δ{delta:.0f}) — 빈번도 많"
                    fired_plan = depart_time()
                else:
                    decision, note = "silent", f"미세(Δ{delta:.0f}) — 빈번도 적"
        elif not cancelled and kind != "event":
            ft = fire_time()
            if moving:
                note = "이동 중 (override2)"
            elif fired_plan is not None and fired_plan == depart_time():
                note = "이미 동일 plan 안내"
            elif fired_plan is None and t >= ft - BAND:
                # R2: 첫 알림 = band 시작 이후 첫 trigger에서 무조건 fire (지각 방지)
                decision = "fire"
                content = ["약속명/시각", f"출발 {fmt(depart_time())}"]
                note = f"발사창 {fmt(ft)}±7.5" + ("" if t <= ft + BAND else " (창 경과 후 첫 trigger — 생성기 가드 필요)")
                fired_plan = depart_time()
            else:
                note = "이르다"

        # HOW (fire 시에만)
        modality = []
        if decision == "fire":
            ch = CHANNELS[state_now]
            if depth_high:
                modality = [m for m, ok in
                            [("popup", ch["visual"]), ("vibrate", ch["vibe"]), ("voice", ch["sound"])] if ok]
            else:
                modality = ["popup"] if ch["visual"] else ["voice"]
            k = 3 if depth_high else 1
            extra = []
            if not inst.familiar:
                extra += ["경로/수단", "출구"]
            if any(e.kind.startswith("weather") and e.time <= t for e in inst.events):
                extra += ["우산"]
            if inst.familiar and any(e.kind == "transit_delay" and abs(e.d_travel) > BAND and e.time <= t for e in inst.events):
                extra += ["경로/수단(익숙도 해제)"]
            content += extra[:k]

        rows.append((fmt(t), kind + ("" if state_now == "default" else f"/{state_now}"),
                     decision, " | ".join(content) + (f"  [{','.join(modality)}]" if modality else "") +
                     (f"  ({note})" if note else "")))

    # 자동 체크
    fires = [r for r in rows if r[2] == "fire"]
    checks.append(("발사 횟수", len(fires)))
    if any("⚠" in r[3] for r in rows):
        checks.append(("경고", "발사창을 발사 없이 통과"))
    return rows, checks


# ---------------- 샘플 instance 10개 ----------------
M = lambda h, m=0: h * 60 + m
INSTANCES = [
    Instance("I01", "KTX·익숙 | 비(후)+상대지연10+KTX지연20+통화 (공통시나리오 유사)", "KTX", True, events=[
        Event(M(15, 50), "weather_rain", d_travel=5),
        Event(M(16, 5), "cp_delay", d_appt=10, forced=True),
        Event(M(16, 20), "state", state="통화", dur=20),
        Event(M(16, 35), "transit_delay", d_travel=20),
    ]),
    Instance("I02", "지하철·낯섦 | 교통+5(미세)만", "지하철", False, events=[
        Event(M(16, 10), "transit_delay", d_travel=5),
    ]),
    Instance("I03", "근거리도보·익숙 | 비(전, 도보→승격)+회의", "근거리도보", True, events=[
        Event(M(15, 50), "weather_rain", d_travel=10),
        Event(M(16, 20), "state", state="회의", dur=30),
    ]),
    Instance("I04", "KTX·낯섦 | 위험기상(강제+20)", "KTX", False, events=[
        Event(M(15, 45), "weather_severe", d_travel=20, forced=True),
    ]),
    Instance("I05", "지하철·익숙 | 상대 취소(중반)", "지하철", True, events=[
        Event(M(16, 10), "cp_cancel"),
    ]),
    Instance("I06", "지하철·낯섦 | 장소변경(+15)+운전", "지하철", False, events=[
        Event(M(15, 55), "cp_move", d_travel=15, forced=True),
        Event(M(16, 15), "state", state="운전", dur=25),
    ]),
    Instance("I07", "KTX·익숙 | 상대지연60+교통+5", "KTX", True, events=[
        Event(M(15, 55), "cp_delay", d_appt=60, forced=True),
        Event(M(16, 30), "transit_delay", d_travel=5),
    ]),
    Instance("I08", "근거리도보·낯섦 | 비(후)+상대지연10+통화", "근거리도보", False, events=[
        Event(M(16, 5), "cp_delay", d_appt=10, forced=True),
        Event(M(16, 25), "weather_rain", d_travel=10),
        Event(M(16, 40), "state", state="통화", dur=15),
    ]),
    Instance("I09", "no-op | 약속 없음", "지하철", True, has_appt=False),
    Instance("I10", "no-op | 약속 오전 완료", "지하철", True, has_appt=False),
]

if __name__ == "__main__":
    print("# Sanity 합성 출력 — 10 instance × 4 persona\n")
    print(f"초기값: B_early={B_EARLY}, B_late={B_LATE}, prep={PREP}, band=±{BAND}\n")
    print("## 변별력 요약 (instance별 persona 간 서로 다른 GT 시퀀스 수)\n")
    print("| instance | 고유 시퀀스 수/4 | 비고 |")
    print("|---|---|---|")
    for inst in INSTANCES:
        seqs = set()
        for pvec in PERSONAS.values():
            rows, _ = synth(inst, pvec)
            seqs.add(tuple((r[0], r[2], r[3].split("(")[0]) for r in rows))
        n = len(seqs)
        print(f"| {inst.iid} | {n} | {'⚠ 변별 없음' if n == 1 and inst.has_appt else ('no-op 동일 정상' if not inst.has_appt else '')} |")
    print()
    for inst in INSTANCES:
        print(f"## {inst.iid} — {inst.desc}\n")
        for pname, pvec in PERSONAS.items():
            rows, checks = synth(inst, pvec)
            print(f"### {pname} (빈번 {'많' if pvec[0] else '적'}/정도 {'강' if pvec[1] else '약'}/lead {'미리' if pvec[2] else '임박'})\n")
            print("| 시각 | 종류 | 결정 | 내용/메모 |")
            print("|---|---|---|---|")
            for r in rows:
                print(f"| {r[0]} | {r[1]} | {'**fire**' if r[2]=='fire' else 'silent'} | {r[3]} |")
            print("\n" + " / ".join(f"{k}: {v}" for k, v in checks) + "\n")
