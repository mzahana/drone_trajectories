"""
Script for Computing Position and Velocity Statistics from Trajectory Data

This script reads trajectory data in CSV or TXT format from a specified directory.
Each file should contain timestamp, tx, ty, and tz columns, representing time and
3D position data. The script computes the mean and standard deviation of positions (tx, ty, tz),
calculates the velocity components (vx, vy, vz) and their magnitudes, and then computes
the mean and standard deviation of the velocity magnitudes.

Additionally, it computes and prints the maximum length of all position vectors and
the maximum velocity magnitudes from all trajectory files. These values are also saved
in the respective .npz files.

The script also computes, saves, and prints the covariance matrices and their inverses
for both position and velocity datasets, and performs a whitening transformation on the data.

The results, including position and velocity statistics and covariance matrices, are saved 
in two .npz files: pos_stats.npz and vel_stats.npz. It also generates histograms for the positions 
and velocity magnitudes.

Usage:
    python compute_stats.py <directory_path>

Example:
    python compute_stats.py /path/to/directory

Where '/path/to/directory' is the path to the directory containing your CSV/TXT files.
"""

import pandas as pd
import numpy as np
import os
import glob
import sys
import matplotlib.pyplot as plt

def process_file(filename, pos_mean, pos_L, vel_mean, vel_L, max_pos_length, max_vel_magnitude, dirs):
    df = pd.read_csv(filename)

    # Calculate differences for velocities and velocity magnitudes
    df['vx'] = df['tx'].diff() / df['timestamp'].diff()
    df['vy'] = df['ty'].diff() / df['timestamp'].diff()
    df['vz'] = df['tz'].diff() / df['timestamp'].diff()
    df['vel_magnitude'] = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)

    # Drop the first row for velocity data
    df_vel = df.drop(0).reset_index(drop=True)

    # Whitening transformations for positions
    pos_data = df[['tx', 'ty', 'tz']].values
    pos_centered = pos_data - pos_mean
    transformed_pos = np.dot(pos_L, pos_centered.T).T
    df_transformed_white_pos = pd.DataFrame(transformed_pos, columns=['tx', 'ty', 'tz'])
    df_transformed_white_pos.insert(0, 'timestamp', df['timestamp'])  # Insert timestamp as the first column

    # Whitening transformations for velocities
    vel_data = df_vel[['vx', 'vy', 'vz']].values
    vel_centered = vel_data - vel_mean
    transformed_vel = np.dot(vel_L, vel_centered.T).T
    df_transformed_white_vel = pd.DataFrame(transformed_vel, columns=['vx', 'vy', 'vz'])
    df_transformed_white_vel.insert(0, 'timestamp', df_vel['timestamp'])  # Insert adjusted timestamp for velocity

    # Max normalization
    normalized_pos_max = pos_data / max_pos_length
    df_transformed_max_pos = pd.DataFrame(normalized_pos_max, columns=['tx', 'ty', 'tz'])
    df_transformed_max_pos.insert(0, 'timestamp', df['timestamp'])

    normalized_vel_max = vel_data / max_vel_magnitude
    df_transformed_max_vel = pd.DataFrame(normalized_vel_max, columns=['vx', 'vy', 'vz'])
    df_transformed_max_vel.insert(0, 'timestamp', df['timestamp'])

    # Save the transformed data
    save_transformed_data(df_transformed_white_pos, 'white_norm_pos_'+os.path.basename(filename), dirs['pos_whitening'])
    save_transformed_data(df_transformed_white_vel, 'white_norm_vel_'+os.path.basename(filename), dirs['vel_whitening'])

    # Save the max normalized data
    save_transformed_data(df_transformed_max_pos, 'max_norm_pos_'+os.path.basename(filename), dirs['pos_max'])
    save_transformed_data(df_transformed_max_vel, 'max_norm_vel_'+os.path.basename(filename), dirs['vel_max'])

def save_transformed_data(data, filename, directory):
    data.to_csv(os.path.join(directory, filename), index=False)

def compute_stats(pos_df, vel_df, max_pos_length, max_vel_magnitude):
    pos_stats = {
        "input_mean": pos_df.mean().tolist(),
        "input_std": pos_df.std().tolist(),
        "cov_matrix": pos_df.cov().values,
        "L_matrix": np.linalg.cholesky(np.linalg.inv(pos_df.cov())).tolist(),
        "max_length": max_pos_length
    }
    vel_stats = {
        "input_mean": vel_df.mean().tolist(),
        "input_std": vel_df.std().tolist(),
        "cov_matrix": vel_df.cov().values,
        "L_matrix": np.linalg.cholesky(np.linalg.inv(vel_df.cov())).tolist(),
        "max_velocity": max_vel_magnitude
    }
    return pos_stats, vel_stats

def print_stats(pos_file, vel_file, pos_stats, vel_stats):
    print(f"Files saved: {os.path.abspath(pos_file)} and {os.path.abspath(vel_file)}")
    print("\nPosition Statistics:")
    for key, value in pos_stats.items():
        print(f"{key}: {value}")
    print("\nVelocity Statistics:")
    for key, value in vel_stats.items():
        print(f"{key}: {value}")

