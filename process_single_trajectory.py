import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse
import numpy as np
import os

def read_trajectory(file_path):
    df = pd.read_csv(file_path)
    return df

def process_trajectory(df, inp_seg_len, out_seg_len, compute_velocity=False):
    input_segments = []
    output_segments = []
    
    if compute_velocity:
        # Compute velocity (difference in position / difference in time)
        df_velocity = df[['tx', 'ty', 'tz']].diff() / df['timestamp'].diff().values[:, None]
        df = df_velocity.dropna()
    
    for i in range(0, len(df) - inp_seg_len - out_seg_len + 1):
        input_segment = df.iloc[i:i+inp_seg_len][['tx', 'ty', 'tz']].values.T
        output_segment = df.iloc[i+inp_seg_len:i+inp_seg_len+out_seg_len][['tx', 'ty', 'tz']].values.T
        
        input_segments.append(input_segment)
        output_segments.append(output_segment)
        
    input_segments = np.array(input_segments).transpose(1, 2, 0)
    output_segments = np.array(output_segments).transpose(1, 2, 0)
    
    return input_segments, output_segments

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process drone trajectory data.')
    parser.add_argument('file_path', type=str, help='Path to the CSV or TXT file containing the drone position trajectory')
    parser.add_argument('inp_seg_len', type=int, help='Length of input segments')
    parser.add_argument('out_seg_len', type=int, help='Length of output segments')
    parser.add_argument('--compute_velocity', action='store_true', help='Compute velocity trajectory instead of position')
    parser.add_argument('--save_path', type=str, default='segments.npz', help='Path to save the .npz file')
    
    args = parser.parse_args()
    
    file_path = args.file_path
    inp_seg_len = args.inp_seg_len
    out_seg_len = args.out_seg_len
    compute_velocity = args.compute_velocity
    save_path = args.save_path
    
    df = read_trajectory(file_path)
    input_segments, output_segments = process_trajectory(df, inp_seg_len, out_seg_len, compute_velocity)
    
    num_input_segments = input_segments.shape[2]
    num_output_segments = output_segments.shape[2]
    
    print(f"Number of input segments: {num_input_segments}")
    print(f"Number of output segments: {num_output_segments}")
    
    # Save segments and additional information to .npz file
    np.savez(save_path, 
             input_segments=input_segments, 
             output_segments=output_segments, 
             num_input_segments=num_input_segments, 
             num_output_segments=num_output_segments,
             inp_seg_len=inp_seg_len,
             out_seg_len=out_seg_len)
