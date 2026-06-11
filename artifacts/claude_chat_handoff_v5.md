# Claude Chat 핸드오프 v5 — Proactive Agent Benchmark (AAAI 타겟)

> **목적**: claude.ai 챗 세션(설계 확정)을 Cowork 구현 세션으로 이어가기 위한 self-contained context.
> **이전**: v4(Cowork Q1~9 + persona 초안), v3(평가 설계), v2(NeurIPS 시점), `repo_analysis_v3.md`.
> **v5 = v4 위에 이번 세션 결정을 쌓음.** persona 구조가 v4에서 크게 바뀜(6축→2축). 이 문서가 최신 기준.
> **다음 단계 = 구현**: GT 파이프라인 → log 생성 → env 이벤트 루프.

---

## 0. 한 줄 요약 / 포지셔닝 (유지)

- **타겟**: AAAI (dataset 논문). Base = KnowU-Bench 재활용.
- **Core message**:
  > 기존 벤치는 *무엇을 할지/어떻게 추론할지*를 평가한다. 우리는 그 결정을
  > **언제(WHEN)·어떤 방식(HOW)으로 전달해야 사용자가 거슬리지 않게 수용하는가**를 평가한다.
- persona 비노출 → 선호를 behavioral log에서 추론.
- 포지션: "GUI-grounded **결정** 벤치" (조작 벤치 아님). Track1-only.
- **PrefDisco 연결 (논문 무기)**: 우리 2층 구조(상황 > 선호)는 PrefDisco의 context-override(응급 시 선호 뒤집힘)의 **mobile delivery 버전**. 인용하며 차별화.

---

## 1. ★ Persona 구조 (v4에서 대폭 개정 — 6축 → 2축)

### 축 2개 (2×2 = 4 persona)

| 축 | 레벨 | 정하는 것 |
|---|---|---|
| **빈번도** | 적게 / 많게 | **미세조정 재알림 여부**. 적게=band 안 시각조정·날씨 미세변동 silent 유지, 많게=업데이트도 fire |
| **정도** | 약 / 강 | ① modality 채널 풍부도 ② content 요소 우선순위 깊이 ③ **정보수집(tool 호출) 깊이** — 약=날씨앱 안 뒤짐, 강=조회함 |

| | 정도 약 (popup, terse, 수집 얕음) | 정도 강 (음성·진동, rich, 수집 깊음) |
|---|---|---|
| **빈번 적** | P_A | P_B |
| **빈번 많** | P_C | P_D |

### persona 속성 (축 아님, 개별 부여)
- **lead-time**: 미리 / 임박. 4명에 2:2 배정. (빈번도와 분리 — "아침에 미리 vs 닥쳐서"는 재알림 빈도와 별개 선호)

### 공통 강제 (persona 무관)
- **약속 성립 영향 변화는 누구든 알림**: 상대 지연(10분이든 1h든), 취소, 장소변경. → 빈번도가 가르는 건 *미세조정*뿐.
- modality 1층·content 1층 (아래 2번).

### 보류 (완성 후 재검토)
- Weather-sens(정도 축에 흡수됨 — 우산·날씨조회는 content 요소+수집 깊이로 처리), Action-level(비채점), 빈번도·lead 분리 확정됨, 3번째 축 후보(정보 활용 정도).
- v4의 6 persona(하준 등) 벡터·이름 → **4 persona로 재설계 필요** (구현 시).

---

## 2. ★ Modality·Content 규칙 — 2층 구조

### Modality (2층)
- **1층 — 상황 강제 (persona 무관)**: 원리 = **"현재 user_state가 어떤 감각 채널을 쓸 수 있나" (채널 가용성)**. 상황 열거 불필요 — 새 상황도 채널 판정으로 닫힘.
  - 예: 폰 보는 중=시각 열림→popup 충분 / 회의=소리 막힘→무음·시각 / 운전=시각 막힘→음성 / 취침=시각·진동 약함→소리.
  - **GT**: 시나리오 user_state마다 채널맵 사전 정의. 예: `state=회의 → {시각:O, 소리:X, 진동:△}`.
- **2층 — persona 정도 (열린 채널 안에서)**: 약=최소(popup) / 강=풍부(음성·진동·소리).
- 충돌 시 **1층 우선**. (정도 강이어도 회의중엔 무음 popup.)
- 1층 판정 = agent가 에뮬에서 현재 state를 *읽고* 추론 (CASE V). 2층 = log에서 선호 추론.

### Content (2층 + 우선순위)
- **1층 — 강제 (극소)**: **약속 성립 영향만** — 취소/장소변경/상대지연. (우산·경로 등은 강제 아님 — 추천 하나하나가 agent 호출=비용이라 취향 영역. persona가 정함.)
- **2층 — persona 정도가 요소 우선순위로**: "강=전부"가 아니라 **우선순위 낮은 요소까지 포함**. 약=상위 1개, 강=2~3개.
- **상황우선 덮개**: 익숙도(history)가 content를 끔 — 익숙한 곳은 정도 강이어도 경로 생략. 단 **실시간 이상(사고/악천후) 시 다시 켬** ("평소대로면 생략, 평소와 다르면 알림").

