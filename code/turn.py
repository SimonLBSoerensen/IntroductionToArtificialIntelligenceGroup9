import sys
sys.path.insert(0, "/home/ai1/git/code/lib")

from gyro import gyro
from mics import sensor_overview

gyro_sensor = gyro(sensor_overview["gryo"])
gyro_sensor.reset()




