# trigger_bench 구현 체크리스트

> 원칙: knowu_bench와 완전 분리 (import 0). 설계 출처: design/gt_design_v1.md(v1.1), template_matrix_v1.md, personas_v1.md, sanity_gt/.

## Phase 1 — API 키 없이 검증 가능한 전부 (이번 세션)
- [x] core.py — 상수·persona·Instance/Event 스키마
- [x] matrix.py — 변인 행렬 + 층화 샘플러 (Core 90 + no-op 10, pairwise ≥2, 시드 고정)
- [x] gt.py — GT 합성기 (sanity R1~R6 포함, R6 신규 구현)
- [x] logs.py — 정형 event_type 로그 생성기 (4 persona × clean/noise)
- [x] mock.py — MCP mock (instance 이벤트와 정합하는 route/weather 응답)
- [x] env.py — text-state 트리거 루프 (관찰 = 로그+시각+state+이벤트+자기 알림 이력)
- [x] agents.py — OracleRule / AllSilent / Random (+ LLM 클라이언트 골격)
- [x] score.py — A-layer (decision F1, band, critical miss, 중복, no-op restraint)
- [x] run_smoke.py — 생성→실행→채점 end-to-end, oracle≈만점 / silent 저점 확인
- [x] 스모크 테스트 통과 (oracle F1=1.0, silent=0.0, allfire=0.323)
- [ ] git 커밋 (design 문서 / trigger_bench 분리)

## Phase 2 — API 필요 (다음)
- [x] LLM agent 실호출 코드 + JSON 파서 (실행은 로컬)
- [x] B-layer judge 구현 — binary 기준 4종(modality/content/grounded/seq_consistent)
- [ ] rationale source·groundedness 채점 (LLM 출력 대상)
- [x] LLM 로그 렌더러 + 신호 보존 validator
- [x] oracle probe 구현 (realism 통계는 확장 시)
- [ ] 실험 매트릭스 러너 (clean/noise × log/oracle-persona)

## Phase 3 — GUI subset
- [ ] KnowU env 어댑터 (분리 유지, trigger_bench 쪽에서 호출)
- [ ] 시간 점프 PoC
