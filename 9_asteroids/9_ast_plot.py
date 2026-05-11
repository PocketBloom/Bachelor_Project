import numpy as np
import pandas as pd
# In order to grab the path with the csv file from any directory
from pathlib import Path

import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt

# Load tudatpy modules
from tudatpy.interface import spice
from tudatpy.dynamics import environment_setup, propagation_setup, simulator
from tudatpy.astro import element_conversion
from tudatpy.util import result2array
from tudatpy.astro.time_representation import DateTime



# 1. Define the asteroid class, and the extract the values
class Asteroid_Table:
    def __init__(self, name, a, e, i_ec, node, peri, M):
        self.name = name
        
        self.a = float(a)
        self.e = float(e)
        self.i_ec = float(i_ec)    # Inclination
        self.node = float(node)    # Longitude of ascending node
        self.peri = float(peri)    # Argument of periapsis
        self.M = float(M)          # Mean Anomaly (Note: Tudat uses True Anomaly for conversion)


# Define how to read the csv file
def load_asteroids(csv_file):
    df = pd.read_csv(csv_file)

    return [
        Asteroid_Table(
            row["name"],
            row["a"],
            row["e"],
            row["i"],
            row["node"],
            row["peri"],
            row["M"],
            #row["epoch"]
        )
        for _, row in df.iterrows()
    ]


# Load the data from the csv file with the asteroids
# Since the csv file is in a different dictionary I print my entire path to it

# Load asteroid data
asteroids = load_asteroids("/home/emmabob/Bachelor_Project/Table_of_Asteroids/asteroids_full_precision.csv")


# 2. Simulation Environment
spice.load_standard_kernels()
simulation_start_epoch = DateTime(2000, 1, 1).to_epoch()
simulation_end_epoch   = DateTime(2001, 1, 1).to_epoch()

bodies_to_create = ["Sun"]
global_frame_origin = "Sun"
global_frame_orientation = "J2000"

body_settings = environment_setup.get_default_body_settings(
    bodies_to_create, global_frame_origin, global_frame_orientation)


# Add each asteroid from the class to the environment
for ast in asteroids:
    body_settings.add_empty_settings(ast.name)

bodies = environment_setup.create_system_of_bodies(body_settings)


# 3. Setup Accelerations
bodies_to_propagate = [ast.name for ast in asteroids]
central_bodies = ["Sun"] * len(bodies_to_propagate)

acceleration_settings = {}
for ast_name in bodies_to_propagate:
    acceleration_settings[ast_name] = {
        "Sun": [propagation_setup.acceleration.point_mass_gravity()]
    }

acceleration_models = propagation_setup.create_acceleration_models(
    bodies, acceleration_settings, bodies_to_propagate, central_bodies
)

# 4. Initial States

# In seperate Jupyter Notebook I calculated the true anomaly list:

mu_list = [3.0616536207911196, 2.2486890774951678, -1.5479575105729457, 2.7711783765331095, -2.5632150191803316, 2.4772437956967965, -3.059958244959158, 2.6482594642004296, 1.7921861903308103]

# Loop through the class elements and convert Keplerian to Cartesian
sun_gravitational_parameter = bodies.get("Sun").gravitational_parameter
initial_states_list = []

for ast, mu in zip(asteroids, mu_list):
    ast_initial_state = element_conversion.keplerian_to_cartesian_elementwise(
        gravitational_parameter = sun_gravitational_parameter,
        semi_major_axis = ast.a * 149597870691,     # AU to meters
        eccentricity = ast.e,
        inclination = np.radians(ast.i_ec),
        argument_of_periapsis = np.radians(ast.peri),
        longitude_of_ascending_node = np.radians(ast.node),
        true_anomaly = mu, 
    )
    initial_states_list.append(ast_initial_state)

# Concatenate all initial states into one long vector
initial_state_vector = np.concatenate(initial_states_list)

# 5. Integration & Propagation Settings
termination_settings = propagation_setup.propagator.time_termination(simulation_end_epoch)
integrator_settings = propagation_setup.integrator.runge_kutta_fixed_step(
    time_step = 3600.0, # Increased step to 1 day for faster 1-year simulation
    coefficient_set = propagation_setup.integrator.CoefficientSets.rk_4 
)

propagator_settings = propagation_setup.propagator.translational(
    central_bodies,
    acceleration_models,
    bodies_to_propagate,
    initial_state_vector,
    simulation_start_epoch,
    integrator_settings,
    termination_settings
)

# 6. Run simulation
print("Commencing simulation")
dynamics_simulator = simulator.create_dynamics_simulator(bodies, propagator_settings)
states = dynamics_simulator.propagation_results.state_history
states_array = result2array(states)

# 7. Plotting all 9 Asteroids

print("Beginning to plot")

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('9 Asteroid Trajectories around the Sun')

# The states_array columns are: [Time, x1, y1, z1, vx1, vy1, vz1, x2, y2, z2...]
for i, ast in enumerate(asteroids):
    # Calculate column indices for this specific asteroid
    # index 0 is time, so asteroid i starts at 1 + (i * 6)
    start_col = 1 + (i * 6)
    ax.plot(states_array[:, start_col], 
            states_array[:, start_col+1], 
            states_array[:, start_col+2], 
            label=ast.name)

# Plot the Sun
ax.scatter(0, 0, 0, color='orange', marker='o', s=100, label="Sun")

ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')
ax.set_zlabel('z [m]')
plt.tight_layout()
plt.show()

print("End of plot")