# 파일럿 러너 — 20 instance × 4 persona: 로그 렌더링→probe→LLM agent 평가→A/B 채점→보고서
"""
로컬 실행 (repo 루트에서):
  cd src/trigger_bench
  pip install openai
  python3 run_pilot.py                # 전체 파이프라인
  python3 run_pilot.py --no-render    # 로그 LLM 렌더링 생략 (skeleton 그대로)
  python3 run_pilot.py --dry          # API 없이 구조 점검 (oracle agent 대체)
출력: data/pilot/ (로그·instance·원시결과) + ../../design/pilot_results_v1.md
"""
import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

from core import PERSONAS, fmt
from env import run_episode
from gt import synth
from matrix import sample
from score import aggregate, score_run

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "pilot")
REPORT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "design", "pilot_results_v1.md")
PIDS = list(PERSONAS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--n-core", type=int, default=16)
    ap.add_argument("--n-noop", type=int, default=4)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--judge-only", action="store_true",
                    help="저장된 raw_results.json으로 5단계(judge)부터 재개")
    args = ap.parse_args()
    os.makedirs(f"{DATA}/logs", exist_ok=True)

    if args.judge_only:
        return _judge_only()

    # 1) instance + GT
    insts, cov = sample(n_core=args.n_core, n_noop=args.n_noop, seed=42)
    json.dump([i.to_dict() for i in insts], open(f"{DATA}/instances.json", "w"), ensure_ascii=False, indent=1)
    gt_dump = {i.iid: {pid: [vars(d) for d in synth(i, pid)] for pid in PIDS} for i in insts}
    json.dump(gt_dump, open(f"{DATA}/gt.json", "w"), ensure_ascii=False, indent=1, default=str)
    print(f"[1/5] instances {len(insts)} (pairwise {cov['coverage']:.0%}) → {DATA}/")

    # 2) 로그 (하이브리드)
    from render_logs import build_all
    log_summary = build_all(f"{DATA}/logs", use_llm=not (args.no_render or args.dry))
    json.dump(log_summary, open(f"{DATA}/log_summary.json", "w"), ensure_ascii=False, indent=1)
    print(f"[2/5] logs: {len(log_summary)}벌, 렌더링 {'생략' if args.no_render or args.dry else '완료'}")

    # 3) oracle probe
    probe_res = {}
    if not args.dry:
        from probe import run_probe
        probe_res = run_probe(f"{DATA}/logs")
        json.dump(probe_res, open(f"{DATA}/probe.json", "w"), ensure_ascii=False, indent=1)
        for m, r in probe_res.items():
            print(f"[3/5] probe {m}: {r['axis_accuracy']}")
    else:
        print("[3/5] probe 생략 (dry)")

    # 4) agent 평가 (기본 조건: noise 로그)
    if args.dry:
        from agents import OracleRuleAgent
        mk = lambda inst, pid: OracleRuleAgent(inst, pid)
        model_name = "oracle(dry)"
    else:
        from agents import LLMAgent
        from llm import AGENT_MODEL
        mk = lambda inst, pid: LLMAgent()
        model_name = AGENT_MODEL
    logs = {pid: open(f"{DATA}/logs/{pid}_noise.txt").read() for pid in PIDS}

    jobs = [(inst, pid) for inst in insts for pid in PIDS]

    def _run(job):
        inst, pid = job
        res = run_episode(inst, pid, logs[pid], mk(inst, pid))
        return inst.iid, pid, res

    raw = {}
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for iid, pid, res in ex.map(_run, jobs):
            raw[f"{iid}/{pid}"] = res
            sys.stdout.write(f"\r[4/5] runs {len(raw)}/{len(jobs)}")
    print()
    json.dump(raw, open(f"{DATA}/raw_results.json", "w"), ensure_ascii=False, indent=1, default=str)
    # raw 출처 기록 — judge-only 재실행 시 보고서 오라벨 방지 (pilot_analysis_v1 §4)
    json.dump({"agent_model": model_name}, open(f"{DATA}/run_meta.json", "w"), ensure_ascii=False)

    # 5) 채점 A + B
    inst_by_id = {i.iid: i for i in insts}
    rows = [score_run(inst_by_id[k.split("/")[0]], k.split("/")[1], v) for k, v in raw.items()]
    a_metrics = aggregate(rows)
    print(f"[5/5] A-layer: {a_metrics}")

    b_metrics, judge_rows = {}, []
    if not args.dry:
        from judge import aggregate_judge, judge_run
        for k, v in raw.items():
            iid, pid = k.split("/")
            judge_rows.append(judge_run(inst_by_id[iid], pid, v))
        b_metrics = aggregate_judge(judge_rows)
        json.dump([r for rows_ in judge_rows for r in rows_],
                  open(f"{DATA}/judge.json", "w"), ensure_ascii=False, indent=1)
        print(f"      B-layer: {b_metrics}")

    _write_report(model_name, len(insts), cov, log_summary, probe_res, a_metrics, b_metrics)
    print(f"보고서: {os.path.normpath(REPORT)}")


