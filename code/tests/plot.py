import matplotlib.pyplot as plt
import numpy as np
def load_dict_from_file(filename):
    import pickle
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict

hist = load_dict_from_file(r"C:\Users\simon\Desktop\hist_fullSpeed.pck")
print(hist)
plt.figure()
plt.subplot2grid((3,2),(0,0))
plt.plot(hist["LineDect"]["r_l"], label="r_l")
plt.legend()
plt.subplot2grid((3,2),(0,1))
plt.plot(hist["LineDect"]["r_r"], label="r_r")
plt.legend()

plt.subplot2grid((3,2),(1,0))
plt.plot(hist["LineDect"]["line_l"], label="line_l")
plt.legend()
plt.subplot2grid((3,2),(1,1))
plt.plot(hist["LineDect"]["line_r"], label="line_r")
plt.legend()

plt.subplot2grid((3,2),(2,0))
plt.plot(hist["LineDect"]["change_l"], label="change_l")
plt.legend()
plt.subplot2grid((3,2),(2,1))
plt.plot(hist["LineDect"]["change_r"], label="change_r")
plt.legend()
#plt.show()


plt.figure()
plt.rcParams["font.size"] = "20"
plt.subplot2grid((2,1),(0,0))
plt.plot(hist["LineDect"]["r_l"], label="Left sensor")
plt.vlines(x=np.argmin(hist["LineDect"]["r_l"]), ymin=np.min(20) ,ymax=np.max(80), label="Line",linestyles="dotted",color='r')
#plt.ylim(20,80)
plt.legend()

plt.ylabel("Intensity")
plt.grid(True)

plt.subplot2grid((2,1),(1,0))
plt.plot(hist["LineDect"]["r_r"], label="Right sensor")
plt.vlines(x=np.argmin(hist["LineDect"]["r_r"]), ymin=np.min(0) ,ymax=np.max(70), label="Line",linestyles="dotted",color='r')
#plt.ylim(0,70)
plt.legend()
plt.xlabel("Sample")
plt.ylabel("Intensity")
plt.grid(True)


plt.show()