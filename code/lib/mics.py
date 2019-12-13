import numpy as np
from ev3dev2.sensor import INPUT_1, INPUT_4, INPUT_2, INPUT_3
sensor_overview = {"v_color": INPUT_1, "r_color": INPUT_4, "ultra": INPUT_4, "gryo": INPUT_3, "touch": INPUT_2}

def running_update(x, N, mu, var, alpha):
    '''
        @arg x: the current data sample
        @arg N : the number of previous samples
        @arg mu: the mean of the previous samples
        @arg var : the variance over the previous samples
        @retval (N+1, mu', var') -- updated mean, variance and count
        From: https://stackoverflow.com/questions/1174984/how-to-efficiently-calculate-a-running-standard-deviation
    '''
    N = N + 1
    rho = 1.0/N
    d = x - mu

    mu = alpha * d + (1-alpha) * mu

    var += rho*((1-rho)*d**2 - var)
    return (N, mu, var)

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


class Hysteresis():
    def __init__(self, low, high, init_val = False):
        self.low = low
        self.high = high
        self.state = init_val

    def set(self, low=None, high=None):
        if low is not None:
            self.low = low
        if high is not None:
            self.high = high

    def cal(self, val):
        if val >= self.high:
            self.state = True
        elif val <= self.low:
            self.state = False
        elif self.state and val <= self.low:
            self.state = False
        elif not self.state and val >= self.high:
            self.state = True
        return self.state

from collections import deque
class SmartLine:
    def __init__(self, hist_max=10, std_min=0.5, std_scale=5, first_add_pos = [2, -2], first_add_times = 4, sensor_std_start =0 , save_hist = False):
        self.hist = deque(maxlen=hist_max)
        self.std_min = std_min
        self.std_scale = std_scale
        self.on_line = False
        self.first_time = True
        self.first_add_pos = first_add_pos
        self.first_add_times = first_add_times
        self.save_hist = save_hist
        self.data_hist = {}
        self.hist_index = 0
        self.sensor_std = sensor_std_start

    def __add_to_hist(self, name, data, count_index = False):
        if name not in self.data_hist:
            self.data_hist[name] = []
        self.data_hist[name].append([self.hist_index, data])

        if count_index:
            self.hist_index += 1

    def get_hist(self):
        return self.data_hist

    def cal_on_line(self, sensor):
        add_hist = True
        line_dect = False
        if len(self.hist):
            sensor_mean = np.mean(self.hist)
            std_temp = np.std(self.hist)
            if std_temp >= self.std_min:
                self.sensor_std = std_temp

            std_sensor = self.sensor_std * self.std_scale
            low_border = sensor_mean - std_sensor

            if self.save_hist:
                self.__add_to_hist("sensor_mean", sensor_mean)
                self.__add_to_hist("std_temp", std_temp)
                self.__add_to_hist("sensor_std", self.sensor_std)
                self.__add_to_hist("std_sensor", std_sensor)
                self.__add_to_hist("low_border", low_border)

            if sensor <= low_border:
                line_dect = True
                add_hist = False
                if not self.on_line:
                    self.on_line = True
                    if self.save_hist:
                        self.__add_to_hist("line_start", True)

            else:
                if self.on_line and self.save_hist:
                    self.__add_to_hist("line_end", True)

                line_dect = False
                self.on_line = False

        if add_hist:
            if self.save_hist:
                self.__add_to_hist("hist_add", True)
            if self.first_time:
                for rand_i in range(self.first_add_times):
                    self.hist.append(sensor + self.first_add_pos[rand_i % len(self.first_add_pos)])
            self.first_time = False
            self.hist.append(sensor)

        # Have to be last
        if self.save_hist:
            self.__add_to_hist("line_dect", line_dect)
            self.__add_to_hist("sensor", sensor, count_index=True) #Have to be last
        return line_dect