def _judge_only():
    """1~4단계 산출물(data/pilot/)을 로드해 judge+보고서만 재실행."""
    from core import Instance
    from judge import aggregate_judge, judge_run
    meta_path = f"{DATA}/run_meta.json"
    agent_label = (json.load(open(meta_path))["agent_model"] if os.path.exists(meta_path)
                   else "출처미상(run_meta.json 없음 — 구버전 raw)")
    insts = [Instance.from_dict(d) for d in json.load(open(f"{DATA}/instances.json"))]
    inst_by_id = {i.iid: i for i in insts}
    raw = json.load(open(f"{DATA}/raw_results.json"))
    probe_res = json.load(open(f"{DATA}/probe.json")) if os.path.exists(f"{DATA}/probe.json") else {}
    log_summary = json.load(open(f"{DATA}/log_summary.json"))

    rows = [score_run(inst_by_id[k.split("/")[0]], k.split("/")[1], v) for k, v in raw.items()]
    a_metrics = aggregate(rows)

    # run 단위 병렬 judge + 부분 저장(judge_partial.json)으로 중단 시 재개 가능
    import threading
    part_path = f"{DATA}/judge_partial.json"
    done = json.load(open(part_path)) if os.path.exists(part_path) else {}
    if done:
        print(f"[judge] 부분 결과 {len(done)}/{len(raw)}건 재사용")
    lock = threading.Lock()

    def _j(k):
        iid, pid = k.split("/")
        res = judge_run(inst_by_id[iid], pid, raw[k])
        with lock:
            done[k] = res
            json.dump(done, open(part_path, "w"), ensure_ascii=False)
            print(f"[judge] {len(done)}/{len(raw)}", flush=True)

    with ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(_j, [k for k in raw if k not in done]))
    judge_rows = [done[k] for k in raw]
    b_metrics = aggregate_judge(judge_rows)
    json.dump([r for rows_ in judge_rows for r in rows_],
              open(f"{DATA}/judge.json", "w"), ensure_ascii=False, indent=1)
    os.remove(part_path)  # 완료 후 부분 캐시 제거 — 다음 실행이 stale 결과를 재사용하지 않게
    print(f"A-layer: {a_metrics}\nB-layer: {b_metrics}")
    cov = {"coverage": -1}
    _write_report(agent_label, len(insts), cov, log_summary, probe_res, a_metrics, b_metrics)
    print(f"보고서: {os.path.normpath(REPORT)}")


def _write_report(model, n, cov, logs, probe_res, a, b):
    L = [f"# 파일럿 결과 v1 — {model}, {n} instance × 4 persona\n",
         f"- pairwise coverage: " + (f"{cov['coverage']:.0%}" if cov.get("coverage", -1) >= 0 else "(judge-only 재실행)"),
         f"- 로그: {len(logs)}벌 " + (f"(렌더링 롤백 평균 {sum(v['violations_rolled_back'] for v in logs.values())}건)"
                                    if next(iter(logs.values()))['violations_rolled_back'] >= 0 else "(렌더링 생략)"),
         "\n## Oracle probe (로그→persona 축 복원률)\n"]
    for m, r in probe_res.items():
        L.append(f"- {m}: {r['axis_accuracy']}")
    L.append("\n## A-layer (rule)\n")
    L += [f"- {k}: {v}" for k, v in a.items()]
    if b:
        L.append("\n## B-layer (judge, fire별 binary 기준)\n")
        L += [f"- {k}: {v}" for k, v in b.items()]
    L.append("\n## 해석 가이드\n- oracle 규칙 agent는 F1 1.0이 정상 (스모크로 검증됨)."
             "\n- FTR = no-op instance 오발사율. critical_miss = 1층 강제 누락."
             "\n- probe: 강 모델 ≥90%가 로그 합격선 (personas_v1 §3).")
    with open(REPORT, "w") as f:
        f.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
