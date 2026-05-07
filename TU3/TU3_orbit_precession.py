
# Goal: Simulate an accurate orbit and perihelion precession for TU3 
# (Then it can be applied to the other asteroids)

# Chapter 1: Apply General Relativity & Solar quadrupole Moment 
# Also apply the Yarkowsky effect
# For this argue why these effects are the only relevant

# Chapter 2: Is it okay to use the Sun as a point-mass
# Will several bodies be needed? Earth/ Jupiter? Their gravity?

# -----------------------------------------------------------------------------

# Firstly, follow the example for Solar System Propagation using Multi-Body Dynamics

# Load standard modules
import numpy as np
from matplotlib import pyplot as plt

# Load tudatpy modules
from tudatpy.interface import spice
from tudatpy import dynamics
from tudatpy.dynamics import environment_setup, propagation_setup, propagation, simulator
from tudatpy import constants
from tudatpy.util import result2array
from tudatpy.astro.time_representation import DateTime
from tudatpy.astro import element_conversion

# Step 1: Setup Conditions/ Basic Conditions

# Load spice kernels
spice.load_standard_kernels()

# Set simulation start and end epochs (total simulation time of 5 years)
# Start dat = 25th of April 2004 (arbitrary choice)
# Tudat works in J2000, so use seconds
simulation_start_epoch = DateTime(2000, 4, 25).to_epoch()
simulation_end_epoch   = simulation_start_epoch + 15 * constants.JULIAN_YEAR


# Step 2: Define bodies in simulation

# These bodies exist isnide of SPICE and are well-defined
larger_bodies_to_create = [
    "Sun",
    "Earth",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune"
]

# Manually add 1998 TU3
asteroid_name = "1998-TU3"

bodies_to_create = larger_bodies_to_create + [asteroid_name]
bodies_to_propagate = bodies_to_create

# Create bodies in simulation.

# Pull on the data already known for the larger bodies
body_settings = environment_setup.get_default_body_settings(larger_bodies_to_create)
# Manually add empty settings for the asteroid
body_settings.add_empty_settings(asteroid_name)

# Thus, the environment becomes:
body_system = environment_setup.create_system_of_bodies(body_settings)


# Step 3: Create Propagation Setup (barycentric and hierarchic)

# Central bodies for barycentric propagation
# Ensures that every body propagates around the Solar System's Barycenter 
central_bodies_barycentric = ["SSB"] * len(bodies_to_create)

# Central bodies for hierarchical parent body propagation
# Assigns each body to their local parent body
central_bodies_hierarchical = []
for body_name in bodies_to_create:
    if body_name == "Moon":
        central_bodies_hierarchical.append("Earth")
    elif body_name == "Sun":
        central_bodies_hierarchical.append("SSB")
    else:
        # Planets and asteroids are assigned to the Sun
        central_bodies_hierarchical.append("Sun")


# Step 4: Define the accelerations acting on each body

acceleration_dict = {}

for body_i in bodies_to_propagate:
    current_accelerations = {}
    
    for body_j in bodies_to_create:
        if body_i != body_j:
            # The physics behind the code: only the Sun and Planets have gravity
            # They will therefore tug on the other bodies
            # E.g. the Earth will tug a bit on Jupiter and vice versa
            # However, the asteroid (1998 TU3) does not (it is too small)
            if body_j != "1998-TU3": 
                current_accelerations[body_j] = [
                    # Assume each body is a point mass
                    propagation_setup.acceleration.point_mass_gravity()
                ]
                
    acceleration_dict[body_i] = current_accelerations


# Step 5: Define the Initial States of Each Body
# This is where we mix SPICE data (for the planets) with Keplerian data (the asteroid)

