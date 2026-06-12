# Sanity 합성 출력 — 10 instance × 4 persona

초기값: B_early=30, B_late=10, prep=10, band=±7.5

## 변별력 요약 (instance별 persona 간 서로 다른 GT 시퀀스 수)

| instance | 고유 시퀀스 수/4 | 비고 |
|---|---|---|
| I01 | 4 |  |
| I02 | 4 |  |
| I03 | 4 |  |
| I04 | 4 |  |
| I05 | 4 |  |
| I06 | 4 |  |
| I07 | 4 |  |
| I08 | 4 |  |
| I09 | 1 | no-op 동일 정상 |
| I10 | 1 | no-op 동일 정상 |

## I01 — KTX·익숙 | 비(후)+상대지연10+KTX지연20+통화 (공통시나리오 유사)

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:00 | grid | silent |   (이르다) |
| 15:15 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup]  (발사창 15:20±7.5) |
| 15:30 | grid | silent |   (이미 동일 plan 안내) |
| 15:45 | grid | silent |   (이미 동일 plan 안내) |
| 15:50 | event | silent |   (미세(Δ5) + 이동 중) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 도착예정 16:55 vs 약속 17:10 | 우산  [popup]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:20 | event/통화 | silent |   (state→통화(20분)) |
| 16:30 | grid/통화 | silent |   (이동 중 (override2)) |
| 16:35 | event/통화 | **fire** | transit_delay 갱신 | 도착예정 17:15 vs 약속 17:10 | 우산  [popup]  (승격(Δ20>7.5) — persona 무관) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 3

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup,vibrate,voice]  (발사창 15:40±7.5) |
| 15:50 | event | silent |   (미세(Δ5) + 이동 중) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 도착예정 16:55 vs 약속 17:10 | 우산  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:20 | event/통화 | silent |   (state→통화(20분)) |
| 16:30 | grid/통화 | silent |   (이동 중 (override2)) |
| 16:35 | event/통화 | **fire** | transit_delay 갱신 | 도착예정 17:15 vs 약속 17:10 | 우산 | 경로/수단(익숙도 해제)  [popup,vibrate]  (승격(Δ20>7.5) — persona 무관) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 3

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup]  (발사창 15:40±7.5) |
| 15:50 | event | silent |   (미세(Δ5) + 이동 중) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 도착예정 16:55 vs 약속 17:10 | 우산  [popup]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:20 | event/통화 | silent |   (state→통화(20분)) |
| 16:30 | grid/통화 | silent |   (이동 중 (override2)) |
| 16:35 | event/통화 | **fire** | transit_delay 갱신 | 도착예정 17:15 vs 약속 17:10 | 우산  [popup]  (승격(Δ20>7.5) — persona 무관) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 3

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:00 | grid | silent |   (이르다) |
| 15:15 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup,vibrate,voice]  (발사창 15:20±7.5) |
| 15:30 | grid | silent |   (이미 동일 plan 안내) |
| 15:45 | grid | silent |   (이미 동일 plan 안내) |
| 15:50 | event | silent |   (미세(Δ5) + 이동 중) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 도착예정 16:55 vs 약속 17:10 | 우산  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:20 | event/통화 | silent |   (state→통화(20분)) |
| 16:30 | grid/통화 | silent |   (이동 중 (override2)) |
| 16:35 | event/통화 | **fire** | transit_delay 갱신 | 도착예정 17:15 vs 약속 17:10 | 우산 | 경로/수단(익숙도 해제)  [popup,vibrate]  (승격(Δ20>7.5) — persona 무관) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 3

