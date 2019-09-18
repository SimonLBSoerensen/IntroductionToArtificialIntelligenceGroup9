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

import sys
sys.path.insert(0, "/home/ai1/git/code/lib")
import joke

joke.play_joke("start_up")

import time
import motor

sensor_overwie = {"v_color": INPUT_2, "r_color": INPUT_3, "ultra": INPUT_4, "gryo": INPUT_1}


infrared_sensor = lego.UltrasonicSensor(sensor_overwie["ultra"])
color_sensor_v = lego.ColorSensor(sensor_overwie["v_color"])
color_sensor_r = lego.ColorSensor(sensor_overwie["r_color"])


def get_color():
    return [color_sensor_v.color_name, color_sensor_r.color_name]


#tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)
#tank_drive.stop()

while True:
    dist = infrared_sensor.distance_centimeters
    color = get_color()
    if dist < 4:
        print("Grep:", dist, ". Color: ", color)
    else:
        print("Not grep:", dist, ". Color: ", color)



    time.sleep(0.2)



joke.play_joke("end")
