import numpy as np
import skfuzzy.control as ctrl
import skfuzzy as fuzz
import matplotlib.pyplot as plt

def save_dict_to_file(dict , filename):
    import pickle
    with open(filename, 'wb') as handle:
        pickle.dump(dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

def load_dict_from_file(filename):
    import pickle
    with open(filename, 'rb') as handle:
        dict = pickle.load(handle)
    return dict

plot_vars = False
save_sampels = True

# Sparse universe makes calculations faster, without sacrifice accuracy.
# Only the critical points are included here; making it higher resolution is
# unnecessary.
angle_universe = np.linspace(-30, 30, 7)
distance_universe = np.linspace(0, 150, 11)
motor_universe = np.linspace(0, 100, 11)

# Create the three fuzzy variables - two inputs, one output
angle_var = ctrl.Antecedent(angle_universe, 'angle')
distance_var = ctrl.Antecedent(distance_universe, 'distance')
motor_l_var = ctrl.Consequent(motor_universe, 'motor_l')
motor_r_var = ctrl.Consequent(motor_universe, 'motor_r')

angle_var.automf(number=2, names=["left", "right"])
angle_var['left'] = fuzz.trapmf(angle_var.universe, [-30,-30,0,10])
angle_var['right'] = fuzz.trapmf(angle_var.universe, [-10,0,30,30])

distance_var.automf(number=3, names=["close", "medium", "far"])
distance_var['close'] = fuzz.trapmf(distance_var.universe, [-20,-10,20,40])
distance_var['medium'] = fuzz.trimf(distance_var.universe, [10,30,75])
distance_var['far'] = fuzz.trapmf(distance_var.universe, [20,75,150,150])

for motor_var in [motor_l_var, motor_r_var]:
    motor_var.automf(number=4, names=["stop", "slow", "normal", "fast"])
    motor_var['stop'] = fuzz.trimf(motor_var.universe, [-10,0,10])
    motor_var['slow'] = fuzz.trimf(motor_var.universe, [0,10,50])
    motor_var['normal'] = fuzz.trimf(motor_var.universe, [10,90,100])
    motor_var['fast'] = fuzz.trimf(motor_var.universe, [90,100,110])

if plot_vars:
    angle_var.view()
    plt.show()

    distance_var.view()
    plt.show()

    motor_l_var.view()
    plt.show()

    motor_r_var.view()
    plt.show()


rules = []

rule = ctrl.Rule(antecedent=(angle_var["left"]),
                 consequent=(motor_l_var["normal"]),
                 label="angel: left")
rules.append(rule)

rule = ctrl.Rule(antecedent=(~angle_var["left"]),
                 consequent=(motor_l_var["slow"]),
                 label="angel: !left")
rules.append(rule)

rule = ctrl.Rule(antecedent=(angle_var["right"]),
                 consequent=(motor_r_var["normal"]),
                 label="angel: right")
rules.append(rule)

rule = ctrl.Rule(antecedent=(~angle_var["right"]),
                 consequent=(motor_r_var["slow"]),
                 label="angel: !right")
rules.append(rule)

rule = ctrl.Rule(antecedent=(distance_var["close"]),
                 consequent=(motor_l_var["slow"], motor_r_var["slow"]),
                 label="distance: close")
rules.append(rule)

rule = ctrl.Rule(antecedent=(distance_var["medium"]),
                 consequent=(motor_l_var["normal"], motor_r_var["normal"]),
                 label="distance: medium")
rules.append(rule)

rule = ctrl.Rule(antecedent=(distance_var["far"]),
                 consequent=(motor_l_var["fast"], motor_r_var["fast"]),
                 label="distance: fast")
rules.append(rule)

system = ctrl.ControlSystem(rules=rules)
system.view()
plt.show()


angel_dist_pre = 100

sim = ctrl.ControlSystemSimulation(system, flush_after_run=angel_dist_pre * angel_dist_pre + 1)

# We can simulate at higher resolution with full accuracy
angel_sampel_space = np.linspace(-30, 30, angel_dist_pre)
dist_sample_space = np.linspace(0, 150, angel_dist_pre)
angel_sampel, dist_sample = np.meshgrid(angel_sampel_space, dist_sample_space)
motor_l_sampels = np.zeros_like(angel_sampel)
motor_r_sampels = np.zeros_like(angel_sampel)

# Loop through the system 21*21 times to collect the control surface



index_dict = {}

for i_angle in range(len(angel_sampel_space)):
    for j_dist in range(len(dist_sample_space)):
        angel = angel_sampel[i_angle, j_dist]
        dist = dist_sample[i_angle, j_dist]
        sim.input['angle'] = angel
        sim.input['distance'] = dist

        sim.compute()
        motor_l_sampels[i_angle, j_dist] = sim.output['motor_l']
        motor_r_sampels[i_angle, j_dist] = sim.output['motor_r']

        index_dict[(angel, dist)] = [i_angle, j_dist]



# Plot the result in pretty 3D with alpha blending
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Required for 3D plotting

fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(221, projection='3d')

surf = ax.plot_surface(angel_sampel, dist_sample, motor_l_sampels, rstride=1, cstride=1, cmap='viridis',
                       linewidth=0.4, antialiased=True)

ax.set_xlabel("Angel")
ax.set_ylabel("Distance")
ax.set_zlabel("Motor pro")
plt.title("Left motor")

#fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(222, projection='3d')
cset = ax.contourf(angel_sampel, dist_sample, motor_l_sampels, zdir='z', offset=np.min(motor_l_sampels), cmap='viridis', alpha=0.5)
cset = ax.contourf(angel_sampel, dist_sample, motor_l_sampels, zdir='x', offset=np.max(angel_sampel), cmap='viridis', alpha=0.5)
cset = ax.contourf(angel_sampel, dist_sample, motor_l_sampels, zdir='y', offset=np.max(dist_sample), cmap='viridis', alpha=0.5)

ax.set_xlabel("Angel")
ax.set_ylabel("Distance")
ax.set_zlabel("Motor pro")
plt.title("Left motor")

ax = fig.add_subplot(223, projection='3d')

surf = ax.plot_surface(angel_sampel, dist_sample, motor_r_sampels, rstride=1, cstride=1, cmap='viridis',
                       linewidth=0.4, antialiased=True)

ax.set_xlabel("Angel")
ax.set_ylabel("Distance")
ax.set_zlabel("Motor pro")
plt.title("Right motor")

#fig = plt.figure(figsize=(8, 8))
ax = fig.add_subplot(224, projection='3d')
cset = ax.contourf(angel_sampel, dist_sample, motor_r_sampels, zdir='z', offset=np.min(motor_r_sampels), cmap='viridis', alpha=0.5)
cset = ax.contourf(angel_sampel, dist_sample, motor_r_sampels, zdir='x', offset=np.max(angel_sampel), cmap='viridis', alpha=0.5)
cset = ax.contourf(angel_sampel, dist_sample, motor_r_sampels, zdir='y', offset=np.max(dist_sample), cmap='viridis', alpha=0.5)

ax.set_xlabel("Angel")
ax.set_ylabel("Distance")
ax.set_zlabel("Motor pro")
plt.title("Right motor")

plt.show()

if save_sampels:
    np.save("motor_l_samples.npy", motor_l_sampels)
    np.save("motor_r_samples.npy", motor_r_sampels)
    np.save("angel_sample_space.npy", angel_sampel_space)
    np.save("dist_sample_space.npy", dist_sample_space)
    save_dict_to_file(index_dict, "index_dict.pkl")

#motor_l_sampels = np.load(r"C:\Users\simon\OneDrive - Syddansk Universitet\Studie\7 semester\AI\AIGit\code\tests\motor_l_samples.npy")
#motor_r_sampels = np.load(r"C:\Users\simon\OneDrive - Syddansk Universitet\Studie\7 semester\AI\AIGit\code\tests\motor_r_samples.npy")
#angel_sample_space = np.load(r"C:\Users\simon\OneDrive - Syddansk Universitet\Studie\7 semester\AI\AIGit\code\tests\angel_sample_space.npy")
#dist_sample_space = np.load(r"C:\Users\simon\OneDrive - Syddansk Universitet\Studie\7 semester\AI\AIGit\code\tests\dist_sample_space.npy")