#!/usr/bin/env python3
# ========== 센서 테스트 ==========

# import os, sys

# from dog.app_control.app.routes import index
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dog import Mydog
import os
import time
from time import sleep

# 작업 디렉토리 변경
abspath = os.path.abspath(os.path.dirname(__file__)) 
# print(abspath)
os.chdir(abspath) 


# mydog 초기화
if __name__ == "__main__":
    my_dog = Mydog()
sleep(0.5)

# ========== ultrasonic ==========
"""
API:
    Pidog.read_distance()
        return the distance read by ultrasound
        - return float
"""
def ultrasonic_test():
    while True:
        try:
            distance = my_dog.read_distance()
            distance = round(distance,2)
            print(f"Distance: {distance} cm")
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[INFO] 측정 종료")

# ========== imu ==========
"""
SH3001: 3축 가속도계 + 3축 자이로스코프 + 1축 온도계
API:
    Pidog.accData = [ax, ay, az]
        the acceleration value, default gravity 1G = -16384
        note that the accelerometer direction is opposite to the actual acceleration direction

    Pidog.gyroData = [gx, gy, gz]
        the gyro value

more to see: ../pidog/sh3001.py

"""
def imu_test():
    while True:
        try:
            ax, ay, az = my_dog.accData
            gx, gy, gz = my_dog.gyroData
            print(f"accData: {ax}, {ay}, {az}       gyroData: {gx}, {gy}, {gz}")
            time.sleep(0.2)
        except KeyboardInterrupt:
            print("\n[INFO] IMU 테스트 종료")

# ========== dual touch ==========
"""
API:
    Pidog.dual_touch.read()
        - return str, dual_touch status:
            - 'N'  no touch
            - 'L'  left touched
            - 'LS' left slide
            - 'R'  right touched
            - 'RS' right slide
"""
def dual_touch_test():
    while True:
        try:
            touch_status = my_dog.dual_touch.read()
            print(f"touch_status: {touch_status}")
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[INFO] Dual touch 테스트 종료")

# ========== rgb ==========
"""
API:
    Pidog.rgb_strip.set_mode(style='breath', color='white', bps=1, brightness=1):

        Set the display mode of the rgb light strip

        - style  str, display style, could be: "breath", "boom", "bark", "speak", "listen"
        - color  str, list or hex, display color,
                  could be: 16-bit rgb value, eg: #a10a0a;
                  or 1*3 list of rgb, eg: [255, 100, 80];
                  or predefined colors:"white", "black", "red", "yellow", "green", "blue", "cyan", "magenta", "pink"
        - bps    float or int, beats per second, this number of style actions executed per second

    Pidog.rgb_strip.close():
        - turn off rgb display


more to see: ../pidog/rgb_strip.py
"""
def rgb_test():
    while True:
        try:
            # style="breath", color="pink"
            my_dog.rgb_strip.set_mode(style="breath", color='pink')
            time.sleep(3)

            # style:"listen", color=[0, 255, 255]
            my_dog.rgb_strip.set_mode(style="listen", color=[0, 255, 255])
            time.sleep(3)

            # style:"boom", color="#a10a0a"
            my_dog.rgb_strip.set_mode(style="boom", color="#a10a0a")
            time.sleep(3)

            # style:"boom", color="#a10a0a", brightness=0.5, bps=2.5
            my_dog.rgb_strip.set_mode(style="boom", color="#a10a0a", bps=2.5, brightness=0.5)
            time.sleep(3)

            # close
            my_dog.rgb_strip.close()
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n[INFO] RGB 테스트 종료")

# ========== sound ==========
"""
API:
    Pidog.speak(name, volume=100)
        play sound effecf in the file "../sounds"
        - name    str, file name of sound effect, no suffix required, eg: "angry"
        - volume  int, volume 0-100, default 100
"""
def sound_test(sound_name):
    try:
        if sound_name in os.listdir('../sounds'):
            sound_name = sound_name.split('.')[0]
            print(f"사운드 재생: {sound_name}")
            my_dog.speak(sound_name)
            time.sleep(3)
    except KeyboardInterrupt:
        print("\n[INFO] Sound 테스트 종료")


# ========== sound direaction ==========
"""
API:
    Pidog.ears.isdetected():
        return    bool, whether the sound direction recognition module has detected the sound

    Pidog.ears.read()
        return    int, the azimuth of the identified sound, 0 ~ 359

more to see: ../pidog/sound_direction.py

"""
def sound_direction_test():
    while True:
        try:
            if my_dog.ears.isdetected():
                direction = my_dog.ears.read()
                print(f"sound direction: {direction}")
        except KeyboardInterrupt:
            print("\n[INFO] Sound direction 테스트 종료")

# ========== main ==========
# ultrasonic, imu, dual touch, rgb, sound, sound direction
actions = [
    "ultrasonic_test",
    "imu_test",
    "dual_touch_test",
    "rgb_test",
    "sound_test",
    "sound_direction_test"
]
def print_menu():
    print("실행할 테스트를 선택하세요:")
    print("1. ultrasonic")
    print("2. imu")
    print("3. dual touch")
    print("4. rgb")
    print("5. sound")
    print("6. sound direction")
    print("q. 전체 종료")
    print("* sound를 실행하기 위해서는 sudo로 파일 실행해야 함.\n")

def main():
    while True:
        try:
            print_menu()
            action = input("테스트 선택 (1~6, q): ")
            if action in ["1", "2", "3", "4", "5", "6"]:
                eval(f"{actions[int(action) - 1]}()")
            elif action == "q":
                break
        except ValueError:
            print("[INFO] 동작 또는 q를 입력하세요.")
            continue
    print("closing ...")
    my_dog.close()
