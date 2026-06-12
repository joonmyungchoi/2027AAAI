# trigger_bench

Proactive 알림 WHEN·HOW 벤치마크 (KnowU-Bench와 독립). 설계: `design/gt_design_v1.md`, `design/template_matrix_v1.md`, `design/personas_v1.md`.

## 원격 서버 실행 (conda)

```bash
# repo 받기 + 키 설정
git clone <repo> && cd 2027AAAI
echo "OPENAI_API_KEY=sk-..." > .env        # 루트에. .gitignore가 커버함

# 환경 세팅 (env 이름 인자 생략 시 trigger_bench)
bash src/trigger_bench/setup_env.sh

# 파일럿 실행 (20 instance × 4 persona, gpt-5.5 agent + gpt-5.5-pro judge)
conda activate trigger_bench
cd src/trigger_bench
python run_pilot.py
```

옵션: `--dry`(API 없이 구조 점검) / `--no-render`(로그 LLM 렌더링 생략) / `--n-core N --n-noop M`(규모) / `--workers K`(동시 실행 수).

모델 변경은 환경변수: `TB_AGENT_MODEL`, `TB_JUDGE_MODEL`, `TB_RENDER_MODEL`, `TB_PROBE_WEAK`.

## 출력

- `data/pilot/` — instances.json, gt.json, logs/(8벌), raw_results.json, probe.json, judge.json
- `design/pilot_results_v1.md` — 요약 보고서 (probe 복원률, A-layer F1·FTR·critical miss, B-layer binary 4종)

## 파이프라인 (run_pilot.py)

instance 샘플링(matrix) → GT 합성(gt) → 로그 skeleton(logs)+LLM 렌더링(render_logs)+validator → oracle probe(probe) → agent 평가(env+agents) → A 채점(score) + B judge(judge) → 보고서.

API 키 없이 전체 무결성 검증: `python run_smoke.py` (oracle F1=1.0이어야 정상).
