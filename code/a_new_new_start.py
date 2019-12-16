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
        return base_pro * change, base_pro * (1 - lower_pro)
    else:
        return base_pro, base_pro


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

    wait_max_time = 20
    print("Press witin {} sec for ready for reset else exit will hapen".format(wait_max_time))
    hasBeenPreds = False
    now = datetime.now()
    while (datetime.now() - now).seconds < wait_max_time:
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

def get_diff_s(time_start, time_now = time.clock()):
    return time_now - time_start

#Run time
base_drive_pro = 30
base_backing_drive_pro = -30
turn_speed = 20
min_time_before_hline = 0.5


states = [
    ["F", 1],
    ["L"],
    ["F", 1],
    ["R"],
    ["F", 1],
    ["T"],
]

states = [
    ["F", 1], #F1, L, P, F2, R, P, F3, L, P, F3, L, P, F3, R, P, F3
    ["L"],
    ["P"],
    ["F", 2],
    ["R"],
    ["P"],
    ["F", 3],
    ["L"],
    ["P"],
    ["F", 3],
    ["L"],
    ["P"],
    ["F", 3],
    ["R"],
    ["P"],
    ["F", 3]
]

#states_string = "F2, T, F2, T, F1, F3, L, F1, L, F4, L, F2, R, F1, R, F1, R, F4, F1, T, F4, F1, L, F1, T, F1, T, F1, T, F1, R, F5, L, F1, L, F3, F1, L, F3, F1, T, F1, F1, F1, F1, T, F2, R, F1, T, F1, R, F1, F1, T, F3, F1, R, F1, F3, T, F1, F3, L, F4, T, F2, L, F1, T, F1, L, F2, T, F4, T, F2, F1, L, F1, T, F2, F1, L, F1, R, F2, R, F1, T, F1, L, F2, F1, F1, T, F2, F2, R, F2, R, F1, F1, T, F1, F1, T, F2, R, F1, L, F2, F1, T, F4, F1, T, F2, F3, L, F1, L, F1, L, F2, R, F2, R, F1, R, F3, L, F1, T, F1, R, F4, L, F1, R, F1, T, F2, L, F1, F1, T, F1, T, F1, T, F2, R, F1, F1, T, F1, F3, L, F4, R, F4, T, F3, T, F1, F2, R, F2, R, F1, L, F1, T, F3, F1, L, F1, L, F1, L, F1, L, F1, L, F1, L, F1, T, F1, T, F1, L, F1, T, F2, F1, T, F3, L,"
#states_string = "F1, L, P, F2, R, P, F3, L, P, F3, L, P, F3, R, P, F3,"
states_string = "F1, R, F1, R, F1, R, F1, R, F1, L, F1, L, F1, L, F1, L, F1, T, O," #8 drive
#states_string = "F2,T,F2,T,O" #T test
#states_string = "F1,R,F1,R,F1,R,F1,R,O" #R test
#states_string = "F1,L,F1,L,F1,L,F1,L,O" #L test
#states_string = "B4, T, B4, T, O" #Back test
#states_string = "F4,R,F4,R,F4,R,F4,R,O" #F test


state_times = {}
states = []
temp = None
for i in range(len(states_string)):
    if states_string[i] == " ":
        continue

    if states_string[i] == ",":
        if temp is not None:
            states.append(temp)
        temp = None
    else:
        if temp is None:
            temp = [states_string[i]]
        else:
            temp.append(int(states_string[i]))

if temp is not None:
    states.append(temp)


for i in range(len(states)):
    if len(states[i]) < 2:
        states[i].append(None)

states_index = 0

