#!/usr/bin/env bash
# 개발용 스크립트: venv 생성(시스템 vilib 공유), 의존성 설치, 서버 실행
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# venv를 시스템 site-packages에 연결 → /home/pi/vilib 그대로 사용
if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv --system-site-packages
fi
# 가상환경 활성화
# shellcheck disable=SC1091
source .venv/bin/activate

# ~/vilib을 인식시키기 위해 /home/pi와 프로젝트 루트를 PYTHONPATH에 추가
export PYTHONPATH="/home/pi:${PROJECT_ROOT}:${PYTHONPATH:-}"
export VILIB_HOME="/home/pi/vilib"

# .env 자동 로드(있다면)
if [[ -f ".env" ]]; then
  set -a
  # shellcheck disable=SC1090
  source .env
  set +a
fi

# 기본 환경값
export SECRET_TOKEN="${SECRET_TOKEN:-000000}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export VIDEO_TAKEOVER="${VIDEO_TAKEOVER:-1}"   # 1이면 카메라/포트 선점 프로세스 종료 시도
# FastAPI 모듈을 쓰는 경우 지정(없으면 app.main로 실행)
export APP_MODULE="${APP_MODULE:-}"

python3 -m pip install -U pip
python3 -m pip install -r requirements.txt

echo "[dev] python: $(which python3)"
echo "[dev] PYTHONPATH: ${PYTHONPATH}"
echo "[dev] HOST:PORT = ${HOST}:${PORT}"
echo "[dev] VIDEO_TAKEOVER=${VIDEO_TAKEOVER}"
echo "[dev] APP_MODULE=${APP_MODULE:-'(app.main 사용)'}"

# 카메라/스트리머 점유 해제 옵션
if [[ "${VIDEO_TAKEOVER}" == "1" ]]; then
  echo "[dev] trying to free :9000 and /dev/video0 ..."
  # :9000 점유 프로세스 종료
  if command -v fuser >/dev/null 2>&1; then
    fuser -k 9000/tcp || true
  fi
  # /dev/video0 점유 프로세스 종료(주의: 필요한 프로세스까지 죽을 수 있음)
  if command -v fuser >/dev/null 2>&1 && [[ -e /dev/video0 ]]; then
    fuser -k /dev/video0 || true
  fi
  # 흔한 스트리머들 종료
  pkill -f "mjpg|v4l2|rtsp|libcamera" || true
fi

echo "──────────────────────────────────────────────"
echo "[dev] 서버 기동…"
echo "──────────────────────────────────────────────"

# 실행: FastAPI 모듈이 지정되면 uvicorn, 아니면 python -m app.main
if [[ -n "${APP_MODULE}" ]]; then
  # uvicorn 필요
  if ! command -v uvicorn >/dev/null 2>&1; then
    python3 -m pip install "uvicorn[standard]" fastapi
  fi
  exec uvicorn "${APP_MODULE}" --reload --host "${HOST}" --port "${PORT}"
else
  # app/main.py가 진입점이어야 함
  exec python3 -m app.main
fi
