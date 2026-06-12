# 파일럿 분석 v1 — judge 베이스라인·침묵 calibration 주장 범위·probe 난이도

> 작성: 2026-06-13. 데이터: `data/pilot/` (20 instance × 4 persona).
> ⚠ **데이터 출처**: raw_results.json은 oracle 규칙 agent(--dry) 출력 (708 결정 전수에 rationale 부재, content가 GT와 글자 단위 동일로 확인). 따라서 §1의 B-layer 수치는 gpt-5.5 성능이 아니라 **"완벽한 알림"에 대한 judge 채점 = judge 천장(베이스라인)**이다.
> judge.json↔run 매핑: raw 키 순서 × fire 시간순으로 149행 복원, judge행 time 필드와 149/149 일치 검증 완료.

---

## 1. B-layer 천장 분석 (judge 베이스라인 — gpt-5.5 성능 아님)

### 1.1 기준 × persona 분해 (oracle 입력, n=149 fire)

| 기준 | P_A | P_B | P_C | P_D | 전체 | 실패 n |
|---|---|---|---|---|---|---|
| modality_fit | 0.875 (40) | **1.000** (33) | **0.735** (34) | **1.000** (42) | 0.906 | 14 |
| content_fit | 0.850 | **0.636** | 0.647 | 0.905 | 0.772 | 34 |
| grounded | 0.925 | 0.939 | 0.853 | 0.905 | 0.906 | 14 |
| seq_consistent | 0.975 | 0.970 | 0.971 | 0.976 | 0.973 | 4 |

### 1.2 실패 패턴 분류 (reason 전수 분류 — 66 실패 셀)

| 패턴 | 건수 | 분류 | 근거 |
|---|---|---|---|
| **M1. 채널 어휘 매핑 부재** — judge가 voice ∉ {sound,vibe}로 판정 | modality 14/14 | **judge 입력 결함** (GT 정상) | CHANNELS는 {visual,sound,vibe}, modality 출력은 {popup,vibrate,voice}인데 매핑을 프롬프트에 안 줌. 운전 state(visual=0)에서 GT가 voice를 합성하면 전부 0 처리. P_C(0.735)에 집중된 이유 = 약 persona 루브릭 "약(popup만)"이 popup 불가 state와 충돌 |
| **C1. 깊이 한도 ↔ 강제 요소 모순** — "약=1요소인데 3요소", "강=2~3인데 4~5" | content 34/34 | **루브릭 모호** (GT 정상) | GT_content = 1층강제 ∪ top-k라 강제 요소(변경공지·갱신·즉시출발)가 끼면 k 초과가 정상. 루브릭이 숫자 한도만 줘서 judge가 기대 요소 목록(프롬프트에 있었음!)보다 개수 규칙을 우선함. P_B/P_D(강, 4~5요소)·P_C(약, 3요소) 집중과 정확히 일치 |
| **G1. 도착예정 산식 오해** — judge가 ETA = 현재시각+이동시간으로 재계산 | grounded 13/14 | **judge 입력 결함** (GT 정상) | GT 도착예정 = 안내된 출발시각+이동시간 (R3: user는 안내를 따름, 이동 중 가정). facts에 권장 출발시각·이동중 여부가 없어 judge가 "지금 출발" 가정. C010/C012/C013/C015 전부 이 패턴 |
| **G2. 파생 수치 검증 불가** — "지각 15분이 도구 사실값에 없음" | grounded 1/14 | judge 입력 결함 | R6 "지각 N분"은 (도착예정−약속시각) 파생값인데 facts에 산출 근거 미제공 |
| **S1. delta-awareness 부재** — "지각 5분 위험"→"정시 도착" 전환 설명 없음 | seq 4/4 (전부 C015 t=1015) | **GT 보강 후보** (judge는 룰대로 채점) | 상황 호전(약속 +10 지연으로 지각 해소) 시 GT content에 변화 설명 요소가 없음. R5는 "도착 영향"만 규정 — 직전 안내 대비 delta 명시 규칙이 빠져 있음 |

**judge 환각: 0건.** 모든 실패 reason의 산술은 judge가 받은 입력 기준으로는 정확했다. 천장 미달의 원인은 전부 우리 쪽(루브릭 문구·judge 입력·GT 규칙 1건)이다. → 수정 후 천장 재측정 시 4 기준 모두 ≥0.97 기대.

### 1.3 judge.py 수정안 (구체 문구)

1. **JUDGE_TMPL [상황]에 추가**.
   `- 채널 어휘 매핑: popup→visual, vibrate→vibe, voice→sound. modality 적합성은 이 매핑으로 판정.`
2. **modality_rule 교체**: `"약=최소(popup), 강=가용 채널 풍부하게"` → `"약=가용 채널 중 최소 1개(visual 가용 시 popup, 불가 시 vibrate/voice 중 1개도 적합), 강=가용 채널을 풍부하게"`.
3. **기준 2 교체**: `"persona 깊이에 맞는 요소 수·우선순위인가 (과소·과다 모두 0)"` → `"[기대 요소] 목록과 대조해 채점 — 목록에 있는 요소의 포함은 과다가 아니다. 강제 요소(변경공지·갱신·즉시 출발·취소)는 persona 깊이 한도에 세지 않는다. 과소·과다 판정은 기대 요소 목록 대비로만 한다."`
4. **facts 보강** (judge_run에서 gtd로 산출 가능): `권장 출발시각 {X}, 직전 안내 기준 이동 {중/전}` 추가 + 기준 3에 `"도착예정은 안내된 출발시각+이동시간 기준이다 (현재시각 기준 아님). 지각 N분 = 도착예정−약속시각으로 계산해 검증."`
5. **GT 규칙 R7 신설 검토** (gt.py): 재알림 content에서 직전 안내 대비 핵심 값이 바뀌면(지각↔정시, 출발시각 변경) 변화 요소를 명시 — S1 해소. 강제 요소이므로 깊이 한도 비포함.

