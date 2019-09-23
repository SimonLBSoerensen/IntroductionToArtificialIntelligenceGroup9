import numpy as np
import ev3dev2
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_4, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2 import sensor
from ev3dev2 import display
from ev3dev2.sensor import lego
import ev3dev2.fonts as fonts
from ev3dev2 import button
from ev3dev2.sound import Sound
import time


import sys
sys.path.insert(0, "/home/ai1/git/code/lib")
import joke
from gyro import gyro
from fuzzy import FuzzyStraight
from mics import sensor_overview

ultrasonicSensor_sensor = lego.UltrasonicSensor(sensor_overview["ultra"])
gyro_sensor = gyro(sensor_overview["gryo"])
gyro_sensor.reset()


tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

dist_old = 255

fuzzyStraight = FuzzyStraight()

n_h_lines = 3


class LineDect:
    def __init__(self):
        self.color_sensor_v = lego.ColorSensor(sensor_overview["v_color"])
        self.color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])

    def on_line(self):
        return [self.color_sensor_v.color_name == "Black", self.color_sensor_r.color_name == "Black"]

    def on_h_line(self):
        c_l, c_r = self.on_line()
        return c_l and c_r


ld = LineDect()

angel_offset = 0

while True:
    angel = gyro_sensor.get_angel()

    dist = ultrasonicSensor_sensor.distance_centimeters

    if dist == 255:
        dist = dist_old
    dist_old = dist

    line_l, line_r = ld.on_line()

    if line_r:
        angel_offset += 1
    elif line_l:
        angel_offset -= 1
    else:
        gyro_sensor.add_offset(angel_offset/2)
        angel_offset = 0

    if ld.on_h_line():
        if n_h_lines <= 0:
            tank_drive.stop()
            tank_drive.off()
            break
        else:
            n_h_lines -= 1

    motor_l_pro, motor_r_pro = fuzzyStraight.cal(angel, dist)

    tank_drive.on(SpeedPercent(motor_l_pro),SpeedPercent(motor_r_pro))
    print(["{:.2f}".format(motor_l_pro), "{:.2f}".format(motor_r_pro)],
          "Angel offset: {}".format(angel_offset), "Lines:", [line_l, line_r])

    time.sleep(0.01)