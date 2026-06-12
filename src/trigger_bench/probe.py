# oracle probe — 로그만 보고 persona 축(빈번도/정도/lead) 복원률 측정 (design_review P0-2, personas_v1 §3)
import json

from core import PERSONAS
from llm import AGENT_MODEL, PROBE_WEAK_MODEL, chat_json

PROBE_SYS = """사용자 모바일 행동 로그를 보고 알림 선호 3축을 분류하라.
- frequency: "low"(업데이트성 알림은 빨리 dismiss, DnD 사용) | "high"(업데이트도 열람, 알림센터 자주 확인)
- depth: "weak"(무음/popup 선호, 조회 얕음) | "strong"(진동·소리 모드, 경로·날씨 깊게 조회)
- lead: "early"(약속 40~60분 전 도착, 아침에 캘린더 확인) | "late"(직전 도착, 출발 직전 검색)
JSON만 출력: {"frequency":"low|high","depth":"weak|strong","lead":"early|late","evidence":{"frequency":"...","depth":"...","lead":"..."}}"""


def probe(log_text, model):
    return chat_json(model, PROBE_SYS, log_text)


def run_probe(log_dir, models=(AGENT_MODEL, PROBE_WEAK_MODEL), tags=("clean", "noise")):
    results = {}
    for model in models:
        per_axis = {"frequency": 0, "depth": 0, "lead": 0}
        total = 0
        detail = {}
        for pid, (freq_high, depth_high, lead_early) in PERSONAS.items():
            truth = {"frequency": "high" if freq_high else "low",
                     "depth": "strong" if depth_high else "weak",
                     "lead": "early" if lead_early else "late"}
            for tag in tags:
                pred = probe(open(f"{log_dir}/{pid}_{tag}.txt").read(), model)
                total += 1
                hit = {ax: pred.get(ax) == truth[ax] for ax in per_axis}
                for ax, ok in hit.items():
                    per_axis[ax] += ok
                detail[f"{pid}_{tag}"] = {"pred": {k: pred.get(k) for k in per_axis}, "hit": hit}
        results[model] = {"axis_accuracy": {ax: round(c / total, 3) for ax, c in per_axis.items()},
                          "detail": detail}
    return results
