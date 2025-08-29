# 명령 매핑과 실행 로직(상태 관리 포함)
# preset_actions에 의존하는 동작(짖기/헐떡이기/하울링 등)은 해당 모듈이 설치되어 있어야 합니다.
try:
    from preset_actions import *  # bark, pant, bark_action, body_twisting, hand_shake, high_five, push_up, howling, scratch, shake_head
except Exception:
    # preset_actions가 없는 환경에서도 서버/UI 개발이 가능하도록 noop 대체
    def _noop(*args, **kwargs):
        print('[preset_actions missing] called')
    bark = pant = bark_action = body_twisting = hand_shake = high_five = push_up = howling = scratch = shake_head = _noop


SIT_HEAD_PITCH = -40
STAND_HEAD_PITCH = 0
STATUS_STAND = 0
STATUS_SIT = 1
STATUS_LIE = 2


class CommandExecutor:
    '''
    '''
    def __init__(self, dog):
        '''
        '''
        # 하드웨어 드라이버 보관
        self.dog = dog
        # 현재 자세 상태
        self.current_status = STATUS_LIE
        # 명령 테이블 구성
        self.COMMANDS = {
            "forward": {
                "commands": ["forward"],
                "function": lambda: self.dog.do_action('forward', speed=98),
                "after": "forward",
                "status": STATUS_STAND,
                "head_pitch": STAND_HEAD_PITCH,
            },
            "backward": {
                "commands": ["backward"],
                "function": lambda: self.dog.do_action('backward', speed=98),
                "after": "backward",
                "status": STATUS_STAND,
                "head_pitch": STAND_HEAD_PITCH,
            },
            "turn left": {
                "commands": ["turn left"],
                "function": lambda: self.dog.do_action('turn_left', speed=98),
                "after": "turn left",
                "status": STATUS_STAND,
                "head_pitch": STAND_HEAD_PITCH,
            },
            "turn right": {
                "commands": ["turn right"],
                "function": lambda: self.dog.do_action('turn_right', speed=98),
                "after": "turn right",
                "status": STATUS_STAND,
                "head_pitch": STAND_HEAD_PITCH,
            },
            "trot": {
                "commands": ["trot", "run"],
                "function": lambda: self.dog.do_action('trot', speed=98),
                "after": "trot",
                "status": STATUS_STAND,
                "head_pitch": STAND_HEAD_PITCH,
            },
            "stop": {
                "commands": ["stop"],
            },
            "lie down": {
                "commands": ["lie down"],
                "function": lambda: self.dog.do_action('lie', speed=70),
                "head_pitch": STAND_HEAD_PITCH,
                "status": STATUS_LIE,
            },
            "stand up": {
                "commands": ["stand up", "stand"],
                "function": lambda: self.dog.do_action('stand', speed=70),
                "head_pitch": STAND_HEAD_PITCH,
                "status": STATUS_STAND,
            },
            "sit": {
                "commands": ["sit", "sit down", "set", "set down"],
                "function": lambda: self.dog.do_action('sit', speed=70),
                "head_pitch": SIT_HEAD_PITCH,
                "status": STATUS_SIT,
            },
            "bark": {
                "commands": ["bark", "park", "fuck"],
                "function": lambda: bark(self.dog.hw(), self.dog.head_state(), pitch_comp=self.dog.pitch_comp()),
            },
            "bark harder": {
                "commands": ["bark harder", "park harder", "fuck harder", "bark harbor", "park harbor", "fuck harbor"],
                "function": lambda: bark_action(self.dog.hw(), self.dog.head_state(), 'single_bark_1'),
            },
            "pant": {
                "commands": ["pant", "paint"],
                "function": lambda: pant(self.dog.hw(), self.dog.head_state(), pitch_comp=self.dog.pitch_comp()),
            },
            "wag tail": {
                "commands": ["wag tail", "wake tail", "wake town", "wait town", "wait tail", "wake time", "wait time", "wait tail"],
                "function": lambda: self.dog.do_action('wag_tail', speed=100),
                "after": "wag tail",
            },
            "shake head": {
                "commands": ["shake head"],
                "function": lambda: shake_head(self.dog.hw(), self.dog.head_state()),
            },
            "stretch": {
                "commands": ["stretch"],
                "function": self._stretch,
                "after": "stand up",
                "status": STATUS_STAND,
            },
            "doze off": {
                "commands": ["doze off", "does off"],
                "function": lambda: self.dog.do_action('doze_off', speed=95),
                "after": "doze off",
                "status": STATUS_LIE,
            },
            "push-up": {
                "commands": ["push up", "push-up"],
                "function": lambda: push_up(self.dog.hw()),
                "after": "push-up",
                "status": STATUS_STAND,
            },
            "howling": {
                "commands": ["howling"],
                "function": lambda: howling(self.dog.hw()),
                "after": "sit",
                "status": STATUS_SIT,
            },
            "twist body": {
                "commands": ["twist body", "taste body", "twist party", "taste party"],
                "function": lambda: body_twisting(self.dog.hw()),
                "before": "stretch",
                "after": "sit",
                "status": STATUS_STAND,
            },
            "scratch": {
                "commands": ["scratch"],
                "function": lambda: scratch(self.dog.hw()),
                "after": "sit",
                "head_pitch": SIT_HEAD_PITCH,
                "status": STATUS_SIT,
            },
            "handshake": {
                "commands": ["handshake"],
                "function": lambda: hand_shake(self.dog.hw()),
                "after": "sit",
                "head_pitch": SIT_HEAD_PITCH,
                "status": STATUS_SIT,
            },
            "high five": {
                "commands": ["high five", "hi five"],
                "function": lambda: high_five(self.dog.hw()),
                "after": "sit",
                "head_pitch": SIT_HEAD_PITCH,
                "status": STATUS_SIT,
            },
        }

        # 낱말 목록을 평탄화해 공개
        self.AVAILABLE_COMMANDS = []
        for name in self.COMMANDS:
            self.AVAILABLE_COMMANDS.extend(self.COMMANDS[name]["commands"])

    def available(self):
        '''
        '''
        return list(self.AVAILABLE_COMMANDS)

    def _stretch(self):
        '''
        '''
        self.dog.do_action('stretch', speed=10)
        self.dog.wait_all_done()

    def set_head_pitch_init(self, pitch: int):
        '''
        '''
        self.dog.set_head_pitch_comp(pitch)

    def change_status(self, status: int):
        '''
        '''
        self.current_status = status
        if status == STATUS_STAND:
            self.set_head_pitch_init(STAND_HEAD_PITCH)
            self.dog.do_action('stand', speed=70)
        elif status == STATUS_SIT:
            self.set_head_pitch_init(SIT_HEAD_PITCH)
            self.dog.do_action('sit', speed=70)
        elif status == STATUS_LIE:
            self.set_head_pitch_init(STAND_HEAD_PITCH)
            self.dog.do_action('lie', speed=70)

    def run(self, command: str | None):
        '''
        '''
        if not command:
            return
        # 다리 동작 중이면 큐를 비워서 중첩 방지
        if hasattr(self.dog, 'is_legs_done') and not self.dog.is_legs_done():
            return
        for name in self.COMMANDS:
            entry = self.COMMANDS[name]
            if command in entry.get("commands", []):
                # 머리 보정
                if "head_pitch" in entry:
                    self.set_head_pitch_init(entry["head_pitch"])
                # 자세 변경
                if "status" in entry and getattr(self, 'current_status') != entry["status"]:
                    self.change_status(entry["status"])
                # 선행 동작
                if "before" in entry:
                    b = entry["before"]
                    if b in self.COMMANDS and "function" in self.COMMANDS[b]:
                        self.COMMANDS[b]["function"]()
                # 본 동작
                if "function" in entry:
                    entry["function"]()
                # 후행 동작(연속 유지용)
                return entry.get("after")

        # 매칭 실패 시 아무 것도 하지 않음
        return None


# 이전 버전과의 호환을 위한 심플 API
AVAILABLE_COMMANDS = []  # loop에서 import 가능하도록 비워두되, 실제 목록은 실행 시 executor.available() 사용
