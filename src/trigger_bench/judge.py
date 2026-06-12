# B-layer judge — persona 사전 개인화 루브릭 + 기준별 binary 채점 (PrefDisco·ProPerSim 차용, related_work §5)
import json
import re

from core import CHANNELS, PERSONAS, PREP, fmt
from llm import JUDGE_MODEL, chat_json
from gt import synth
from mock import MockMCP

JUDGE_SYS = """모바일 proactive 알림 채점관이다. agent가 보낸 알림 1건을 기준별로 독립 채점한다.
각 기준은 0(위반) 또는 1(충족). JSON만 출력:
{"modality_fit":0|1,"content_fit":0|1,"grounded":0|1,"seq_consistent":0|1,"reason":"한 줄"}"""

JUDGE_TMPL = """[persona 선호 — 채점 기준 개인화]
{rubric}

[상황]
- 시각 {time}, 사용자 상태: {state} (가용 채널: {channels})
- 채널 어휘 매핑: popup→visual, vibrate→vibe, voice→sound. modality 적합성은 이 매핑으로 판정.
- 도구 사실값(이 수치와 다르면 grounded=0): {facts}

[기준]
1. modality_fit — 가용 채널 안에서 persona 풍부도에 맞나. {modality_rule}
2. content_fit — [기대 요소] 목록과 대조해 채점 — 목록에 있는 요소의 포함은 과다가 아니다. 강제 요소(변경공지·갱신·즉시 출발·취소 공지)는 persona 깊이 한도에 세지 않는다. 과소·과다 판정은 기대 요소 목록 대비로만 한다. 기대 요소: {expected_content}
3. grounded — 알림 속 수치(시각·소요시간·지연분)가 도구 사실값·파생값과 일치하나. 도착예정 = 안내된 출발시각 + 이동시간이다 (현재시각 + 이동시간이 아님). 지각 N분 = 현재시각 − 필요 출발시각. 수치 없으면 1.
4. seq_consistent — 직전 알림들과 모순 없나. 변경 알림이면 무엇이 바뀌었는지 드러나나. 이전 알림 없으면 1.

[직전 알림 이력]
{history}

[채점 대상 알림]
modality: {modality}
content: {content}"""


def _rubric(pid):
    f, d, l = PERSONAS[pid]
    return (f"빈번도 {'많음(업데이트도 알림 원함)' if f else '적음(꼭 필요한 것만)'} / "
            f"정도 {'강(풍부한 채널·핵심 2~3요소, 강제 요소 제외)' if d else '약(가용 채널 중 최소 1개·핵심 1요소, 강제 요소 제외)'} / "
            f"lead {'미리(여유 있게)' if l else '임박(직전에)'}")


def _advised_depart(gt_decisions, t):
    """R3 재구성 — t 이전 GT 안내 중 마지막 출발시각(절대 분). 안내 전이면 None.
    '즉시 출발(지각 N분 위험)'은 gt._impact상 필요 출발시각 = 알림시각 − N (fired_plan=depart())."""
    dep = None
    for d in gt_decisions:
        if d.time >= t or d.decision != "fire":
            continue
        for c in d.content:
            if c.startswith("출발 "):
                hh, mm = c.split()[1].split(":")
                dep = int(hh) * 60 + int(mm)
            elif c.startswith("즉시 출발"):
                m = re.search(r"지각 (\d+)분", c)
                dep = d.time - int(m.group(1)) if m else d.time
    return dep


def judge_run(inst, pid, results):
    """fire 결정만 채점. 반환: 기준별 점수 리스트."""
    gt_decisions = synth(inst, pid)
    gt_seq = {d.time: d for d in gt_decisions}
    mcp = MockMCP(inst)
    history, rows = [], []
    for r in results:
        act = r["action"]
        if act.get("decision") != "fire":
            continue
        t = r["time"]
        gtd = gt_seq.get(t)
        state = gtd.state if gtd else "default"
        ch = [k for k, v in CHANNELS[state].items() if v]
        route, weather = mcp.route(t), mcp.weather(t)
        appt_now = inst.appt + sum(e.d_appt for e in inst.events if e.time <= t)
        dep = _advised_depart(gt_decisions, t)
        if dep is None:
            dep_info = "출발 안내 전"
        elif t >= dep:
            dep_info = f"안내된 출발 {fmt(dep)} — 사용자는 안내를 따라 이동 중으로 가정 (도착예정 = {fmt(dep)} + 이동시간)"
        else:
            dep_info = f"안내된 출발 {fmt(dep)} (아직 출발 전)"
        facts = (f"이동 {route['duration_min']}분({route['mode']}), 날씨 {weather['condition']}, "
                 f"약속 {inst.dest} {fmt(appt_now)}, 준비 {PREP}분 "
                 f"(필요 출발 = 약속 − 이동 − 준비), {dep_info}")
        expected = " | ".join(gtd.content) if gtd and gtd.decision == "fire" else "(GT는 silent — content 채점은 참고만)"
        prompt = JUDGE_TMPL.format(
            rubric=_rubric(pid), time=t, state=state, channels=",".join(ch), facts=facts,
            modality_rule="약=가용 채널 중 최소 1개(visual 가용 시 popup, 불가 시 voice), 강=가용 채널 풍부하게",
            expected_content=expected,
            history="\n".join(history) or "(없음)",
            modality=act.get("modality"), content=act.get("content"))
        res = chat_json(JUDGE_MODEL, JUDGE_SYS, prompt)
        rows.append({"time": t, **{k: res.get(k) for k in
                                   ("modality_fit", "content_fit", "grounded", "seq_consistent")},
                     "reason": res.get("reason", "")})
        history.append(f"[{t}] {act.get('modality')} {act.get('content')}")
    return rows


def aggregate_judge(all_rows):
    keys = ("modality_fit", "content_fit", "grounded", "seq_consistent")
    flat = [r for rows in all_rows for r in rows if all(r.get(k) in (0, 1) for k in keys)]
    n = len(flat)
    return {k: round(sum(r[k] for r in flat) / n, 3) if n else None for k in keys} | {"judged_fires": n}
