import os
import threading
from .control_state import ControlState
from .server import create_app
from .robot.loop import loop
from .utils.net import get_ip


def main():
    '''
    함수 설명: 서버와 제어 루프를 함께 기동하는 엔트리포인트
    입력값: 없음
    출력값: 없음
    '''
    secret_token = os.getenv('SECRET_TOKEN', '000000')
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '8000'))

    cs = ControlState()
    app, socketio = create_app(cs, secret_token)

    # 상태 브로드캐스트 콜백
    def on_state(payload: dict):
        socketio.emit('state', payload)

    # 제어 루프는 스레드로 실행
    t = threading.Thread(target=loop, args=(cs, on_state), daemon=True)
    t.start()

    ip = get_ip()
    print(f"[INFO] open http://{ip}:{port}  (토큰: {secret_token})")
    socketio.run(app, host=host, port=port)


if __name__ == '__main__':
    main()
