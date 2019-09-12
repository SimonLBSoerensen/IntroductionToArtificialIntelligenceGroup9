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

from collections import deque
import time
import threading
import socket


udp_packet = None
def rec_UDP():
    global udp_packet

    while True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('10.0.0.15', 5000))
        data, addr = sock.recvfrom(1024)
        udp_packet = data


listen_UDP = threading.Thread(target=rec_UDP)
listen_UDP.start()

#tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

# drive in a turn for 5 rotations of the outer motor
# the first two parameters can be unit classes or percentages.
#tank_drive.on_for_rotations(SpeedPercent(50), SpeedPercent(75), 10)

# drive in a different turn for 3 seconds
#tank_drive.on_for_seconds(SpeedPercent(60), SpeedPercent(30), 3)

infrared_sensor = lego.UltrasonicSensor()

disp = display.Display()

dists = deque(maxlen=5)

tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

bt = button.Button()



while True:
    dist = infrared_sensor.distance_centimeters
    dists.append(dist)
    avg_dist = sum(dists)/len(dists)

    avg_dist = min(avg_dist, 100)
    avg_dist = max(avg_dist, 0)
    avg_dist = -avg_dist

    tank_drive.on(avg_dist, avg_dist)

    print(avg_dist, udp_packet)

    if bt.ENTER:
        break
    if udp_packet == b"exit":
        break

    time.sleep(0.1)

tank_drive.stop()