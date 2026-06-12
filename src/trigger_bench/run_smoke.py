# end-to-end 스모크 테스트 — 생성(100)→로그→env→채점, oracle≈만점/silent·allfire 저점 검증
import json
import sys

from agents import AllFireAgent, AllSilentAgent, OracleRuleAgent, RandomAgent
from env import run_episode
from logs import generate, linearize
from matrix import sample
from score import aggregate, score_run


def main():
    insts, cov = sample(n_core=90, n_noop=10, seed=42)
    print(f"instances: {len(insts)} (core {sum(i.has_appt for i in insts)}, "
          f"noop {sum(not i.has_appt for i in insts)})")
    print(f"pairwise coverage(≥2): {cov['pairs_covered']}/{cov['pairs_total']} = {cov['coverage']:.1%}")

    logs = {pid: linearize(generate(pid)[0][-40:]) for pid in ["P_A", "P_B", "P_C", "P_D"]}

    agents = {
        "oracle": lambda inst, pid: OracleRuleAgent(inst, pid),
        "all_silent": lambda inst, pid: AllSilentAgent(),
        "all_fire": lambda inst, pid: AllFireAgent(),
        "random": lambda inst, pid: RandomAgent(seed=1),
    }
    print(f"\n{'agent':<12} {'F1':>6} {'prec':>6} {'rec':>6} {'critMiss':>9} {'dup':>5} {'noopViol':>9} {'decisions':>10}")
    ok = True
    for name, mk in agents.items():
        rows = []
        for inst in insts:
            for pid in ["P_A", "P_B", "P_C", "P_D"]:
                results = run_episode(inst, pid, logs[pid], mk(inst, pid))
                rows.append(score_run(inst, pid, results))
        m = aggregate(rows)
        print(f"{name:<12} {m['f1']:>6} {m['precision']:>6} {m['recall']:>6} "
              f"{str(m['critical_miss_rate']):>9} {m['duplicates']:>5} {m['noop_violations']:>9} {m['decisions']:>10}")
        if name == "oracle" and m["f1"] < 0.999:
            ok = False
            print("  ⚠ oracle이 만점이 아님 — env/GT/채점기 불일치!")
        if name == "all_silent" and m["f1"] > 0.01:
            ok = False

    print("\nSMOKE", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
