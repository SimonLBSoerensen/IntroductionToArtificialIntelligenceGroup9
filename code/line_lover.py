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
from mics import sensor_overview, Hysteresis

ultrasonicSensor_sensor = lego.UltrasonicSensor(sensor_overview["ultra"])
gyro_sensor = gyro(sensor_overview["gryo"])
gyro_sensor.reset()


tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

dist_old = 255

fuzzyStraight = FuzzyStraight()

n_h_lines = 3


class LineDect:
    def __init__(self, low = 10, high = 15):
        self.color_sensor_l = lego.ColorSensor(sensor_overview["v_color"])
        self.color_sensor_l.mode = 'REF-RAW'
        self.color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])
        self.color_sensor_r.mode = 'REF-RAW'
        self.hyst_r = Hysteresis(low, high)
        self.hyst_l = Hysteresis(low, high)
        self.wasOnLine = False
        self.last_lines = None

    def get_ref(self):
        r_l = self.color_sensor_l.reflected_light_intensity
        r_r = self.color_sensor_l.reflected_light_intensity
        return r_l, r_r

    def on_line(self):
        r_l, r_r = self.get_ref()

        line_r = not self.hyst_r.cal(r_r)
        line_l = not self.hyst_r.cal(r_l)
        self.last_lines = [line_r, line_l]
        return [line_r, line_l]

    def on_h_line(self):
        c_l, c_r = self.on_line()
        if not self.wasOnLine:
            self.wasOnLine = c_l and c_r
        return c_l and c_r

    def get_last_line(self):
        return self.last_lines

    def was_line(self):
        if self.wasOnLine:
            self.wasOnLine = False
            return True
        else:
            return False

import threading
import time

exitFlags = {}
class Thread_runner(threading.Thread):
    def __init__(self, thread_name, exitFlags, func, sleep):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.exitFlags = exitFlags
        self.exitFlags[self.thread_name] = False
        self.func = func
        self.sleep = sleep

    def get_kill(self):
        return self.exitFlags[self.thread_name]

    def kill(self):
        self.exitFlags[self.thread_name] = True

    def run(self):
        while True:
            self.func()
            if self.get_kill():
                break
            if self.sleep > 0:
                time.sleep(self.sleep)






ld = LineDect()

kills = {}
line_th = Thread_runner("line", kills, ld.on_h_line, 0)
line_th.start()

angel_offset = 0

while True:
    angel = gyro_sensor.get_angel()

    dist = ultrasonicSensor_sensor.distance_centimeters

    if dist == 255:
        dist = dist_old
    dist_old = dist

    line_l, line_r = ld.get_last_line()

    if line_r:
        angel_offset += 1
    elif line_l:
        angel_offset -= 1
    else:
        gyro_sensor.add_offset(angel_offset/2)
        angel_offset = 0

    if ld.was_line():
        n_h_lines -= 1
    if n_h_lines <= 0:
        tank_drive.stop()
        tank_drive.off()
        break

    motor_l_pro, motor_r_pro = fuzzyStraight.cal(angel, dist)

    #tank_drive.on(SpeedPercent(motor_l_pro),SpeedPercent(motor_r_pro))
    #print(["{:.2f}".format(motor_l_pro), "{:.2f}".format(motor_r_pro)],
    #      "Angel offset: {}".format(angel_offset), "Lines:", [line_l, line_r],
    #      "n_h_lines:", n_h_lines, "rli:", ld.get_ref())

    #time.sleep(0.01)