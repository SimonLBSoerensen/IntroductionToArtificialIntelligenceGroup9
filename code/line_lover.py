import numpy as np
import ev3dev2
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_D, SpeedPercent, MoveTank
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
import threading
import signal
import pickle
from collections import deque

import sys
sys.path.insert(0, "/home/ai1/git/code/lib")
import joke
from gyro import gyro
from fuzzy import FuzzyStraight
from mics import sensor_overview, Hysteresis, SmartLine
from cusum import cusum

#ultrasonicSensor_sensor = lego.UltrasonicSensor(sensor_overview["ultra"])
gyro_sensor = gyro(sensor_overview["gryo"])
histDict = {}


tank_drive = MoveTank(OUTPUT_B, OUTPUT_D)

dist_old = 255

fuzzyStraight = FuzzyStraight()


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


class LineDect:
    def __init__(self, exitFlags, low = 25, high = 30, hist_length=100, threadName="line", threadSleep=0.0, makeHist = False, histDict = {}, histKey = "LineDect"):
        self.color_sensor_l = lego.ColorSensor(sensor_overview["v_color"])
        self.color_sensor_l.mode = 'REF-RAW'
        self.color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])
        self.color_sensor_r.mode = 'REF-RAW'

        self.sensor_left_hist = deque(maxlen=hist_length)
        self.sensor_right_hist = deque(maxlen=hist_length)

        self.was_on_line = False
        self.last_lines = [False, False]
        self.mutex = threading.Lock()
        self.exitFlags = exitFlags
        self.threadName = threadName
        #self.line_th = Thread_runner(self.threadName, self.exitFlags, self.update_hist, threadSleep)
        self.line_th.start()
        self.makeHist = makeHist

        self.smart_line_left = SmartLine()
        self.smart_line_right = SmartLine()

        if makeHist:
            histDict[histKey] = {}
            self.histDict = histDict[histKey]

            self.histDict["r_l"] = []
            self.histDict["r_r"] = []
            self.histDict["line_l"] = []
            self.histDict["line_r"] = []

    def kill(self):
        self.line_th.kill()

    def set_hist(self, lines = None, online = None):
        self.mutex.acquire()
        if lines is not None:
            self.last_lines = lines
        if online is not None:
            self.was_on_line = online
        self.mutex.release()

    def get_hist(self):
        self.mutex.acquire()
        was_on_line = self.was_on_line
        lines = self.last_lines
        self.mutex.release()
        return lines, was_on_line

    def get_ref(self):
        r_l = self.color_sensor_l.reflected_light_intensity
        r_r = self.color_sensor_r.reflected_light_intensity

        if self.makeHist:
            self.histDict["r_l"].append(r_l)
            self.histDict["r_r"].append(r_r)
        return r_l, r_r

    def on_line(self):
        r_l, r_r = self.get_ref()

        line_r = self.smart_line_right.cal_on_line(r_r)
        line_l = self.smart_line_left.cal_on_line(r_l)

        if self.makeHist:
            self.histDict["line_l"].append(line_l)
            self.histDict["line_r"].append(line_r)

        #print([r_l, r_r], [line_l, line_r], [change_l, change_r])
        return [line_l, line_r]

    def on_h_line(self, lines=None):
        if lines is None:
            lines = self.on_line()
        online = lines[0] and lines[1]
        return online

    def update_hist(self):
        lines = self.on_line()
        online = self.on_h_line(lines=lines)
        self.set_hist(lines=lines, online=online)

    def get_last_line(self):
        lines, wasonline = self.get_hist()
        return lines

    def was_line(self):
        lines, wasonline = self.get_hist()
        if wasonline:
            self.set_hist(online=False)
            return True
        else:
            return False


exitFlags = {}
#ld = LineDect(exitFlags, threadSleep=0.001, makeHist=True, histDict=histDict)

angel_offset = 0


def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    for key in exitFlags:
        exitFlags[key] = True
    tank_drive.stop()
    tank_drive.off()
    print("Saving hist to hist.pck")
    with open('hist.pck', 'wb') as handle:
        pickle.dump(histDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    exit(0)
signal.signal(signal.SIGINT, keyboardInterruptHandler)

color_sensor_l = lego.ColorSensor(sensor_overview["v_color"])
color_sensor_l.mode = 'REF-RAW'
color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])
color_sensor_r.mode = 'REF-RAW'
gyro_sensor.reset()

smart_line_left = SmartLine()
smart_line_right = SmartLine()

was_on_line = False

n_h_lines = 3
while True:
    angel = gyro_sensor.get_angel()

    dist = 254

    if dist == 255:
        dist = dist_old
    dist_old = dist

    r_l = color_sensor_l.reflected_light_intensity
    r_r = color_sensor_r.reflected_light_intensity
    line_l = smart_line_left.cal_on_line(r_l)
    line_r = smart_line_right.cal_on_line(r_r)
    on_line = line_l and line_r

    if on_line and not was_on_line:
        n_h_lines -= 1

    if n_h_lines <= 0:
        tank_drive.stop()
        tank_drive.off()
        break

    if not on_line:
        if line_r:
            angel_offset += 1
        elif line_l:
            angel_offset -= 1
        else:
            if angel_offset != 0:
                gyro_sensor.add_offset(angel_offset / 2)
            angel_offset = 0

    if on_line:
        was_on_line = True
    else:
        was_on_line = False

    print(was_on_line, n_h_lines)

    motor_l_pro, motor_r_pro = fuzzyStraight.cal(angel, dist)
    motor_l_pro *= 0.4
    motor_r_pro *= 0.4

    #print([line_l, line_r], was_on_line, angel, angel_offset, [motor_l_pro, motor_r_pro], n_h_lines)

    tank_drive.on(SpeedPercent(motor_l_pro), SpeedPercent(motor_r_pro))
    #print(["{:.2f}".format(motor_l_pro), "{:.2f}".format(motor_r_pro)],
    #      "Angel offset: {}".format(angel_offset), "Lines:", [line_l, line_r],
    #      "n_h_lines:", n_h_lines, "rli:", ld.get_ref())

    time.sleep(0.01)

