#!/usr/bin/env python3
"""
Script Name: compute_velocity.py

Description:
This script processes multiple CSV files containing timestamped drone position trajectories.
For each CSV file in the specified directory, it computes the velocities (vx, vy, vz) using
finite differences of the position data with respect to time. The processed CSV files are
saved in a new output directory with a meaningful name containing the word "velocity".

Features:
- Computes velocities based on position data (tx, ty, tz) and timestamps.
- Option to output only timestamps and velocities, excluding position data.
- Uses argparse for command-line argument parsing.
- Displays a progress bar during processing.
- Prints the total count of processed files.

Usage:
    python compute_velocity.py path_to_csv_directory [--velocity-only]

Arguments:
    path_to_csv_directory   Path to the directory containing the input CSV files.

Options:
    --velocity-only         If set, the output CSV files will contain only timestamps and velocities.

Example:
    # Include both positions and velocities in the output
    python compute_velocity.py /path/to/csv_directory

    # Output only timestamps and velocities
    python compute_velocity.py /path/to/csv_directory --velocity-only
"""

import os
import pandas as pd
import argparse
from tqdm import tqdm

def compute_velocity(df):
    # Compute time differences
    dt = df['timestamp'].diff().shift(-1)
    # Compute position differences
    dx = df['tx'].diff().shift(-1)
    dy = df['ty'].diff().shift(-1)
    dz = df['tz'].diff().shift(-1)
    # Compute velocities
    df['vx'] = dx / dt
    df['vy'] = dy / dt
    df['vz'] = dz / dt
    # Remove the last row where velocity cannot be computed
    df = df.iloc[:-1]
    return df

def process_files(input_dir, velocity_only):
    # Create output directory with a meaningful name
    parent_dir = os.path.dirname(os.path.abspath(input_dir))
    output_dir = os.path.join(parent_dir, 'velocity_processed_csv_files')
    os.makedirs(output_dir, exist_ok=True)

    # Get list of CSV files in the input directory
    file_list = [f for f in os.listdir(input_dir) if f.endswith('.csv')]
    total_files = len(file_list)

    # Process each CSV file with progress bar
    with tqdm(total=total_files, desc='Processing files', unit='file') as pbar:
        for filename in file_list:
            file_path = os.path.join(input_dir, filename)
            df = pd.read_csv(file_path)
            df = compute_velocity(df)
            if velocity_only:
                df = df[['timestamp', 'vx', 'vy', 'vz']]
            output_file = os.path.join(output_dir, filename)
            df.to_csv(output_file, index=False)
            # Update progress bar
            pbar.update(1)

    print(f"\nTotal files processed: {total_files}")

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='Compute velocities from position data in CSV files.')
        parser.add_argument('input_directory', help='Path to the directory containing the CSV files.')
        parser.add_argument('--velocity-only', action='store_true',
                            help='Output only timestamps and velocities without position data.')
        args = parser.parse_args()
        process_files(args.input_directory, args.velocity_only)
