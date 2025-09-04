#!/usr/bin/env python3
# ========== 기본 동작 테스트 ==========

import os, sys

from dog.app_control.app.routes import index
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dog import Mydog
from time import sleep

# mydog 초기화
if __name__ == "__main__":
    my_dog = Mydog()
sleep(0.5)

# global 변수 설정
## leg 움직임은 제외함 # no standing action
actions = [
    # [이름, head_pitch_조정(-1이면 마지막 pitch 유지), 속도]
    ['stand', 0, 50], # 일어나기
    ['sit', -30, 50], # 앉기
    ['lie', 0, 20], # 눕기
    ['lie_with_hands_out', 0,  20], # 손을 뻣고 눕기
    ['doze_off', -30, 90], # 졸기
    ['stretch', 20, 20], # 스트레칭
    ['push_up', -30, 50], # 푸쉬업
    ['shake_head', -1, 90], # 고개 흔들기
    ['tilting_head', -1, 60], # 고개 기울이기
    ['wag_tail', -1, 100], # 꼬리 흔들기
]

last_head_pitch = 0       # 마지막 head pitch

# ========== status ==========

def main():
    def basic_action(action):
        global last_head_pitch

        if action not in [a[0] for a in actions]: # action: 동작명
            raise ValueError("유효하지 않은 동작 이름")
        else:
            # 현재 동작 중지 후 실행
            my_dog.body_stop()
            
            # 동작 정보 가져오기
            name, head_pitch_adjust, speed = [a for a in actions if a[0] == action][0]
            
            # 헤드 피치 조정값 반영 (-1이면 이전 값 유지)
            if head_pitch_adjust != -1:
                last_head_pitch = head_pitch_adjust
            
            # 머리 각도 이동 (yaw, roll, pitch)
            my_dog.head_move_raw([[0, 0, last_head_pitch]], immediately=False, speed=60)
            
            # 본 동작 실행
            my_dog.do_action(name, step_count=10, speed=speed, pitch_comp=last_head_pitch)
            my_dog.wait_all_done()

    def print_menu():
        print("\n=== 동작을 입력하세요. (Ctrl+C/q로 종료) ===")
        print("hint: stand, sit, lie, wag_tail...")

    while True:
        try:
            print_menu()
            action = input("동작 입력: ")
            if action in ('q', 'quit', 'exit'):
                break
            basic_action(action)
        except ValueError:
            print("[INFO] 동작 또는 q를 입력하세요.")
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] 사용자 종료(Ctrl+C).")
    except Exception as e:
        print(f"\033[31mERROR: {e}\033[m")
    finally:
        try:
            my_dog.close()
        except Exception:
            pass
        print("프로그램 종료")
