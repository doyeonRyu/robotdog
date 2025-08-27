AVAILABLE_COMMANDS = [
    'forward', 'backward', 'turn left', 'turn right',
    'sit', 'stand up', 'lie down', 'bark', 'wag tail', 'pant', 'scratch'
]


def run_command(dog, cmd: str | None):
    '''
    함수 설명: 명령 문자열을 받아 로봇 동작 실행
    입력값: dog(드라이버), cmd(str|None)
    출력값: 없음
    '''
    if not cmd:
        return
    # 최소 골격: 로그 출력/간단 매핑
    if cmd in AVAILABLE_COMMANDS:
        dog.do(cmd)
    else:
        print(f"[WARN] Unknown command: {cmd}")
