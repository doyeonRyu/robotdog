# 엔트리 포인트. 서버 실행, 소캣 준비, 제어 루프 스레드 시작. 비디오 스트림 시작 / 종료
import os
import threading
from .control_state import ControlState
from .server import create_app
from .robot.loop import loop
from .utils.net import get_ip
from .video import Video
from .gpt_runner import GPTRunner


def main():
    '''
    함수 설명: 서버와 제어 루프, 비디오 스트림을 함께 기동
    입력값: 없음
    출력값: 없음
    '''
    secret_token = os.getenv('SECRET_TOKEN', '000000')
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))

    cs = ControlState()

    # 비디오(MJPEG) 시작: Vilib가 설치되어 있지 않으면 내부에서 안전하게 실패 로그만 출력
    video = Video(vflip=False, hflip=False, port=9000)
    video.start()

    # GPT 실행기 설정(사용자 제공 경로/명령)
    gpt = GPTRunner(
        workdir="~/pidog/gpt_examples",
        python_bin="~/my_venv/bin/python3",
        script="gpt_dog.py",
        extra_args=["--keyboard"],
        use_sudo=False  # sudo 비번 대기로 멈추는 현상 방지
    )
    print("[GPT] Runner ready: ~/pidog/gpt_examples gpt_dog.py --keyboard")

    app, socketio = create_app(cs, secret_token, video, gpt)

    # 상태 브로드캐스트 콜백
    def on_state(payload: dict):
        socketio.emit('state', payload)

    # 제어 루프 스레드
    t = threading.Thread(target=loop, args=(cs, on_state), daemon=True)
    t.start()

    ip = get_ip()
    print(f"[INFO] open http://{ip}:{port}  (토큰: {secret_token})")
    try:
        socketio.run(app, host=host, port=port)
    finally:
        video.stop()


if __name__ == '__main__':
    main()
