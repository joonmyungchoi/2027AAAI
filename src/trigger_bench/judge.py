# B-layer judge — persona 사전 개인화 루브릭 + 기준별 binary 채점 (PrefDisco·ProPerSim 차용, related_work §5)
import json

from core import CHANNELS, PERSONAS
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
- 도구 사실값(이 수치와 다르면 grounded=0): {facts}

[기준]
1. modality_fit — 가용 채널 안에서 persona 풍부도에 맞나. {modality_rule}
2. content_fit — persona 깊이에 맞는 요소 수·우선순위인가 (과소·과다 모두 0). 기대 요소: {expected_content}
3. grounded — 알림 속 수치(시각·소요시간·지연분)가 도구 사실값과 일치하나. 수치 없으면 1.
4. seq_consistent — 직전 알림들과 모순 없나. 변경 알림이면 무엇이 바뀌었는지 드러나나. 이전 알림 없으면 1.

[직전 알림 이력]
{history}

[채점 대상 알림]
modality: {modality}
content: {content}"""


def _rubric(pid):
    f, d, l = PERSONAS[pid]
    return (f"빈번도 {'많음(업데이트도 알림 원함)' if f else '적음(꼭 필요한 것만)'} / "
            f"정도 {'강(풍부한 채널·내용 2~3요소)' if d else '약(popup만·핵심 1요소)'} / "
            f"lead {'미리(여유 있게)' if l else '임박(직전에)'}")


def judge_run(inst, pid, results):
    """fire 결정만 채점. 반환: 기준별 점수 리스트."""
    gt_seq = {d.time: d for d in synth(inst, pid)}
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
        facts = f"이동 {route['duration_min']}분({route['mode']}), 날씨 {weather['condition']}, 약속 {inst.dest}"
        expected = " | ".join(gtd.content) if gtd and gtd.decision == "fire" else "(GT는 silent — content 채점은 참고만)"
        prompt = JUDGE_TMPL.format(
            rubric=_rubric(pid), time=t, state=state, channels=",".join(ch), facts=facts,
            modality_rule="약=최소(popup), 강=가용 채널 풍부하게", expected_content=expected,
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
