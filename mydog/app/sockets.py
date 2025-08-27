from flask_socketio import SocketIO, emit, disconnect


def create_socketio(app, control_state, secret_token: str):
    '''
    함수 설명: Socket.IO 서버 생성 및 이벤트 바인딩
    입력값: app(Flask), control_state(ControlState), secret_token(str)
    출력값: SocketIO 객체
    '''
    sio = SocketIO(app, cors_allowed_origins='*')

    @sio.on('connect')
    def on_connect():
        token = app.current_request_args.get('token') if hasattr(app, 'current_request_args') else None
        # 최소 골격: 쿼리스트링 토큰 검사 대신, 클라이언트 측 첫 이벤트에서 검사
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
        control_state.update_toggle(data.get('name', ''), bool(data.get('on', False)))

    @sio.on('btn')
    def on_btn(data):
        control_state.set_button(data.get('name', ''))

    @sio.on('voice')
    def on_voice(data):
        control_state.set_voice(data.get('text', ''))

    return sio