## I02 — 지하철·낯섦 | 교통+5(미세)만

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 16:20 | 경로/수단  [popup]  (발사창 15:50±7.5) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:10 | event | silent |   (미세(Δ5) — 빈번도 적) |
| 16:15 | grid | silent |   (이르다) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | silent |   (이르다) |
| 16:10 | event | **fire** | 약속명/시각 | 출발 16:15 | 경로/수단 | 출구  [popup,vibrate,voice]  (첫 알림 (이벤트 trigger에서 창 도달)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | silent |   (이르다) |
| 16:10 | event | **fire** | 약속명/시각 | 출발 16:15 | 경로/수단  [popup]  (첫 알림 (이벤트 trigger에서 창 도달)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 16:20 | 경로/수단 | 출구  [popup,vibrate,voice]  (발사창 15:50±7.5) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:10 | event | **fire** | transit_delay 업데이트 | 출발 16:15 | 경로/수단 | 출구  [popup,vibrate,voice]  (미세(Δ5) — 빈번도 많) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

## I03 — 근거리도보·익숙 | 비(전, 도보→승격)+회의

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 15:50 | event | **fire** | 약속명/시각 | 출발 16:25 | 우산  [popup]  (첫 알림 (이벤트 trigger에서 창 도달)) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:15 | grid | silent |   (이미 동일 plan 안내) |
| 16:20 | event/회의 | silent |   (state→회의(30분)) |
| 16:30 | grid/회의 | silent |   (이동 중 (override2)) |
| 16:45 | grid/회의 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 15:50 | event | silent |   (이르다 (첫 알림 전, 이벤트 흡수)) |
| 16:00 | grid | silent |   (이르다) |
| 16:15 | grid | **fire** | 약속명/시각 | 출발 16:25 | 우산  [popup,vibrate,voice]  (발사창 16:15±7.5) |
| 16:20 | event/회의 | silent |   (state→회의(30분)) |
| 16:30 | grid/회의 | silent |   (이동 중 (override2)) |
| 16:45 | grid/회의 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 15:50 | event | silent |   (이르다 (첫 알림 전, 이벤트 흡수)) |
| 16:00 | grid | silent |   (이르다) |
| 16:15 | grid | **fire** | 약속명/시각 | 출발 16:25 | 우산  [popup]  (발사창 16:15±7.5) |
| 16:20 | event/회의 | silent |   (state→회의(30분)) |
| 16:30 | grid/회의 | silent |   (이동 중 (override2)) |
| 16:45 | grid/회의 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 15:50 | event | **fire** | 약속명/시각 | 출발 16:25 | 우산  [popup,vibrate,voice]  (첫 알림 (이벤트 trigger에서 창 도달)) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:15 | grid | silent |   (이미 동일 plan 안내) |
| 16:20 | event/회의 | silent |   (state→회의(30분)) |
| 16:30 | grid/회의 | silent |   (이동 중 (override2)) |
| 16:45 | grid/회의 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

## I04 — KTX·낯섦 | 위험기상(강제+20)

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:00 | grid | silent |   (이르다) |
| 15:15 | grid | **fire** | 약속명/시각 | 출발 15:50 | 경로/수단  [popup]  (발사창 15:20±7.5) |
| 15:30 | grid | silent |   (이미 동일 plan 안내) |
| 15:45 | grid+event | **fire** | weather_severe 변경공지 | 새 출발 15:30 | 경로/수단  [popup]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid+event | **fire** | weather_severe 변경공지 | 새 출발 15:30 | 경로/수단 | 출구 | 우산  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid+event | **fire** | weather_severe 변경공지 | 새 출발 15:30 | 경로/수단  [popup]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:00 | grid | silent |   (이르다) |
| 15:15 | grid | **fire** | 약속명/시각 | 출발 15:50 | 경로/수단 | 출구  [popup,vibrate,voice]  (발사창 15:20±7.5) |
| 15:30 | grid | silent |   (이미 동일 plan 안내) |
| 15:45 | grid+event | **fire** | weather_severe 변경공지 | 새 출발 15:30 | 경로/수단 | 출구 | 우산  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

## I05 — 지하철·익숙 | 상대 취소(중반)

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 16:20  [popup]  (발사창 15:50±7.5) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:10 | event | **fire** | 취소 공지  [popup]  (override1: 취소 — 이후 전부 silent) |
| 16:15 | grid | silent |  |
| 16:30 | grid | silent |  |
| 16:45 | grid | silent |  |
| 17:00 | grid | silent |  |

발사 횟수: 2

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | silent |   (이르다) |
| 16:10 | event | **fire** | 취소 공지  [popup,vibrate,voice]  (override1: 취소 — 이후 전부 silent) |
| 16:15 | grid | silent |  |
| 16:30 | grid | silent |  |
| 16:45 | grid | silent |  |
| 17:00 | grid | silent |  |

발사 횟수: 1

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | silent |   (이르다) |
| 16:10 | event | **fire** | 취소 공지  [popup]  (override1: 취소 — 이후 전부 silent) |
| 16:15 | grid | silent |  |
| 16:30 | grid | silent |  |
| 16:45 | grid | silent |  |
| 17:00 | grid | silent |  |

발사 횟수: 1

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 16:20  [popup,vibrate,voice]  (발사창 15:50±7.5) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:10 | event | **fire** | 취소 공지  [popup,vibrate,voice]  (override1: 취소 — 이후 전부 silent) |
| 16:15 | grid | silent |  |
| 16:30 | grid | silent |  |
| 16:45 | grid | silent |  |
| 17:00 | grid | silent |  |

발사 횟수: 2

## I06 — 지하철·낯섦 | 장소변경(+15)+운전

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 16:20 | 경로/수단  [popup]  (발사창 15:50±7.5) |
| 15:55 | event | **fire** | cp_move 변경공지 | 새 출발 16:05 | 경로/수단  [popup]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:15 | grid+event/운전 | silent |   (이동 중 (override2)) |
| 16:30 | grid/운전 | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 15:55 | event | **fire** | cp_move 변경공지 | 새 출발 16:05 | 경로/수단 | 출구  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:15 | grid+event/운전 | silent |   (이동 중 (override2)) |
| 16:30 | grid/운전 | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 15:55 | event | **fire** | cp_move 변경공지 | 새 출발 16:05 | 경로/수단  [popup]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:15 | grid+event/운전 | silent |   (이동 중 (override2)) |
| 16:30 | grid/운전 | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 1

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 16:20 | 경로/수단 | 출구  [popup,vibrate,voice]  (발사창 15:50±7.5) |
| 15:55 | event | **fire** | cp_move 변경공지 | 새 출발 16:05 | 경로/수단 | 출구  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이미 동일 plan 안내) |
| 16:15 | grid+event/운전 | silent |   (이동 중 (override2)) |
| 16:30 | grid/운전 | silent |   (이동 중 (override2)) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

## I07 — KTX·익숙 | 상대지연60+교통+5

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:00 | grid | silent |   (이르다) |
| 15:15 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup]  (발사창 15:20±7.5) |
| 15:30 | grid | silent |   (이미 동일 plan 안내) |
| 15:45 | grid | silent |   (이미 동일 plan 안내) |
| 15:55 | event | **fire** | cp_delay 변경공지 | 도착예정 16:50 vs 약속 18:00  [popup]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid+event | silent |   (미세(Δ5) + 이동 중) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |
| 17:15 | grid | silent |   (이동 중 (override2)) |
| 17:30 | grid | silent |   (이동 중 (override2)) |
| 17:45 | grid | silent |   (이동 중 (override2)) |
| 18:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup,vibrate,voice]  (발사창 15:40±7.5) |
| 15:55 | event | **fire** | cp_delay 변경공지 | 도착예정 16:50 vs 약속 18:00  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid+event | silent |   (미세(Δ5) + 이동 중) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |
| 17:15 | grid | silent |   (이동 중 (override2)) |
| 17:30 | grid | silent |   (이동 중 (override2)) |
| 17:45 | grid | silent |   (이동 중 (override2)) |
| 18:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup]  (발사창 15:40±7.5) |
| 15:55 | event | **fire** | cp_delay 변경공지 | 도착예정 16:50 vs 약속 18:00  [popup]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid+event | silent |   (미세(Δ5) + 이동 중) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |
| 17:15 | grid | silent |   (이동 중 (override2)) |
| 17:30 | grid | silent |   (이동 중 (override2)) |
| 17:45 | grid | silent |   (이동 중 (override2)) |
| 18:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:00 | grid | silent |   (이르다) |
| 15:15 | grid | **fire** | 약속명/시각 | 출발 15:50  [popup,vibrate,voice]  (발사창 15:20±7.5) |
| 15:30 | grid | silent |   (이미 동일 plan 안내) |
| 15:45 | grid | silent |   (이미 동일 plan 안내) |
| 15:55 | event | **fire** | cp_delay 변경공지 | 도착예정 16:50 vs 약속 18:00  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:00 | grid | silent |   (이동 중 (override2)) |
| 16:15 | grid | silent |   (이동 중 (override2)) |
| 16:30 | grid+event | silent |   (미세(Δ5) + 이동 중) |
| 16:45 | grid | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |
| 17:15 | grid | silent |   (이동 중 (override2)) |
| 17:30 | grid | silent |   (이동 중 (override2)) |
| 17:45 | grid | silent |   (이동 중 (override2)) |
| 18:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

