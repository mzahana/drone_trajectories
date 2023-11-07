"""
3D Trajectory Generator Script

This script generates three types of 3D trajectories: linear, circular, and lemniscate (infinity-shaped),
and saves them as individual `.txt` files. Each trajectory file contains a series of points with the
fields timestamp, tx, ty, and tz, representing time and the 3D coordinates of the trajectory at that time.

Trajectories are generated with user-defined parameters such as constant velocities for linear trajectories
and varying circle center points, radii, heights, and speeds for circular trajectories. The lemniscate
trajectories are generated with random scales and tilted in 3D space according to a random normal vector.

Usage:
    python generate_random_trajectories.py <output_directory> [--dt <time_step>] [--noise <noise_level>]

Arguments:
    output_directory: Mandatory. The directory where the trajectory files will be saved.
                      The script will create the directory if it does not exist.
    --dt:            Optional. The time delta between each point in the trajectory. Default is 0.1 seconds.
    --noise:         Optional. The level of Gaussian noise to apply to the trajectory points. Default is 0.01.
    --ntraj:         Optional. The number of random trajectories for each trajectory type. Default is 100.
    --npoints        Minimum number of points in each trajectory. If the random generated trajectory has less than that, it will be not saved.

Each generated trajectory point includes a small amount of Gaussian noise to simulate real-world data
inaccuracies. Users can specify the noise level to adjust the variance of the added noise.

Example:
    python generate_random_trajectories.py ./trajectories --dt 0.1 --noise 0.02 --ntraj 1000

This will generate the trajectory files in the `./trajectories` directory, with a time step of 0.1 seconds
and a noise level of 0.02 on the trajectory points.

The script will automatically generate 100 files for each trajectory type with randomized parameters.
The files are named `line_<i>.txt` for linear trajectories, `circle_<i>.txt` for circular trajectories,
and `lemniscate_<i>.txt` for lemniscate trajectories, where `<i>` is the index of the file starting from 1.
"""

import os
import numpy as np
import argparse
import math

# Function to add Gaussian noise to a point
def add_noise(point, noise_level):
    return point + np.random.normal(0, noise_level, size=point.shape)

# Function to generate a linear trajectory with noise
def linear_trajectory(initial_point, velocity, duration, dt, noise_level=0.01):
    # timestamps = np.arange(0, duration, dt)
    num_points = int(duration / dt) + 1  # +1 to include the endpoint
    timestamps = np.linspace(0, duration, num_points)
    data = []
    for t in timestamps:
        point = np.array(initial_point)+ np.array([velocity[0] * t, velocity[1] * t, velocity[2] * t])
        noisy_point = add_noise(point, noise_level)
        data.append([t, *noisy_point])
    return data

def generate_speed(min_speed, max_speed):
    if min_speed >= max_speed:
        print(f" Error min_speed {min_speed} >= max_speed {max_speed}.")
        return []
    
    if (min_speed >=0 and max_speed > 0) or ( min_speed <0 and max_speed <=0):
        np.random.uniform(min_speed, max_speed)
    elif min_speed < 0 and max_speed > 0:
        speed = np.random.choice([
            np.random.uniform(min_speed, -0.5),  # Exclude values very close to zero
            np.random.uniform(0.5, max_speed)     # Exclude values very close to zero
        ])
        return speed

def generate_normal_vector():
    vector = np.random.normal(0, 1, 3)
    if np.linalg.norm(vector) < 1e-3:
        return np.array([0, 0, 1])  # Default to the upward-pointing vector if too close to zero
    return vector

# Function to generate a circular trajectory with noise
def circular_trajectory(center, radius, height, tangential_speed, normal, duration, dt, noise_level=0.01):
    num_points = int(duration / dt) + 1  # +1 to include the endpoint
    timestamps = np.linspace(0, duration, num_points)
    data = []
    rot_matrix = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))
    angular_speed = tangential_speed / radius  # Calculate angular speed from tangential speed and radius
    
    for t in timestamps:
        angle = angular_speed * t  # angle now represents the angular position
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        z = center[2] + height
        point = np.array([x, y, z])
        rotated_point = rot_matrix.dot(point)
        noisy_point = add_noise(rotated_point, noise_level)
        data.append([t, *noisy_point])
    return data

# Function to generate a lemniscate (infinity-shaped) trajectory with noise
def lemniscate_trajectory(scale, omega, normal, duration, dt, noise_level=0.01):
    # timestamps = np.arange(0, duration, dt)
    num_points = int(duration / dt) + 1  # +1 to include the endpoint
    timestamps = np.linspace(0, duration, num_points)
    data = []
    rot_matrix = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))
    for t in timestamps:
        theta = omega * t
        x = (scale * np.cos(theta)) / (1 + np.sin(theta)**2)
        y = (scale * np.cos(theta) * np.sin(theta)) / (1 + np.sin(theta)**2)
        z = 0  # Lemniscate is initially in the XY plane
        point = np.array([x, y, z])
        rotated_point = rot_matrix.dot(point)
        noisy_point = add_noise(rotated_point, noise_level)
        data.append([t, *noisy_point])
    return data

def tangent_velocity(theta, scale, speed):
    # Derivatives of the parametric equations for the lemniscate of Bernoulli
    dx_dtheta = -scale * (np.sin(theta) * (1 + np.sin(theta)**2) - 2 * np.cos(theta)**2 * np.sin(theta)) / (1 + np.sin(theta)**2)**2
    dy_dtheta = scale * (np.cos(theta)**3 - np.cos(theta)) / (1 + np.sin(theta)**2)**2
    # Add a small epsilon to avoid division by zero
    epsilon = 1e-8
    velocity_denominator = np.sqrt(dx_dtheta**2 + dy_dtheta**2) + epsilon
    # The magnitude of the velocity vector
    return speed / velocity_denominator

