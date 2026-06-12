# 설계 리뷰 — handoff v5 보완/수정/추가 포인트

> 작성: 2026-06-11. 관점: AAAI 리뷰어가 공격할 지점 + 설계 빈칸.
> KnowU/PrefDisco는 참고만 — 동일할 필요 없음.

---

## P0 — 논문 생존 직결

### 1. 규모 부족 (최대 약점)
- 현재 확정안 = 공통 시나리오 **1벌** × 4 persona × 11 결정 포인트 = **44 판정**. dataset 논문으로 성립 불가.
- 보완안 — 시나리오 **템플릿화**. 변인 행렬(목적지 익숙도 × 날씨 유무/시점 × 상대 이벤트 종류/시점 × user state 스케줄 × 약속 시각/이동수단)에서 instance 수십~수백 개 프로그램 생성.
  - 부수 이득 ① GT가 행렬에서 결정론적으로 도출됨 (LLM 생성 의존 ↓, §9-1 부담 ↓).
  - 부수 이득 ② 고정 1벌의 암기/오염 리스크 해소.
  - 공통 1벌 원칙(persona 간 동일 스트림)은 템플릿 안에서 유지 가능 — instance마다 4 persona 공유.

### 2. GT 타당성 — "그게 정말 사용자가 원하는 것인가"
- 현재 = LLM 생성 + verifier + human spot-check. 리뷰어는 "persona 스펙→GT 도출과 agent의 추론이 같은 해석 회로를 공유(순환성)" + "인간 동의 근거 없음"을 지적할 것.
- 보완안 — persona를 부여받은 annotator가 GT(fire 시점·modality·content)에 동의하는지 **agreement 수치 보고** (3인, kappa). spot-check를 정식 검증 프로토콜로 승격.

### 3. 로그 식별가능성 사전 검증 (벤치 무결성)
- 로그에서 persona 축이 *실제로 복원 가능한지* 증명 단계가 없음. 복원 불가면 벤치가 노이즈를 측정하는 것.
- 보완안 — **oracle probe**: 강한 LLM에 로그만 주고 2축+lead 분류시켜 복원률 보고 (높아야 함). 동시에 약한 모델과 격차가 있어야 변별력 입증.
- 추가 우려 — 빈번도 신호가 `notif_config: important_only` 설정 1~2줄 = 사실상 **lookup이지 추론이 아님**. 행동 증거(업데이트성 알림 dismiss 패턴, DnD 사용 시간대)로 보강하거나, 설정 줄을 빼고 행동만으로 추론하게 할지 결정 필요.

---

## P1 — 평가 설계 빈칸 (구현 전 확정 필요)

### 4. F1 정의 미완
- band 밖 시각에 fire한 경우 — FP인가, FN도 동시인가. (권고: 해당 grid는 FP + 정답 band grid는 FN — "늦게라도 알림"과 "안 알림"을 구분)
- 같은 band에 중복 fire 시 처리. 11포인트 중 fire 정답이 1~3개라 instance 단위 F1 불안정 — **전체 pool 집계**로 명시.

### 5. trigger 간 agent 상태 명세 없음
- agent가 **자기 과거 fire 이력을 보는가** — 재알림/중복 방지 판단에 필수인데 미정의.
- 권고: 노출 컨텍스트 = (로그 H, 현재 시각/state, 누적 이벤트, **자기 알림 이력**). 매 trigger 독립 호출 + 이력 주입인지, 세션 유지인지 확정.

### 6. 실험 조건 매트릭스 미설계
- 본 실험 표가 설계에 없음. 최소 축 — clean/noise × full/RAG × **log vs oracle-persona(직접 제공)**.
- oracle 조건은 "성능 저하가 로그 추론 실패 때문"임을 입증하는 핵심 (없으면 모델 일반 능력 부족과 구분 불가).
- baseline(로그도 없음) 추가 시 3조건 — 차이의 귀속이 깔끔해짐.

### 7. GUI 필요성 방어 논리
- Track1-only(조작 비채점)인데 에뮬레이터를 쓰는 이유를 리뷰어가 물을 것. 11포인트 × GUI 에피소드 × 모델 수 = 평가 비용도 큼.
- 권고: CASE V(state를 GUI에서 읽음) + 동적 이벤트의 popup 도착(Q9b)을 근거로 명문화. 가능하면 **text-state 모드 ablation**으로 "GUI grounding이 점수를 바꾼다"를 직접 보여주면 가장 강함. (바뀌지 않으면 GUI를 버리고 비용을 줄이는 결정도 가능 — 어느 쪽이든 이득)

---

## P2 — 검토 권장

### 8. persona 4개의 confound
- lead 2:2 배정이 2축과 얽힘 (예: P_A=미리, P_B=임박이면 lead 효과와 정도 효과 분리 불가).
- 권고: instance 간 lead 배정 counterbalance, 또는 분석에서 lead를 회귀 통제. 8 persona(2×2×2)가 깔끔하나 비용 2배 — 템플릿화로 instance가 늘면 4개+counterbalance로 충분.

### 9. 정도 축 = 3요소 번들
- modality 풍부도 + content 깊이 + 수집 깊이가 한 축 — 실패 귀속 불가.
- 권고: 채점은 이미 분리돼 있으니 **sub-score(WHEN/modality/content/수집) 분리 보고**를 명시. 축 자체는 유지 가능.

### 10. fire/silent 2-way — "ask(확인)" 부재
- KnowU는 act/ask/silent 3-way. 우리가 consent 차원을 뺀 이유를 명문화 필요.
- 방어 논리: 우리 도메인에선 **알림 자체가 최소 개입형 ask** (실행을 안 하므로 confirm 대상이 없음). 논문에 한 단락 필요.

### 11. judge 신뢰성
- B judge — 평가 대상 모델과 다른 계열 모델 사용(자기 계열 편향), N=3 median 유지, judge-인간 상관 1회 보고하면 방어 완성.

### 12. 기타
- 벤치 이름 미정.
- silent trigger의 rationale — 수집은 하는데 채점 여부 미정 (권고: A-layer에서 "이른 이유" source만 검사, 미채점 시 수집 근거 명시).
- 이벤트 연쇄 GT 갱신 규칙(16:05 +10분 → 16:35 KTX +15분 누적) — 수식 한 줄로 명문화 (발사창 = 약속시각 − travel(실시간) − buffer(persona) ± 7.5).

---

## 요약 — handoff §9에 끼워 넣을 작업

| 우선 | 추가 작업 | 들어갈 위치 |
|---|---|---|
| P0 | 시나리오 템플릿 변인 행렬 설계 | §9-3 앞 (instance화의 전제) |
| P0 | 로그 oracle probe + 빈번도 신호 행동화 | §9-2 (log 생성 직후 검증) |
| P0 | GT 인간 agreement 프로토콜 | §9-1 (spot-check 승격) |
| P1 | F1 세칙·agent 상태 명세·실험 매트릭스 | §9-6 (설계 잔여)에 추가 |
| P1 | text-state ablation 여부 결정 | 실험 설계 시 |
| P2 | lead counterbalance, sub-score 보고, ask 부재 방어 단락 | 논문 작성 시 |
