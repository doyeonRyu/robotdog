from math import atan2, sqrt, pi
from time import sleep
from .driver import my_dog
from .commands import run_command, AVAILABLE_COMMANDS


def map_range(val, in_min, in_max, out_min, out_max):
    '''
    함수 설명: 입력 구간 값을 출력 구간으로 선형 매핑
    입력값: val(float), in_min/max, out_min/max
    출력값: float
    '''
    return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min


def loop(control_state, on_state):
    '''
    함수 설명: 주 제어 루프(조이스틱/버튼/음성 상태를 읽어 동작 수행)
    입력값: control_state(ControlState), on_state(callable)
    출력값: 없음
    '''
    command = None
    last_kx = last_ky = last_qx = last_qy = 0

    while True:
        snap = control_state.snapshot()

        # 거리 센서 값 읽어 Web UI로 브로드캐스트
        distance = round(my_dog.read_distance(), 2)
        on_state({"distance": distance})

        # 좌측 조이스틱(이동)
        kx, ky = snap['kx'], snap['ky']
        if (last_kx, last_ky) != (kx, ky):
            last_kx, last_ky = kx, ky
            if kx != 0 or ky != 0:
                ka = atan2(ky, kx) * 180 / pi
                kr = sqrt(kx**2 + ky**2)
                if kr > 20:  # 데드존
                    if 45 < ka < 135:
                        command = "forward"
                    elif ka > 135 or ka < -135:
                        command = "turn left"
                    elif -45 < ka < 45:
                        command = "turn right"
                    elif -135 < ka < -45:
                        command = "backward"
            else:
                command = None

        # 우측 조이스틱(머리 제어)
        qx, qy = snap['qx'], snap['qy']
        if (last_qx, last_qy) != (qx, qy):
            last_qx, last_qy = qx, qy
            if qx != 0 or qy != 0:
                yaw = int(map_range(qx, 100, -100, -90, 90))
                pitch = int(map_range(qy, -100, 100, -30, 30))
            else:
                yaw = 0
                pitch = 0
            my_dog.set_head(yaw=yaw, pitch=pitch)

        # 버튼 명령
        if snap['last_btn']:
            command = snap['last_btn']

        # 음성 명령
        if snap['voice_text'] and snap['voice_text'] in AVAILABLE_COMMANDS:
            command = snap['voice_text']

        # 명령 실행
        run_command(my_dog, command)

        sleep(0.02)
