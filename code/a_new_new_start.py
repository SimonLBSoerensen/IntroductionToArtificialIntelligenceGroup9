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
from mics import sensor_overview
from gyro import gyro
from fuzzy import FuzzyStraight

# Handling of kill signal
histDict = {}
histDict["rli_left"] = []
histDict["rli_right"] = []
histDict["line_left"] = []
histDict["line_right"] = []
histDict["h_line"] = []
histDict["start_on_hline"] = []
histDict["angel"] = []

def killProcs():
    save_data()
    tank_drive.stop()
    tank_drive.off()

def save_data():
    d = datetime.now()
    timestring = d.strftime("%d-%m-%y-%H-%M-%S")
    filename = 'hists/'+timestring+'.pck'
    print("Saving hist to "+filename)
    with open(filename, 'wb') as handle:
        pickle.dump(histDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("Saving hist done")

def keyboardInterruptHandler(signal, frame):
    print("KeyboardInterrupt (ID: {}) has been caught. Cleaning up...".format(signal))
    killProcs()
    exit(0)
signal.signal(signal.SIGINT, keyboardInterruptHandler)

#Color censors
color_sensor_l = lego.ColorSensor(sensor_overview["v_color"])
color_sensor_l.mode = 'REF-RAW'
color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])
color_sensor_r.mode = 'REF-RAW'

#Button
bnt = TouchSensor(sensor_overview["touch"])

#Gyro sensor
gyro_sensor = gyro(sensor_overview["gryo"])
gyro_sensor.reset()

# Motor drive
tank_drive = MoveTank(OUTPUT_B, OUTPUT_D)
fuzzyStraight = FuzzyStraight()
dist_old = 255
def motor(pro_times, motor_l_pro = 0, motor_r_pro = 0, do_fuz = True):
    if do_fuz:
        dist = 255
        angel = gyro_sensor.get_angel()
        histDict["angel"].append(angel)
        motor_l_pro, motor_r_pro = fuzzyStraight.cal(angel, dist)
        motor_l_pro *= pro_times
        motor_r_pro *= pro_times

    tank_drive.on(SpeedPercent(motor_l_pro), SpeedPercent(motor_r_pro))

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
lf = lineFllow(gyro_sensor)


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


def get_hline(line_left, line_right, pro=0.2):

    if not line_left:
        append_to_hist(rli_left, None)
    if not line_right:
        append_to_hist(rli_right, None)

    h_line = line_left and line_right

    start_on_hline = False
    if get_hline.on_hline and h_line:
        start_on_hline = False
    elif h_line:
        start_on_hline = True
        get_hline.on_hline = True
    elif not h_line:
        get_hline.on_hline = False

    return h_line, start_on_hline
get_hline.on_hline = False



#Calibrate light sensor
print("Sensor calibrate white")
color_sensor_l.calibrate_white()
color_sensor_r.calibrate_white()

for _ in range(hist_length):
    rli_left, rli_right = get_rli()
    append_to_hist(rli_left, rli_right)

print("Done calibrate white")

tank_drive.on(SpeedPercent(60), SpeedPercent(60))
while True:
    rli_left, rli_right = get_rli()
    line_left, line_right = get_lines(rli_left, rli_right, pro=0.2)
    h_line, start_on_hline = get_hline(line_left, line_right)
    #lf.cal(line_left, line_right)
    motor(0.8, do_fuz=True)


    histDict["rli_left"].append(rli_left)
    histDict["rli_right"].append(rli_right)
    histDict["line_left"].append(line_left)
    histDict["line_right"].append(line_right)
    histDict["h_line"].append(h_line)
    histDict["start_on_hline"].append(start_on_hline)
    #print(line_left, line_right)

    if bnt.is_pressed:
        killProcs()
        break








