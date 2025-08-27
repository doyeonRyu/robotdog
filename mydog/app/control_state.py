# app/control_state.py
import threading
from dataclasses import dataclass, field
from time import time


@dataclass
class ControlState:
    '''
    함수 설명: 클라이언트(Web)에서 들어오는 최신 입력 상태를 보관
    입력값: 없음(필드로 상태 저장)
    출력값: 없음(객체 상태로 보관)
    '''
    # 좌/우 조이스틱
    kx: int = 0
    ky: int = 0
    qx: int = 0
    qy: int = 0

    # 토글/버튼 상태
    face_detect: bool = False
    last_btn: str | None = None
    voice_text: str | None = None

    # 내부 관리
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    _last_input_ts: float = field(default_factory=time)

    def update_stick(self, side: str, x: int, y: int):
        '''
        함수 설명: 조이스틱 상태 업데이트
        입력값: side(str: 'left'|'right'), x(int), y(int)
        출력값: 없음
        '''
        with self._lock:
            if side == 'left':
                self.kx, self.ky = x, y
            else:
                self.qx, self.qy = x, y
            self._last_input_ts = time()

    def update_toggle(self, name: str, on: bool):
        '''
        함수 설명: 토글 입력 업데이트
        입력값: name(str), on(bool)
        출력값: 없음
        '''
        with self._lock:
            if name == 'face_detect':
                self.face_detect = on
            self._last_input_ts = time()

    def set_button(self, name: str):
        '''
        함수 설명: 버튼 입력 기록(최근 누른 버튼)
        입력값: name(str)
        출력값: 없음
        '''
        with self._lock:
            self.last_btn = name
            self._last_input_ts = time()

    def set_voice(self, text: str):
        '''
        함수 설명: 음성 명령 텍스트 저장
        입력값: text(str)
        출력값: 없음
        '''
        with self._lock:
            self.voice_text = text
            self._last_input_ts = time()

    def snapshot(self):
        '''
        함수 설명: 현재 상태 스냅샷을 원자적으로 반환
        입력값: 없음
        출력값: dict
        '''
        with self._lock:
            return {
                'kx': self.kx, 'ky': self.ky,
                'qx': self.qx, 'qy': self.qy,
                'face_detect': self.face_detect,
                'last_btn': self.last_btn,
                'voice_text': self.voice_text,
                'last_input_ms': int((time() - self._last_input_ts) * 1000)
            }