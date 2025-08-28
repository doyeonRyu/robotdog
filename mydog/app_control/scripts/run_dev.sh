#!/usr/bin/env bash
# 개발용 스크립트 *vilib 설치된 파이썬으로 실행
set -euo pipefail

# 사용할 파이썬: 기본 /usr/bin/python3 (라즈베리파이에 vilib 설치됨)
PY_BIN="${APP_PYTHON:-/usr/bin/python3}"
echo "[dev] using python: ${PY_BIN}"

# 선택한 파이썬으로 의존성 설치(시스템 파이썬이면 --user로 설치)
"${PY_BIN}" -m pip install --user -U pip >/dev/null 2>&1 || true
"${PY_BIN}" -m pip install --user -r requirements.txt

export SECRET_TOKEN="${SECRET_TOKEN:-000000}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"

exec "${PY_BIN}" -m app.main