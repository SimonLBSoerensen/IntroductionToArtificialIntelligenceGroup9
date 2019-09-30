import matplotlib.pyplot as plt
def load_dict_from_file(filename):
    import pickle
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict

hist = load_dict_from_file(r"C:\Users\simon\Desktop\hist.pck")
print(hist)
plt.figure()
plt.subplot2grid((2,2),(0,0))
plt.plot(hist["LineDect"]["r_l"], label="r_l")
plt.legend()
plt.subplot2grid((2,2),(1,0))
plt.plot(hist["LineDect"]["r_r"], label="r_r")
plt.legend()
plt.subplot2grid((2,2),(0,1))
plt.plot(hist["LineDect"]["line_l"], label="line_l")
plt.legend()
plt.subplot2grid((2,2),(1,1))
plt.plot(hist["LineDect"]["line_r"], label="line_r")
plt.legend()
plt.show()


