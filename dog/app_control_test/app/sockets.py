# Socket.IO 이벤트 핸들러 (stick/btn/toggle/voice). 토큰 인증, 상태 푸시, 얼굴인식 토글 연동
from email.mime import text
from flask_socketio import SocketIO, emit, disconnect
import threading
from .robot.driver import my_dog

def create_socketio(app, control_state, secret_token: str, video=None, gpt=None):
    '''
    함수 설명: Socket.IO 서버 생성 및 이벤트 바인딩(+얼굴인식 토글 연동)
    입력값: app(Flask), control_state(ControlState), secret_token(str), video(Video|None)
    출력값: SocketIO 객체
    '''
    sio = SocketIO(app, cors_allowed_origins='*')

    @sio.on('connect')
    def on_connect():
        print('[SOCKET] client connected')

    @sio.on('auth')
    def on_auth(data):
        token = data.get('token')
        if token != secret_token:
            emit('auth_result', {'ok': False, 'msg': 'invalid token'})
            disconnect()
            return
        emit('auth_result', {'ok': True})

    @sio.on('stick')
    def on_stick(data):
        side = data.get('side', 'left')
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        control_state.update_stick(side, x, y)

    @sio.on('toggle')
    def on_toggle(data):
        name = data.get('name', '')
        on = bool(data.get('on', False))
        control_state.update_toggle(name, on)
        # 얼굴 인식 토글을 영상 모듈에 전달
        if video and name == 'face_detect':
            try:
                video.face_detect(on)
            except Exception as e:
                emit('state', {'warn': f'face_detect error: {e}'})

    @sio.on('btn')
    def on_btn(data):
        control_state.set_button(data.get('name', ''))

    @sio.on('voice')
    def on_voice(data):
        control_state.set_voice(data.get('text', ''))

    # --- Chat with GPT runner ---
    @sio.on('chat_user')
    def on_chat_user(data):
        if not gpt:
            emit('chat_error', {'msg': 'GPT runner not configured'})
            return
        text = (data or {}).get('text', '')
        if not text:
            emit('chat_error', {'msg': 'empty prompt'})
            return
        print(f"[CHAT] user -> GPT: {text[:120]!r}")
        # 상태: 생성 시작
        # emit('chat_status', {'state': 'thinking'})

        def _on_status(state: str):
            print(f"[CHAT] status: {state}")
            sio.emit('chat_status', {'state': state})

        def _on_stream(delta: str):
            # print(f\"[CHAT] stream: {delta!r}\")
            sio.emit('chat_stream', {'delta': delta})

        def _on_done(answer: str, actions: list[str] | None):
            print(f"[CHAT] done. answer_len={len(answer)}, actions={actions or []}")
            sio.emit('chat_done', {'answer': answer, 'actions': actions or []})
            # 동작 실행(순차) - 다리 동작이 끝날 때까지 대기하며 순서대로 버튼 큐잉
            if actions:
                def run_actions(seq):
                    for a in seq:
                        control_state.set_button(a)
                        # 다음 동작 조건 대기
                        while True:
                            try:
                                if my_dog.is_legs_done():
                                    break
                            except Exception:
                                break
                        # 약간의 틱 간격
                threading.Thread(target=run_actions, args=(actions,), daemon=True).start()

        def _on_error(msg: str):
            print(f"[CHAT] error: {msg}")
            sio.emit('chat_error', {'msg': msg})

        threading.Thread(
            target=gpt.ask,
            args=(text, _on_status, _on_stream, _on_done, _on_error),
            daemon=True
        ).start()

    return sio
