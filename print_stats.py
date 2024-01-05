import numpy as np
import sys

def print_stats(file_path):
    try:
        # Load the .npz file
        data = np.load(file_path, allow_pickle=True)

        # Print the contents of the file
        for key in data.files:
            print(f"{key}: {data[key]}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_npz_file>")
    else:
        file_path = sys.argv[1]
        print_stats(file_path)

