import ev3dev2
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_4
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




infrared_sensor = lego.UltrasonicSensor()

#tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)
#tank_drive.stop()

while True:
    print(infrared_sensor.distance_centimeters())
    time.sleep(0.5)



joke.play_joke("end")
