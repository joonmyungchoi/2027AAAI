# 사전 분석 — 논문 2편 + KnowU-Bench 코드 (구현 착수 전 점검)

> 작성: 2026-06-11. 대상: handoff v5 (`artifacts/claude_chat_handoff_v5.md`) 기준 검증.
> 출처: PrefDisco(arXiv 2510.00177v2), KnowU-Bench(arXiv 2604.08455v1), `src/knowu_bench/` 코드.

---

## 1. PrefDisco 검증 결과 — ★ handoff §0 수정 필요

### 실제 내용
- 벤치마크가 아니라 **"evaluation methodology"** — 정적 추론 벤치 10개(MATH-500, MMLU 등)를 대화형 개인화 태스크로 변환. 텍스트 QA 도메인, GUI·알림·타이밍 무관.
- 선호 = 인스턴스 단위 `{(θ_j, v_j, w_j)}` (속성, 값 1–5, 중요도 가중치). 5턴 제한 elicitation, passive user simulator.
- persona 100개 (IPIP Big Five 기반), 10,000 시나리오, 21개 모델.
- 평가 = **Baseline / Discovery / Oracle** 3조건 + **PrefAlign**(속성별 사전 개인화 루브릭 가중평균) + **NormAlign**(Oracle 천장 대비 정규화) + task accuracy safeguard.
- ICLR 2026, Li et al. (UW + AI2). 공동 1저자 Shuyue Stella Li, Avinandan Bose.

### handoff v5 주장 검증
| 주장 | 판정 |
|---|---|
| "no-history cold-start" | ✅ 사실. 논문 Table 1 자기 분류가 "true cold-start; no history". 대비 인용 유지 |
| "context-override (응급 시 선호 뒤집힘)" | ❌ **용어·메커니즘 모두 부정확**. 실제 용어는 "Context-Dependent Preference Instantiation" — 맥락이 선호 *값*을 인스턴스별로 변조하는 것. 우리처럼 상황 규범이 선호를 *누르는 2층 위계*가 아님. 충돌·우선순위 개념 없음 |
| "elicitation 배제로 차별화" | ✅ 성립. 단 로그 기반 추론의 진짜 인접 연구는 PersonaMem·PrefEval 쪽 |

### 수정 권고 (설계 강화 기회)
- **§0 문구 교체**. PrefDisco Limitations에 "does not address ... conflicting preferences across different contexts" 명시 → "PrefDisco가 명시적 한계로 남긴 선호-상황 충돌·override를 우리 2층 구조가 평가" 로 쓰면 차별점이 더 강해짐.
- "proactive" 용어 충돌 주의 — PrefDisco의 proactive는 "선제적 질문", 우리는 "선제적 알림". 관련연구에서 명시 구분.
- 인용 표기 — "PrefDisco (evaluation methodology)", Li et al. 2026, ICLR 2026. PrefAlign은 메트릭 이름(혼동 금지).

### 차용 후보 (채택 여부 결정 필요)
1. **3조건 + NormAlign** — Baseline(선호 無) / Log-Inference(우리) / Oracle(선호 명시). "로그에서 얼마나 회수했나"를 모델별 천장 대비로 측정. 채점 설계(§6)에 추가 검토.
2. **가중 루브릭 채점** — B judge를 홀리스틱 1–5 대신, persona 값에 맞게 사전 개인화된 속성별 루브릭 + 가중평균. judge 환각·편향 감소 근거 인용 가능.
3. **task accuracy safeguard** — 알림 적응이 본 태스크 수행을 깎는지 병행 측정.
4. **인간 검증 프로토콜** — annotator 3명, Fleiss' kappa 보고. GT human spot-check(§9-1)에 복제.
5. GT 생성 시 LLM 3종 랜덤 선택(단일 모델 편향 완화) — multi-verifier와 결합 가능.

---

## 2. KnowU-Bench 논문 — 차별성 확인, 충돌 없음

- Proactive task = **단일 결정** (direct execution / ask consent / silent) + post-rejection restraint. 타이밍 정밀도·modality·content 채점 없음 → 우리 WHEN(±7.5 band)·HOW(modality/content)·11 결정 포인트 시퀀스는 명확한 신규 기여. 충돌 없음.
- 채점 = `S = λ·S_rule + (1−λ)·S_llm` 하이브리드 → 우리 A/B 매핑과 정합 (handoff §8 주장 확인).
- log 형식 `(time, location, action)` 확인 — handoff §7 서술과 일치.
- **"Time sensitive tasks additionally override device time during initialization"** — 디바이스 시간 오버라이드가 공식 기능. 15분 그리드 시뮬의 기반으로 활용 가능 (단 init 시점 한정 — 에피소드 중 시간 점프는 신규, §3-D 참조).
- 관련연구 인용 후보 (우리 Table 1) — ProactiveMobile(Kong 2026), PIRA-Bench(Chai 2026), Pare(Nathani 2026), 20K(Yang 2025), PersonaMem, PrefEval, PrefDisco.

