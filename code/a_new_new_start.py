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
from datetime import datetime
import signal
from collections import deque
import pickle
import sys
sys.path.insert(0, "/home/ai1/git/code/lib")
from gyro import gyro

# Handling of kill signal
histDict = {}
histDict["rli_left"] = []
histDict["rli_right"] = []
histDict["line_left"] = []
histDict["line_right"] = []

def save_data():
    d = datetime.now()
    timestring = d.strftime("%D-%H-%M-%S")
    filename = 'hists/'+timestring+'.pck'
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
    exit(0)
signal.signal(signal.SIGINT, keyboardInterruptHandler)

#Color censors
color_sensor_l = lego.ColorSensor(sensor_overview["v_color"])
color_sensor_l.mode = 'REF-RAW'
color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])
color_sensor_r.mode = 'REF-RAW'

#Gyro sensor
gyro_sensor = gyro(sensor_overview["gryo"])
gyro_sensor.reset()

# Motor drive
tank_drive = MoveTank(OUTPUT_B, OUTPUT_D)

#Hist for ligth intensiti
hist_length = 100
rli_hist = [deque(maxlen=hist_length), deque(maxlen=hist_length)]
def append_to_hist(rli_left, rli_right):
    if rli_left is not None:
        rli_hist[0].append(rli_left)
    if rli_right is not None:
        rli_hist[1].append(rli_right)

def get_sum_hist():
    return sum(rli_hist[0]), sum(rli_hist[1])

def get_rli():
    rli_left = color_sensor_l.reflected_light_intensity
    rli_right = color_sensor_r.reflected_light_intensity
    return rli_left, rli_right

def get_lines(rli_left, rli_right, pro = 0.2):
    rli_sum_left, rli_sum_right = get_sum_hist()


    line_left = True if rli_left*len(rli_hist[0]) < rli_sum_left*pro else False
    line_right = True if rli_right*len(rli_hist[1]) < rli_sum_right*pro else False

    return line_left, line_right

#Calibrate light sensor
color_sensor_l.calibrate_white()
color_sensor_r.calibrate_white()

for _ in range(hist_length):
    rli_left, rli_right = get_rli()
    append_to_hist(rli_left, rli_right)

tank_drive.on(SpeedPercent(30), SpeedPercent(30))
while True:
    rli_left, rli_right = get_rli()
    line_left, line_right = get_lines(rli_left, rli_right, pro=0.2)
    if not line_left:
        append_to_hist(rli_left, None)
    if not line_right:
        append_to_hist(rli_right, None)

    histDict["rli_left"].append(rli_left)
    histDict["rli_right"].append(rli_right)
    histDict["line_left"].append(line_left)
    histDict["line_right"].append(line_right)

    print(line_left, line_right)








