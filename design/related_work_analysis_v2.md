# Related Work 분석 v2 — 2차 면밀 재분석: v1 정정·신규 차용·포지셔닝 보강

> 작성: 2026-06-12. v1(related_work_analysis_v1.md) 이후 7편 전수 재독 (서브에이전트 3, appendix 포함).
> 목적: v1이 놓친 세부(메트릭 수식·judge 프로토콜·limitation·위협) 보완. v1과 중복 내용은 재기술하지 않음 — 두 문서는 세트.

---

## 1. v1 정정사항 (인용 사고 방지 — 논문 집필 전 필수 반영)

| # | v1 주장 | 정정 | 근거 |
|---|---|---|---|
| 1 | FingerTip context ablation = A.6.3, time 제거 7.2→4.1 | **A.6.4** (Table 11). A.6.3은 별개 실험(스크린샷·history 기여, 4.3%는 cold-start 수치 — 4.1과 다른 실험) | FingerTip p.17-18 |
| 2 | FingerTip 프라이버시 검수 "LLM 스크리닝→인간 재검" | 순서가 3단: **인간 1차 제거 → Qwen-VL-Max가 첫/끝 스크린샷만 플래깅 → 인간 재검**. LLM-first가 아님 | FingerTip A.3 p.14 |
| 3 | ProactiveMobile "공개 GUI 데이터" | 4개 소스 중 **약 27%(12,481)는 자체 수집**(MobileAgentBench) | PM Table 1 p.27506 |
| 4 | ProactiveMobile "베이스라인 FTR 40~80%" | 실제 **14~80%**. o1은 평균 14.09%, 텍스트 L1에선 2.73%까지. "일괄 40~80%" 인용은 o1 반례에 깨짐 | PM Table 3 p.27508 |
| 5 | ProPerSim "binary 채점이 연속척도보다 안정 (pilot 근거)" | **무수치 각주 1줄**이 전부 (일치도·표본·비교실험 없음). "pilot 정량 근거"로 인용 금지 — "연속척도가 일관 판정 실패해 binary 전환했다고 보고" 수준으로만 | ProPerSim §4.3 fn.2 p.6 |
| 6 | KnowU "act/ask/silent 3-way" | 평가 지표는 **Act/Silent/Stop 3 rate** — 거절 후 중단(Stop)·post-rejection violation 검사 축을 v1이 누락 | KnowU §4.1 p.7, §3.4 |
| 7 | Best-Match 2단 채점 (ProactiveMobile) | F1 폴백은 **부분점수 아님** — SR은 perfect match 아니면 0, F1은 분석용 최근접 GT 선택에만 사용. 공식 메트릭은 SR(binary)+FTR 둘뿐 | PM §4.2.2 p.27509 |
| 8 | PersonalAlign 데이터 출처 수치 | PersonalAlign은 "91명/60일"로 기재 — 원본 FingerTip "95명/1개월"과 불일치. 인용 시 원본 수치 사용 | PA §4, Table 2 |
| 9 | PrefDisco κ0.463 | **속성 관련성 판정에만** 해당. 루브릭 텍스트·선호값·가중치는 인간 검증 없음 — "검증된 루브릭 프로토콜"로 차용 인용하면 과대 인용 | PD §3 p.6, App.B |

추가: ProactiveMobile PDF는 **본문 11p만** — judge 프롬프트·98% 합의 표본 크기·context ablation은 supplementary 별도 입수 필요.

---

## 2. 신규 차용 후보 (v1 §5에 추가 — 우선순위순)

