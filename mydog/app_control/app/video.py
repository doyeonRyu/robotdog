# Vilib 카메라/MJPEG 스트림 제어 래퍼

class Video:
    '''
    함수 설명: SunFounder Vilib 기반 카메라 구동 및 얼굴인식 토글 래퍼
    입력값: vflip(bool), hflip(bool), port(int)
    출력값: 없음
    '''
    def __init__(self, vflip=False, hflip=False, port=9000):
        self.vflip = vflip
        self.hflip = hflip
        self.port = port
        self._ok = False

    def start(self):
        try:
            from vilib import Vilib
            Vilib.camera_start(vflip=self.vflip, hflip=self.hflip)
            # web=True 로 :9000/mjpg 서버 시작
            Vilib.display(local=False, web=True)
            self._ok = True
            print('[VIDEO] Vilib started on :%d/mjpg' % self.port)
        except Exception as e:
            print(f"[VIDEO][ERR] {e}")
            self._ok = False

    def stop(self):
        if not self._ok: return
        try:
            from vilib import Vilib
            Vilib.camera_close()
        except Exception as e:
            print(f"[VIDEO][STOP][ERR] {e}")

    def face_detect(self, on: bool):
        if not self._ok: return
        try:
            from vilib import Vilib
            Vilib.face_detect_switch(bool(on))
        except Exception as e:
            print(f"[VIDEO][FACE][ERR] {e}")