### CASE별 content 요소표 (확정)

| CASE | 1층(강제) | 2층 우선순위 | 덮개 |
|---|---|---|---|
| I Preference | — | 기본(약속명/시각)만 | — |
| II Map | — | 경로/수단 > 출구 | — |
| III History | — | 상세경로 > 출구 > 랜드마크 | **익숙도가 끔**, 실시간 이상 시 켬 |
| IV Weather | 위험기상(안전영향)만 | 우산 > 실내경로 > 수단변경 | history≠실시간 감지가 트리거 |
| V User State | — | (modality 쪽. content는 길이 조절) | 채널 가용성 |
| VI Counterpart | 취소/장소/지연 | 재안내(새 출발시각) > 사유 | — |

- **소요시간은 content 아님 → rationale** (WHEN 계산 입력. 경로/수단과 같은 지도검색 출력이지만 역할이 다름).

### History의 역할 (확정)
- **본업 = 선호 추론 소스** (log가 곧 history). PersonaMem/PrefEval 계열과 같은 용법. PrefDisco는 정반대(no-history cold-start) — Table 1에서 명시적 대비, 우리 위치 정당화에 인용.
- CASE III = "history에서 **익숙도/패턴** 읽어 content 조절" 칸.
- history 시간추정(평소 1h) vs 실시간(오늘 1h30m) 충돌 = **CASE IV가 시험** (어긋남 감지 → 실시간 우선).

---

## 3. ★ Timing 메커니즘 (확정)

- **그리드**: 15분 간격 trigger. agent 자기예약 없음 (그리드만).
- **band**: 정답 발사시각 **±7.5min** (v4의 ±5에서 개정 — 그리드 15분과 정합. 임의 정답시각이 정확히 1개 그리드에 커버됨).
- **이벤트 즉시 trigger**: 동적 이벤트(메시지·상태변화) 도착 시 그리드 외 추가 trigger 즉시 발생. ("실제 폰 동작과 일치" + 이벤트 직후 fire/silent가 빈번도 변별점)
- **매 trigger에서 agent가 하는 일 (동일)**: ① 현재 상태 조회 ② 발사창 계산 ③ 창 안→fire / 이르다→silent.
- **silent 정의**: 매 trigger binary "지금 액션? silent?". 이유(대기/취소) 구분 안 함 — 건별 정답만.
- **동적 이벤트의 입력 채널**: counterpart 메시지 등은 폰 알림(popup)으로 *agent에게* 도착 → agent가 GUI에서 읽고 감지 (Q9b 정합).
- **동적 CASE 채점**: WHEN 갱신 + HOW 선택 **둘 다, 한 상황으로 통합**.
- **HOW 산출 시점**: fire하는 trigger에서만 modality/content 산출 (= 알리는 순간 결정. silent trigger는 decision만).

---

## 4. ★ 공통 시나리오 (확정)

- **공통 1벌** — 모든 persona가 같은 이벤트 스트림 받음. persona가 "어느 이벤트에 반응하나"를 필터 (반응 레벨에서 persona별 이벤트 차등이 자동 실현).
- Base: 약속 17:00 서울역, 현재 15:30 대전역, KTX ~1h.
- 그리드 7 (15:30~17:00) + 이벤트 4 = **instance당 11 결정 포인트**.

| 시각 | 이벤트 | 시험 |
|---|---|---|
| 15:30 | (초기) 캘린더 약속 | CASE I·II — 첫 plan, lead/travel |
| 15:50 | 비 시작 | CASE IV — history≠실시간, 우산/수단 |
| 16:05 | counterpart "10분 늦어요" | CASE VI — 발사창 +10, 변경공지(강제) |
| 16:20 | user 통화 시작(~16:40) | CASE V — 채널 가용성 |
| 16:35 | KTX 지연 15분 | CASE III·IV — 익숙도 덮개 해제, 재계산 |

- CASE III(익숙도)은 이벤트 아니라 **log에 심김** (목적지 방문 횟수).
- 환경 변화 = **사전 정의 이벤트** (랜덤 X, 재현성).
- 예시 정답 시퀀스 감각: P_A(적/약/미리)=16:00경 1회 fire + "10분 지연"만 재알림, 비/KTX 미세조정 silent. P_D(많/강/임박)=지연·비·KTX 다 업데이트.

---

## 5. ★ 출력 스키마 (확정)

- **하이브리드: content=자연어, rationale=구조화.** (content는 B judge가 풍부도 채점 — 자연어 유리. rationale은 A deterministic 검사 — 구조화 필수.)

```json
// silent trigger
{ "decision": "silent", "rationale": { ... } }

// fire trigger
{
  "decision": "fire",
  "trigger_time": "16:45",
  "modality": ["popup", "vibrate"],
  "content": "서울역 17시 약속, 16:45에 출발하세요. KTX 1시간. 비 예보 — 우산 챙기세요.",
  "rationale": {
    "travel_source": "maps" | "history",
    "travel_estimate": "1h",
    "buffer_basis": "history" | "preference",
    "buffer_estimate": "15min",
    "modality_basis": "log_response_pattern",
    "dynamic_trigger": "counterpart_late_10min" | null
  }
}
```

