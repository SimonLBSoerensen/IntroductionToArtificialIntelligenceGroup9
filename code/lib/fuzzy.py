import sys
sys.path.insert(0, "/home/ai1/git/code/lib")
from mics import load_dict_from_file, find_nearest
import numpy as np

class FuzzyStraight():
    def __init__(self):
        self.motor_l_samples = np.load("/home/ai1/git/code/tests/motor_l_samples.npy")
        self.motor_r_samples = np.load("/home/ai1/git/code/tests/motor_r_samples.npy")
        self.angel_sample_space = np.load("/home/ai1/git/code/tests/angel_sample_space.npy")
        self.dist_sample_space = np.load("/home/ai1/git/code/tests/dist_sample_space.npy")
        self.index_dict = load_dict_from_file("/home/ai1/git/code/tests/index_dict.pkl")

    def cal(self, angel, dist):
        angel_round = find_nearest(self.angel_sample_space, angel)
        dist_round = find_nearest(self.dist_sample_space, dist)
        motor_index = self.index_dict[(angel_round, dist_round)]

        motor_l_pro = self.motor_l_samples[motor_index[0], motor_index[1]]
        motor_r_pro = self.motor_r_samples[motor_index[0], motor_index[1]]

        return motor_l_pro, motor_r_pro