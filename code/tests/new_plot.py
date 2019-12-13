import matplotlib.pyplot as plt
import numpy as np
from collections import deque

def load_dict_from_file(filename):
    import pickle
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict

def askForFile(titel):
    import tkinter as tk
    from tkinter.filedialog import askopenfilename
    root = tk.Tk()
    root.withdraw()

    return askopenfilename(title=titel)

plot_dict = askForFile("Hist file")
plot_dict = load_dict_from_file(plot_dict)

obs_side = {"left":"right", "right":"left"}
pass_plots = []
for key in plot_dict:
    print(key)
    if key in pass_plots:
        continue
    for side in obs_side:
        if side in key:
            plt.figure()
            plt.subplot2grid((2,1), (0, 0))
            plt.plot(plot_dict[key])
            plt.title(key)
            plt.subplot2grid((2, 1), (1, 0))
            other_key = key.replace(side, obs_side[side])
            plt.plot(plot_dict[other_key])
            plt.title(other_key)
            pass_plots.append(other_key)



    data = plot_dict[key]
    plt.figure()
    plt.plot(data)
    plt.title(key)
plt.show()

