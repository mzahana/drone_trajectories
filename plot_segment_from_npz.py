import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Function to load the .npz file and plot the specified input/output segment
def plot_trajectory_segment(npz_filename, segment_index):
    # Load the .npz file
    data = np.load(npz_filename, allow_pickle=True)
    input_segments = data['input_segments']  # assuming the input segments are stored under the key 'inputs'
    output_segments = data['output_segments']  # assuming the output segments are stored under the key 'outputs'

    print(f"Shape of input data: {input_segments.shape}")

    # Extract the specific segment pair
    input_segment = input_segments[:, :, segment_index]
    output_segment = output_segments[:, :, segment_index]

    # Plotting
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot input segment
    ax.plot(input_segment[0, :], input_segment[1, :], input_segment[2, :], label='Input Segment')

    # Plot output segment, assuming it should be plotted separately
    ax.plot(output_segment[0, :], output_segment[1, :], output_segment[2, :], label='Output Segment')

    # Labels and legend
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py /path/to/your/file.npz segment_index")
        sys.exit(1)

    npz_file_path = sys.argv[1]
    segment_index = int(sys.argv[2])

    plot_trajectory_segment(npz_file_path, segment_index)
