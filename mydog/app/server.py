import os
from flask import Flask, request
from .routes import bp as routes_bp
from .sockets import create_socketio


def create_app(control_state, secret_token: str):
    '''
    함수 설명: Flask 앱과 Socket.IO 초기화
    입력값: control_state(ControlState), secret_token(str)
    출력값: (app, socketio)
    '''
    app = Flask(__name__, static_folder=None)
    app.register_blueprint(routes_bp)

    # 간단히 요청 args를 sockets에서 접근 가능하도록 보조 속성 부여
    @app.before_request
    def _capture_args():
        app.current_request_args = request.args

    socketio = create_socketio(app, control_state, secret_token)
    return app, socketio
