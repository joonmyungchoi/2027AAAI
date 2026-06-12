# A-layer 채점기 — decision F1(전체 pool), band, critical miss, 중복 알림, no-op restraint
from gt import synth


def score_run(inst, pid, results):
    """1 persona-run 채점. results = env.run_episode 출력."""
    gt_seq = {d.time: d for d in synth(inst, pid)}
    tp = fp = fn = tn = 0
    crit_total = crit_miss = dup = 0
    fired_contents = []

    for r in results:
        t, act = r["time"], r["action"]
        gtd = gt_seq.get(t)
        if gtd is None:
            continue
        a_fire = act.get("decision") == "fire"
        g_fire = gtd.decision == "fire"
        tp += a_fire and g_fire
        fp += a_fire and not g_fire
        fn += (not a_fire) and g_fire
        tn += (not a_fire) and (not g_fire)
        if g_fire and gtd.forced:
            crit_total += 1
            crit_miss += not a_fire
        if a_fire:
            c = tuple(act.get("content", []))
            if c and c in fired_contents:
                dup += 1
            fired_contents.append(c)

    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "crit_total": crit_total, "crit_miss": crit_miss, "dup": dup,
            "noop_violation": (fp if not inst.has_appt else 0),
            "noop_total": (tp + fp + fn + tn if not inst.has_appt else 0)}


def aggregate(rows):
    """전체 pool 집계 — F1(fire=positive), critical miss rate, restraint."""
    s = {k: sum(r[k] for r in rows) for k in rows[0]}
    prec = s["tp"] / (s["tp"] + s["fp"]) if s["tp"] + s["fp"] else 0.0
    rec = s["tp"] / (s["tp"] + s["fn"]) if s["tp"] + s["fn"] else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {
        "precision": round(prec, 3), "recall": round(rec, 3), "f1": round(f1, 3),
        "critical_miss_rate": round(s["crit_miss"] / s["crit_total"], 3) if s["crit_total"] else None,
        "duplicates": s["dup"], "noop_violations": s["noop_violation"],
        # FTR(False Trigger Rate): GT가 전부 silent인 no-op instance에서의 오발사율 (ProactiveMobile 차용)
        "ftr": round(s["noop_violation"] / s["noop_total"], 3) if s.get("noop_total") else None,
        "decisions": s["tp"] + s["fp"] + s["fn"] + s["tn"],
    }