def lemniscate_trajectory2(scale, speed, normal, duration, dt, noise_level=0.01):
    # Time steps
    t_values = np.arange(0, duration, dt)
    # Initial conditions
    theta_values = [0]

    for _ in t_values[1:]:
        # Get the last theta value
        last_theta = theta_values[-1]
        # Calculate the tangent velocity at this theta
        tangent_vel = tangent_velocity(last_theta, scale, speed)
        # Use it to update theta
        dtheta = dt * speed / tangent_vel
        # Append the new theta value
        theta_values.append(last_theta + dtheta)

    # Compute the x, y values of the lemniscate
    x_values, y_values = scale * np.cos(theta_values) / (1 + np.sin(theta_values)**2), scale * np.sin(theta_values) * np.cos(theta_values) / (1 + np.sin(theta_values)**2)

    # Apply rotation
    rot_matrix = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))
    data = []
    for x, y in zip(x_values, y_values):
        point = np.array([x, y, 0])  # Lemniscate is initially in the XY plane with zero height
        rotated_point = rot_matrix.dot(point)
        noisy_point = add_noise(rotated_point, noise_level)
        data.append(noisy_point.tolist())
    
    return np.column_stack((t_values, data))



# Helper function to save the trajectory to a text file with header
def save_to_txt(filename, trajectory, npoints=100):
    if len(trajectory)==0:
        print(f"No trajectory data to write for {filename}.")
    
    # if len(trajectory) < npoints:
    #     print(f"len(trajectory) < {npoints}. Not saving it.")
    #     return
    with open(filename, 'w') as f:
        # Write the header
        f.write("timestamp,tx,ty,tz\n")
        # Write the trajectory points
        for point in trajectory:
            f.write(f"{point[0]:.2f}, {point[1]:.5f}, {point[2]:.5f}, {point[3]:.5f}\n")

# Function to generate a rotation matrix from two vectors
def rotation_matrix_from_vectors(vec1, vec2):
    a, b = vec1 / np.linalg.norm(vec1), vec2 / np.linalg.norm(vec2)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

# Parse arguments
parser = argparse.ArgumentParser(description="Generate 3D trajectory datasets.")
parser.add_argument("path", help="Output directory for trajectory files.", type=str)
parser.add_argument("--dt", help="Time delta for samples in trajectory.", type=float, default=0.1)
parser.add_argument("--noise", help="Noise level for the trajectory points.", type=float, default=0.01)
parser.add_argument("--ntraj", help="Number of random trajectories for each trajectory type", type=int, default=100)
parser.add_argument("--npoints", help="Minimum number of points in each trajectory", type=int, default=100)
args = parser.parse_args()

# Ensure the output directory exists
output_path = args.path
if not os.path.exists(output_path):
    os.makedirs(output_path)

min_speed = -15 # m/s
max_speed = 15
min_omega = -math.radians(100)
max_omega = math.radians(100) # rad/s
duration = 20.0; # secnods

# Generate a set of velocities for the linear trajectories
line_parameters = [(
    tuple(np.random.uniform(-100, 100, size=3)),            # initial_points, meters
    tuple(np.random.uniform(min_speed, max_speed, size=3))  # velocities, m/s
) for _ in range(args.ntraj)]

# Generate the linear trajectories
for i, (initial_point, velocity) in enumerate(line_parameters, 1):
    traj_data = linear_trajectory(initial_point, velocity, duration, args.dt, args.noise)
    save_to_txt(os.path.join(output_path, f'line_{i}.txt'), traj_data, args.npoints)

# Generate circle parameters
circle_parameters = [(
    np.random.uniform(-50, 50, size=3),  # Center
    np.random.uniform(1, 15),         # Radius
    generate_speed(min_speed, max_speed),                    # Speed, avoiding zero
    tuple(generate_normal_vector())            # Normal vector, directly as np.array
) for _ in range(args.ntraj)]

# Generate circular trajectories with tilt and noise
for i, (center, radius, speed, normal) in enumerate(circle_parameters, 1):
    normal = normal / np.linalg.norm(normal)  # Normalize the normal vector
    # duration = 2 * np.pi * radius / abs(speed)  # Duration to complete one circle
    traj_data = circular_trajectory(center, radius, 0, speed, normal, duration, args.dt, args.noise)
    save_to_txt(os.path.join(output_path, f'circle_{i}.txt'), traj_data, args.npoints)

# Generate lemniscate parameters
lemniscate_parameters = [(
    np.random.uniform(1.0, 30.0),         # Scale
    np.random.uniform(min_omega, max_omega),           # Speed
    tuple(generate_normal_vector()) # Normal vector
) for _ in range(args.ntraj)]

# Generate lemniscate trajectories with tilt and noise
for i, params in enumerate(lemniscate_parameters, 1):
    scale, speed, normal = params
    normal = normal / np.linalg.norm(normal)  # Normalize the normal vector
    traj_data = lemniscate_trajectory(scale, speed, normal, duration, args.dt, args.noise)
    save_to_txt(os.path.join(output_path, f'lemniscate_{i}.txt'), traj_data, args.npoints)

print("Trajectories generated at", output_path)