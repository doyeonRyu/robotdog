#!/usr/bin/env python3
# ========== 카메라 & face detection테스트 ==========
"""
web-cam, color detection, face detection, take photos and so on.

github: https://github.com/sunfounder/vilib.git

more examples to see: ~/vilib/examples/
"""
from dog import Vilib
import time

try:
    # start camera
    # vflip: image vertical flip, hflip:horizontal flip
    Vilib.camera_start(vflip=False,hflip=False)
    # display camera screen
    # local: desktop window display, web: webcam display
    Vilib.display(local=True,web=True) 
    # enable face detection
    Vilib.face_detect_switch(True)
    # wait for vilib launch
    time.sleep(1)
    print('')

    while True:
        n = Vilib.detect_obj_parameter['human_n']
        print(f"\r \033[032m{n:^3}\033[m 얼굴 인식됨.", end='', flush=True)
        time.sleep(1)
        print("\r \033[032m   \033[m 얼굴 인식됨.", end='', flush=True)
        time.sleep(0.1)


except KeyboardInterrupt:
    pass
except Exception as e:
    print(f"\033[31mERROR: {e}\033[m")
finally:
    print("")
    Vilib.camera_close()