### 필드 ↔ 평가 매핑

| 필드 | layer | 평가 |
|---|---|---|
| decision | A | trigger별 fire/silent 정답 → restraint, C1 |
| trigger_time | A | band(±7.5) 안 → WHEN |
| modality | B | persona 선호+채널 가용성 매칭 → HOW |
| content | B | 요소 우선순위+긴급 매칭 → HOW |
| rationale | A | 올바른 source(요행 차단, 추론 증명) |

---

## 6. ★ 채점 (확정)

- **silent/fire**: **F1 메인** (fire=positive) + fire/silent 분리표 보조. ("전부 silent" 게이밍 차단 — silent 6/7=86% 같은 왜곡 방지)
- A(rule, deterministic) / B(LLM judge 1~5, N=3 median) / C(C1 Intrusiveness, C2 Coverage; C3 보류) — v4 유지.
- content B 채점: "CASE 가용요소 중 persona 정도+1층 강제에 맞게 포함했나". 과소·과다 모두 감점.

---

## 7. ★ Log 스키마 (확정)

### 형식 — KnowU 정합 + 정형 이벤트

```
time / app / location / event_type / params      ← agent에 노출
{label, category}                                 ← 숨김 메타 (GT 생성·noise 관리·verifier용)
```

- KnowU 원형: `{time, location, action(자연어), label, category}`, 선형화 `[time] (location) action`, noise 25% 주입, `clean/noise` 토글.
- 우리 차이: action 자연어 대신 **정형 event_type** ("모바일이 실제 찍는 것만, 해석 미주입" 원칙). location·숨김메타·noise 25%·토글은 KnowU 차용 (정합성 방어).
- 참고: ProPerSim은 log 아닌 (A,R) 쌍 LLM요약 메모리. PrefDisco는 no-history. Fara는 agent trajectory. → log 형식 직접 비교 대상은 KnowU뿐.

### 축 ↔ log 신호 (최종)

| 축/속성 | 신호 |
|---|---|
| lead (속성) | `event_arrive` vs 캘린더 약속시각 차 (미리형=40~60분 전 도착 패턴) |
| **빈번도** | **`Settings notif_config` (all_updates/important_only), DnD 사용 빈도** (에피소드 합성 불필요 — 설정 이력 1~2줄. 질문(elicitation)·직접 부여 모두 기각: 전자는 PrefDisco 침범+멀티턴 복잡, 후자는 부분 persona 노출) |
| 정도-modality | `notif_post(mode)` → tap/dismiss 반응속도 |
| 정도-content | 낯선 목적지 `route_search`·출구 조회 깊이 |
| 정도-수집 | Weather/Maps `app_open` 빈도 |
| 익숙도 (CASE III) | 목적지별 방문 횟수 (서울역 N회=익숙, 0회=낯섦) |

- noise: 신호 무관 일상 이벤트(유튜브·메신저 등) ~25%.

---

## 8. 유지 사항 (v4에서 그대로)

- 6 CASES = Internal/External × Static/Dynamic. Gate→Orchestrator→Executor.
- Track1-only (execution·fact 비채점). A/B/C 채점 구조. C3 보류.
- GT = 정적, LLM 생성 + multi-verifier(Fara식) + 필터링(실패 버림). N=5 합의.
- 환경 = KnowU 재활용, 하이브리드 (외부 Maps/Weather=MCP 캐싱 / 폰 네이티브=GUI). AMap MCP가 duration+distance+weather 제공 (신규구현 불필요).
- 다중결정 시퀀스 env 루프 = 신규 구현 (Q9a).
- 채점 인프라 = KnowU rule+judge 재활용 → A/B 매핑.

---

## 9. 다음 단계 (구현, Cowork)

1. **GT 파이프라인 명세·구현**: Generator(LLM) → V1(rule: band) → V2(rubric: rationale) → V3(consistency: N=5, ≥4) → threshold 필터 + human spot-check.
2. **4 persona 확정** (이름·벡터 — 2축+lead 2:2 배정) + **persona별 log 생성** (§7 신호 심기 + noise).
3. **공통 시나리오 instance화** (§4 타임라인 → KnowU task 포맷, 채널맵·이벤트 사전정의).
4. **env 이벤트 루프 구현** (그리드 15분 + 즉시 trigger, 11 결정 포인트).
5. **MCP 캐싱 mock layer** (시나리오별 고정 응답 키).
6. (설계 잔여) CASE V content "길이 조절" 구체화, B judge 프롬프트, C1 α·β 가중치.

---

## 10. 작업 스타일 (JM, 유지)

- 디테일 명확히, 추측 X. Tradeoff 있으면 옵션+추천+근거.
- 확정 사항 반박 시 명시적 깃발.
- **bullet 선호, 줄글 지양, 간결성 우선.** 같은 구조/포맷 일관 유지.
- 질문은 한 번에 하나씩, 결정 누적. (Korean 출력 시 문장 끝 `:` 금지.)

---
*Updated: 이번 claude.ai 세션 종료. 다음(Cowork)은 §9-1(GT 파이프라인)부터 권장.*
