import ev3dev2
from ev3dev2 import motor
from ev3dev2 import sensor
from ev3dev2 import display
from ev3dev2.sensor import lego
infrared_sensor = lego.InfraredSensor(sensor.INPUT_4)

disp = display.Display()

while True:
    dist = infrared_sensor.distance()
    disp.text_grid(dist)

