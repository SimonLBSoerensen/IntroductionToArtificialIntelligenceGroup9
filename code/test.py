import ev3dev2
from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_D, SpeedPercent, MoveTank
from ev3dev2.sensor import INPUT_1, INPUT_4
from ev3dev2.sensor.lego import TouchSensor
from ev3dev2.led import Leds
from ev3dev2 import sensor
from ev3dev2 import display
from ev3dev2.sensor import lego
import ev3dev2.fonts as fonts

from collections import deque
import time

#tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

# drive in a turn for 5 rotations of the outer motor
# the first two parameters can be unit classes or percentages.
#tank_drive.on_for_rotations(SpeedPercent(50), SpeedPercent(75), 10)

# drive in a different turn for 3 seconds
#tank_drive.on_for_seconds(SpeedPercent(60), SpeedPercent(30), 3)

infrared_sensor = lego.UltrasonicSensor()

disp = display.Display()


dists = deque(maxlen=50)

while True:
    dist = infrared_sensor.distance_centimeters
    dists.append(dist)
    avg_dist = sum(dists)/len(dists)
    print(avg_dist)
    disp.draw.text((10,10), avg_dist, font=fonts.load('luBS14'))
    time.sleep(0.1)
