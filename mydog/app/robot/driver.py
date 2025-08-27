import time

class FakeDog:
    '''
    함수 설명: 실제 하드웨어 대신 동작 로그만 출력하는 테스트용 드라이버
    입력값: 없음(메서드 호출로 제어)
    출력값: 없음
    '''
    def set_head(self, yaw=0, pitch=0, roll=0):
        print(f"[HEAD] yaw={yaw} pitch={pitch} roll={roll}")

    def read_distance(self):
        # 가짜 거리값
        return 42.0

    def do(self, action: str):
        print(f"[ACTION] {action}")
        if action in ("sit", "stand up", "lie down"):
            time.sleep(0.2)  # 짧은 동작 지연


# 실제 하드웨어 연결 시 위 FakeDog 대신 실제 드라이버로 교체
my_dog = FakeDog()
