from collections import deque
import numpy as np

class cusum:
    def __init__(self, subgroupmax, subgrouspmax):
        self.subgroups = deque(maxlen=subgrouspmax)
        self.subgroups_mean = deque(maxlen=subgrouspmax)
        self.subgroups_std = deque(maxlen=subgrouspmax)
        self.subgroups_z = deque(maxlen=subgrouspmax)
        self.subgroups_SLi = deque(maxlen=subgrouspmax)
        self.subgroups_SHi = deque(maxlen=subgrouspmax)
        self.subgroupmax = subgroupmax
        self.subgrouspmax = subgrouspmax
        self.current_subgroup = []
        self.changes = deque(maxlen=subgrouspmax)
        self.current_changes = []

    def append(self, x):
        if len(self.current_subgroup) >= self.subgroupmax:
            sub_mean = np.mean(self.current_subgroup)
            sub_std = np.std(self.current_subgroup)
            self.subgroups.append(self.current_subgroup)
            self.subgroups_mean.append(sub_mean)
            self.subgroups_std.append(sub_std)

            subs_mean = self.__sub_groups_mean()
            subs_std = self.__sub_groups_std()
            sub_z = (sub_mean - subs_mean)/(subs_std+0.000001)
            self.subgroups_z.append(sub_z)
            k = len(self.subgroups)
            if k <= 1:
                sub_SLi = 0
            else:
                sub_SLi = -1*max(0,(-1*sub_z-k)+self.subgroups_SLi[-1])
            self.subgroups_SLi.append(sub_SLi)

            if k <= 1:
                sub_SHi = 0
            else:
                sub_SHi = -1*max(0,(sub_z-k)+self.subgroups_SHi[-1])
            self.subgroups_SHi.append(sub_SHi)

            self.current_subgroup = []

            self.changes.append(self.current_changes)
            self.current_changes = []

        self.current_subgroup.append(x)
        change, sli, shi = self.change_happened()
        self.current_changes.append(change)

        return change, sli, shi

    def __sub_groups_mean(self):
        return np.mean(self.subgroups_mean)

    def __sub_groups_std(self):
        return np.std(self.subgroups_std)

    def change_happened(self):
        x = self.current_subgroup[-1]
        if len(self.subgroups_SLi) == 0:
            return False, 0, 0
        sli = self.subgroups_SLi[-1]
        shi = self.subgroups_SHi[-1]

        if x <= sli or x >= shi:
            return True, sli, shi
        else:
            return False, sli, shi

    def is_change(self, x):
        sli = self.subgroups_SLi[-1]
        shi = self.subgroups_SHi[-1]
        if x <= sli or x >= shi:
            return True
        else:
            return False

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    cs = cusum(1,9999)


    def load_dict_from_file(filename):
        import pickle
        with open(filename, 'rb') as handle:
            dict = pickle.load(handle)
        return dict


    hist = load_dict_from_file(r"C:\Users\simon\Desktop\hist.pck")
    changes = []
    slis = []
    shis = []
    for val in hist["LineDect"]["r_l"]:
        change, sli, shi = cs.append(val)
        changes.append(change)
        slis.append(sli)
        shis.append(shi)

    plt.figure()
    plt.subplot2grid((3, 1), (0, 0))
    plt.plot(hist["LineDect"]["r_l"], label="r_l")
    plt.legend()
    plt.subplot2grid((3, 1), (1, 0))
    plt.plot(changes, label="change")
    plt.legend()
    plt.subplot2grid((3, 1), (2, 0))
    plt.plot(slis, label="slis")
    plt.plot(shis, label="shis")
    plt.legend()
    plt.show()


