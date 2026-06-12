# 파일럿 결과 v1 — oracle(dry), 20 instance × 4 persona

- pairwise coverage: 40%
- 로그: 8벌 (렌더링 생략)

## Oracle probe (로그→persona 축 복원률)


## A-layer (rule)

- precision: 1.0
- recall: 1.0
- f1: 1.0
- critical_miss_rate: 0.0
- duplicates: 0
- noop_violations: 0
- ftr: 0.0
- decisions: 708

## 해석 가이드
- oracle 규칙 agent는 F1 1.0이 정상 (스모크로 검증됨).
- FTR = no-op instance 오발사율. critical_miss = 1층 강제 누락.
- probe: 강 모델 ≥90%가 로그 합격선 (personas_v1 §3).
