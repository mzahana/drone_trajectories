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

Each generated trajectory point includes a small amount of Gaussian noise to simulate real-world data
inaccuracies. Users can specify the noise level to adjust the variance of the added noise.

Example:
    python generate_random_trajectories.py ./trajectories --dt 0.1 --noise 0.02

This will generate the trajectory files in the `./trajectories` directory, with a time step of 0.1 seconds
and a noise level of 0.02 on the trajectory points.

The script will automatically generate 100 files for each trajectory type with randomized parameters.
The files are named `line_<i>.txt` for linear trajectories, `circle_<i>.txt` for circular trajectories,
and `lemniscate_<i>.txt` for lemniscate trajectories, where `<i>` is the index of the file starting from 1.
"""

import os
import numpy as np
import argparse

# Function to add Gaussian noise to a point
def add_noise(point, noise_level):
    return point + np.random.normal(0, noise_level, size=point.shape)

# Function to generate a linear trajectory with noise
def linear_trajectory(velocity, duration, dt, noise_level=0.01):
    timestamps = np.arange(0, duration, dt)
    data = []
    for t in timestamps:
        point = np.array([velocity[0] * t, velocity[1] * t, velocity[2] * t])
        noisy_point = add_noise(point, noise_level)
        data.append([t, *noisy_point])
    return data

# Function to generate a circular trajectory with noise
def circular_trajectory(center, radius, height, speed, normal, duration, dt, noise_level=0.01):
    timestamps = np.arange(0, duration, dt)
    data = []
    rot_matrix = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))
    for t in timestamps:
        angle = speed * t
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        z = center[2] + height
        point = np.array([x, y, z])
        rotated_point = rot_matrix.dot(point)
        noisy_point = add_noise(rotated_point, noise_level)
        data.append([t, *noisy_point])
    return data

# Function to generate a lemniscate (infinity-shaped) trajectory with noise
def lemniscate_trajectory(scale, speed, normal, duration, dt, noise_level=0.01):
    timestamps = np.arange(0, duration, dt)
    data = []
    rot_matrix = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))
    for t in timestamps:
        theta = speed * t
        x = (scale * np.cos(theta)) / (1 + np.sin(theta)**2)
        y = (scale * np.cos(theta) * np.sin(theta)) / (1 + np.sin(theta)**2)
        z = 0  # Lemniscate is initially in the XY plane
        point = np.array([x, y, z])
        rotated_point = rot_matrix.dot(point)
        noisy_point = add_noise(rotated_point, noise_level)
        data.append([t, *noisy_point])
    return data

# Helper function to save the trajectory to a text file with header
def save_to_txt(filename, trajectory):
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
args = parser.parse_args()

# Ensure the output directory exists
output_path = args.path
if not os.path.exists(output_path):
    os.makedirs(output_path)

# Generate a set of velocities for the linear trajectories
velocities = [tuple(np.random.uniform(-1, 1, size=3)) for _ in range(100)]


# Generate the linear trajectories
for i, velocity in enumerate(velocities, 1):
    traj_data = linear_trajectory(velocity, 10, args.dt, args.noise)
    save_to_txt(os.path.join(output_path, f'line_{i}.txt'), traj_data)

# Generate circle parameters
circle_parameters = [(
    np.random.uniform(-10, 10, size=3),  # Center
    np.random.uniform(1, 5),             # Radius
    np.random.uniform(0.1, 2),           # Speed
    np.random.normal(0, 1, 3)            # Normal vector, directly as np.array
) for _ in range(100)]

# Generate circular trajectories with tilt and noise
for i, (center, radius, speed, normal) in enumerate(circle_parameters, 1):
    normal = normal / np.linalg.norm(normal)  # Normalize the normal vector
    duration = 2 * np.pi * radius / speed  # Duration to complete one circle
    traj_data = circular_trajectory(center, radius, 0, speed, normal, duration, args.dt, args.noise)
    save_to_txt(os.path.join(output_path, f'circle_{i}.txt'), traj_data)

# Generate lemniscate parameters
lemniscate_parameters = [(
    np.random.uniform(0.5, 2.0),         # Scale
    np.random.uniform(0.1, 2),           # Speed
    tuple(np.random.normal(0, 1, 3)) # Normal vector
) for _ in range(100)]

# Generate lemniscate trajectories with tilt and noise
for i, params in enumerate(lemniscate_parameters, 1):
    scale, speed, normal = params
    normal = normal / np.linalg.norm(normal)  # Normalize the normal vector
    duration = 10  # Duration can be arbitrary; adjust as needed
    traj_data = lemniscate_trajectory(scale, speed, normal, duration, args.dt, args.noise)
    save_to_txt(os.path.join(output_path, f'lemniscate_{i}.txt'), traj_data)

print("Trajectories generated at", output_path)