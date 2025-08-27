# Socket.IO 이벤트 핸들러 (stick/btn/toggle/voice). 토큰 인증, 상태 푸시, 얼굴인식 토글 연동
from flask_socketio import SocketIO, emit, disconnect


def create_socketio(app, control_state, secret_token: str, video=None):
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

    return sio
