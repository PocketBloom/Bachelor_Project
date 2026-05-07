
# Goal: Simulate an accurate orbit and perihelion precession for TU3 
# (Then it can be applied to the other asteroids)

# Middle steps 1: Apply General Relativity & Solar quadrupole Moment 
# Also apply the Yarkowsky effect
# For this argue why these effects are the only relevant

# Middle steps 2: Is it okay to use the Sun as a point-mass
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

# Load spice kernels
spice.load_standard_kernels()

# Set simulation start and end epochs (total simulation time of 5 years)
# Start dat = 25th of April 2004 (arbitrary choice)
# Tudat works in J2000, so use seconds
simulation_start_epoch = DateTime(2000, 4, 25).to_epoch()
simulation_end_epoch   = simulation_start_epoch + 5 * constants.JULIAN_YEAR


# Define bodies in simulation
bodies_to_create = [
    "Sun",
    "Earth",
    "Moon",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Uranus",
    "Neptune",
    # Then include the asteroid
    "1998 TU3"
]

bodies_to_propagate = bodies_to_create

# Create bodies in simulation.
body_settings = environment_setup.get_default_body_settings(bodies_to_create)
body_system = environment_setup.create_system_of_bodies(body_settings)



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
        # Asteroids are assigned to the Sun
        central_bodies_hierarchical.append("Sun")


# Define the accelerations acting on each body
# Assume each body is a point mass
acceleration_dict = {}
for body_i in bodies_to_create:
    current_accelerations = {}
    for body_j in bodies_to_create:
        if body_i != body_j:
            current_accelerations[body_j] = [
                propagation_setup.acceleration.point_mass_gravity()
            ]
    acceleration_dict[body_i] = current_accelerations


# Convert acceleration mappings into acceleration models for both propagation variants
for propagation_variant in ["barycentric", "hierarchical"]:
    central_bodies = central_bodies_barycentric if propagation_variant == "barycentric" else central_bodies_hierarchical

    acceleration_models = propagation_setup.create_acceleration_models(
        body_system = body_system,
        selected_acceleration_per_body = acceleration_dict,
        bodies_to_propagate = bodies_to_propagate,
        central_bodies = central_bodies
    )

    if propagation_variant == "barycentric":
        acceleration_models_barycentric = acceleration_models
    else:
        acceleration_models_hierarchical = acceleration_models


# Define the initial state of each body, taking them from SPICE
for propagation_variant in ["barycentric", "hierarchical"]:
    central_bodies = central_bodies_barycentric if propagation_variant == "barycentric" else central_bodies_hierarchical

    system_initial_state = propagation.get_initial_state_of_bodies(
        bodies_to_propagate = bodies_to_propagate,
        central_bodies = central_bodies,
        body_system = body_system,
        initial_time = simulation_start_epoch #defined at the start
    )

    if propagation_variant == "barycentric":
        system_initial_state_barycentric = system_initial_state
    else:
        system_initial_state_hierarchical = system_initial_state


# Now, to create the conditions for propagation:

# Create termination settings
termination_settings = propagation_setup.propagator.time_termination(simulation_end_epoch) # 5 years after the epoch begins

# Create numerical integrator settings
fixed_step_size = 3600.0    # each hour
integrator_settings = propagation_setup.integrator.runge_kutta_fixed_step(
    fixed_step_size, coefficient_set=propagation_setup.integrator.CoefficientSets.rk_4
)

# Create propagation settings
for propagation_variant in ["barycentric", "hierarchical"]:

    if propagation_variant == "barycentric":
        propagator_settings_barycentric = propagation_setup.propagator.translational(
            central_bodies_barycentric,
            acceleration_models_barycentric,
            bodies_to_propagate,
            system_initial_state_barycentric,
            simulation_start_epoch,
            integrator_settings,
            termination_settings
        )
    else:
        propagator_settings_hierarchical = propagation_setup.propagator.translational(
            central_bodies_hierarchical,
            acceleration_models_hierarchical,
            bodies_to_propagate,
            system_initial_state_hierarchical,
            simulation_start_epoch,
            integrator_settings,
            termination_settings
        )

# Propagate the system of bodies and save the state history (all in one step)
for propagation_variant in ["barycentric", "hierarchical"]:

    if propagation_variant == "barycentric":
        results_barycentric = simulator.create_dynamics_simulator(
            body_system, propagator_settings_barycentric).state_history
            # state_history retrieves the propagated trajectory data
    else:
        results_hierarchical = simulator.create_dynamics_simulator(
            body_system, propagator_settings_hierarchical).state_history
        

# Plot the results
print("Start of plot")

# Convert the state dictionary to a multi-dimensional array
barycentric_system_state_array = result2array(results_barycentric)

fig1 = plt.figure(figsize=(8, 8))
ax1 = fig1.add_subplot(111, projection='3d')
ax1.set_title(f'System state evolution of all bodies w.r.t SSB.')

for i, body in enumerate(bodies_to_propagate):
    # Plot the 3D trajectory of each body
    ax1.plot(barycentric_system_state_array[:, 6 * i + 1], barycentric_system_state_array[:, 6 * i + 2],
             barycentric_system_state_array[:, 6 * i + 3],
             label=body)
    # Plot the initial position of each body
    ax1.scatter(barycentric_system_state_array[0, 6 * i + 1], barycentric_system_state_array[0, 6 * i + 2],
                barycentric_system_state_array[0, 6 * i + 3],
                marker='x')

# Add the position of the central body: the Solar System Barycenter
ax1.scatter(0, 0, 0, marker='x', label="SSB", color='black')

# Add a legend, labels, and use a tight layout to save space
ax1.legend()
ax1.set_xlabel('x [m]')
ax1.set_xlim([-2.5E11, 2.5E11])
ax1.set_ylabel('y [m]')
ax1.set_ylim([-2.5E11, 2.5E11])
ax1.set_zlabel('z [m]')
ax1.set_zlim([-2.5E11, 2.5E11])
plt.tight_layout()

print("End of plot")