| # | 차용 | 출처 | 적용처 |
|---|---|---|---|
| A1 | **FTR 정확 정의**: `FTR = N_ft / N_no-action` — 분모가 **GT=∅ 인스턴스만** | PM §4.2.1 | score.py FTR 구현·논문 정의를 이것과 정합(또는 차이 명시) |
| A2 | **출력포맷 ablation 결과**: Function만 SR 9.18/FTR 93.16 → 자연어 추천 동반 SR 20.82/FTR 13.76 → Think 추가 FTR 2.06/SR 8.02. **자연어 의도 동시 생성이 restraint 학습에 필수 + SR-safety 트레이드오프** | PM Table 5 §4.5 | 우리 agent 출력 스키마에 rationale 텍스트 의무화 정당화 + C-layer 트레이드오프 곡선 보고 |
| A3 | **λ-가중 하이브리드 점수식**: `S = λ·S_rule + (1−λ)·S_llm`, λ=과제별 preference 의존도 비례 | KnowU §3.4 | A/B-layer 합산 정식화 선례 |
| A4 | **Baseline/Oracle 이중 anchor 정규화**: NormAlign = 100×(Discovery−Baseline)/(Oracle−Baseline). persona 미제공=baseline, persona 명시 제공=oracle | PrefDisco Eq.2 | B-layer 개인화 점수 정규화 — log 추론 gain을 모델 간 비교 가능하게. **oracle-persona 조건이 이미 실험 매트릭스에 있으므로 비용 0** |
| A5 | **judge에 집계치 명시 공급**: fire 횟수·간격을 사전 계산해 프롬프트 입력 (judge가 세지 않게) | ProPerSim Table 12 | B-layer 시퀀스 일관성·중복 판정 — A-layer 산출물 재사용 |
| A6 | **top-k 평가의 정량 근거**: 분포 출력+top-3 채점 시 SR 7.2→11.1 | FingerTip A.6.5 | content top-k 채점 인용 근거 |
| A7 | **메트릭↔인간 평점 정렬 검증**: 모델 출력+GT를 인간 5점 평가시켜 자동 지표와 단조성 확인 (그들은 상관계수 미보고 — 우리가 보고하면 우위) | FingerTip A.6.6 | A-layer 점수·B judge 타당성 검증 실험 템플릿 |
| A8 | **루브릭 객관화 지시**: "few/late 같은 표현 금지, 수치로 기술" + 차원 간 모순 금지. 단 **가중치 분산은 프롬프트 지시로 실패**(PrefDisco 예시 importance 4~5 쏠림) → 우리는 규칙 테이블에서 결정론 부여 | ProPerSim Table 7, PD App.F | B judge 루브릭 생성. 생성 모델↔judge 모델 분리 명시(PD는 겹침 — 우리가 한 수 위) |
| A9 | **MTurk 353명 기준(규칙) 검증**: 인간이 instance가 아니라 평가 기준을 검증, 50% 미만 지지 기준 제거 | ProPerSim App.B.1 | "규칙 검수" 프로토콜의 직접 선례 인용 |
| A10 | **2.5× 스텝 자동 실패 상한** + IE = S/max(ask횟수,1) | FingerTip §5.1, KnowU §4.1 | 중복 알림 상한·intrusiveness 정규화 형태 참고 |
| A11 | **누설 점검 프로토콜**: retrieval된 유사 항목이 "같은 task"인지 LLM 판별 후 제외 재실험 | FingerTip A.6.7 | skeleton→GT 누설 점검 (로그가 답을 직접 노출하는지) |
| A12 | **Qscore 정확 사양**: 정규화(1·Scos + 0.1·ΔHt + 0.1·ΔHs), top-k=10, Qwen3-Embedding, 가중치 견고성 검증 포함 | PA Eq.2-4, A.2 | realism 검증(v1 차용 8번)의 구현 사양 확정 |
| A13 | **FA 실측 정의**: negative 100 state 중 fire 비율 (수치 역산 검증 완료). 출처는 ProactiveAgent(Lu et al. 2025b) | PA §6.1 Table 4 | 우리 FTR과의 정의 비교표 |
| A14 | **OOD split 선례**: 2개 시나리오 64 instance held-out | PM §4.4 | 확장 시 unseen 시나리오/persona split (v1 차용 10번 보강) |

---

## 3. 포지셔닝 업데이트 (v1 §2 보강)

### 3.1 차별화 축의 재확인 — 그러나 서술은 좁혀야 함

- **WHEN(분 단위 band)·HOW(modality/content)·멀티 trigger 시퀀스·동적 이벤트 GT 갱신**: 7편 전부 부재 재확인. ProactiveMobile·KnowU는 **한계로조차 언급 안 함** — "시간 차원이 제거된 스냅샷 과제"로 정면 서술 가능.
- 단, **개별 요소는 부분 선점**이 확인됨. 기여 서술을 "결정 여부(fire/silent)"가 아니라 "**결정의 시간·채널·시퀀스 정밀도 + 결정론 규칙 GT**"로 좁혀 쓸 것.
  - fire/silent binary 평가: PersonalAlign이 이미 함 (negative 100 + FA). KnowU도 persona-conditional fire/silent + 거절 후 restraint 점유.
  - no-op/FTR: ProactiveMobile 선점.
  - 시간 tick 기반 proactivity: ProPerSim이 동일 계열 (단 LLM judge GT, 온라인 적응 과제 — 결정론 band 없음).

### 3.2 "선행 논문이 남긴 빈칸" 인용 세트 (서론·related work용)

