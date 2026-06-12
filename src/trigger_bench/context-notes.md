# trigger_bench 구현 컨텍스트 노트

> 작업 중 결정과 근거. 다음 세션이 재도출 없이 이어가기 위한 기록.

- **2026-06-11 패키지 분리**: JM 지시로 `src/trigger_bench/` 신설, knowu_bench import 0. GUI subset은 Phase 3에서 어댑터로만 연결.
- **로그를 LLM 없이 프로그램 생성으로 변경**: 우리 로그는 정형 event_type(자연어 action 아님)이라 템플릿 풀로 결정론 생성 가능. KnowU 레시피(LLM 생성+수작업 리뷰)에서 이탈하지만 ① 재현성 ② 신호 밀도 제어 정밀 ③ 검수 비용 0이 이득. LLM은 노이즈 다양화에 선택적 사용(Phase 2). ⚠ 설계 문서(personas_v1 §2)와 차이 — JM 확인 필요.
- **text-state v1에서 MCP 결과를 관찰에 인라인 제공**: agent 도구 호출 구현 전 단순화. 부작용 — 정도-수집(tool 호출 깊이) 축이 v1에서 평가 불가. Phase 2에서 tool-calling으로 전환 시 rationale 채점과 함께 복원. ⚠ open.
- **A-layer v1 범위**: decision F1·band·critical miss·중복·no-op restraint만. rationale source·groundedness는 LLM agent 출력이 생기는 Phase 2로 (규칙 agent는 rationale을 GT에서 복사하므로 채점 무의미).
- **OracleRuleAgent = gt.synth 재사용**: 채점기 무결성 검증용 (만점 나와야 함). 순환이지만 의도된 것 — 실평가 대상 아님.
- **E4 배치**: 강제/승격 이벤트 있으면 그 시각에 겹침, 없으면 미리/임박 발사창 중 랜덤 선택 (sanity_findings §4-1).
- **pairwise 커버리지**: 전수 1,440셀 중 90개로 모든 레벨 쌍 ≥2 달성은 greedy 보강 샘플링으로. 미달 쌍은 교체 반복.
- **스모크 결과 (2026-06-11)**: 100 instance, 3,936 판정, pairwise 커버리지 실질 100%(유일 미달 쌍 = cancel→E1/E3 무효화로 구조적 불가). oracle F1 1.0 / all_silent 0.0·critMiss 1.0 / all_fire 0.323·dup 3536 — 채점 축들이 게이밍 기준선을 정확히 분리.
- **git 주의**: sandbox에서 .git 락 삭제 불가(Operation not permitted). design 커밋(8896423)은 성공, trigger_bench 커밋은 보류 — 로컬에서 `rm .git/index.lock .git/HEAD.lock` 후 커밋 필요.
- **로그 생성 하이브리드 확정 (2026-06-12, JM)**: 순수 프로그램 → 하이브리드로 변경. 프로그램이 신호 skeleton(밀도·시점), LLM이 표면 렌더링(앱·장소·params 변주, noise 다양화), validator가 신호 보존 사후 검증. logs.py = skeleton 단계로 유지, LLM 렌더러+validator는 Phase 2. 근거: 순수 프로그램은 "합성 티"(규칙적 패턴) 리스크, 순수 LLM은 밀도 제어 상실+GT 모순 위험 — related_work_analysis_v1 §3 참조.
- **Phase 2 구현 완료, 실행은 로컬 (2026-06-12)**: sandbox 프록시가 api.openai.com 차단(403) → llm.py/render_logs.py/probe.py/judge.py/run_pilot.py 구현 후 dry 모드로 구조 검증(oracle F1 1.0). 실 API 실행은 로컬에서 `python3 run_pilot.py`. 모델: agent·렌더러=gpt-5.5, judge=gpt-5.5-pro, probe 약모델=gpt-5-mini(미확인 — 키로 models.list 확인 필요). 키는 .env에서만 로드, 출력 금지.
- **파일럿 규모**: Core 16+no-op 4=20 instance(JM: 교수 승인 후 확장). pairwise 40%는 의도된 것 — 16개로는 전체 쌍 커버 불가, 확장 시 90개에서 충족.
