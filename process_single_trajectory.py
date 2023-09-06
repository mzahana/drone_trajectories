import pandas as pd
import argparse
import numpy as np
from scipy.interpolate import splrep

def read_trajectory(file_path):
    df = pd.read_csv(file_path)
    return df

def process_trajectory(df, inp_seg_len, out_seg_len, compute_velocity=False):
    input_segments = []
    output_segments = []
    spline_data_input = []
    spline_data_output = []
    
    if compute_velocity:
        # Compute velocity (difference in position / difference in time)
        df_velocity = df[['tx', 'ty', 'tz']].diff() / df['timestamp'].diff().values[:, None]
        df = df_velocity.dropna()
    
    for i in range(0, len(df) - inp_seg_len - out_seg_len + 1):
        input_segment = df.iloc[i:i+inp_seg_len][['tx', 'ty', 'tz']].values.T
        output_segment = df.iloc[i+inp_seg_len:i+inp_seg_len+out_seg_len][['tx', 'ty', 'tz']].values.T
        
        input_segments.append(input_segment)
        output_segments.append(output_segment)
        
        # Compute spline representation for the input segment
        tck_x_input = splrep(np.arange(inp_seg_len), input_segment[0], k=3)
        tck_y_input = splrep(np.arange(inp_seg_len), input_segment[1], k=3)
        tck_z_input = splrep(np.arange(inp_seg_len), input_segment[2], k=3)
        spline_data_input.append((tck_x_input, tck_y_input, tck_z_input))
        
        # Compute spline representation for the output segment
        tck_x_output = splrep(np.arange(out_seg_len), output_segment[0], k=3)
        tck_y_output = splrep(np.arange(out_seg_len), output_segment[1], k=3)
        tck_z_output = splrep(np.arange(out_seg_len), output_segment[2], k=3)
        spline_data_output.append((tck_x_output, tck_y_output, tck_z_output))
        
    input_segments = np.array(input_segments).transpose(1, 2, 0)
    output_segments = np.array(output_segments).transpose(1, 2, 0)
    
    # Separate spline data into individual components
    knots_input = [list(t[0][0]) for t in spline_data_input]
    coeffs_input = [list(t[0][1]) for t in spline_data_input]
    knots_output = [list(t[0][0]) for t in spline_data_output]
    coeffs_output = [list(t[0][1]) for t in spline_data_output]

    return input_segments, output_segments, knots_input, coeffs_input, knots_output, coeffs_output

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
    input_segments, output_segments, knots_input, coeffs_input, knots_output, coeffs_output = process_trajectory(df, inp_seg_len, out_seg_len, compute_velocity)
    
    num_input_segments = input_segments.shape[2]
    num_output_segments = output_segments.shape[2]
    
    print(f"Number of input segments: {num_input_segments}")
    print(f"Number of output segments: {num_output_segments}")
    
    # Save segments, spline data, and additional information to .npz file
    npz_data = {
        'input_segments': input_segments,
        'output_segments': output_segments,
        'num_input_segments': num_input_segments,
        'num_output_segments': num_output_segments,
        'inp_seg_len': inp_seg_len,
        'out_seg_len': out_seg_len
    }
    
    for i in range(num_input_segments):
        npz_data[f'knots_input_{i}'] = knots_input[i]
        npz_data[f'coeffs_input_{i}'] = coeffs_input[i]
        
    for i in range(num_output_segments):
        npz_data[f'knots_output_{i}'] = knots_output[i]
        npz_data[f'coeffs_output_{i}'] = coeffs_output[i]
    
    np.savez(save_path, **npz_data)
