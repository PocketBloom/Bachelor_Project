import tudatpy

# Load standard modules
import numpy as np
#from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # or try 'QtAgg'
import matplotlib.pyplot as plt

# Load tudatpy modules
from tudatpy.interface import spice
from tudatpy import dynamics
from tudatpy.dynamics import environment_setup, propagation_setup, simulator
from tudatpy.astro import element_conversion
from tudatpy import constants
from tudatpy.util import result2array
from tudatpy.astro.time_representation import DateTime


# Load spice kernels
spice.load_standard_kernels()

# Set simulation start and end epochs
# So here end of the epoch is a day later :)
# The start day is set to be 1st of January 2000 
simulation_start_epoch = DateTime(2000, 1, 1).to_epoch()
simulation_end_epoch   = DateTime(2001, 1, 1).to_epoch()



#ME TRYING TO FIND TU3

#I assume that I load the spice kernels and use the same start and stop time


# Create default body settings for "Sun"
bodies_to_create_TU3 = ["Sun"]

# Create default body settings for bodies_to_create, with "Sun"/"J2000" as the global frame origin 
# and orientation
# So, we choose to consider the body of Sun

global_frame_origin_TU3 = "Sun"
# I believe we always choose this
global_frame_orientation_TU3 = "ECLIPJ2000"

body_settings_TU3 = environment_setup.get_default_body_settings(
    bodies_to_create_TU3, global_frame_origin_TU3, global_frame_orientation_TU3)

# Add empty settings to body settings
# Create the massless satellite for which the orbit around Sun will be propagated
body_settings_TU3.add_empty_settings("TU3-199")

# Create system of bodies (in this case only Sun)
bodies_TU3 = environment_setup.create_system_of_bodies(body_settings_TU3)

# Define bodies that are propagated
bodies_to_propagate_TU3 = ["TU3-199"]

# Define central bodies of propagation
central_bodies_TU3 = ["Sun"]


# Acceleration model:

# Define accelerations acting on TU3-1998
acceleration_settings_TU3 = dict(
    Sun=[propagation_setup.acceleration.point_mass_gravity()]
)

acceleration_settings_TU3 = {"TU3-199": acceleration_settings_TU3}

# Create acceleration models
acceleration_models_TU3 = propagation_setup.create_acceleration_models(
    bodies_TU3, acceleration_settings_TU3, bodies_to_propagate_TU3, central_bodies_TU3
)

#--------------------------------------------

#Initial state

# Set initial conditions for the satellite that will be
# propagated in this simulation. The initial conditions are given in
# Keplerian elements and later on converted to Cartesian elements

# Let's just test what happens with the same initial state
sun_gravitational_parameter_TU3 = bodies_TU3.get("Sun").gravitational_parameter

initial_state_TU3 = element_conversion.keplerian_to_cartesian_elementwise(
   gravitational_parameter = sun_gravitational_parameter_TU3,
   semi_major_axis = 117815568541, #meters
   eccentricity = 0.4836694929440215, #unitless
   inclination = np.radians(5.415250040031074), #radians
   argument_of_periapsis = np.radians(84.99253804349257),
   longitude_of_ascending_node = np.radians(101.8786744779986),
   true_anomaly = 2.2486890775e+00, #calculated with e, M, and E.
)

# initial_state_TU3 = element_conversion.keplerian_to_cartesian_elementwise(
#     sun_gravitational_parameter_TU3,
#     117815568541, #meters
#     0.4836694929440215, #unitless
#     np.radians(5.415250040031074), #radians
#     np.radians(84.99253804349257),
#     np.radians(101.8786744779986),
#     2.2486890775e+00, #calculated with e, M, and E.
# )


# Create termination settings
termination_settings_TU3 = propagation_setup.propagator.time_termination(simulation_end_epoch)

# Create numerical integrator settings
integrator_settings_TU3 = propagation_setup.integrator.runge_kutta_fixed_step(
    time_step = 24*3600.0,
    coefficient_set = propagation_setup.integrator.CoefficientSets.rk_4 )

# Create propagation settings
propagator_settings_TU3 = propagation_setup.propagator.translational(
    central_bodies_TU3,
    acceleration_models_TU3,
    bodies_to_propagate_TU3,
    initial_state_TU3,
    simulation_start_epoch,
    integrator_settings_TU3,
    termination_settings_TU3
)

