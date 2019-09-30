from collections import deque
import numpy as np

class cusum:
    def __init__(self, subgroupmax, subgrouspmax, k = 0.5):
        self.subgroups = deque(maxlen=subgrouspmax)
        self.subgroups_mean = deque(maxlen=subgrouspmax)
        self.subgroups_std = deque(maxlen=subgrouspmax)
        self.subgroups_z = deque(maxlen=subgrouspmax)
        self.subgroups_SLi = deque(maxlen=subgrouspmax)
        self.subgroups_SHi = deque(maxlen=subgrouspmax)
        self.subgroupmax = subgroupmax
        self.subgrouspmax = subgrouspmax
        self.current_subgroup = []
        self.z_hist = []
        self.k = k

    def reset(self, subgroupmax=None, subgrouspmax=None, k = 0.5):
        self.subgroups = deque(maxlen=subgrouspmax)
        self.subgroups_mean = deque(maxlen=subgrouspmax)
        self.subgroups_std = deque(maxlen=subgrouspmax)
        self.subgroups_z = deque(maxlen=subgrouspmax)
        self.subgroups_SLi = deque(maxlen=subgrouspmax)
        self.subgroups_SHi = deque(maxlen=subgrouspmax)

        if subgroupmax is not None:
            self.subgroupmax = subgroupmax
        if subgrouspmax is not None:
            self.subgrouspmax = subgrouspmax

        self.current_subgroup = []
        self.z_hist = []
        self.k = k

    def append(self, x):
        if len(self.current_subgroup) >= self.subgroupmax:
            sub_mean = np.mean(self.current_subgroup)
            sub_std = np.std(self.current_subgroup)
            self.subgroups.append(self.current_subgroup)
            self.subgroups_mean.append(sub_mean)
            self.subgroups_std.append(sub_std)

            subs_mean = self.__sub_groups_mean()
            subs_std = np.std(self.subgroups_mean)
            sub_z = (sub_mean - subs_mean)/(subs_std+0.000001)
            self.z_hist.append(sub_z)
            self.subgroups_z.append(sub_z)
            k = len(self.subgroups)
            if k <= 1:
                sub_SLi = 0
            else:
                last_sli = self.subgroups_SLi[-1]
                a = -1*sub_z-self.k
                sub_SLi = -1*max(0, a + last_sli)
            self.subgroups_SLi.append(sub_SLi)

            if k <= 1:
                sub_SHi = 0
            else:
                last_shi = self.subgroups_SHi[-1]
                b = sub_z-self.k
                sub_SHi = max(0, b + last_shi)
            self.subgroups_SHi.append(sub_SHi)

            self.current_subgroup = []

        self.current_subgroup.append(x)

        return self.get_sli_shi()

    def get_sli_shi(self):
        if len(self.subgroups):
            sli = self.subgroups_SLi[-1]
            shi = self.subgroups_SHi[-1]
        else:
            sli = 0
            shi = 0
        return sli, shi

    def change(self, x = None, low_t = -1.0, high_t = 0.0):
        if x is None:
            x = self.current_subgroup[-1]

        sli, shi = self.get_sli_shi()

        change = [False, False]
        if sli <= low_t:
            change[0] = True
        if shi >= low_t:
            change[1] = True
        return change


    def __sub_groups_mean(self):
        return np.mean(self.subgroups_mean)

    def __sub_groups_std(self):
        return np.mean(self.subgroups_std)

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    cs = cusum(3,9999, k = 0.5)


    def load_dict_from_file(filename):
        import pickle
        with open(filename, 'rb') as handle:
            dict = pickle.load(handle)
        return dict


    hist = load_dict_from_file(r"C:\Users\simon\Desktop\hist.pck")
    test_vals = []
    for val in hist["LineDect"]["r_l"]:
        test_vals.append(val)

    changes = []
    slis = []
    shis = []

    t_low = -1

    for val in test_vals:
        sli, shi = cs.append(val)
        slis.append(sli)
        shis.append(shi)

        lchange, hchange = cs.change(low_t = -1, high_t = 0)
        changes.append(lchange)


    plt.figure()
    plt.subplot2grid((4, 1), (0, 0))
    plt.plot(test_vals, label="r_l")
    plt.legend()
    plt.subplot2grid((4, 1), (1, 0))
    plt.plot(changes, label="change")
    plt.legend()
    plt.subplot2grid((4, 1), (2, 0))
    plt.plot(slis, label="slis")
    plt.plot(shis, label="shis")
    plt.legend()
    plt.subplot2grid((4, 1), (3, 0))
    plt.plot(slis, label="slis")
    plt.plot(shis, label="shis")
    plt.plot(test_vals, label="r_l")
    plt.legend()
    plt.show()


    plt.figure()
    plt.subplot2grid((2, 1), (0, 0))
    plt.plot(hist["LineDect"]["r_r"], label="r_r")
    plt.legend()
    plt.grid(True)
    plt.subplot2grid((2, 1), (1, 0))
    plt.plot(hist["LineDect"]["r_l"], label="r_l")
    plt.legend()
    plt.grid(True)
    plt.show()

