# GT 합성기 — gt_design_v1.1 규칙(수식·override·R1~R6)을 결정론적으로 실행
from dataclasses import dataclass, field

from core import BAND, GRID, PREP, CHANNELS, PERSONAS, TRANSPORT, fmt, buffer_of


@dataclass
class Decision:
    time: int
    kind: str              # grid / event / grid+event
    decision: str          # fire / silent
    content: list = field(default_factory=list)
    modality: list = field(default_factory=list)
    note: str = ""
    forced: bool = False   # 1층 강제/승격 fire 여부 (critical miss 채점용)
    state: str = "default"


def build_triggers(inst):
    """grid + 이벤트 즉시 trigger. R4: 창은 최종 T_appt까지."""
    final_appt = inst.appt + sum(e.d_appt for e in inst.events)
    win_start = inst.appt - 90
    grids = list(range(win_start, final_appt + 1, GRID))
    times = sorted(set(grids + [e.time for e in inst.events]))
    return times, set(grids)


def window_start(inst, pid):
    """미리 persona가 KTX 등에서 창 90분 초과 시 그리드 단위 확장."""
    travel0 = TRANSPORT[inst.transport][0]
    need = travel0 + buffer_of(pid) + PREP + BAND
    win = 90 if need <= 90 else int(-(-need // GRID)) * GRID
    return inst.appt - win


def synth(inst, pid):
    """instance × persona -> GT Decision 시퀀스 (결정론)."""
    freq_high, depth_high, _ = PERSONAS[pid]
    buffer = buffer_of(pid)

    times, grid_set = build_triggers(inst)
    # persona별 창 확장분의 추가 그리드
    ws = window_start(inst, pid)
    if inst.has_appt and ws < min(times):
        extra = list(range(ws, min(times), GRID))
        times = sorted(set(extra + times))
        grid_set |= set(extra)

    if not inst.has_appt:
        return [Decision(t, "grid", "silent", note=f"no-op({inst.noop_kind})") for t in sorted(grid_set)]

    appt, travel = inst.appt, TRANSPORT[inst.transport][0]
    cancelled, fired_plan = False, None
    state_now, state_until = "default", -1
    ev_by_time = {e.time: e for e in inst.events}
    out = []

    ft = lambda: appt - travel - PREP - buffer
    depart = lambda: appt - travel - PREP

    for t in times:
        ev = ev_by_time.get(t)
        kind = ("grid+event" if t in grid_set else "event") if ev else "grid"
        d = Decision(t, kind, "silent")

        if ev and ev.kind == "state":
            state_now, state_until = ev.state, t + ev.dur
            d.note = f"state→{ev.state}"
        if state_until >= 0 and t > state_until:
            state_now = "default"
        d.state = state_now

        moving = fired_plan is not None and t >= fired_plan  # R3

        if ev and ev.kind != "state":
            old_ft = ft()
            appt += ev.d_appt
            travel += ev.d_travel
            if ev.kind == "cp_cancel":
                cancelled = True
                d.decision, d.content, d.forced = "fire", ["취소 공지"], True
                d.note = "override1"
            elif cancelled:
                d.note = "취소 후 무효"
            elif ev.forced:
                d.decision, d.forced = "fire", True
                d.content = [f"{ev.kind} 변경공지", _impact(moving, fired_plan, travel, appt, depart, t)]
                d.note = "override3"
                if not moving:
                    fired_plan = depart()
            elif fired_plan is None:
                if t >= ft() - BAND:  # R1
                    d.decision = "fire"
                    d.content = ["약속명/시각", _impact(False, None, travel, appt, depart, t)]
                    d.note = "첫 알림(이벤트 trigger)"
                    fired_plan = depart()
                else:
                    d.note = "이르다(첫 알림 전)"
            else:
                delta = abs(ft() - old_ft)
                if delta > BAND:
                    d.decision, d.forced = "fire", True
                    d.content = [f"{ev.kind} 갱신", _impact(moving, fired_plan, travel, appt, depart, t)]
                    d.note = f"승격(Δ{delta:.0f})"
                    if not moving:
                        fired_plan = depart()
                elif moving:
                    d.note = f"미세+이동중"
                elif freq_high:
                    d.decision = "fire"
                    d.content = [f"{ev.kind} 업데이트", f"출발 {fmt(depart())}"]
                    d.note = "미세—빈번도 많"
                    fired_plan = depart()
                else:
                    d.note = "미세—빈번도 적"
        elif not cancelled:
            f = ft()
            if moving:
                d.note = "이동중(override2)"
            elif fired_plan is not None and fired_plan == depart():
                d.note = "동일 plan 안내됨"
            elif fired_plan is None and t >= f - BAND:  # R2
                d.decision = "fire"
                d.content = ["약속명/시각", _impact(False, None, travel, appt, depart, t)]
                d.note = f"발사창 {fmt(f)}±{BAND}"
                fired_plan = depart()
            else:
                d.note = "이르다"

        if d.decision == "fire":
            d.modality = _modality(state_now, depth_high)
            d.content += _content_extra(inst, t, depth_high)
        out.append(d)
    return out


def _impact(moving, fired_plan, travel, appt, depart, now):
    if moving:
        return f"도착예정 {fmt(fired_plan + travel)} vs 약속 {fmt(appt)}"
    dp = depart()
    if dp < now:  # R6
        return f"즉시 출발(지각 {now - dp:.0f}분 위험)"
    return f"출발 {fmt(dp)}"


def _modality(state, depth_high):
    ch = CHANNELS[state]
    if depth_high:
        return [m for m, ok in [("popup", ch["visual"]), ("vibrate", ch["vibe"]), ("voice", ch["sound"])] if ok]
    return ["popup"] if ch["visual"] else ["voice"]


def _content_extra(inst, t, depth_high):
    k = 3 if depth_high else 1
    extra = []
    if not inst.familiar:
        extra += ["경로/수단", "출구"]
    if any(e.kind.startswith("weather") and e.time <= t for e in inst.events):
        extra += ["우산"]
    if inst.familiar and any(e.kind == "transit_delay" and abs(e.d_travel) > BAND and e.time <= t for e in inst.events):
        extra += ["경로/수단(익숙도 해제)"]
    return extra[:k]
