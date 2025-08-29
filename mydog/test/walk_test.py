#!/usr/bin/env python3
# ========== Walk 동작 테스트 ==========

from mydog import MyDog
from time import sleep

# mydog 초기화
my_dog = MyDog()
sleep(0.5)

# global 변수 설정
actions = [
    # [이름, head_pitch_조정(-1이면 마지막 pitch 유지), 속도]
    ['trot', 0, 95],
    ['forward', 0, 98],
    ['backward', 0, 98],
    ['turn_left', 0, 98],
    ['turn_right', 0, 98],
]
actions_len = len(actions)

last_head_pitch = 0       # 마지막 head pitch
STANDUP_ACTIONS = ['trot', 'forward', 'backward', 'turn_left', 'turn_right']

def walk_action(index: int):
    """
    Function: walk_action
    - 숫자 index에 해당하는 보행 동작 실행
    """
    global last_head_pitch

    # 범위 체크
    if index < 0 or index >= actions_len:
        print(f"[WARN] 유효하지 않은 동작 인덱스: {index}")
        return

    # 현재 동작 중지 후 실행
    my_dog.body_stop()

    name, head_pitch_adjust, speed = actions[index]

    # 서서 시작해야 하는 동작이면 일어서기
    if name in STANDUP_ACTIONS:
        last_head_pitch = 0
        my_dog.do_action('stand', speed=90)

    # 헤드 피치 조정값 반영 (-1이면 이전 값 유지)
    if head_pitch_adjust != -1:
        last_head_pitch = head_pitch_adjust

    # 머리 각도 이동 (yaw, roll, pitch)
    my_dog.head_move_raw([[0, 0, last_head_pitch]], immediately=False, speed=60)

    # 본 동작 실행
    my_dog.do_action(name, step_count=10, speed=speed, pitch_comp=last_head_pitch)


def print_menu():
    print("\n=== 어떤 보행 동작을 진행할까요? (Ctrl+C/q로 종료) ===")
    print("  0: trot")
    print("  1: forward")
    print("  2: backward")
    print("  3: turn_left")
    print("  4: turn_right")
    print("  q: 종료\n", end='')


def main():
    while True:
        try:
            print_menu()
            index_str = input("번호 입력: ").strip().lower()
            if index_str in ('q', 'quit', 'exit'):
                break
            index = int(index_str)
            walk_action(index)
        except ValueError:
            print("[INFO] 숫자(0~4) 또는 q를 입력하세요.")
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
        print("[INFO] 자원 정리 완료. 프로그램을 종료합니다.")