## I08 — 근거리도보·낯섦 | 비(후)+상대지연10+통화

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | **fire** | 약속명/시각 | 출발 16:35 | 경로/수단  [popup]  (발사창 16:05±7.5) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 새 출발 16:45 | 경로/수단  [popup]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이미 동일 plan 안내) |
| 16:25 | event | **fire** | weather_rain 갱신 | 새 출발 16:35 | 경로/수단  [popup]  (승격(Δ10>7.5) — persona 무관) |
| 16:30 | grid | silent |   (이미 동일 plan 안내) |
| 16:40 | event/통화 | silent |   (state→통화(15분)) |
| 16:45 | grid/통화 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 3

### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | silent |   (이르다) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 새 출발 16:45 | 경로/수단 | 출구  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이미 동일 plan 안내) |
| 16:25 | event | **fire** | weather_rain 갱신 | 새 출발 16:35 | 경로/수단 | 출구 | 우산  [popup,vibrate,voice]  (승격(Δ10>7.5) — persona 무관) |
| 16:30 | grid | silent |   (이미 동일 plan 안내) |
| 16:40 | event/통화 | silent |   (state→통화(15분)) |
| 16:45 | grid/통화 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | silent |   (이르다) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 새 출발 16:45 | 경로/수단  [popup]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이미 동일 plan 안내) |
| 16:25 | event | **fire** | weather_rain 갱신 | 새 출발 16:35 | 경로/수단  [popup]  (승격(Δ10>7.5) — persona 무관) |
| 16:30 | grid | silent |   (이미 동일 plan 안내) |
| 16:40 | event/통화 | silent |   (state→통화(15분)) |
| 16:45 | grid/통화 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 2

### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent |   (이르다) |
| 15:45 | grid | silent |   (이르다) |
| 16:00 | grid | **fire** | 약속명/시각 | 출발 16:35 | 경로/수단 | 출구  [popup,vibrate,voice]  (발사창 16:05±7.5) |
| 16:05 | event | **fire** | cp_delay 변경공지 | 새 출발 16:45 | 경로/수단 | 출구  [popup,vibrate,voice]  (override3: 1층 강제) |
| 16:15 | grid | silent |   (이미 동일 plan 안내) |
| 16:25 | event | **fire** | weather_rain 갱신 | 새 출발 16:35 | 경로/수단 | 출구 | 우산  [popup,vibrate,voice]  (승격(Δ10>7.5) — persona 무관) |
| 16:30 | grid | silent |   (이미 동일 plan 안내) |
| 16:40 | event/통화 | silent |   (state→통화(15분)) |
| 16:45 | grid/통화 | silent |   (이동 중 (override2)) |
| 17:00 | grid | silent |   (이동 중 (override2)) |

발사 횟수: 3

## I09 — no-op | 약속 없음

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



## I10 — no-op | 약속 오전 완료

### P_A 윤서 (빈번 적/정도 약/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



### P_B 도현 (빈번 적/정도 강/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



### P_C 하은 (빈번 많/정도 약/lead 임박)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



### P_D 지훈 (빈번 많/정도 강/lead 미리)

| 시각 | 종류 | 결정 | 내용/메모 |
|---|---|---|---|
| 15:30 | grid | silent | no-op (약속 없음/완료) |
| 15:45 | grid | silent | no-op (약속 없음/완료) |
| 16:00 | grid | silent | no-op (약속 없음/완료) |
| 16:15 | grid | silent | no-op (약속 없음/완료) |
| 16:30 | grid | silent | no-op (약속 없음/완료) |
| 16:45 | grid | silent | no-op (약속 없음/완료) |
| 17:00 | grid | silent | no-op (약속 없음/완료) |



