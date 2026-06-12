#!/usr/bin/env bash
# trigger_bench 원격 실행용 conda 환경 세팅 스크립트
set -e

ENV_NAME=${1:-trigger_bench}

# 1) conda 환경 생성 (이미 있으면 재사용)
if conda env list | grep -q "^${ENV_NAME} "; then
    echo "[setup] conda env '${ENV_NAME}' 이미 존재 — 재사용"
else
    conda create -y -n "${ENV_NAME}" python=3.11
fi

# 2) 의존성 설치
conda run -n "${ENV_NAME}" pip install -r "$(dirname "$0")/requirements.txt"

# 3) .env 확인 (repo 루트 — 이 스크립트 기준 2단계 위)
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
if [ -f "${ROOT}/.env" ] && grep -q "OPENAI_API_KEY=" "${ROOT}/.env"; then
    echo "[setup] .env OK (${ROOT}/.env)"
else
    echo "[setup] ⚠ ${ROOT}/.env 에 OPENAI_API_KEY=sk-... 를 추가하세요"
fi

echo "[setup] 완료. 실행:"
echo "  conda activate ${ENV_NAME}"
echo "  cd $(dirname "$0") && python run_pilot.py"
