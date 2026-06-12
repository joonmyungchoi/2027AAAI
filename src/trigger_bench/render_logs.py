# 하이브리드 로그 2·3단계 — LLM 표면 렌더링 + 신호 보존 validator (personas_v1 §2 확정)
import json
from collections import Counter

from llm import RENDER_MODEL, chat_json
from logs import generate, linearize

RENDER_SYS = """모바일 행동 로그 다양화 도구다. 입력은 정형 로그 entry 배열(JSON).
각 entry의 time/event_type/label/category는 절대 바꾸지 말 것.
바꿀 수 있는 것: app 이름(같은 기능군 내 실제 앱명으로), location(같은 의미 유지, 표현 다양화), params(의미 유지, 값 표현 다양화).
noise entry(label=noise)는 event_type도 일상적인 다른 것으로 바꿔도 됨(단 알림/경로/날씨 관련 금지).
출력: {"entries": [...]} — 입력과 같은 길이, 같은 순서."""


def _validate(orig, rendered):
    """신호 보존 검증 — 위반 entry는 원본으로 롤백, 위반 목록 반환."""
    fixed, violations = [], []
    if len(rendered) != len(orig):
        return orig, ["length_mismatch"]
    for o, r in zip(orig, rendered):
        bad = []
        for f in ("time", "label", "category"):
            if r.get(f) != o[f]:
                bad.append(f)
        if o["label"] == "signal" and r.get("event_type") != o["event_type"]:
            bad.append("event_type")
        if not all(k in r for k in ("time", "app", "location", "event_type", "params")):
            bad.append("schema")
        if bad:
            violations.append({"time": o["time"], "fields": bad})
            fixed.append(o)
        else:
            fixed.append(r)
    return fixed, violations


def render(pid, entries, batch=40):
    """entry 배치 렌더링 + validator. 반환: (렌더된 entries, 위반 수)."""
    out, nviol = [], 0
    for i in range(0, len(entries), batch):
        chunk = entries[i:i + batch]
        resp = chat_json(RENDER_MODEL, RENDER_SYS, json.dumps({"entries": chunk}, ensure_ascii=False))
        rendered = resp.get("entries", [])
        fixed, viol = _validate(chunk, rendered)
        out += fixed
        nviol += len(viol)
    return out, nviol


def build_all(out_dir, pids=("P_A", "P_B", "P_C", "P_D"), use_llm=True):
    """4 persona × clean/noise 로그 생성(+렌더링) 저장."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    summary = {}
    for pid in pids:
        clean, noisy = generate(pid)
        for tag, entries in (("clean", clean), ("noise", noisy)):
            if use_llm:
                entries, nviol = render(pid, entries)
            else:
                nviol = -1
            with open(f"{out_dir}/{pid}_{tag}.json", "w") as f:
                json.dump(entries, f, ensure_ascii=False, indent=1)
            with open(f"{out_dir}/{pid}_{tag}.txt", "w") as f:
                f.write(linearize(entries))
            sig = Counter(e["category"] for e in entries if e["label"] == "signal")
            summary[f"{pid}_{tag}"] = {"entries": len(entries), "violations_rolled_back": nviol,
                                       "signal_by_axis": dict(sig)}
    return summary
