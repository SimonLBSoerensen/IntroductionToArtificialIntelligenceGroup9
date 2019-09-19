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
sensor_overview = {"v_color": INPUT_2, "r_color": INPUT_3, "ultra": INPUT_4, "gryo": INPUT_1}
class gyro:
    def __init__(self, gyrosensor_pin, mode='GYRO-G&A'):
        self.gyro_sensor = lego.GyroSensor(gyrosensor_pin)
        self.gyro_sensor.mode = mode
        self.offset = 0

    def reset(self):
        self.offset = self.gyro_sensor.angle

    def get_angel(self):
        return self.gyro_sensor.angle - self.offset

    def get_angel_and_rate(self):
        gyro_angel, gyro_rate = self.gyro_sensor.angle_and_rate
        gyro_angel -= self.offset
        return [gyro_angel, gyro_rate]


def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


motor_l_samples = np.load("/home/ai1/git/code/tests/motor_l_samples.npy")
motor_r_samples = np.load("/home/ai1/git/code/tests/motor_r_samples.npy")
angel_sample_space = np.load("/home/ai1/git/code/tests/angel_sample_space.npy")
dist_sample_space = np.load("/home/ai1/git/code/tests/dist_sample_space.npy")

ultrasonicSensor_sensor = lego.UltrasonicSensor(sensor_overview["ultra"])
gyro_sensor = gyro(sensor_overview["gryo"])
gyro_sensor.reset()

tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

dist_old = 255

while True:
    angel = gyro_sensor.get_angel()
    dist = ultrasonicSensor_sensor.distance_centimeters

    if dist == 255:
        dist = dist_old
    dist_old = dist

    angel_idx = find_nearest(angel_sample_space, angel)
    dist_idx = find_nearest(dist_sample_space, dist)

    angel_round = angel_sample_space[angel_idx]
    dist_round = dist_sample_space[dist_idx]

    motor_l_pro = motor_l_samples[angel_idx, dist_idx]
    motor_r_pro = motor_r_samples[angel_idx, dist_idx]

    tank_drive.on(SpeedPercent(motor_l_pro),SpeedPercent(motor_r_pro))

    print([angel, angel_round], [dist, dist_round], [motor_l_pro, motor_r_pro])