# Convert acceleration mappings into acceleration models for both propagation variants
for propagation_variant in ["barycentric", "hierarchical"]:
    central_bodies = central_bodies_barycentric if propagation_variant == "barycentric" else central_bodies_hierarchical

    # i. Get initial state for planets from SPICE
    planets_initial_state = propagation.get_initial_state_of_bodies(
        bodies_to_propagate = larger_bodies_to_create,
        central_bodies = central_bodies[:-1], # Exclude TU3
        body_system = body_system,
        initial_time = simulation_start_epoch
    )

    # ii. Define TU3 state from Keplerian Elements 
    # The different coordinates are converted to Cartesian coordinates
    # Use the Sun's gravitational parameter for the conversion

    sun_gravitational_parameter = body_system.get("Sun").gravitational_parameter

    initial_state_tu3 = element_conversion.keplerian_to_cartesian_elementwise(
        gravitational_parameter = sun_gravitational_parameter,
        semi_major_axis = 117815568541,                                 # meters
        eccentricity = 0.4836694929440215,                              # unitless
        inclination = np.radians(5.415250040031074),                    # radians
        argument_of_periapsis = np.radians(84.99253804349257),          # rad
        longitude_of_ascending_node = np.radians(101.8786744779986),    # rad
        true_anomaly = 2.2486890775e+00,                                # rad, calculated with e, M, and E.
    )

    # iii. Combine the initial states
    # If hierarchical, then TU3 is w.r.t Sun. If barycentric, it's adjusted to SSB
    if propagation_variant == "barycentric":
        # Get Sun's state w.r.t SSB to shift the asteroid's state
        sun_state_ssb = planets_initial_state[0:6] 
        initial_state_tu3 = initial_state_tu3 + sun_state_ssb

    combined_initial_state = np.concatenate((planets_initial_state, initial_state_tu3))

    if propagation_variant == "barycentric":
        system_initial_state_barycentric = combined_initial_state
    else:
        system_initial_state_hierarchical = combined_initial_state



# Step 6: Create the conditions for propagation:

# Create termination settings
termination_settings = propagation_setup.propagator.time_termination(simulation_end_epoch) # 5 years after the epoch begins

# Create numerical integrator settings
fixed_step_size = 3600.0    # each hour
integrator_settings = propagation_setup.integrator.runge_kutta_fixed_step(
    fixed_step_size, coefficient_set=propagation_setup.integrator.CoefficientSets.rk_4
)


# Creating acceleration models and propagator settings
accel_models_bary = propagation_setup.create_acceleration_models(body_system, acceleration_dict, bodies_to_propagate, central_bodies_barycentric)
accel_models_hier = propagation_setup.create_acceleration_models(body_system, acceleration_dict, bodies_to_propagate, central_bodies_hierarchical)

propagator_settings_barycentric = propagation_setup.propagator.translational(
    central_bodies_barycentric, accel_models_bary, bodies_to_propagate, 
    system_initial_state_barycentric, simulation_start_epoch, integrator_settings, termination_settings
)

propagator_settings_hierarchical = propagation_setup.propagator.translational(
    central_bodies_hierarchical, accel_models_hier, bodies_to_propagate, 
    system_initial_state_hierarchical, simulation_start_epoch, integrator_settings, termination_settings
)

# Then
# Step 7, run the simulation:

# Using print commands to keep track of the progress
print("now running the barycentric simulation...")
results_barycentric = simulator.create_dynamics_simulator(body_system, propagator_settings_barycentric).state_history



# Step 8: Plot the results
print("Start of plot")

barycentric_array = result2array(results_barycentric)

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Solar System + 1998 TU3 Trajectories (Barycentric)')

for i, body in enumerate(bodies_to_propagate):
    # Each body has 6 columns (x, y, z, vx, vy, vz) + 1 for time
    ax.plot(barycentric_array[:, 6*i+1], barycentric_array[:, 6*i+2], barycentric_array[:, 6*i+3], label=body)

ax.scatter(0, 0, 0, marker='o', color='yellow', label="SSB/Sun Center")
ax.legend(loc='upper left', bbox_to_anchor=(1.05, 1))
ax.set_xlabel('x [m]')
ax.set_ylabel('y [m]')
ax.set_zlabel('z [m]')

# Expanded limits to see at least out to Saturn
limit = 2.0E12 
ax.set_xlim([-limit, limit])
ax.set_ylim([-limit, limit])
ax.set_zlim([-limit, limit])

plt.tight_layout()
plt.show()

print("End of plot")