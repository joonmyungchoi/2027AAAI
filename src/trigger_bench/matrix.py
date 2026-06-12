# 변인 행렬 샘플러 — Core 90(pairwise ≥2) + no-op 10, 시드 고정 (설계: template_matrix_v1 §2~3, sanity_findings §4)
import random

from core import GRID, PREP, TRANSPORT, APPT_DEFAULT, Event, Instance
from gt import synth, build_triggers

LEVELS = {
    "S1": [True, False],                                    # 익숙 / 낯섦
    "S2": list(TRANSPORT.keys()),
    "E1": ["none", "rain_pre", "rain_post", "severe"],
    "E2": ["none", "delay10", "delay60", "cancel", "move"],
    "E3": ["none", "plus5", "plus20"],
    "E4": ["none", "통화", "회의", "운전"],
}
VARS = list(LEVELS.keys())


def _rain_delta(transport):
    return 10 if TRANSPORT[transport][1] >= 15 else 5


def _build_instance(iid, cfg, rng):
    s1, s2 = cfg["S1"], cfg["S2"]
    # E2=취소면 E1/E3 무효화 (template_matrix 제약)
    if cfg["E2"] == "cancel":
        cfg = {**cfg, "E1": "none", "E3": "none"}
    appt = APPT_DEFAULT
    travel0 = TRANSPORT[s2][0]
    depart0 = appt - travel0 - PREP
    jitter = lambda base: base + rng.choice([-15, -10, -5, 0, 5, 10, 15])
    events = []

    # 미세 이벤트 ≥1개는 출발 전 배치 (sanity_findings §4-2)
    pre_depart = lambda base: min(jitter(base), depart0 - 5)

    if cfg["E1"] == "rain_pre":
        events.append(Event(pre_depart(depart0 - 30), "weather_rain", d_travel=_rain_delta(s2)))
    elif cfg["E1"] == "rain_post":
        events.append(Event(jitter(depart0 + 20), "weather_rain", d_travel=_rain_delta(s2)))
    elif cfg["E1"] == "severe":
        events.append(Event(jitter(depart0 - 15), "weather_severe", d_travel=20, forced=True))

    if cfg["E2"] == "delay10":
        events.append(Event(jitter(appt - 55), "cp_delay", d_appt=10, forced=True))
    elif cfg["E2"] == "delay60":
        events.append(Event(jitter(appt - 65), "cp_delay", d_appt=60, forced=True))
    elif cfg["E2"] == "cancel":
        events.append(Event(jitter(appt - 50), "cp_cancel"))
    elif cfg["E2"] == "move":
        events.append(Event(jitter(appt - 60), "cp_move", d_travel=15, forced=True))

    if cfg["E3"] == "plus5":
        events.append(Event(pre_depart(depart0 - 10), "transit_delay", d_travel=5))
    elif cfg["E3"] == "plus20":
        events.append(Event(jitter(depart0 + 10), "transit_delay", d_travel=20))

    if cfg["E4"] != "none":
        # 강제/승격 이벤트 있으면 그 시각을 덮게, 없으면 발사창 부근 (sanity_findings §4-1)
        anchor = next((e.time for e in events if e.forced or abs(e.d_travel) > 7.5), None)
        if anchor is None:
            anchor = depart0 - rng.choice([10, 30])  # 임박/미리 창 중 택일
        events.append(Event(anchor - 5, "state", state=cfg["E4"], dur=25))

    # 시각 충돌·정렬 정리 (5분 스냅, 중복 시 +5)
    used = set()
    for e in sorted(events, key=lambda e: e.time):
        e.time = max(appt - 90 + 5, int(round(e.time / 5) * 5))
        while e.time in used:
            e.time += 5
        used.add(e.time)
    events.sort(key=lambda e: e.time)
    return Instance(iid, s2, s1, appt=appt, events=events)


def _pairs(cfg):
    return {(a, str(cfg[a]), b, str(cfg[b])) for i, a in enumerate(VARS) for b in VARS[i + 1:]}


def _valid(inst):
    """GT 모호성 가드: 4 persona 모두 합성 가능 + band 경계 ±2.5 침범 없음."""
    try:
        for pid in ["P_A", "P_B", "P_C", "P_D"]:
            for d in synth(inst, pid):
                pass
        return True
    except Exception:
        return False


def sample(n_core=90, n_noop=10, seed=42, min_pair=2):
    rng = random.Random(seed)
    insts, cover = [], {}
    tries = 0
    while len(insts) < n_core and tries < n_core * 100:
        tries += 1
        cfg = {v: rng.choice(LEVELS[v]) for v in VARS}
        # 미달 쌍 우선 보강 (greedy)
        if len(insts) > n_core // 3:
            lacking = [p for p, c in cover.items() if c < min_pair]
            if lacking:
                p = rng.choice(lacking)
                cfg[p[0]] = eval(p[1]) if p[1] in ("True", "False") else p[1]
                cfg[p[2]] = eval(p[3]) if p[3] in ("True", "False") else p[3]
        inst = _build_instance(f"C{len(insts) + 1:03d}", cfg, rng)
        if not _valid(inst):
            continue
        insts.append(inst)
        for p in _pairs(cfg):
            cover[p] = cover.get(p, 0) + 1

    noops = [Instance(f"N{i + 1:03d}", rng.choice(LEVELS["S2"]), True, has_appt=False,
                      noop_kind=rng.choice(["약속없음", "오전완료", "내일약속"]))
             for i in range(n_noop)]

    # 커버리지 리포트
    all_pairs = set()
    for i, a in enumerate(VARS):
        for b in VARS[i + 1:]:
            for la in LEVELS[a]:
                for lb in LEVELS[b]:
                    all_pairs.add((a, str(la), b, str(lb)))
    covered = sum(1 for p in all_pairs if cover.get(p, 0) >= min_pair)
    report = {"pairs_total": len(all_pairs), "pairs_covered": covered,
              "coverage": round(covered / len(all_pairs), 3)}
    return insts + noops, report
