# GT 합성 명세 v1.1 — 요소 규칙 → persona 마스크 → 결정론적 GT

> 작성: 2026-06-11. 확정 합의 기반 (JM + Claude 세션).
> **v1.1**: sanity 합성(10×4, `sanity_gt/`)에서 발견된 규칙 수정 R1~R6 반영 — §1.5 참조. 수치 확정: B_early=30, B_late=10, prep=10.
> 원칙: GT는 LLM 생성물이 아니라 **규칙 합성 결과**. 인간은 instance가 아니라 **규칙을 검수**.
> handoff v5 §9-1(GT 파이프라인)의 Generator+multi-verifier 구조를 본 명세로 대체.

---

## 1. WHEN — 합성 수식과 요소 함수

### 기본 수식

```
fire_time = T_appt − travel(loc_now → dest; 실시간, 날씨, 수단) − buffer(persona.lead) − prep
```

| 항 | 정의 | 소스 |
|---|---|---|
| T_appt | 유효 약속시각. 동적 이벤트로 갱신 (상대 +10분 지연 → +10) | 캘린더 + 이벤트 |
| travel | 실시간 소요시간. 날씨 보정(비→도보 구간 +α), 수단 지연(KTX +15) 반영 | mock Maps/Weather 캐시 |
| buffer | persona lead 속성. 미리형 = +B_early, 임박형 = +B_late | persona |
| prep | 고정 준비시간 | 시나리오 정의값 |

- B_early/B_late/α 등 수치는 시나리오 캘리브레이션에서 확정 (open item §6).
- **스냅 규칙**: Δ 라벨은 5분 단위로 정의. fire_time은 분 단위 계산 후 band ±7.5 적용 → 정확히 1개 그리드 커버 (handoff §3 정합).

### Override 표 (우선순위 순 — 위가 이김)

| # | 조건 | GT |
|---|---|---|
| 1 | 약속 취소 | 취소 공지 1회 fire (1층 강제), 이후 출발 알림 전부 silent |
| 2 | user 이미 이동 중 / 도착 | 출발 알림 silent |
| 3 | 1층 강제 이벤트 (취소·장소변경·상대지연·위험기상) | persona 무관, 해당 trigger에서 fire |
| 4 | 미세변동 (아래 승격 규칙 미달) | 빈번도 많 = fire, 적 = silent |
| 5 | 그 외 | fire_time band 내 그리드 = fire, 이외 silent |

### 미세변동 → 성립영향 승격 규칙

```
|new_fire_time − 직전 알린 출발시각| > 7.5min  →  성립영향 (1층 강제로 승격, persona 무관 fire)
이하                                        →  미세변동 (빈번도 필터)
```

### 동적 이벤트 라벨 (이벤트당 4튜플)

```
event := (ΔT_appt, Δtravel, 강제여부, 재알림분류)
```

| 이벤트 (handoff §4) | ΔT_appt | Δtravel | 강제 | 분류 |
|---|---|---|---|---|
| 상대 "10분 늦어요" | +10 | 0 | ✅ (변경공지) | — |
| 비 시작 | 0 | +α (도보 구간) | ✗ | 승격 규칙 적용 |
| KTX 지연 15분 | 0 | +15 | ✗ | 승격 규칙 적용 |
| user 통화 시작 | 0 | 0 | ✗ | WHEN 무관 (HOW 채널맵만 변경) |

### 1.5 보정 규칙 R1~R6 (sanity 합성 결과, 2026-06-11 확정)

| # | 규칙 |
|---|---|
| R1 | 빈번도 필터(override 4)는 **재알림에만** 적용. 첫 알림 미발사 상태에선 이벤트 trigger라도 band 시작 도달 시 fire |
| R2 | 첫 알림 = band 시작(ft−7.5) 이후 **첫 trigger에서 무조건 fire** |
| R3 | 이동 중 판정(override 2) = **마지막 안내한 출발시각** 기준 (user는 안내를 따른다고 가정) |
| R4 | 관찰 창·그리드는 **T_appt 갱신을 따라 연장** (상대 +60 → 그리드도 18:00까지) |
| R5 | 이동 중 변경공지 content = **도착 영향** ("도착예정 vs 약속"), 출발시각 안내는 출발 전만 |
| R6 | 필요 출발시각 < 현재인 강제 이벤트 → content "**즉시 출발 + 지각 N분**" |

- 윈도 정책: 기본 90분, `travel+buffer+prep+7.5 > 90`이면 그리드 단위 확장 (KTX×미리=120분).
- 상세 근거: `design/sanity_gt/sanity_findings.md`.

---

## 2. HOW — 합성 규칙

### Modality

```
GT_modality = f(채널맵[user_state]) ∩ persona.정도
```

- 채널맵 (상황층, persona 무관): `state → {시각, 소리, 진동}` 가용성. 시나리오 사전 정의 (handoff §2).
- persona층: 약 = 가용 채널 중 최소(popup), 강 = 가용 채널 모두(popup+진동/음성).