def plot_histograms(pos_df, vel_df, vel_mag_df):
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    axs[0, 0].hist(pos_df['tx'], bins=30, color='blue', alpha=0.7)
    axs[0, 0].set_title('Histogram of tx')
    axs[0, 1].hist(pos_df['ty'], bins=30, color='green', alpha=0.7)
    axs[0, 1].set_title('Histogram of ty')
    axs[1, 0].hist(pos_df['tz'], bins=30, color='red', alpha=0.7)
    axs[1, 0].set_title('Histogram of tz')
    axs[1, 1].hist(vel_mag_df, bins=30, color='purple', alpha=0.7)
    axs[1, 1].set_title('Histogram of Velocity Magnitude')

    plt.tight_layout()
    plt.show()

def compute_stats_and_transform(directory):
    all_files = glob.glob(os.path.join(directory, "*.csv")) + glob.glob(os.path.join(directory, "*.txt"))
    position_data = []
    velocity_data = []
    vel_magnitude_data = []  # For storing vel_magnitude separately

    max_pos_length = 0
    max_vel_magnitude = 0

    for filename in all_files:
        df = pd.read_csv(filename)
        df['vx'] = df['tx'].diff() / df['timestamp'].diff()
        df['vy'] = df['ty'].diff() / df['timestamp'].diff()
        df['vz'] = df['tz'].diff() / df['timestamp'].diff()
        df['vel_magnitude'] = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)
        df.dropna(subset=['vx', 'vy', 'vz', 'vel_magnitude'], inplace=True)

        position_data.append(df[['tx', 'ty', 'tz']])
        velocity_data.append(df[['vx', 'vy', 'vz']])
        vel_magnitude_data.append(df['vel_magnitude'])

        # Update maximum position vector length and velocity magnitude
        max_pos_length = max(max_pos_length, np.max(np.sqrt(df['tx']**2 + df['ty']**2 + df['tz']**2)))
        max_vel_magnitude = max(max_vel_magnitude, df['vel_magnitude'].max())

    if not position_data or not velocity_data:
        print("No CSV/TXT files found or files are empty.")
        return

    combined_pos_df = pd.concat(position_data, ignore_index=True)
    combined_vel_df = pd.concat(velocity_data, ignore_index=True)
    combined_vel_magnitude_df = pd.concat(vel_magnitude_data, ignore_index=True)

    # Compute statistics and Cholesky decomposition
    pos_stats, vel_stats = compute_stats(combined_pos_df, combined_vel_df, max_pos_length, max_vel_magnitude)

    # Create directories for transformed data and determine the parent directory
    # parent_dir = os.path.dirname(directory)
    # transformed_pos_dir = os.path.join(parent_dir, 'transformed_position_data')
    # transformed_vel_dir = os.path.join(parent_dir, 'transformed_velocity_data')
    # os.makedirs(transformed_pos_dir, exist_ok=True)
    # os.makedirs(transformed_vel_dir, exist_ok=True)

    # Create directories
    # parent_dir = os.path.join(directory, 'transformed_trajectories')
    parent_dir = os.path.dirname(directory)
    # Create the transformed_trajectories directory in the parent directory
    transformed_dir = os.path.join(parent_dir, 'transformed_trajectories')
    os.makedirs(transformed_dir, exist_ok=True)
    dirs = {
        'pos_whitening': os.path.join(transformed_dir, 'pos_trajectories_whitening_normalization'),
        'pos_max': os.path.join(transformed_dir, 'pos_trajectories_max_normalization'),
        'vel_whitening': os.path.join(transformed_dir, 'vel_trajectories_whitening_normalization'),
        'vel_max': os.path.join(transformed_dir, 'vel_trajectories_max_normalization')
    }
    for dir in dirs.values():
        os.makedirs(dir, exist_ok=True)

    # Save the statistics in the parent directory
    pos_stats_file = os.path.join(transformed_dir, 'pos_stats.npz')
    vel_stats_file = os.path.join(transformed_dir, 'vel_stats.npz')
    np.savez(pos_stats_file, **pos_stats)
    np.savez(vel_stats_file, **vel_stats)

    # Print statistics
    print_stats(pos_stats_file, vel_stats_file, pos_stats, vel_stats)

    
    # Process each file to transform and save data
    for filename in all_files:
        process_file(filename, pos_stats['input_mean'], pos_stats['L_matrix'], 
                     vel_stats['input_mean'], vel_stats['L_matrix'],
                     max_pos_length, max_vel_magnitude,
                     dirs)


    # Plot histograms of the original and velocity magnitude data
    plot_histograms(combined_pos_df, combined_vel_df, combined_vel_magnitude_df)

    # Print the paths to the saved npz files and the transformed directories
    print("Directories created and files saved:")
    print(f"Parent directory: {transformed_dir}")
    for key, value in dirs.items():
        print(f"{key}: {value}")
    print(f"pos_stats.npz saved at: {os.path.join(transformed_dir, 'pos_stats.npz')}")
    print(f"vel_stats.npz saved at: {os.path.join(transformed_dir, 'vel_stats.npz')}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compute_stats.py <directory_path>")
    else:
        directory_path = sys.argv[1]
        compute_stats_and_transform(directory_path)
