import ev3dev2
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2 import sensor
from ev3dev2 import display
from ev3dev2.sensor import lego
import ev3dev2.fonts as fonts
from ev3dev2 import button

import time

def frange(start, end, step = 1, include_end = False):
    nums = []
    num = start
    while num < end:
        nums.append(num)
        num += step
    if include_end:
        nums.append(end)
    return nums


def morto_curve(time_step, start, end, std_slope = 10):
    """
    :param time_step is between 0 and 1 and resepent how fare the time is from 0=start to 1=end:
    :param start:
    :param end:
    :return:
    """
    import math
    if time_step < 0:
        return start
    elif time_step > 1:
        return end

    def std_motor_cureve(x):
        return 1 / (1 + math.exp(-1 * std_slope * (x - 0.5)))

    std_motor_pro = std_motor_cureve(time_step)

    diff = end - start
    diff *= std_motor_pro

    motor_pro = start + diff

    return motor_pro


def motor_cheange_sec(start, end, sec, steps):
    sec_par_step = sec / steps
    sec_std = 1/sec

    motor_pro = []

    for step in range(steps):
        sec_step = sec_par_step * step
        sec_step_std = sec_std * sec_step
        motor_pro.append(morto_curve(sec_step_std, start, end))

    return motor_pro, sec_par_step



infrared_sensor = lego.UltrasonicSensor()

tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

motor_pro_steps, sec_par_step = motor_cheange_sec(0, 50, 5, 100)


for pro_step in motor_pro_steps:
    dist = infrared_sensor.distance_centimeters
    print(dist)

    pro_step = SpeedPercent(pro_step)

    tank_drive.on(pro_step, pro_step)

    time.sleep(sec_par_step)


tank_drive.stop()