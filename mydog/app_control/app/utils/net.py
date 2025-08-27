import os
import socket


def get_ip():
    '''
    함수 설명: 라즈베리파이의 유효한 IP를 탐색하여 반환
    입력값: 없음
    출력값: str (IP 문자열) 또는 '127.0.0.1'
    '''
    # 간단한 방식: 소켓을 외부로 연결 시도 후 로컬 주소 취득
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        # ifconfig 파싱 대체(최소 골격): 실패 시 localhost
        return "127.0.0.1"
