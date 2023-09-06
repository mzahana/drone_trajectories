import numpy as np
import matplotlib.pyplot as plt
import argparse

def visualize_npz_shapes(npz_path):
    # Load the .npz file
    data = np.load(npz_path)
    
    # Extract the main arrays
    input_segments = data['input_segments']
    output_segments = data['output_segments']
    
    # Extract shapes
    input_shape = input_segments.shape
    output_shape = output_segments.shape
    
    # Extract a sample knot and coefficient for input and output to get the common size
    common_size_input_knot = data['knots_input_0'].shape[0]
    common_size_input_coeff = data['coeffs_input_0'].shape[0]
    common_size_output_knot = data['knots_output_0'].shape[0]
    common_size_output_coeff = data['coeffs_output_0'].shape[0]
    
    # Create a 2D figure
    fig, ax = plt.subplots()
    
    # Plot the shapes
    bar_width = 0.35
    index = np.arange(3)  # tx, ty, tz
    labels = ['tx', 'ty', 'tz']
    
    bars_input = ax.bar(index, [input_shape[1]]*3, bar_width, color='blue', label='Input Segments')
    bars_output = ax.bar(index + bar_width, [output_shape[1]]*3, bar_width, color='red', label='Output Segments')
    
    # Overlay text inside bars and on top of bars
    for bar in bars_input:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval/2, f"{input_shape[2]}", ha='center', va='bottom', color='white', weight='bold')
        ax.text(bar.get_x() + bar.get_width()/2, yval, f"{yval}", ha='center', va='bottom', color='black', weight='bold')
    
    for bar in bars_output:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval/2, f"{output_shape[2]}", ha='center', va='bottom', color='white', weight='bold')
        ax.text(bar.get_x() + bar.get_width()/2, yval, f"{yval}", ha='center', va='bottom', color='black', weight='bold')
    
    # Add text annotation for common size of knots and coefficients
    ax.text(0.05, 0.95, f"Common size of knots for input segments: {common_size_input_knot}", transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='blue', alpha=0.5))
    ax.text(0.05, 0.90, f"Common size of coeffs for input segments: {common_size_input_coeff}", transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='blue', alpha=0.5))
    ax.text(0.05, 0.85, f"Common size of knots for output segments: {common_size_output_knot}", transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='red', alpha=0.5))
    ax.text(0.05, 0.80, f"Common size of coeffs for output segments: {common_size_output_coeff}", transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='red', alpha=0.5))
    
    # Set labels and title
    ax.set_xlabel('Dimensions')
    ax.set_ylabel('Segment Length')
    ax.set_title('Segment Lengths and Counts in .npz file')
    ax.set_xticks(index + bar_width/2)
    ax.set_xticklabels(['tx', 'ty', 'tz'])
    ax.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize the shape of arrays in an .npz file.')
    parser.add_argument('npz_path', type=str, help='Path to the .npz file')
    args = parser.parse_args()
    
    visualize_npz_shapes(args.npz_path)
