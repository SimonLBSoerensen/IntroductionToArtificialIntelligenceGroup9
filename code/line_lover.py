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

touchSensor = lego.TouchSensor(sensor_overview["touch"])

tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

dist_old = 255

fuzzyStraight = FuzzyStraight()

while True:
    angel = gyro_sensor.get_angel()

    dist = ultrasonicSensor_sensor.distance_centimeters

    if dist == 255:
        dist = dist_old
    dist_old = dist

    motor_l_pro, motor_r_pro = fuzzyStraight.cal(angel, dist)

    tank_drive.on(SpeedPercent(motor_l_pro),SpeedPercent(motor_r_pro))

    print(["{:.2f}".format(motor_l_pro), "{:.2f}".format(motor_r_pro)])

    if touchSensor.is_pressed:
        stop = True

        touchtime = time.time()

        tank_drive.stop()
        tank_drive.off()

        while touchSensor.is_pressed:
            if round(time.time() - touchtime) > 1:
                stop = False

        if stop:
            break
        else:
            gyro_sensor.reset()
