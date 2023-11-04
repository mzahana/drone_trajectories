"""
3D Trajectory Generator Script

This script generates two types of 3D trajectory datasets: linear and circular.
Each trajectory is saved to a separate text file with columns for timestamp, tx, ty, and tz.
The linear trajectories have a user-defined constant velocity and optional random noise.
The circular trajectories are defined by a constant speed and parameters for the circle (center, radius, height),
and are now generated on a plane with a randomized normal vector, creating tilted circles.

Usage:
  python generate_trajectories.py <output_directory> [--dt <time_step>]

Arguments:
  output_directory: The directory where the trajectory files will be saved.
  --dt:             Optional. Time step in seconds for the trajectory points. Default is 0.1 seconds.

Example:
  python generate_trajectories.py ./trajectories --dt 0.05

This will generate the trajectories and save them in the './trajectories' directory with a time step of 0.05 seconds.

"""

import os
import numpy as np
import argparse

# Set up the argument parser
parser = argparse.ArgumentParser(description="Generate 3D trajectory datasets with linear and tilted circular trajectories.")
parser.add_argument("path", help="Directory where the trajectory files will be saved.", type=str)
parser.add_argument("--dt", help="Time step in seconds for the trajectory points. Default is 0.1 sec.", type=float, default=0.1)
args = parser.parse_args()

# Directory where the files will be saved
output_path = args.path
dt = args.dt  # Time step in seconds

# Ensure the directory exists
if not os.path.exists(output_path):
    os.makedirs(output_path)

def save_to_txt(filename, data):
    """Save data to a .txt file in the given directory."""
    complete_path = os.path.join(output_path, filename)
    with open(complete_path, 'w') as f:
        f.write("timestamp,tx,ty,tz\n")
        for line in data:
            f.write(",".join(str(x) for x in line) + "\n")

def rotation_matrix_from_vectors(vec1, vec2):
    """Find the rotation matrix that aligns vec1 to vec2"""
    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def circular_trajectory(center, radius, height, speed, normal, duration):
    """Generate a tilted circular trajectory."""
    timestamps = np.arange(0, duration, dt)
    data = []
    angular_speed = speed / radius
    # Create rotation matrix to tilt the circle
    rot_matrix = rotation_matrix_from_vectors(np.array([0,0,1]), np.array(normal))
    for t in timestamps:
        theta = angular_speed * t
        x, y, z = radius * np.cos(theta), radius * np.sin(theta), height
        # Apply rotation to the circle points
        rotated_point = rot_matrix.dot(np.array([x, y, z]))
        tx, ty, tz = rotated_point + center
        data.append([t, tx, ty, tz])
    return data

def linear_trajectory(velocity, duration, noise=0):
    """Generate a linear trajectory."""
    timestamps = np.arange(0, duration, dt)
    data = []
    for t in timestamps:
        tx = velocity[0] * t + np.random.uniform(-noise, noise)
        ty = velocity[1] * t + np.random.uniform(-noise, noise)
        tz = velocity[2] * t + np.random.uniform(-noise, noise)
        data.append([t, tx, ty, tz])
    return data

def lemniscate_trajectory(scale, speed, normal, duration):
    """Generate a tilted lemniscate (infinity-shaped) trajectory."""
    timestamps = np.arange(0, duration, dt)
    data = []
    # Create rotation matrix to tilt the lemniscate
    rot_matrix = rotation_matrix_from_vectors(np.array([0, 0, 1]), np.array(normal))
    for t in timestamps:
        theta = speed * t
        x = (scale * np.cos(theta)) / (1 + np.sin(theta)**2)
        y = (scale * np.cos(theta) * np.sin(theta)) / (1 + np.sin(theta)**2)
        z = 0  # Lemniscate is initially in the XY plane
        # Apply rotation to the lemniscate points
        rotated_point = rot_matrix.dot(np.array([x, y, z]))
        data.append([t, *rotated_point])
    return data

# Generate random velocities and circle parameters with random normal vectors
velocities = [tuple(np.random.uniform(-5, 5, 3)) for _ in range(100)]
circle_parameters = [(
    tuple(np.random.uniform(-10, 10, 3)),  # Center
    np.random.uniform(1, 10),  # Radius
    np.random.uniform(-5, 5),  # Height
    np.random.uniform(0.1, 5),  # Speed
    tuple(np.random.normal(0, 1, 3))  # Normal vector
) for _ in range(100)]

# Generate random lemniscate parameters with random normal vectors
lemniscate_parameters = [(
    np.random.uniform(1, 5),  # Scale
    np.random.uniform(0.1, 2),  # Speed
    tuple(np.random.normal(0, 1, 3))  # Normal vector
) for _ in range(100)]

# Save linear trajectories
for i, v in enumerate(velocities):
    trajectory = linear_trajectory(v, 10)  # Duration of 10 seconds
    save_to_txt(f"line_{i+1}.txt", trajectory)

# Save circular trajectories with tilt
for i, params in enumerate(circle_parameters):
    center, radius, height, speed, normal = params
    duration = 2 * np.pi * radius / speed  # Duration to complete one circle
    trajectory = circular_trajectory(center, radius, height, speed, normal, duration)
    save_to_txt(f"circle_{i+1}.txt", trajectory)

# Save lemniscate trajectories with tilt
for i, params in enumerate(lemniscate_parameters):
    scale, speed, normal = params
    duration = 10  # Duration can be arbitrary; adjust as needed
    trajectory = lemniscate_trajectory(scale, speed, normal, duration)
    save_to_txt(f"lemniscate_{i+1}.txt", trajectory)

print("Trajectories generated at", output_path)
