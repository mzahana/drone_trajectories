import pandas as pd
import argparse
import numpy as np
import os

def read_trajectory(file_path):
    df = pd.read_csv(file_path)
    return df

def compute_velocity(df):
    df_velocity = df[['tx', 'ty', 'tz']].diff() / df['timestamp'].diff().values[:, None]
    return df_velocity.dropna()

def divide_into_segments(df, seg_len, compute_velocity=False):
    segments = []
    
    if compute_velocity:
        df = compute_velocity(df)
    
    for i in range(0, len(df) - seg_len + 1, seg_len):
        segment = df.iloc[i:i+seg_len][['tx', 'ty', 'tz']].values.T
        segments.append(segment)
        
    segments = np.array(segments).transpose(1, 2, 0)
    
    return segments

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Divide drone trajectories into consecutive segments.')
    parser.add_argument('dir_path', type=str, help='Path to the directory containing the drone position trajectory files')
    parser.add_argument('seg_len', type=int, help='Length of each segment')
    parser.add_argument('--compute_velocity', action='store_true', help='Compute velocity segments instead of position')
    parser.add_argument('--save_path', type=str, default='segments.npz', help='Path to save the .npz file')
    
    args = parser.parse_args()
    
    dir_path = args.dir_path
    seg_len = args.seg_len
    compute_velocity = args.compute_velocity
    save_path = args.save_path
    
    segment_dict = {}
    
    for filename in os.listdir(dir_path):
        if filename.endswith('.csv') or filename.endswith('.txt'):
            file_path = os.path.join(dir_path, filename)
            df = read_trajectory(file_path)
            segments = divide_into_segments(df, seg_len, compute_velocity)
            
            num_segments = segments.shape[2]
            print(f"Number of segments for {filename}: {num_segments}")
            
            # Flatten the 3D array to 2D
            segments_2D = segments.reshape(-1, segments.shape[2])
            
            # Save to dictionary
            segment_dict[filename] = segments_2D
    
    # Save segments and additional information to .npz file
    np.savez(save_path, **segment_dict, seg_len=seg_len)
