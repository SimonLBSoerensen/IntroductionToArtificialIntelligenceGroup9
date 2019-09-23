import numpy as np
from ev3dev2.sensor import INPUT_1, INPUT_4, INPUT_2, INPUT_3
sensor_overview = {"v_color": INPUT_2, "r_color": INPUT_3, "ultra": INPUT_4, "gryo": INPUT_1, "touch": INPUT_3}

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
    def __init__(self, low, high, init_val = 0):
        self.low = low
        self.high = high
        self.state = init_val

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
