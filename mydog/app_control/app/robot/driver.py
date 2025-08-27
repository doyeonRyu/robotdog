from time import sleep

try:
    from pidog import Pidog
except Exception:
    Pidog = None


class DogDriver:
    '''
    '''
    def __init__(self):
        '''
        '''
        self._dog = Pidog() if Pidog else None
        # 머리 상태(yaw, roll, pitch)
        self._yaw = 0
        self._roll = 0
        self._pitch = 0
        self._pitch_comp = 0
        if self._dog:
            try:
                self._dog.do_action('stand')
            except Exception:
                pass

    # --- 하드웨어 핸들 ---
    def hw(self):
        return self._dog

    def head_state(self):
        return [self._yaw, self._roll, self._pitch]

    def pitch_comp(self):
        return self._pitch_comp

    # --- 핵심 제어 ---
    def set_head(self, yaw=None, pitch=None, roll=None):
        '''
        '''
        if yaw is not None: self._yaw = int(yaw)
        if pitch is not None: self._pitch = int(pitch)
        if roll is not None: self._roll = int(roll)
        if not self._dog:
            print(f"[HEAD] yaw={self._yaw} pitch={self._pitch} roll={self._roll}")
            return
        try:
            # Pidog의 head_move: 리스트 포즈 방식
            self._dog.head_move([[self._yaw, self._roll, self._pitch]], pitch_comp=self._pitch_comp, immediately=True, speed=100)
        except TypeError:
            # 일부 버전은 키워드 인자를 받음
            self._dog.head_move(yaw=self._yaw, pitch=self._pitch, roll=self._roll, speed=80)

    def set_head_pitch_comp(self, pitch: int):
        '''
        '''
        self._pitch_comp = int(pitch)
        # 현재 머리 상태로 즉시 적용
        if self._dog:
            try:
                self._dog.head_move([[self._yaw, self._roll, self._pitch]], pitch_comp=self._pitch_comp, immediately=True, speed=80)
            except Exception:
                pass

    def do_action(self, name: str, speed: int = 80):
        '''
        '''
        if not self._dog:
            print(f"[ACTION] {name} speed={speed}")
            sleep(0.1)
            return
        try:
            self._dog.do_action(name, speed=speed)
        except Exception as e:
            print(f"[ACTION][ERR] {e}")

    def wait_all_done(self):
        '''
        '''
        if self._dog and hasattr(self._dog, 'wait_all_done'):
            try:
                self._dog.wait_all_done()
            except Exception:
                pass
        else:
            sleep(0.1)

    def is_legs_done(self):
        '''
        '''
        if self._dog and hasattr(self._dog, 'is_legs_done'):
            try:
                return bool(self._dog.is_legs_done())
            except Exception:
                return True
        return True

    def read_distance(self):
        '''
        '''
        if not self._dog:
            return 42.0
        try:
            if hasattr(self._dog, 'read_distance'):
                return float(self._dog.read_distance())
            if hasattr(self._dog, 'ultrasonic') and hasattr(self._dog.ultrasonic, 'read'):
                return float(self._dog.ultrasonic.read())
        except Exception as e:
            print(f"[DIST][ERR] {e}")
        return 0.0

    def close(self):
        '''
        '''
        try:
            if self._dog and hasattr(self._dog, 'close'):
                self._dog.close()
        except Exception:
            pass


# 전역 인스턴스
my_dog = DogDriver()
