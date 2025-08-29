# !/usr/bin/env bash
# 개발용 스크립트 *가상환경 생성(시스템 vilib 공유), 의존성 설치, 서버 실행
set -euo pipefail

# venv를 시스템 site-packages에 연결 → /home/pi/vilib 그대로 사용
if [ ! -d ".venv" ]; then
  python -m venv .venv --system-site-packages
fi
source .venv/bin/activate

# ~/vilib을 인식시키기 위해 /home/pi를 PYTHONPATH에 추가
export PYTHONPATH="/home/pi:${PYTHONPATH:-}"
export VILIB_HOME="/home/pi/vilib"

python -m pip install -U pip
python -m pip install -r requirements.txt

export SECRET_TOKEN="${SECRET_TOKEN:-000000}"
export HOST="${HOST:-0.0.0.0}"
export PORT="${PORT:-8000}"
export VIDEO_TAKEOVER="${VIDEO_TAKEOVER:-1}"   # 앱 시작 시 :9000 / /dev/video0 선점 프로세스 종료

echo "[dev] python: $(which python)"
echo "[dev] PYTHONPATH: ${PYTHONPATH}"
exec python -m app.main