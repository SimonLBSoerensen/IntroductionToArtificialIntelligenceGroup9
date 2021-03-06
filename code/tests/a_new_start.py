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
import time as pytime
import threading
import signal
import pickle
from collections import deque

import sys
sys.path.insert(0, "/home/ai1/git/code/lib")
import joke
from gyro import gyro
from fuzzy import FuzzyStraight
from mics import sensor_overview, Hysteresis, SmartLine, running_update
from cusum import cusum

#ultrasonicSensor_sensor = lego.UltrasonicSensor(sensor_overview["ultra"])

histDict = {}
histDict["t_r_lr"] = []
histDict["r_l"] = []
histDict["r_l_std"] = []
histDict["r_l_mean"] = []
histDict["r_r"] = []
histDict["line_l"] = []
histDict["line_r"] = []
histDict["t_line_r"] = []
histDict["t_line_l"] = []
write_data = True

exitFlags = {}
angel_offset = 0

test_name = "hist"

def save_data():
    filename = 'hists/'+test_name+'.pck'
    print("Saving hist to "+filename)
    with open(filename, 'wb') as handle:
        pickle.dump(histDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Saving hist done")

def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    ld.kill = True
    for key in exitFlags:
        exitFlags[key] = True
    tank_drive.stop()
    tank_drive.off()
    if write_data:
        save_data()
    exit(0)
signal.signal(signal.SIGINT, keyboardInterruptHandler)

color_sensor_l = lego.ColorSensor(sensor_overview["v_color"])
color_sensor_l.mode = 'REF-RAW'
color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])
color_sensor_r.mode = 'REF-RAW'

gyro_sensor = gyro(sensor_overview["gryo"])
tank_drive = MoveTank(OUTPUT_B, OUTPUT_D)
gyro_sensor.reset()

fuzzyStraight = FuzzyStraight()
dist_old = 255

was_on_line = False

sound = Sound()
print("calibrate white in 3")
pytime.sleep(3)
print("calibrate white now")
color_sensor_l.calibrate_white()
color_sensor_r.calibrate_white()
print("calibrate white done. Running in 3")
pytime.sleep(3)


class lineFllow:
    def __init__(self, gyro_sensor):
        self.angel_offset = 0
        self.gyro_sensor = gyro_sensor

    def cal(self, line_left, line_right):
        if line_left:
            self.angel_offset += 5
        elif line_right:
            self.angel_offset -= 5
        else:
            if self.angel_offset != 0:
                self.gyro_sensor.add_offset(self.angel_offset / 2)
            self.angel_offset = 0

class lineDect:
    def __init__(self, color_sensor_left, color_sensor_right, hist_length = 5):
        self.color_sensor_left = color_sensor_left
        self.color_sensor_right = color_sensor_right

        self.smart_line_left = SmartLine()
        self.smart_line_right = SmartLine()
        self.left_line_hist = deque(maxlen=hist_length)
        self.right_line_hist = deque(maxlen=hist_length)
        self.left_has_been_line = 0
        self.right_has_been_line = 0
        self.kill = False
        self.r_l_hist = deque(maxlen=100)
        tl = threading.Thread(target=self.update_line_l, daemon=True)
        tl.start()
        tr = threading.Thread(target=self.update_line_r, daemon=True)
        tr.start()


    def update_line_r(self):
        self.r_l = self.color_sensor_left.reflected_light_intensity
        self.line_l = False
        self.r_l_N = 1
        self.r_l_mean = self.r_l
        self.r_l_std = 0

        while not self.kill:
            self.r_l = self.color_sensor_left.reflected_light_intensity

            if self.r_l < self.r_l_mean-(self.r_l_std*5):
                self.line_l = True
                if self.r_l_N < 5:
                    self.r_l_N, self.r_l_mean, self.r_l_std = running_update(self.r_l, self.r_l_N,
                                                                             self.r_l_mean, self.r_l_std)
            else:
                self.line_l = False
                self.r_l_N, self.r_l_mean, self.r_l_std = running_update(self.r_l, self.r_l_N,
                                                                     self.r_l_mean, self.r_l_std)


            #self.line_l = self.smart_line_left.cal_on_line(self.r_l)
            #self.left_line_hist.append(self.line_l)
            #self.left_has_been_line = np.sum(self.left_line_hist) > 0
            if write_data:
                histDict["t_line_l"].append(pytime.process_time())
                histDict["line_l"].append(self.line_l)
                histDict["r_l"].append(self.r_l)
                histDict["r_l_std"].append(self.r_l_std)
                histDict["r_l_mean"].append(self.r_l_mean)

    def update_line_l(self):
        while not self.kill:
            self.r_r = self.color_sensor_right.reflected_light_intensity
            self.line_r = self.smart_line_right.cal_on_line(self.r_r)
            self.right_line_hist.append(self.line_r)
            self.right_has_been_line = np.sum(self.right_line_hist) > 0
            if write_data:
                histDict["t_line_r"].append(pytime.process_time())
                histDict["line_r"].append(self.line_r)
                histDict["r_r"].append(self.r_r)

    def get_lines(self):
        return self.line_l, self.line_r

    def h_line(self):
        return self.left_has_been_line and self.right_has_been_line


def motor(pro_times, motor_l_pro = 0, motor_r_pro = 0, do_fuz = True):
    if do_fuz:
        dist = 255
        angel = gyro_sensor.get_angel()
        motor_l_pro, motor_r_pro = fuzzyStraight.cal(angel, dist)
        motor_l_pro *= pro_times
        motor_r_pro *= pro_times

    tank_drive.on(SpeedPercent(motor_l_pro), SpeedPercent(motor_r_pro))


ld = lineDect(color_sensor_l, color_sensor_r)
lf = lineFllow(gyro_sensor)

test_name += "_withlinecal_"

if len(sys.argv) > 1:
    test_name += sys.argv[1]
    motor_pro = int(sys.argv[1])
else:
    motor_pro = 0
histDict["motor_pro"] = motor_pro

motor(0, motor_pro, motor_pro, do_fuz=False)
while True:
    line_l, line_r = ld.get_lines()

    #lf.cal(line_l, line_r)


    #time.sleep(0.01)

if write_data:
    save_data()
tank_drive.stop()
tank_drive.off()
ld.kill = True