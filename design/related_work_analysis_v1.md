# Related Work 분석 v1 — Proactive 논문 7편: History 구성·GT 생성·차용점

> 작성: 2026-06-12. artifacts/ 7편 전수 분석 (서브에이전트 5 + 기존 분석 2).
> 용도: ① 우리 설계 보완 ② Table 1(비교표) 초안 ③ related work 집필 소스.

---

## 1. 한눈 비교표 (Table 1 초안)

| 논문 (venue) | History 구성 | 선호 출처 | WHEN 타이밍 | HOW (modality/content) | GT 생성 | GT 검증 | silent 평가 |
|---|---|---|---|---|---|---|---|
| **FingerTip 20K** (ICLR'26) | 실사용자 95명×1개월 수집 (스크린샷+a11y tree+action) | 사용자 본인 행동 | ✗ (사용자가 폰 든 시점 고정) | ✗ | 사용자 행동 자체 = GT | 간접 (유사도 분석, 인간 평점 상관) | ✗ |
| **ProactiveMobile** (CVPR'26, Xiaomi) | 공개 GUI 데이터 + LLM 합성 프로필, noise 5~20× | 명시적 user profile (자연어) | ✗ (스냅샷 1회 결정) | ✗ (출력=API 함수) | 6 MLLM 후보→클러스터 top-3 | 3단: rule→LLM→**3인 2/3 합의** ($210K, 4개월) | ✅ FTR |
| **PersonalAlign** (ACL'26 추정) | FingerTip 실로그 재활용, 사후 마이닝 | 실로그 (자연어 intent) | ✗ (**trigger 시각 예측을 future work로 명시**) | ✗ | Qscore 3-Gaussian 필터→인간 검수 | annotator 검수 (agreement 미보고) | ✅ negative 100 state, False-Alarm |
| **ProPerSim** (ICLR'26) | LLM 시뮬레이션, (A,R)쌍 LLM 요약 메모리 | 명시적 rating 피드백 | △ (2.5분 tick, LLM 주관 판정) | ✗ (텍스트 추천만) | user simulator 실시간 LLM 채점 | 인간 합리성 검사 90.5% (kappa 없음) | ✅ No-Rec 채점 |
| **PersonaVLM** (preprint) | LLM 합성 멀티모달 대화 (선호 drift 확률 주입) | 대화 이력 | ✗ (reactive QA) | ✗ | LLM 초안→4인 검수 (~40 person-hours) | 3기준 검수, 모호 폐기 (kappa 없음) | ✗ |
| **KnowU-Bench** (base) | LLM 생성+수작업 리뷰, 자연어 action, noise 25% | 행동 로그 (자연어) | ✗ (단일 act/ask/silent) | ✗ | profile habits → rule+judge | judge↔인간 26개×4인 MAE | ✅ 3-way |
| **PrefDisco** (ICLR'26) | 없음 (cold-start) | elicitation (질문) | ✗ | ✗ | 선호 프로필 = 구성상 정답 | 속성 관련성 3인 κ0.463 | ✗ |
| **우리** | **프로그램 결정론 생성**, 정형 event_type, noise 25% | **행동 로그 추론** (2축+lead) | **✅ 그리드+이벤트, band ±7.5, 시퀀스 7~13 결정** | **✅ 채널맵×정도, content top-k** | **규칙 테이블→persona 마스크 결정론 합성** | **규칙 검수+spot-check+judge↔인간** | ✅ F1+FTR+no-op |

## 2. 신규성 안전 판정

- **WHEN(분 단위·시퀀스)** — 7편 중 누구도 안 함. 가장 가까운 건 ProPerSim(2.5분 tick이지만 LLM 주관 채점, 결정론 band 없음). **PersonalAlign 부록 C가 "Proactive Triggering (T't, S't 예측)"을 명시적 future work로 남김 — 우리 자리를 선행 논문이 직접 지목해준 셈. 반드시 인용.**
- **HOW(modality/content)** — 7편 전부 없음. 출력이 의도 문장/API 함수/텍스트 추천뿐.
- **로그 기반 선호 추론** — KnowU(자연어 로그)만 동류. ProactiveMobile은 profile이 자연어로 명시 제공(추론 아님 — 표면 서사가 겹치니 본문에서 명확히 구분 필요).
- **위협 요인** — ProactiveMobile(CVPR, Xiaomi 산업 규모)이 "mobile proactive benchmark" 자리를 선점. 정면 비교 필수, 차별축은 시간적 결정·알림 채널·로그 추론·결정론 GT.

## 3. History 구축 — 방식 스펙트럼과 우리 위치

- 스펙트럼: 실사용자 수집(FingerTip) > 실로그 마이닝(PersonalAlign) > LLM 시뮬레이션(ProPerSim·PersonaVLM) > LLM 합성+검수(KnowU·ProactiveMobile) > **프로그램 결정론 생성(우리, 유일)** > 없음(PrefDisco).
- 우리 방식 방어 논리 보강 (프로그램 생성 확정에 추가 근거).
  - ProactiveMobile도 노이즈를 프로그램적으로 주입(5~20×) — "통제된 노이즈"는 이미 관행.
  - PersonaVLM도 선호 drift를 "probabilistically induce" — 프로그램적 신호 주입의 선례.
  - FingerTip의 실데이터 GT는 인간조차 30.3%만 맞히는 노이즈 문제 — 우리 결정론 GT의 반대 근거로 인용.
- **realism 검증 추가 (신규 아이디어)**: PersonalAlign의 Qscore(semantic similarity + temporal/scenario entropy) 통계를 우리 합성 로그에 계산, 실데이터(FingerTip/AndroidIntent)와 분포 구조 비교 → "합성이지만 실로그다움" 정량 방어. oracle probe와 함께 로그 검증 2종 세트.
- noise 25% 정당화: PersonalAlign의 moment/preference/routine 3계층 용어 차용 — noise = "moment intent".

## 4. GT 생성·검증 — 관행 대비 우리 프로토콜

- 관행: LLM 후보 생성 → 다인 합의가 표준 (ProactiveMobile 3인 2/3·judge-human 98%, PersonaVLM 4인 3기준·40 person-hours). agreement 정량 보고는 드묾 (PrefDisco κ0.463이 거의 유일 — PersonalAlign·ProPerSim·PersonaVLM 모두 미보고).
- 우리 차별: GT가 LLM 생성물이 아니라 규칙 합성 → 인간은 instance가 아니라 **규칙**을 검수. 비교표에서 "검증 가능성·재현성" 축으로 공격 가능.
- 보고 기준점 (우리가 넘어야 할 수치): 합의율 2/3 이상, judge↔인간 일치 ~98%(ProactiveMobile), 검수 규모 person-hours 명시(PersonaVLM).

## 5. 차용 확정 후보 (우선순위순)

| # | 차용 | 출처 | 적용처 |
|---|---|---|---|
| 1 | **FTR(False Trigger Rate) / False-Alarm** 용어·메트릭 | ProactiveMobile, PersonalAlign | score.py의 noop_violation → FTR로 개명, no-op 평가 표준화. 베이스라인 FTR 40~80%는 동기부여 인용 |
| 2 | **cross-track 분리 실험** — WHEN 학습이 HOW에 전이 안 됨을 보여 두 축의 독립성 입증 | FingerTip A.6.2 | 실험 설계 (분석 섹션) |
| 3 | **context ablation** — time 제거 시 최대 하락(7.2→4.1) | FingerTip A.6.3 | 우리 WHEN 축 중요성의 외부 근거 + 로그/이벤트/persona 제거 ablation 템플릿 |
| 4 | **Over/Under-Frequency 분리 채점** | ProPerSim | 빈번도 축 채점 — 과알림/과침묵 양방향 위반 분리 |
| 5 | **차원별 binary 채점이 연속척도보다 안정** (pilot 근거) | ProPerSim | B judge 설계 재검토 — 1~5 홀리스틱 대신 기준별 binary 합산 옵션 |
| 6 | **인간 baseline** (별도 annotator 20명) | FingerTip | 리더보드에 인간 성능 행 추가 |
| 7 | **LLM 전수 스크리닝 → 인간은 플래그만 재검** | FingerTip (프라이버시 검수 구조) | 우리 spot-check 비용 절감 |
| 8 | **합성 로그 realism 통계 검증** (Qscore류) | PersonalAlign | §3 참조 — oracle probe와 세트 |
| 9 | **모델 패널 난이도 분층** (5모델 정답수 L1~L3) | ProactiveMobile | instance 난이도 라벨 — 분석 섹션용 |
| 10 | **temporal/OOD split** (unseen persona/event_type) | FingerTip | 확장(150~200) 시 split 설계 |
| 11 | Best-Match 2단 채점 (동치→F1 fallback) | ProactiveMobile | content 다중 정답 허용 시 |
| 12 | in-situ 평가 용어 | PersonaVLM | 논문 서술용 |

## 6. 인용 정보 정리

- FingerTip 20K — Yang et al. (Tsinghua), **ICLR 2026**, arXiv:2507.21071.
- ProPerSim — Kim et al. (KAIST·SNU), **ICLR 2026**, arXiv:2509.21730.
- PersonalAlign(벤치=AndroidIntent) — Lyu et al. (HIT Shenzhen), **ACL 2026 추정**(GitHub명 기반 — 인용 전 확인), arXiv:2601.09636.
- PersonaVLM — Nie et al. (NJU·ByteDance), **preprint** (venue 미정), arXiv:2604.13074. 관련성 낮음 — "개인화는 하나 proactive 개입 결정은 안 다루는" 대표 예시로만.
- ProactiveMobile — Kong et al. (Xiaomi HyperAI), **CVPR 2026**, pp.27503-27513.
- (기존) KnowU-Bench arXiv:2604.08455 / PrefDisco **ICLR 2026** arXiv:2510.00177.
- ⚠ 용어 주의: "proactive"가 논문마다 다른 뜻 — 질문하기(PrefDisco), 의도 예측(FingerTip·ProactiveMobile), 추천(ProPerSim). 우리 정의(알림 개입의 WHEN·HOW)를 서두에 명시.

## 7. 우리 설계에의 반영 (액션)

- [ ] score.py: noop_violation → **FTR** 개명 + over/under-frequency 분리 지표 추가
- [ ] B judge 설계 시 binary-기준별 채점 옵션 검토 (ProPerSim pilot 근거)
- [ ] 로그 검증 2종 세트: oracle probe + realism 통계 (Phase 2)
- [ ] 실험 설계에 cross-track·context ablation·인간 baseline 반영
- [ ] gt_design §4 검수에 "LLM 스크리닝→플래그 재검" 구조 반영
- [ ] Table 1을 본 문서 §1 기반으로 논문용으로 다듬기
