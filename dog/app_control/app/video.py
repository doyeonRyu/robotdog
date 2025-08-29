import time
import socket
from urllib.request import urlopen, Request

class Video:

    def __init__(self, vflip=False, hflip=False, port=9000, host='127.0.0.1'):
        self.vflip = vflip
        self.hflip = hflip
        self.port = port
        self._ok = False
        self._external = False
        self.host = host

    def _stream_url(self):
        return f"http://{self.host}:{self.port}/mjpg"

    def _probe_stream(self, timeout=1.0) -> bool:
        """포트가 이미 열려 있고 MJPEG가 응답하는지 가볍게 확인."""
        try:
            # TCP 포트 체크
            with socket.create_connection((self.host, self.port), timeout=timeout):
                pass
            # 간단 요청으로 응답만 확인
            req = Request(self._stream_url(), headers={'User-Agent':'VideoProbe'})
            with urlopen(req, timeout=timeout) as resp:
                return resp.status in (200, 302)
        except Exception:
            return False

    def start(self, retries: int = 3, ready_timeout: float = 5.0) -> bool:
        """스트림이 준비될 때까지 대기. 이미 외부 스트림이 있으면 재시작하지 않음."""
        if self._ok:
            return True
        # 외부 스트림이 이미 뜨면 그대로 사용(충돌 방지)
        if self._probe_stream(timeout=0.8):
            self._ok = True
            self._external = True
            print(f"[VIDEO] external stream detected on :{self.port}/mjpg (skip Vilib start)")
            return True
        # 내부에서 Vilib 시작 시도 + 준비 대기/재시도
        for attempt in range(1, retries + 1):
            try:
                from vilib import Vilib
                Vilib.camera_start(vflip=self.vflip, hflip=self.hflip)
                Vilib.display(local=False, web=True)
                t0 = time.time()
                while not getattr(Vilib, "flask_start", False):
                    if time.time() - t0 > ready_timeout:
                        raise TimeoutError("Vilib web server not ready")
                    time.sleep(0.05)
                self._ok = True
                self._external = False
                print(f"[VIDEO] Vilib started on :{self.port}/mjpg (attempt {attempt})")
                return True
            except Exception as e:
                print(f"[VIDEO][WARN] start failed (attempt {attempt}/{retries}): {e}")
                # 실패 시 정리 후 재시도
                try:
                    from vilib import Vilib
                    Vilib.camera_close()
                except Exception:
                    pass
                time.sleep(0.5)
                # 다음 루프 전에 외부 스트림이 떠버렸는지도 체크
                if self._probe_stream(timeout=0.8):
                    self._ok = True
                    self._external = True
                    print(f"[VIDEO] external stream detected during retry on :{self.port}/mjpg")
                    return True
        print("[VIDEO][ERR] failed to start video after retries")
        return False
