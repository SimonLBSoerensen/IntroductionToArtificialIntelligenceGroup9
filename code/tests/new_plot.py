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

for key in plot_dict:
    print(key)
    data = plot_dict[key]
    plt.figure()
    plt.plot(data)
    plt.title(key)
plt.show()

