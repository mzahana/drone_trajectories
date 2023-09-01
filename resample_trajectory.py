import pandas as pd
import argparse
import os
import numpy as np

def read_trajectory(file_path):
    df = pd.read_csv(file_path)
    return df

import numpy as np

def resample_trajectory(df, sampling_time):
    # Sort DataFrame by timestamp
    df = df.sort_values('timestamp')
    
    # Create a new array of timestamps at the given sampling time intervals
    new_timestamps = np.arange(df['timestamp'].min(), df['timestamp'].max(), sampling_time)
    
    # Interpolate tx, ty, tz values at the new timestamps
    new_tx = np.interp(new_timestamps, df['timestamp'], df['tx'])
    new_ty = np.interp(new_timestamps, df['timestamp'], df['ty'])
    new_tz = np.interp(new_timestamps, df['timestamp'], df['tz'])
    
    # Create a new DataFrame with the resampled trajectory
    df_resampled = pd.DataFrame({
        'timestamp': new_timestamps,
        'tx': new_tx,
        'ty': new_ty,
        'tz': new_tz
    })
    
    return df_resampled



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Resample drone trajectories at a given sampling time.')
    parser.add_argument('dir_path', type=str, help='Path to the directory containing the drone position trajectory files')
    parser.add_argument('sampling_time', type=float, help='Sampling time in seconds')
    
    args = parser.parse_args()
    
    dir_path = args.dir_path
    sampling_time = args.sampling_time
    
    # Create resampled_trajectories directory with sampling time in milliseconds if it doesn't exist
    resampled_dir_name = f"resampled_trajectories_{int(sampling_time * 1000)}ms"
    resampled_dir_path = os.path.join(os.path.dirname(dir_path), resampled_dir_name)
    
    if not os.path.exists(resampled_dir_path):
        os.makedirs(resampled_dir_path)
    
    for filename in os.listdir(dir_path):
        if filename.endswith('.csv') or filename.endswith('.txt'):
            file_path = os.path.join(dir_path, filename)
            df = read_trajectory(file_path)
            
            df_resampled = resample_trajectory(df, sampling_time)
            
            resampled_file_path = os.path.join(resampled_dir_path, filename)
            df_resampled.to_csv(resampled_file_path, index=False)
            
            print(f"Resampled {filename} and saved to {resampled_file_path}")