state = states[states_index][0]
state_arg = states[states_index][1]
state_arg_org = states[states_index][1]
state_start_time = time.clock()
state_memory = None
old_state = None
print("Start state is:", state, state_arg)
while True:
    while bnt.is_pressed:
        time.sleep(0.1)
    print("Press to calibrate")
    while not bnt.is_pressed:
        time.sleep(0.1)

    print("Calibrateing")
    upstart_predsiters()

    print("Reset state")
    states_index = 0
    state = states[states_index][0]
    state_arg = states[states_index][1]
    state_memory = None

    if bnt.is_pressed:
        print("Release button")

        while bnt.is_pressed:
            time.sleep(0.1)

    print("Press to start")
    while not bnt.is_pressed:
        time.sleep(0.1)
    while bnt.is_pressed:
        time.sleep(0.1)

    rep_time = time.clock()
    rep_times = []

    while True:
        go_to_next_state = False
        left_pro, right_pro = (0, 0)

        rli_left, rli_right = get_rli()
        line_left, line_right = get_lines(rli_left, rli_right, pro=0.40)
        h_line, start_on_hline = get_hline(line_left, line_right)
        if state == "P":
            if not h_line:
                stop_drive(drive_off=False)
                go_to_next_state = True
            else:
                left_pro, right_pro = lineflwoere_F(line_left, line_right, base_drive_pro, change=1.9, lower_pro=0.1)

        if state == "PB":
            if not h_line:
                stop_drive(drive_off=False)
                go_to_next_state = True
            else:
                left_pro, right_pro = lineflwoere_B(line_left, line_right, base_backing_drive_pro,
                                                    change=1.30, lower_pro=0.1)

        elif state == "O":
            states_index = -1
            go_to_next_state = True
            rep_times.append(time.clock() - rep_time)
            rep_time = time.clock()

        elif state == "F":
            state_run_time = time.clock() - state_start_time

            if start_on_hline and state_run_time > min_time_before_hline:
                state_arg -= 1
            elif start_on_hline and state_run_time < min_time_before_hline:
                print("Hline seen but state time is:", state_run_time, state_start_time, time.clock())

            if state_arg == 0:
                stop_drive(drive_off=False)
                go_to_next_state = True
            else:
                left_pro, right_pro = lineflwoere_F(line_left, line_right, base_drive_pro, change=1.9, lower_pro=0.15)

        elif state == "B":
            state_run_time = time.clock() - state_start_time

            if start_on_hline and state_run_time > min_time_before_hline:
                state_arg -= 1
            elif start_on_hline and state_run_time < min_time_before_hline:
                print("Hline seen but state time is:", state_run_time, state_start_time, time.clock())

            if state_arg == 0:
                stop_drive(drive_off=False)
                go_to_next_state = True
            else:
                left_pro, right_pro = lineflwoere_B(line_left, line_right, base_backing_drive_pro,
                                                    change=1.20, lower_pro=0.1)

        elif state == "R" or state == "L":
            if state == "R":
                temp = line_right
                line_right = line_left
                line_left = temp

            if state_memory is None:
                print(datetime.now(), state, state_memory)
                left_pro, right_pro = (turn_speed, turn_speed)
                state_memory = ["pre_turn", 400 * 1000, datetime.now()]
                print(datetime.now(), state, "to", state_memory)

            elif state_memory[0] == "pre_turn":
                if state_memory[1] > (datetime.now() - state_memory[2]).microseconds:
                    left_pro, right_pro = (turn_speed, turn_speed)
                else:
                    left_pro, right_pro = (0, 0)
                    print(datetime.now(), state, state_memory)
                    state_memory = ["start_turn"]
                    print(datetime.now(), state, "to", state_memory)

            elif state_memory[0] == "start_turn" and line_left and (not line_right):
                print(datetime.now(), state, state_memory)
                state_memory = ["mid_turn"]
                print(datetime.now(), state, "to", state_memory)
            elif state_memory[0] == "start_turn":
                left_pro, right_pro = (turn_speed, -turn_speed)

            elif state_memory[0] == "mid_turn" and (not line_left) and line_right:
                print(datetime.now(), state, state_memory)
                state_memory = ["end_turn"]
                print(datetime.now(), state, "to", state_memory)
            elif state_memory[0] == "mid_turn":
                left_pro, right_pro = (turn_speed, -turn_speed)

            elif state_memory[0] == "end_turn" and (not line_right):
                print(datetime.now(), state, state_memory)
                state_memory = ["post_turn", 150 * 1000, datetime.now()]
                print(datetime.now(), state, "to", state_memory)
            elif state_memory[0] == "end_turn":
                left_pro, right_pro = (turn_speed, -turn_speed)

            elif state_memory[0] == "post_turn":
                if state_memory[1] > (datetime.now() - state_memory[2]).microseconds:
                    left_pro, right_pro = (turn_speed, -turn_speed)
                else:
                    left_pro, right_pro = (0, 0)
                    print(datetime.now(), state, state_memory)
                    stop_drive(drive_off=False)
                    go_to_next_state = True
                    print(datetime.now(), state, "done", state_memory)

            if state == "R":
                temp = right_pro
                right_pro = left_pro
                left_pro = temp

        elif state == "T":
            if state_memory is None:
                print(datetime.now(), state, state_memory)
                left_pro, right_pro = (turn_speed, turn_speed)
                state_memory = ["pre_turn", 400 * 1000, datetime.now()]
                print(datetime.now(), state, "to", state_memory)

            elif state_memory[0] == "pre_turn":
                if state_memory[1] > (datetime.now() - state_memory[2]).microseconds:
                    left_pro, right_pro = (turn_speed, turn_speed)
                else:
                    left_pro, right_pro = (0, 0)
                    print(datetime.now(), state, state_memory)
                    state_memory = ["start_turn", True] #True is that it is in the first part
                    print(datetime.now(), state, "to", state_memory)

            elif state_memory[0] == "start_turn" and line_left and (not line_right):
                print(datetime.now(), state, state_memory)

                state_memory = ["mid_turn", state_memory[1]]
                print(datetime.now(), state, "to", state_memory)
            elif state_memory[0] == "start_turn":
                left_pro, right_pro = (turn_speed, -turn_speed)

            elif state_memory[0] == "mid_turn" and (not line_left) and line_right:
                print(datetime.now(), state, state_memory)
                state_memory = ["end_turn",state_memory[1]]
                print(datetime.now(), state, "to", state_memory)
            elif state_memory[0] == "mid_turn":
                left_pro, right_pro = (turn_speed, -turn_speed)

            elif state_memory[0] == "end_turn" and (not line_right):
                print(datetime.now(), state, state_memory)

                if state_memory[1]:
                    state_memory = ["start_turn", False]
                    print(datetime.now(), state, "next part", state_memory)
                else:
                    print(datetime.now(), state, state_memory)
                    state_memory = ["post_turn", 150 * 1000, datetime.now()]
                    print(datetime.now(), state, "to", state_memory)

            elif state_memory[0] == "end_turn":
                left_pro, right_pro = (turn_speed, -turn_speed)

            elif state_memory[0] == "post_turn":
                if state_memory[1] > (datetime.now() - state_memory[2]).microseconds:
                    left_pro, right_pro = (turn_speed, -turn_speed)
                else:
                    left_pro, right_pro = (0, 0)
                    print(datetime.now(), state, state_memory)
                    stop_drive(drive_off=False)
                    go_to_next_state = True
                    print(datetime.now(), state, "done", state_memory)

        if go_to_next_state:
            print("Finding next state, last took:", time.clock() - state_start_time,"s")
            if state not in state_times:
                state_times[state] = []
            state_times[state].append([state_arg_org, old_state, time.clock() - state_start_time])

            states_index += 1
            if states_index >= len(states):
                #End of states
                print("Done with states", line_left, line_right, h_line, start_on_hline)
                break

            next_state = states[states_index][0]

            if h_line and (next_state == "B" or next_state == "F"):
                print("Handling on h line")
                if next_state == "B":
                    state = "PB"
                    states_index -= 1
                if next_state == "F":
                    state = "P"
                    states_index -= 1
            else:
                #Load new state
                print("Loading new state")
                old_state = state
                state = states[states_index][0]
                state_arg = states[states_index][1]
                state_arg_org = states[states_index][1]
                state_start_time = time.clock()
                state_memory = None

            print("New state is:", state, state_arg, state_start_time)


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

        if bnt.is_pressed:
            stop_drive(drive_off=False)
            print(state_times)
            print("Reptimes:", rep_times)
            break










killProcs()
