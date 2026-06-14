# 파일럿 결과 v1 — gpt-5.5, 5 instance × 4 persona

- pairwise coverage: (judge-only 재실행)
- 로그: 8벌 (렌더링 생략)

## Oracle probe (로그→persona 축 복원률)

- gpt-5.5: {'frequency': 1.0, 'depth': 1.0, 'lead': 1.0}
- gpt-5-mini: {'frequency': 1.0, 'depth': 1.0, 'lead': 0.875}

## A-layer (rule)

- precision: 0.245
- recall: 0.893
- f1: 0.385
- critical_miss_rate: 0.0
- duplicates: 0
- noop_violations: 1
- ftr: 0.036
- decisions: 176

## B-layer (judge, fire별 binary 기준)

- modality_fit: 0.99
- content_fit: 0.069
- grounded: 0.255
- seq_consistent: 0.725
- judged_fires: 102

## 해석 가이드
- oracle 규칙 agent는 F1 1.0이 정상 (스모크로 검증됨).
- FTR = no-op instance 오발사율. critical_miss = 1층 강제 누락.
- probe: 강 모델 ≥90%가 로그 합격선 (personas_v1 §3).
