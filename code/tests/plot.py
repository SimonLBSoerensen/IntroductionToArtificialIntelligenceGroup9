import sys
sys.path.insert(0, "../lib")
from mics import SmartLine


import matplotlib.pyplot as plt
import numpy as np
from collections import deque
def load_dict_from_file(filename):
    import pickle
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict

def plot_SL(data):
    sl = SmartLine(save_hist=True, std_scale=7)
    for i, sensor_data in enumerate(data):
        sl.cal_on_line(sensor_data)

    sl_hist = sl.get_hist()
    sensor = np.array(sl_hist["sensor"])
    sensor_mean = np.array(sl_hist["sensor_mean"])
    std_sensor = np.array(sl_hist["std_sensor"])

    plt.figure()
    plt.plot(sensor[:,0], sensor[:,1], label="Sensor")
    plt.errorbar(sensor_mean[:,0], sensor_mean[:,1], yerr=std_sensor[:,1], label='mean with std_hist', uplims=True)

    if "line_dect" in sl_hist:
        line_dect = np.array(sl_hist["line_dect"])
        plt.plot(line_dect[:, 0], line_dect[:, 1], label="line_dect")

    if "line_start" in sl_hist:
        line_start = np.array(sl_hist["line_start"])
        plt.vlines(x=line_start[:, 0], ymin=0, ymax=np.max(sensor[:, 1]), color="g")
    if "line_end" in sl_hist:
        line_end = np.array(sl_hist["line_end"])
        plt.vlines(x=line_end[:,0], ymin=0, ymax=np.max(sensor[:,1]), color="r")

hys_min_max = [25,30]

hist = load_dict_from_file(r"C:\Users\simon\Desktop\hist\hist.pck")
print(hist)

plt.figure()
plt.plot(hist["t"], hist["r_r"], label="r_r")
plt.show()

plot_SL(hist["r_r"])
plt.show()

plt.figure()
plt.plot(hist["angel"], label="angel", c="g")
plt.plot(hist["angel_offset"], label="angel_offset", c="r")
plt.legend()

plt.figure()
plt.subplot2grid((2,2),(0,0))
plt.plot(hist["r_l"], label="r_l")
plt.legend()
plt.grid(True)
plt.subplot2grid((2,2),(0,1))
plt.plot(hist["r_r"], label="r_r")
plt.legend()
plt.grid(True)

plt.subplot2grid((2,2),(1,0))
plt.plot(hist["line_l"], label="line_l")
plt.legend()
plt.grid(True)
plt.subplot2grid((2,2),(1,1))
plt.plot(hist["line_r"], label="line_r")
plt.legend()
plt.grid(True)

plt.show()


plt.figure()
plt.rcParams["font.size"] = "20"
plt.subplot2grid((2,1),(0,0))
plt.plot(hist["r_l"], label="Left sensor")
plt.hlines(y=hys_min_max, xmin=0, xmax=len(hist["r_l"]))
#plt.vlines(x=np.argmin(hist["LineDect"]["r_l"]), ymin=np.min(20) ,ymax=np.max(80), label="Line",linestyles="dotted",color='r')
#plt.ylim(20,80)
plt.legend()
plt.ylabel("Intensity")
plt.grid(True)

plt.subplot2grid((2,1),(1,0))
plt.plot(hist["r_r"], label="Right sensor")
plt.hlines(y=hys_min_max, xmin=0, xmax=len(hist["r_l"]))
#plt.vlines(x=np.argmin(hist["LineDect"]["r_r"]), ymin=np.min(0) ,ymax=np.max(70), label="Line",linestyles="dotted",color='r')
#plt.ylim(0,70)
plt.legend()
plt.xlabel("Sample")
plt.ylabel("Intensity")
plt.grid(True)





plot_SL(hist["r_l"])
plot_SL(hist["r_r"])
plt.show()