---

## 3. 코드 분석 — 재활용 vs 신규 구현

### 재활용 가능 (handoff §8 주장 대부분 확인)
| 항목 | 위치 | 비고 |
|---|---|---|
| Task 등록·실행 | `tasks/base.py` (BaseTask), `tasks/registry.py` | initialize_task / is_successful / tear_down 라이프사이클 |
| Proactive 베이스 | `tasks/definitions/routine/base_routine_task.py` | 로그 컨텍스트를 goal에 주입, `expectation={should_act, actions}` — 우리 trigger task의 출발점 |
| 로그 주입 (full/RAG) | `runtime/utils/user_log_context.py` (build_user_log_context) | clean/noise는 파일 분리(`*_noise_25pct.json`) 방식 |
| LLM judge | task 내 `query_user_agent_judge` + 루브릭 (예: `preference/commute_routing_bad_weather.py`) | 가중 루브릭 패턴 이미 존재 — B 채점 매핑 용이 |
| AMap MCP | `runtime/mcp_server.py` — dashscope SSE `amap-maps` 클라이언트 | ✅ handoff 주장 사실. 단 mock/캐싱 레이어는 없음 |
| 시간 제어 | `runtime/setup/clock.py`, `app_helpers/system.py` (auto_time) | init 시 디바이스 시간 오버라이드 가능 |
| 이벤트 주입 채널 | `runtime/controller.py` adb broadcast, mattermost/mastodon docker backend | counterpart 메시지는 backend로 주입 가능 |

### 신규 구현 필요 (handoff §9와 대조)
1. **멀티 트리거 env 루프** — 현재 구조는 태스크당 단일 에피소드(1 instruction → N GUI step → 1 채점). 15분 그리드 7회 + 이벤트 4회 = 11 결정 포인트 루프는 전면 신규. handoff Q9a 예상과 일치.
2. **에피소드 중 시간 점프** — init 시간 오버라이드는 있으나 trigger 간 "15:30→15:45" 점프 메커니즘 없음. adb `date -s` 류 + 앱 상태 정합성 검증 필요. **리스크 항목** — 에뮬레이터에서 시간 점프 시 앱(캘린더·알림) 동작 검증 선행 권장.
3. **event_type 정형 로그 생성기** — 기존 로그는 자연어 action. 우리 `time/app/location/event_type/params` 포맷 + 숨김 메타는 신규 생성 (스키마는 §7 확정대로).
4. **noise 런타임 토글** — 현재 파일 레벨 분리. 동일 방식 차용하면 추가 구현 불필요 (persona별 clean/noise 2벌 생성).
5. **MCP mock/캐싱 레이어** — 시나리오별 고정 응답 키. `mcp_server.py`의 SyncMCPClient 래핑으로 구현.
6. **출력 스키마 파서 + A 채점기** — fire/silent, band ±7.5, rationale source 검사. 기존 rule check 패턴 위에 신규 작성.

---

## 4. 종합 — handoff v5 대비 변경 요약

| # | 항목 | 조치 |
|---|---|---|
| 1 | §0 PrefDisco "context-override" 표현 | **수정 필수** — 실제 용어로 교체, Limitations 인용으로 차별점 강화 |
| 2 | §6 채점 | 검토 — Oracle/Baseline 조건 + NormAlign, 가중 루브릭, accuracy safeguard 채택 여부 |
| 3 | 관련연구 Table 1 | PersonaMem·PrefEval·ProactiveMobile·PIRA-Bench·Pare 포함 |
| 4 | §8 "환경=KnowU 재활용" | 대체로 사실. 단 **시간 점프·멀티 트리거 루프는 전면 신규** — §9 순서에서 env 루프(§9-4)의 기술 리스크가 가장 큼. 시간 점프 PoC를 §9-1보다 먼저 돌려볼 가치 있음 |
| 5 | §7 noise 토글 | 파일 분리 방식 차용으로 단순화 (런타임 토글 불필요) |