수정 후 **judge 천장 재측정(oracle 재채점) → gpt-5.5 실채점** 순서 필수. 천장 미보정 상태의 B 수치는 어떤 모델에 대해서도 보고 불가.

---

## 2. "침묵 calibration 실패" 주장의 가능 범위 (교수 보고용)

기록된 gpt-5.5 A-layer (⚠ raw 유실 — 당시 콘솔 기록): recall 0.964 / precision 0.333 / F1 0.494, critical miss 0, FTR 0.027.

### 주장 가능한 것
- "**놓치지는 않지만 침묵을 못 한다**": recall 0.964 + critical miss 0 (안전) vs precision 0.333 (GT fire 1건당 ~2건 과알림). 방향성은 관련 연구와 정합 — KnowU proactive 실패의 60%가 불필요 개입, PersonalAlign 베이스라인 FA 62~98% (related_work_analysis_v2 §3.2).
- **더 날카로운 버전 (권장)**: FTR 0.027 ↔ precision 0.333의 대비. **빈 상황(no-op instance)에서는 잘 참는데, 약속 맥락 안에서의 미세 침묵(재알림 억제·빈번도 필터)을 못 한다.** 이는 PersonalAlign류 negative-set FA로는 안 보이고 우리 시퀀스 설계에서만 드러나는 실패 모드 — 벤치 존재 이유와 직결.

### 필수 caveat (보고 시 명기)
1. **원자료 유실** — 수치는 당시 실행 기록이며 재현 불가 상태. 풀 파이프라인 재실행으로 재확보 전까지 "예비 관찰"로 한정.
2. 20 instance(core 16) × 1 모델 × 1 실행 — 분산 미측정, pairwise 40%.
3. B-layer는 천장 미보정(content 0.772)이라 인용 불가 — §1 수정 후 재채점.
4. precision 저하의 원인 분해(중복 재알림 vs band 밖 발사 vs 빈번도 필터 위반) 미실시 — raw 재확보 후 duplicates/band 지표로 분해할 것.

---

## 3. Probe 3축 100% — 난이도 완화 후보

원인 진단 (P_A_noise.txt 등 8벌 검토).

- **(P1) 프롬프트가 정답표를 제공**: PROBE_SYS가 축별 판별 규칙("low=업데이트 빨리 dismiss·DnD 사용", "early=40~60분 전 도착")을 그대로 줌 — 추론이 아니라 패턴 lookup. agent 실평가 프롬프트에는 이 힌트가 없으므로 probe 100%는 난이도 증거가 못 됨.
- **(P2) 신호가 수치로 직접 기재**: `event_arrive early_min=43~60` (lead 정답이 평문), `notif_dismiss dwell_s=2` (빈번도 정답이 평문). 계산·결합 불필요.
- **(P3) 신호 과밀**: 신호 비율 76~75% (P_A 53/70 ~ P_D 78/104), 같은 신호가 3주에 5~8회 반복.

후보 (우선순위순).

| # | 조치 | 구현 |
|---|---|---|
| 1 | **probe 2단화**: 힌트 있는 현행 probe = "로그 신호 존재 검증"(합격선 유지), **힌트 없는 probe 추가** = 난이도 측정. 약모델은 후자에서 <90%여야 합격 | probe.py에 PROBE_SYS_BLIND 추가 — 축 이름과 라벨만 주고 판별 규칙 삭제 |
| 2 | **파생 신호화**: `early_min=43` 삭제 → `geo.place_visit 13:17` + 캘린더 일정 14:00을 별도 행으로 — lead는 두 행 결합·계산해야 나옴. `dwell_s=2` → notif_recv 행과 다음 행동 행의 시간차로 | logs.py skeleton 단계 |
| 3 | **신호 밀도 절반**: 축당 증거 이벤트 5~8회 → 2~3회 (oracle probe 합격선 ≥90%은 유지되는지 페어 검증) | logs.py 반복 횟수 파라미터화 |
| 4 | **모순 신호 주입**: persona와 반대 방향 이벤트를 소량(예: early형이 한 번 지각) — "moment intent" 라벨로 (PersonalAlign 3계층 용어, v1 차용) | logs.py noise 풀 확장 |
| 5 | noise 25% 상향은 **보류** — 2·3으로 먼저 떨어뜨리고, 효과 없으면 noise 40% 조건을 ablation 스위치로 | — |

---

## 4. gpt-5.5 실측 결과 (자리 — 재실행 후 기입)

> 선행 조건: §1.3 judge 수정 → oracle 재채점으로 천장 ≥0.97 확인 → 풀 파이프라인 실행(`python3 run_pilot.py`, --dry 금지).
> run_pilot 버그 수정 필요: raw_results.json에 agent 출처(model명) 기록 + `_judge_only`가 raw의 출처를 보고서 헤더에 사용 (현재 AGENT_MODEL을 무조건 찍어 이번 오라벨 사고 발생).

| 지표 | oracle 천장 (재측정) | gpt-5.5 |
|---|---|---|
| A: F1 / precision / recall | — | |
| A: critical_miss / dup / FTR | — | |
| B: modality / content / grounded / seq | | |
| probe(blind): 강 / 약 | | |
