# Persona 확정 v1 — 4종 벡터·lead 배정·로그 신호 행동화

> 작성: 2026-06-11. 전제: handoff v5 §1 (2축), gt_design_v1 §3 (persona 마스크), design_review P2-8 (confound).

---

## 1. 4 Persona 확정

| ID | 이름 | 빈번도 | 정도 | lead | 한 줄 캐릭터 |
|---|---|---|---|---|---|
| P_A | 윤서 | 적 | 약 | **미리** | 조용한 미니멀리스트 — 꼭 필요한 것만, 일찍 한 번 |
| P_B | 도현 | 적 | 강 | **임박** | 한 방에 풍부하게 — 닥쳐서 받되 전부 담아서 |
| P_C | 하은 | 많 | 약 | **임박** | 가볍게 자주 — 짧은 popup으로 계속 업데이트 |
| P_D | 지훈 | 많 | 강 | **미리** | 풀 서비스 — 일찍부터, 바뀔 때마다, 풍부하게 |

### lead 배정 근거 (confound 해소)
- 미리 = {P_A, P_D}, 임박 = {P_B, P_C} → 빈번도 양 레벨·정도 양 레벨 각각에 미리/임박 1:1. 어느 축과도 정렬되지 않는 균형 배정 (design_review P2-8 counterbalance 충족).

### GT 파라미터 매핑 (gt_design §1·§2 입력)

| 파라미터 | P_A 윤서 | P_B 도현 | P_C 하은 | P_D 지훈 |
|---|---|---|---|---|
| buffer | B_early=30분* | B_late=10분* | B_late=10분* | B_early=30분* |
| 미세변동 재알림 (override 4) | silent | silent | fire | fire |
| modality (가용 채널 내) | 최소 popup | 풍부 (진동·음성 포함) | 최소 popup | 풍부 |
| content k | 1 | 2~3 | 1 | 2~3 |
| 수집 깊이 (rationale 기대) | 얕음 (history 위주) | 깊음 (maps·weather 조회) | 얕음 | 깊음 |

\* 초기값. 샘플 10개 수동 합성(sanity)에서 확정. prep=10분 공통 초기값.

---

## 2. 로그 신호 명세 (행동화 — 설정 줄 의존 제거)

### 결정: `Settings notif_config` 1줄 신호 **제거**
- 사유: 설정 1줄 = lookup이지 추론이 아님 (design_review P0-2). 아래 행동 패턴으로 대체.
- fallback: oracle probe(§3)에서 빈번도 축 복원률이 기준 미달이면 간접 설정(예: 특정 앱 알림 끔 이력)을 약한 신호로 재도입.

### 축별 행동 신호 (event_type 로그에 심는 패턴)

| 축 | 레벨 | 신호 패턴 (로그 entry 유형) |
|---|---|---|
| 빈번도 | 적 | 업데이트성 `notif_post` → `notif_dismiss` <3초 반복 (주 수회) / 저녁 시간대 `dnd_on` 규칙적 / 배지 누적 방치 |
| | 많 | 업데이트성 `notif_post` → `notif_tap` 열람 / `notif_center_open` 빈번 / 날씨·교통 위젯 `widget_refresh` |
| 정도 | 약 | 알림 모드 무음·popup 유지 이력 / `route_search` 기본 결과에서 종료 / Weather `app_open` 희박 |
| | 강 | 진동+소리 모드 사용 / `route_search` → 출구·대안경로 하위 조회 연쇄 / Weather·Maps `app_open` 빈번 / 음성 안내 사용 이력 |
| lead | 미리 | 약속별 `event_arrive` − 약속시각 = 40~60분 전 패턴 (로그 내 복수 약속 일관) / 전날·아침 캘린더 `app_open` |
| | 임박 | `event_arrive` 5~10분 전 또는 정시 / 출발 직전 `route_search` |
| 익숙도 (instance 변인) | — | 익숙 목적지 풀 3~5곳 × 방문 N회 (template_matrix §4) |

- 형식은 handoff §7 그대로 — `time / app / location / event_type / params` + 숨김 `{label, category}`, noise 25%.
- 신호 밀도 초기값: 축당 8~12 entry (로그 전체 4~6주 분량). oracle probe 결과로 조정.

### 생성 방식: 하이브리드 (2026-06-12 확정)
1. **프로그램 = 신호 계획(skeleton)** — 축별 신호 종류·개수·날짜·시간대 결정 (밀도 제어 + GT 정합 보장. `trigger_bench/logs.py`가 이 단계)
2. **LLM = 표면 렌더링** — slot별 앱·장소·params 변주 + noise 이벤트 다양화 (현실감. Phase 2)
3. **rule validator = 사후 검증** — 스키마·신호 보존 확인, 위반 entry만 재생성
- 검증 2종 세트: oracle probe(복원률) + realism 통계(PersonalAlign Qscore류, 실데이터와 분포 비교).

---

## 3. 검증 게이트 (로그 생성 직후, design_review P0-2)

```
oracle probe: 강 LLM(2종)에 로그만 제공 → 2축+lead 3분류 과제
통과 기준(초기): 강 모델 복원 정확도 ≥ 90% (축별), 미달 축은 신호 밀도 증강 후 재생성
보조 보고: 약 모델과의 복원률 격차 (변별력 근거)
```

---

## 4. Open Items

- [ ] B_early/B_late/prep — sanity 합성에서 확정 (그리드상 미리/임박 fire가 다른 grid에 떨어지는지 확인)
- [ ] 신호 밀도(축당 entry 수)·로그 총 길이 — oracle probe로 튜닝
- [ ] event_type 어휘 사전 (notif_post/dismiss/tap, app_open, route_search, event_arrive, dnd_on …) — 로그 생성기 구현 시 확정
- [ ] persona 이름·시나리오 배경(거주지·직업 등 표면 속성) — 로그 생성 프롬프트 작성 시
