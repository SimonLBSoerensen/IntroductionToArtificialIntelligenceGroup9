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
from gyro import gyro

#joke.play_joke("start_up")

import time
import motor

sensor_overview = {"v_color": INPUT_2, "r_color": INPUT_3, "ultra": INPUT_4, "gryo": INPUT_1}





infrared_sensor = lego.UltrasonicSensor(sensor_overview["ultra"])
color_sensor_v = lego.ColorSensor(sensor_overview["v_color"])
color_sensor_r = lego.ColorSensor(sensor_overview["r_color"])
gyro_sensor = gyro(sensor_overview["gryo"])


def get_color():
    return [color_sensor_v.color_name, color_sensor_r.color_name]


def print_sensor(comment=""):
    dist = infrared_sensor.distance_centimeters
    color = get_color()
    gyro = gyro_sensor.get_angel_and_rate()

    print(comment, dist, color, gyro)


tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

gyro_sensor.reset()
angel, angel_rate = gyro_sensor.get_angel_and_rate()
old_angel = angel
print("Start angel:", angel)

time.sleep(5)
for angel_diff in [90, 90, 90, 90]:
    tank_drive.on(SpeedPercent(20), SpeedPercent(-20))
    angel, angel_rate = gyro_sensor.get_angel_and_rate()

    while angel-old_angel < angel_diff:
        angel, angel_rate = gyro_sensor.get_angel_and_rate()

        if angel-old_angel >= angel_diff:
            break

        print_sensor()
        #time.sleep(0.1)

    tank_drive.stop()
    print("Pause angel:", angel, "diff:", angel-old_angel)
    old_angel = angel
    time.sleep(5)

tank_drive.stop()

#joke.play_joke("end")
