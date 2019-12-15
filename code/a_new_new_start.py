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
sys.path.insert(0, "/home/ai1/git/IntroductionToArtificialIntelligenceGroup9/code/lib")
from mics import sensor_overview
from gyro import gyro
from fuzzy import FuzzyStraight

import time

# Handling of kill signal
histDict = {}

def add_to_hist(name, data):
    if name in histDict:
        histDict[name].append(data)
    else:
        histDict[name] = [data]


def stop_drive(drive_off = True):
    tank_drive.stop()
    if drive_off:
        tank_drive.off()

def killProcs():
    save_data()
    stop_drive()


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
#gyro_sensor = gyro(sensor_overview["gryo"])
#gyro_sensor.reset()

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


def get_hline(line_left, line_right, pro=0.2):

    if not line_left:
        append_to_hist(rli_left, None)
    if not line_right:
        append_to_hist(None, rli_right)

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

# Line flowere state mashine

def lineflwoere_F(line_left, line_right, base_pro, change, lower_pro):
    if line_left and not line_right:
        return base_pro * (1-lower_pro), base_pro * change
    elif not line_left and line_right:
        return base_pro * change, base_pro * (1-lower_pro)
    else:
        return base_pro, base_pro

def lineflwoere_B(line_left, line_right, base_pro, change, lower_pro):
    if line_left and not line_right:
        return base_pro * (1 - lower_pro), base_pro * change
    elif not line_left and line_right:
        return base_pro*change, base_pro * (1 - lower_pro)
    else:
        return base_pro, base_pro


def upstart_predsiters():
    get_hline.on_hline = False

    #Calibrate light sensor
    print("Sensor calibrate white")
    color_sensor_l.calibrate_white()
    color_sensor_r.calibrate_white()

    for _ in range(hist_length):
        rli_left, rli_right = get_rli()
        append_to_hist(rli_left, rli_right)

    print("Done calibrate white")

    base_drive_pro = 60
    tank_drive.on(SpeedPercent(base_drive_pro), SpeedPercent(base_drive_pro))


def buttonHandle():
    # None = 0
    # exit = 1
    # restart = 2

    if not bnt.is_pressed:
        return 0
    print("Button press")
    stop_drive(drive_off=False)
    print("Release button")
    while bnt.is_pressed:
        time.sleep(0.1)

    print("Press witin 2 sec for ready for reset else exit will hapen")
    hasBeenPreds = False
    now = datetime.now()
    while (datetime.now() - now).seconds < 2:
        if bnt.is_pressed:
            hasBeenPreds = True
            print("Reset pressed")
            break
        time.sleep(0.1)

    if hasBeenPreds:
        return 2

    print("No pressd exit will happen")
    return 1

def trim(val, min, max):
    if min <= val <= max:
        return val
    elif val > max:
        return max
    else:
        return min



#Run time

base_drive_pro = 60
turn_speed = 40
upstart_predsiters()

state = "R"
state_arg = 3
state_memory = None

while True:
    go_to_next_state = False
    left_pro, right_pro = (0, 0)

    rli_left, rli_right = get_rli()
    line_left, line_right = get_lines(rli_left, rli_right, pro=0.2)
    h_line, start_on_hline = get_hline(line_left, line_right)

    if state == "F":
        if start_on_hline:
            state_arg -= 1

        if state_arg == 0:
            stop_drive(drive_off=False)
            go_to_next_state = True
        else:
            left_pro, right_pro = lineflwoere_F(line_left, line_right, base_drive_pro, change=1.9, lower_pro=0.05)

    elif state == "B":
        if start_on_hline:
            state_arg -= 1

        if state_arg == 0:
            stop_drive(drive_off=False)
            go_to_next_state = True
        else:
            left_pro, right_pro = lineflwoere_B(line_left, line_right, base_drive_pro, change = 1.05, lower_pro=0.02)

    elif state == "R":
        if state_memory is None:
            state_memory = "start"


        if state_memory == "start":
            print(state, state_memory)
            left_pro, right_pro = (turn_speed, -turn_speed)

        elif line_left and not line_right:
            print(state, state_memory)
            state_memory = "mid_turn"

        elif state_memory == "mid_turn" and not line_left and line_right:
            print(state, state_memory)
            state_memory = "end_turn"
            left_pro, right_pro = (turn_speed * (1-0.2), -turn_speed * (1-0.2))

        elif state_memory == "end_turn" and not line_right:
            print(state, state_memory)
            stop_drive(drive_off=False)
            go_to_next_state = True



    if go_to_next_state:
        state_memory = None
        pass
    else:
        left_pro = trim(left_pro, -100, 100)
        right_pro = trim(right_pro, -100, 100)
        tank_drive.on(SpeedPercent(left_pro), SpeedPercent(right_pro))

    add_to_hist("rli_left", rli_left)
    add_to_hist("rli_right", rli_right)
    add_to_hist("line_left", line_left)
    add_to_hist("line_right", line_right)
    add_to_hist("h_line", h_line)
    add_to_hist("start_on_hline", start_on_hline)
    add_to_hist("left_pro", left_pro)
    add_to_hist("right_pro", right_pro)


    event = buttonHandle()
    if event == 1:
        killProcs()
        break
    elif event == 2:
        upstart_predsiters()