| 논문 | 그들이 남긴 빈칸 | 우리 해소 |
|---|---|---|
| PersonalAlign App.C.2/C.3 | Proactive Triggering (T't,S't) 수식 정의했으나 **미평가** — "online 환경+User Agent 필요해 future work". 판단 신호도 시간+scenario 2개뿐, 동적 이벤트는 future work | 우리가 정확히 이 빈칸의 최초 벤치마크화. **미인용 시 "이미 제안된 아이디어" 공격 위험 — 반드시 인용** |
| PersonalAlign App.A.3 | 온라인 평가 불가(ADB·자동판정·재현성) → 오프라인 golden trajectory만 | 결정론 GT+시뮬레이션 시퀀스가 재현성·자동채점 해소 |
| FingerTip A.1 | 실로그 재식별 위험 자인, **"synthetic replay 탐색 필요" 직접 권고** | 우리 프로그램 합성이 그들이 권고한 방향의 구현 |
| PersonalAlign §4.3 | 실로그 마이닝 가능한 routine이 **인당 3~5건뿐** | "실로그만으론 trigger 벤치 규모 불가" — 합성 정당화 |
| ProPerSim §6.4 | worst persona(2.5점)가 **시간창 조건부 선호** 때문에 실패 + persona당 A100 10일+$30 비용 | 타이밍 개인화가 가장 어렵다는 외부 증거 + 결정론 GT의 비용 우위 |
| PrefDisco §5 | 210개 조합 중 **29.0%가 음수 NormAlign** (어설픈 개인화 < generic) | "개인화는 자연 발생하지 않는다" — 전용 벤치 동기 |
| PersonalAlign Table 4 | 베이스라인 FA: 대부분 모델 92~98% (무조건 fire 붕괴), GPT-5.1도 62% | silent restraint가 현 모델에 매우 어렵다는 동기 인용 |
| KnowU §4.4 Fig.5 | proactive 실패의 60%가 Intervention(불필요 개입), Passive는 20% — **과잉 발사가 3배** | intrusiveness 계열 메트릭 동기 |

### 3.3 신규 위협 (v1에 없음 — 후속 조치 필요)

1. **PIRA-Bench** (Chai et al., 2026.3) — GUI 기반 proactive intent recommendation. KnowU §2.2가 인용.
2. **Pare** (Nathani et al., arXiv:2604.00842) — "Simulating Active Users to Evaluate Proactive Assistants". rule-based 평가 + user simulator. **제목만으로 우리와 가장 가까울 수 있음 — 정독 필수.**
3. ProactiveMobile supplementary 미입수 (judge 프롬프트·98% 표본·context ablation).
4. PersonaVLM의 동적 persona(drift): 우리 정적 persona 가정에 리뷰 가능 — "시퀀스 7~13 trigger는 단기간이라 drift 무시 가능" 방어 준비.
5. PersonaVLM 2,034건 검수가 40 person-hours: "instance 검수도 싸다" 반론 가능 — 규칙 검수의 우위는 비용이 아니라 **일관성·확장성(규칙 수정→전체 재합성)**으로 논증할 것.

### 3.4 방어 준비 (리뷰 예상 공격)

- "텍스트 로그는 쉬운 모달리티": ProactiveMobile에서 text가 multimodal보다 일관되게 높음 (26.04 vs 15.61). 그들 해석("시각 grounding 병목이지 추론 난이도 차이 아님")을 인용해 우리 과제의 난이도는 모달리티가 아니라 **시간 추론**에 있음을 선제 서술.
- "GT 다양성 부족(one GT per instance)": ProactiveMobile은 1~3개 multi-GT. 우리는 결정론 GT이므로 "다양성은 LLM 합의의 부산물, 우리는 band(±7.5)·top-k가 허용 폭을 구조적으로 정의"로 대응.
- "judge 의존": ProactiveMobile도 SR 판정에 Gemini referee 필요하면서 "objective evaluation" 표방 — 우리 A-layer는 judge 0으로 완전 결정론임을 찌를 것.

---

## 4. 우리 설계 반영 액션 (v1 §7 대체 — 통합 갱신)

- [ ] **score.py**: FTR 분모를 PM 정의(GT=∅ pool)와 정합 + over/under-frequency 분리 (v1) + 2.5×류 중복 상한 검토 (A10)
- [ ] **agent 출력 스키마**: rationale 자연어 의무 포함 (A2 근거)
- [ ] **B judge**: 기준별 binary (인용 수위는 §1-5 정정대로) + 집계치 사전 공급 (A5) + 루브릭 수치 앵커·가중치 규칙 부여 (A8) + 생성/judge 모델 분리 명시
- [ ] **실험 매트릭스**: oracle-persona 조건을 NormAlign anchor로 활용 (A4) — 추가 비용 0
- [ ] **검증 실험**: judge↔인간 (v1) + 메트릭↔인간 정렬 (A7) + 누설 점검 (A11) + realism Qscore (A12, 사양 확정)
- [ ] **binary vs 연속 judge 비교 실험**을 우리 부록에 추가 검토 — ProPerSim 각주가 무수치이므로 우리가 정량 근거 제공 시 기여
- [ ] **신규 논문 2편 입수·정독**: PIRA-Bench, Pare(arXiv:2604.00842) + ProactiveMobile supplementary
- [ ] **Table 1 (비교표)**: KnowU Table 1(제3자 분류: PM=User Logs ✗, FingerTip=User Model ✗)과 교차 검증
- [ ] **related work 용어 구분 문단**: PrefDisco proactive=in-conversation elicitation, ProPerSim=온라인 적응, 우리=unprompted intervention timing

---

## 5. 인용 정보 추가·정정

- PersonalAlign FA 메트릭의 원출처: **ProactiveAgent (Lu et al. 2025b)** — 원문 확인 후 직접 인용 검토.
- Pare: Nathani et al., arXiv:2604.00842.
- v1 §6의 venue 정보는 유지. PersonalAlign 데이터 수치는 원본 FingerTip(95명/1개월) 기준으로 통일.
