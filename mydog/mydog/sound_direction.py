#!/usr/bin/env python3

import spidev # SPI 통신을 위한 라이브러리
from gpiozero import OutputDevice, InputDevice


class SoundDirection():
    """
    Class: SoundDirection
    - 음성 방향 인식 클래스
    """
    CS_DELAY_US = 500  # Mhz
    CLOCK_SPEED = 10000000  # 10 MHz

    def __init__(self, busy_pin=6):
        """
        Function: __init__
        - 초기화 함수
        """
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        #
        self.busy = InputDevice(busy_pin, pull_up=False)

    def read(self):
        """
        Function: read
        - SPI를 통해 데이터를 읽어옵니다.
        """
        result = self.spi.xfer2([0, 0, 0, 0, 0, 0], self.CLOCK_SPEED,
                                self.CS_DELAY_US)


        l_val, h_val = result[4:]  # ignore the fist two values
        # print([h_val, l_val])
        if h_val == 255:
            return -1
        else:
            val = (h_val << 8) + l_val
            val = (360 + 160 - val) % 360  # Convert zero
            return val

    def isdetected(self):
        """
        Function: isdetected
        - 음성 인식 여부를 확인합니다.
        """
        return self.busy.value == 0


if __name__ == '__main__':
    from time import sleep
    sd = SoundDirection()
    while True:
        if sd.isdetected():
            print(f"Sound detected at {sd.read()} degrees")
        sleep(0.2)