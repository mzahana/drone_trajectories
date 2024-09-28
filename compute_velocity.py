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
- Option to resample data to have regular sampling time intervals.
- Uses argparse for command-line argument parsing.
- Displays a progress bar during processing.
- Prints the total count of processed files.

Usage:
    python compute_velocity.py path_to_csv_directory [--velocity-only] [--resample] [--sample-time SAMPLE_TIME]

Arguments:
    path_to_csv_directory       Path to the directory containing the input CSV files.

Options:
    --velocity-only             Output only timestamps and velocities without position data.
    --resample                  Resample data to have regular sampling time intervals.
    --sample-time SAMPLE_TIME   The sample time interval in seconds for resampling (default: 0.1).

Example:
    # Include both positions and velocities in the output, resample data to 0.1-second intervals
    python compute_velocity.py /path/to/csv_directory --resample

    # Output only timestamps and velocities, resample data to 0.05-second intervals
    python compute_velocity.py /path/to/csv_directory --velocity-only --resample --sample-time 0.05
"""

import os
import pandas as pd
import argparse
import numpy as np
from tqdm import tqdm
from scipy.interpolate import interp1d

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

def resample_data(df, sample_time):
    from scipy.interpolate import interp1d

    # Ensure the data is sorted by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Create new timestamps
    start_time = df['timestamp'].iloc[0]
    end_time = df['timestamp'].iloc[-1]
    new_timestamps = np.arange(start_time, end_time, sample_time)

    # Remove duplicate timestamps if any
    df = df.drop_duplicates(subset='timestamp')

    # Interpolate positions
    interp_tx = interp1d(df['timestamp'], df['tx'], kind='linear', fill_value="extrapolate")
    interp_ty = interp1d(df['timestamp'], df['ty'], kind='linear', fill_value="extrapolate")
    interp_tz = interp1d(df['timestamp'], df['tz'], kind='linear', fill_value="extrapolate")

    # Get interpolated positions
    new_tx = interp_tx(new_timestamps)
    new_ty = interp_ty(new_timestamps)
    new_tz = interp_tz(new_timestamps)

    # Create new DataFrame
    new_df = pd.DataFrame({
        'timestamp': new_timestamps,
        'tx': new_tx,
        'ty': new_ty,
        'tz': new_tz
    })
    return new_df

def process_files(input_dir, velocity_only, resample, sample_time):
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
            # Read the CSV file
            df = pd.read_csv(file_path)

            # Ensure that the columns are of numeric types
            df['timestamp'] = pd.to_numeric(df['timestamp'], errors='coerce')
            df['tx'] = pd.to_numeric(df['tx'], errors='coerce')
            df['ty'] = pd.to_numeric(df['ty'], errors='coerce')
            df['tz'] = pd.to_numeric(df['tz'], errors='coerce')

            # Drop rows with NaN values in essential columns
            df = df.dropna(subset=['timestamp', 'tx', 'ty', 'tz'])

            if resample:
                df = resample_data(df, sample_time)

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
    parser.add_argument('--resample', action='store_true',
                        help='Resample data to have regular sampling time intervals.')
    parser.add_argument('--sample-time', type=float, default=0.1,
                        help='Sample time interval in seconds for resampling (default: 0.1).')
    args = parser.parse_args()
    process_files(args.input_directory, args.velocity_only, args.resample, args.sample_time)
