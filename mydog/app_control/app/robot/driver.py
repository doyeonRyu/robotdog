# 실제 Pidog 하드웨어 드라이버(가능한 안전하게 동작하도록 기본자세 위주)
# 설치 전제: `pip install pidog robot-hat` (또는 SunFounder 스크립트로 설치)
from time import sleep

try:
    from pidog import Pidog
except Exception as e:
    Pidog = None


class DogDriver:
    '''
    함수 설명: Pidog 하드웨어 제어를 위한 어댑터 클래스
    입력값: 없음(생성 시 내부 객체 초기화)
    출력값: 없음
    '''
    def __init__(self):
        # Pidog 라이브러리가 없는 환경에서도 서버 개발 테스트 가능하게 예외 처리
        self._dog = Pidog() if Pidog else None
        # 초기 머리 각도(안전값)
        self._yaw = 0
        self._pitch = 0
        self._roll = 0
        # 전원/자세 초기화(필요 시 주석 해제)
        if self._dog:
            try:
                # my_dog 초기자세(서 있는 자세 또는 안정자세)
                self._dog.do_action('stand')
            except Exception:
                pass

    def set_head(self, yaw=0, pitch=0, roll=0):
        '''
        함수 설명: 머리(yaw/pitch/roll) 제어
        입력값: yaw(int), pitch(int), roll(int)
        출력값: 없음
        '''
        self._yaw, self._pitch, self._roll = yaw, pitch, roll
        if not self._dog:
            print(f"[HEAD] yaw={yaw} pitch={pitch} roll={roll}")
            return
        try:
            # Pidog의 머리 서보 제어 메서드(키트 버전에 따라 API 차이가 있을 수 있음)
            # 예: self._dog.head_move(yaw=yaw, pitch=pitch, roll=roll, speed=80)
            self._dog.head_move(yaw=yaw, pitch=pitch, roll=roll, speed=80)
        except Exception as e:
            print(f"[HEAD][ERR] {e}")

    def read_distance(self):
        '''
        함수 설명: 초음파 센서 거리 읽기(cm)
        입력값: 없음
        출력값: float
        '''
        if not self._dog:
            return 42.0
        try:
            # 키트 버전에 따라: self._dog.read_distance() 또는 self._dog.ultrasonic.read()
            if hasattr(self._dog, 'read_distance'):
                return float(self._dog.read_distance())
            if hasattr(self._dog, 'ultrasonic') and hasattr(self._dog.ultrasonic, 'read'):
                return float(self._dog.ultrasonic.read())
        except Exception as e:
            print(f"[DIST][ERR] {e}")
        return 0.0

    def do(self, action: str):
        '''
        함수 설명: 문자열 명령을 Pidog 동작으로 매핑하여 실행
        입력값: action(str) – 'sit', 'stand up', 'lie down', 'forward' 등
        출력값: 없음
        '''
        if not self._dog:
            print(f"[ACTION] {action}")
            sleep(0.1)
            return
        try:
            # 기본 동작 매핑(키트 제공 do_action 이름과 맞추기)
            mapping = {
                'sit': 'sit',
                'stand up': 'stand',
                'lie down': 'lie',
                'bark': 'bark',
                'wag tail': 'wag_tail',
                'pant': 'pant',
                'scratch': 'scratch',
                # 이동류는 키트별 API가 다름: 간단히 방향 액션 존재 시 사용
                'forward': 'forward',
                'backward': 'backward',
                'turn left': 'turn_left',
                'turn right': 'turn_right',
            }
            act = mapping.get(action)
            if act:
                # 대부분의 SunFounder 예제는 do_action(name, speed) 형태
                self._dog.do_action(act, speed=80)
            else:
                print(f"[ACTION][WARN] Unknown: {action}")
        except Exception as e:
            print(f"[ACTION][ERR] {e}")


# 전역 드라이버 인스턴스
my_dog = DogDriver()