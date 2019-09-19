import numpy as np
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


motor_l_sampels = np.load("motor_l_sampels.npy")
motor_r_sampels = np.load("motor_r_sampels.npy")
angel_sampel_space = np.load("angel_sampel_space.npy")
dist_sample_space = np.load("dist_sample_space.npy")

angel_resampel_space = np.linspace(-30, 30)
dist_resample_space = np.linspace(0, 150)
angel_sampel, dist_sample = np.meshgrid(angel_resampel_space, dist_resample_space)
motor_re_sampel = np.zeros_like(angel_sampel)
motor_re_sampel_get = np.zeros_like(angel_sampel)

for a_i, angle in enumerate(angel_resampel_space):
    for d_j, dist in enumerate(dist_resample_space):
        angle_idx = find_nearest(angel_sampel_space, angle)
        dist_idx = find_nearest(dist_sample_space, dist)

        motor_re_sampel[a_i, d_j] = motor_l_sampels[angle_idx, dist_idx]
        motor_re_sampel_get[angle_idx, dist_idx] = motor_l_sampels[angle_idx, dist_idx]

# Plot the result in pretty 3D with alpha blending
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(121, projection='3d')

surf = ax.plot_surface(angel_sampel, dist_sample, motor_re_sampel, rstride=1, cstride=1, cmap='viridis',
                       linewidth=0.4, antialiased=True)


ax.set_xlabel("Angel")
ax.set_ylabel("Distance")
ax.set_zlabel("Motor left")

#fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(122, projection='3d')
cset = ax.contourf(angel_sampel, dist_sample, motor_re_sampel, zdir='z', offset=np.min(motor_l_sampels), cmap='viridis', alpha=0.5)
cset = ax.contourf(angel_sampel, dist_sample, motor_re_sampel, zdir='x', offset=np.max(angel_sampel), cmap='viridis', alpha=0.5)
cset = ax.contourf(angel_sampel, dist_sample, motor_re_sampel, zdir='y', offset=np.max(dist_sample), cmap='viridis', alpha=0.5)

ax.set_xlabel("Angel")
ax.set_ylabel("Distance")
ax.set_zlabel("Motor left")

plt.show()