### Content

```
GT_content = 1층강제요소 ∪ top-k(CASE 우선순위표) − 익숙도마스크
k = persona.정도 (약=1, 강=2~3)
익숙도마스크: history 익숙 → 경로 요소 제거. 단 실시간 이상(사고·악천후·지연) 시 복원
```

- CASE 우선순위표 = handoff §2 표 그대로.

---

## 3. Persona 마스크 — persona가 끼는 지점 (경계 고정)

| 결정 | 상황층 (persona 무관) | persona층 |
|---|---|---|
| fire/silent | override 1~3, band 판정 | 빈번도 (미세변동 재알림 여부) |
| trigger_time | T_appt·travel 계산 | buffer (lead) |
| modality | 채널맵 | 정도 (채널 풍부도) |
| content | 1층 강제, 익숙도 덮개 | 정도 (top-k 깊이) |

이 표 밖에서 persona가 GT에 개입하는 일은 없음. 합성은 전부 기계적.

---

## 4. 인간 검수 프로토콜 (3단)

| 단계 | 대상 | 방법 | 보고 |
|---|---|---|---|
| ① 규칙 검수 | 요소 함수·override 표·CASE 우선순위표·채널맵 (수십 줄) | annotator 3명, 항목별 동의/수정 | 항목별 agreement |
| ② 합성 spot-check | persona×템플릿 층화 표본 20~30 instance의 GT 시퀀스 | 타당성 평가. **불일치 시 instance가 아니라 규칙을 수정** 후 전체 재합성 | 동의율 |
| ③ judge 검증 (B-layer) | trajectory 20~30개 | 인간 3~4명 채점 vs judge, KnowU Fig.4 방식 | MAE·상관 |

- ②의 "규칙 수정 → 재합성" 원칙이 일관성 보장의 핵심 (개별 GT 패치 금지).

---

## 5. 루브릭 확정 목록

### A-layer (rule, deterministic)

| 루브릭 | 내용 | 비고 |
|---|---|---|
| decision F1 | fire/silent, 전체 pool 집계 | 기존 (handoff §6) |
| trigger_time | band ±7.5 | 기존 |
| rationale source | travel_source·buffer_basis 등 정합 | 기존 |
| **content groundedness** | content 내 수치(소요시간·출발시각·지연분)가 mock MCP 캐시 값과 일치 | ★신규 — 환각 차단 |
| **중복 알림** | 같은 band 내 상태변화 없는 재알림 감점 | ★신규 |
| **critical miss** | 1층 강제(취소·장소변경·위험기상) 누락 — **평균에 안 섞고 별도 지표 보고** | ★신규 — 안전성 서사 |

### B-layer (LLM judge, persona 값 기반 사전 개인화 루브릭 + 기준별 독립 채점)

| 루브릭 | 내용 | 비고 |
|---|---|---|
| modality 적합 | 채널맵 + 정도 매칭 | 기존 |
| content 우선순위 적합 | top-k 요소 포함, 과소·과다 모두 감점 | 기존 |
| **시퀀스 일관성** | ① 직전 알림과 모순 여부 ② 업데이트 알림의 delta-awareness ("KTX 15분 지연으로 출발 16:30로 변경") | ★신규 — 멀티 trigger 벤치만 가능한 차별화 축 |

### C-layer

- C1 Intrusiveness, C2 Coverage 유지 (handoff §6). critical miss는 C2와 연계 보고.

---

## 6. 관련 확정 사항 + Open Items

### 확정 (이번 세션)
- P0-1: 시나리오 **템플릿화** — 변인 행렬에서 instance 프로그램 생성, GT는 본 명세로 자동 합성.
- P0-2: 로그 = KnowU 레시피 (persona 조건 LLM 생성 + 수작업 리뷰 + label 붙인 noise 25%) + **oracle probe** (로그만으로 2축+lead 복원률 보고 — 두 논문 다 안 한 차별화).
- P0-3: GT 검증 = 본 명세 §4 (규칙 검수 + spot-check + judge↔human).
- B judge = PrefDisco식 사전 개인화 루브릭 + 기준별 독립 채점.

### Open
- [ ] B_early/B_late, α(비 보정), k(정도별 content 깊이) 수치 캘리브레이션
- [ ] 빈번도 log 신호의 행동화 — `notif_config` 설정 1줄(lookup 위험)을 행동 패턴(업데이트 알림 즉시 dismiss 등)으로 보강/대체
- [ ] 템플릿 변인 행렬 설계 (목적지 익숙도 × 날씨 × 상대이벤트 × state 스케줄 × 약속시각/수단) — instance 목표 수 결정
- [ ] 시퀀스 일관성 judge 프롬프트
- [ ] handoff §9-1 갱신 (Generator+multi-verifier → 규칙 합성 + §4 검수)