# Create simulation object and propagate the dynamics
dynamics_simulator_TU3 = simulator.create_dynamics_simulator(
    bodies_TU3, propagator_settings_TU3
)
# Extract the resulting state history and convert it to an ndarray
states_TU3 = dynamics_simulator_TU3.propagation_results.state_history
states_array_TU3 = result2array(states_TU3)

print(
    f"""
Single Sun-Orbiting Satellite Example.
The initial position vector of TU3 is [km]: \n{
    states_TU3[simulation_start_epoch][:3] / 1E3}
The initial velocity vector of TU3 is [km/s]: \n{
    states_TU3[simulation_start_epoch][3:] / 1E3}
\nAfter {simulation_end_epoch} seconds the position vector of TU3 is [km]: \n{
    states_TU3[simulation_end_epoch][:3] / 1E3}
And the velocity vector of TU3 is [km/s]: \n{
    states_TU3[simulation_end_epoch][3:] / 1E3}
    """
)


# To examine how far apart the "real" values of TU3 are from JPL Horizon

# All the states made by Tudat are put into statues_TU3
print(len(states_TU3))


# Extract columns
t_TU3  = states_array_TU3[:, 0]

x_TU3  = states_array_TU3[:, 1]
y_TU3  = states_array_TU3[:, 2]
z_TU3  = states_array_TU3[:, 3]

vx_TU3 = states_array_TU3[:, 4]
vy_TU3 = states_array_TU3[:, 5]
vz_TU3 = states_array_TU3[:, 6]

print(x_TU3[0])

# After having imported and created the data in another python file
# Extract the data from a CSV file:
import pandas as pd

# Load CSV
csv_data = pd.read_csv("asteroid_66146_vectors.csv")

# Convert columns to arrays
x_JPL = csv_data["x"].to_numpy()
y_JPL = csv_data["y"].to_numpy()
z_JPL = csv_data["z"].to_numpy()

vx_JPL = csv_data["vx"].to_numpy()
vy_JPL = csv_data["vy"].to_numpy()
vz_JPL = csv_data["vz"].to_numpy()

print(states_TU3[0])
print(states_array_TU3[5])
print(x_JPL[0])


# Then compare the values from Tudat and JPL Horizon
 
x_comp = x_TU3 - x_JPL 
y_comp = y_TU3 - y_JPL
z_comp = z_TU3 - z_JPL

vx_comp = vx_TU3 - vx_JPL 
vy_comp = vy_TU3 - vy_JPL
vz_comp = vz_TU3 - vz_JPL


# Printing the difference

import matplotlib.pyplot as plt

t_TU3_days = t_TU3 / (24*3600)  # From seconds to days


# =========================
# POSITION DIFFERENCES
# =========================

plt.figure(figsize=(10, 6))

plt.plot(t_TU3_days, x_comp, label='x difference')
plt.plot(t_TU3_days, y_comp, label='y difference')
plt.plot(t_TU3_days, z_comp, label='z difference')

plt.xlabel('Time')
plt.ylabel('Position Difference [m]')
plt.title('Tudat vs JPL Position Differences')

plt.legend()
plt.grid(True)

plt.show()


# =========================
# VELOCITY DIFFERENCES
# =========================

plt.figure(figsize=(10, 6))

plt.plot(t_TU3_days, vx_comp, label='vx difference')
plt.plot(t_TU3_days, vy_comp, label='vy difference')
plt.plot(t_TU3_days, vz_comp, label='vz difference')

plt.xlabel('Time')
plt.ylabel('Velocity Difference [m/s]')
plt.title('Tudat vs JPL Velocity Differences')

plt.legend()
plt.grid(True)

plt.show()




# Printing the orbit:

# # Define a 3D figure using pyplot
# fig = plt.figure(figsize=(6,6), dpi=125)
# ax = fig.add_subplot(111, projection='3d')
# ax.set_title(f'TU3 trajectory around Sun')

# # Plot the positional state history
# ax.plot(states_array_TU3[:, 1], states_array_TU3[:, 2], states_array_TU3[:, 3], label=bodies_to_propagate_TU3[0], linestyle='-.')
# ax.scatter(0.0, 0.0, 0.0, label="Sun", marker='o', color='orange')

# print("Before final graph")

# # Add the legend and labels, then show the plot
# ax.legend()
# ax.set_xlabel('x [m]')
# ax.set_ylabel('y [m]')
# ax.set_zlabel('z [m]')
# ax.set_aspect('equal')
# plt.show()
# plt.close('all')

# print("End of code")