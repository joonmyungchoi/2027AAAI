# text-state 트리거 루프 — 매 trigger마다 관찰(로그+시각+state+이벤트+자기 알림 이력)을 만들어 agent 호출
from core import fmt
from gt import build_triggers, window_start
from mock import MockMCP

EVENT_TEXT = {
    "weather_rain": "날씨 알림: 비가 내리기 시작했습니다",
    "weather_severe": "기상특보: 호우경보 발효",
    "cp_delay": "상대 메시지: \"늦을 것 같아요\"",
    "cp_cancel": "상대 메시지: \"오늘 약속 취소해야 할 것 같아요\"",
    "cp_move": "상대 메시지: \"장소를 바꿔야 할 것 같아요\"",
    "transit_delay": "교통 알림: 운행 지연 발생",
}


def run_episode(inst, pid, log_text, agent):
    """1 persona-run. agent.decide(obs) -> dict(decision, modality?, content?, rationale?)"""
    times, grid_set = build_triggers(inst)
    ws = window_start(inst, pid)
    if inst.has_appt and ws < min(times):
        times = sorted(set(list(range(ws, min(times), 15)) + times))
    mcp = MockMCP(inst)
    ev_by_time = {e.time: e for e in inst.events}
    state_now, state_until = "default", -1
    seen_events, my_notifs, results = [], [], []

    for t in times:
        ev = ev_by_time.get(t)
        if ev and ev.kind == "state":
            state_now, state_until = ev.state, t + ev.dur
        if state_until >= 0 and t > state_until:
            state_now = "default"
        new_event = EVENT_TEXT.get(ev.kind) if ev else None
        if new_event:
            extra = f" (+{ev.d_appt}분)" if ev.d_appt else ""
            seen_events.append(f"[{fmt(t)}] {new_event}{extra}")

        cal = f"{fmt(inst.appt)} 약속 @{inst.dest}" if inst.has_appt else "(오늘 약속 없음)"
        if inst.has_appt and ev and ev.kind == "cp_delay":
            cal += f" → 상대 {ev.d_appt}분 지연 통보됨"

        obs = {
            "time": t, "time_str": fmt(t), "state": state_now,
            "calendar": cal,
            "new_event": (f"{new_event} (+{ev.d_appt}분)" if ev and ev.d_appt else new_event) if new_event else None,
            "events_so_far": list(seen_events),
            "mcp": mcp.snapshot(t),
            "my_notifications": list(my_notifs),
            "user_log": log_text,
        }
        act = agent.decide(obs)
        results.append({"time": t, "action": act})
        if act.get("decision") == "fire":
            my_notifs.append(f"[{fmt(t)}] {','.join(act.get('modality', []))}: "
                             f"{' | '.join(act.get('content', [])) if isinstance(act.get('content'), list) else act.get('content', '')}")
    return results


def render_obs(obs):
    """LLM agent용 텍스트 관찰 (규칙 agent는 dict 직접 사용)."""
    lines = [
        f"## 현재 시각: {obs['time_str']} / 사용자 상태: {obs['state']}",
        f"## 캘린더: {obs['calendar']}",
        f"## 방금 도착한 이벤트: {obs['new_event'] or '(없음)'}",
        "## 지금까지의 이벤트:\n" + ("\n".join(obs["events_so_far"]) or "(없음)"),
        "## 도구 조회 결과:\n" + obs["mcp"],
        "## 내가 보낸 알림 이력:\n" + ("\n".join(obs["my_notifications"]) or "(없음)"),
        "## 사용자 행동 로그(최근 4주):\n" + obs["user_log"],
    ]
    return "\n\n".join(lines)
