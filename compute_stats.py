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

The results, including position and velocity statistics, are saved in two .npz files:
pos_stats.npz and vel_stats.npz. It also generates histograms for the positions and
velocity magnitudes.

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

def process_file(filename):
    df = pd.read_csv(filename)

    # Calculate differences for velocities and handle NaN values
    df['vx'] = df['tx'].diff() / df['timestamp'].diff()
    df['vy'] = df['ty'].diff() / df['timestamp'].diff()
    df['vz'] = df['tz'].diff() / df['timestamp'].diff()

    # Drop the first row where the velocities are NaN due to diff
    df.dropna(subset=['vx', 'vy', 'vz'], inplace=True)

    # Compute velocity magnitude
    df['vel_magnitude'] = np.sqrt(df['vx']**2 + df['vy']**2 + df['vz']**2)

    return df

def compute_stats_and_plot(directory):
    all_files = glob.glob(os.path.join(directory, "*.csv")) + glob.glob(os.path.join(directory, "*.txt"))
    position_data = []
    velocity_data = []

    max_pos_length = 0
    max_vel_magnitude = 0

    for filename in all_files:
        df = process_file(filename)
        position_data.append(df[['tx', 'ty', 'tz']])
        velocity_data.append(df[['vel_magnitude']])

        # Update maximum position vector length and velocity magnitude
        max_pos_length = max(max_pos_length, np.max(np.sqrt(df['tx']**2 + df['ty']**2 + df['tz']**2)))
        max_vel_magnitude = max(max_vel_magnitude, df['vel_magnitude'].max())

    if not position_data or not velocity_data:
        print("No CSV/TXT files found or files are empty.")
        return

    combined_pos_df = pd.concat(position_data, ignore_index=True)
    combined_vel_df = pd.concat(velocity_data, ignore_index=True)

    # Compute Position Stats
    pos_stats = {
        "input_mean": combined_pos_df.mean().tolist(),
        "input_std": combined_pos_df.std().tolist(),
        "target_mean": combined_pos_df.mean().tolist(),
        "target_std": combined_pos_df.std().tolist(),
        "max_length": max_pos_length
    }

    # Compute Velocity Stats
    vel_stats = {
        "input_mean": [combined_vel_df['vel_magnitude'].mean()] * 3,
        "input_std": [combined_vel_df['vel_magnitude'].std()] * 3,
        "target_mean": [combined_vel_df['vel_magnitude'].mean()] * 3,
        "target_std": [combined_vel_df['vel_magnitude'].std()] * 3,
        "max_velocity": max_vel_magnitude
    }

    # Save the Statistics
    pos_stats_file = 'pos_stats.npz'
    vel_stats_file = 'vel_stats.npz'
    np.savez(pos_stats_file, **pos_stats)
    np.savez(vel_stats_file, **vel_stats)

    # Print file save locations, the Statistics, and maximum values
    print(f"Files saved: {os.path.abspath(pos_stats_file)} and {os.path.abspath(vel_stats_file)}")
    print("\nPosition Statistics:")
    print("Mean:", pos_stats["input_mean"])
    print("Standard Deviation:", pos_stats["input_std"])
    print("Maximum Position Vector Length:", max_pos_length)
    print("\nVelocity Magnitude Statistics:")
    print("Mean:", vel_stats["input_mean"])
    print("Standard Deviation:", vel_stats["input_std"])
    print("Maximum Velocity Magnitude:", max_vel_magnitude)

    # Plot histograms
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))

    axs[0, 0].hist(combined_pos_df['tx'].dropna(), bins=30, color='blue', alpha=0.7)
    axs[0, 0].set_title('Histogram of tx')

    axs[0, 1].hist(combined_pos_df['ty'].dropna(), bins=30, color='green', alpha=0.7)
    axs[0, 1].set_title('Histogram of ty')

    axs[1, 0].hist(combined_pos_df['tz'].dropna(), bins=30, color='red', alpha=0.7)
    axs[1, 0].set_title('Histogram of tz')

    axs[1, 1].hist(combined_vel_df['vel_magnitude'].dropna(), bins=30, color='purple', alpha=0.7)
    axs[1, 1].set_title('Histogram of Velocity Magnitude')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compute_stats.py <directory_path>")
    else:
        directory_path = sys.argv[1]
        compute_stats_and_plot(directory_path)
