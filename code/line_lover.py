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
sensor_overview = {"v_color": INPUT_2, "r_color": INPUT_3, "ultra": INPUT_4, "gryo": INPUT_1, "touch": INPUT_3}

def restart():
    import os
    import sys
    os.startfile(sys.argv[0])
    sys.exit()

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

def save_dict_to_file(dict , filename):
    import pickle
    with open(filename, 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_dict_from_file(filename):
    import pickle
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]


motor_l_samples = np.load("/home/ai1/git/code/tests/motor_l_samples.npy")
motor_r_samples = np.load("/home/ai1/git/code/tests/motor_r_samples.npy")
angel_sample_space = np.load("/home/ai1/git/code/tests/angel_sample_space.npy")
dist_sample_space = np.load("/home/ai1/git/code/tests/dist_sample_space.npy")
index_dict = load_dict_from_file("/home/ai1/git/code/tests/index_dict.pkl")

ultrasonicSensor_sensor = lego.UltrasonicSensor(sensor_overview["ultra"])
gyro_sensor = gyro(sensor_overview["gryo"])
gyro_sensor.reset()

touchSensor = lego.TouchSensor(sensor_overview["touch"])

tank_drive = MoveTank(OUTPUT_A, OUTPUT_D)

dist_old = 255



while True:
    angel = gyro_sensor.get_angel()

    dist = ultrasonicSensor_sensor.distance_centimeters

    if dist == 255:
        dist = dist_old
    dist_old = dist

    angel_round = find_nearest(angel_sample_space, angel)
    dist_round = find_nearest(dist_sample_space, dist)
    motor_index = index_dict[(angel_round, dist_round)]

    motor_l_pro = motor_l_samples[motor_index[0], motor_index[1]]
    motor_r_pro = motor_r_samples[motor_index[0], motor_index[1]]

    tank_drive.on(SpeedPercent(motor_l_pro),SpeedPercent(motor_r_pro))

    print(["{:.2f}".format(angel),       "{:.2f}".format(angel_round)],
          ["{:.2f}".format(dist),        "{:.2f}".format(dist_round)],
          ["{:.2f}".format(motor_l_pro), "{:.2f}".format(motor_r_pro)])

    if touchSensor.is_pressed:
        stop = False

        touchtime = time.time()

        tank_drive.stop()
        tank_drive.off()

        while touchSensor.is_pressed:
            if round(time.time() - touchtime) > 5:
                stop = True

        if stop:
            break
