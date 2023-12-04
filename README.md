# Drone Trajectory Processing and Visualization

This repository contains a collection of Python scripts for processing and visualizing drone trajectories. The scripts perform various operations such as segmenting trajectories into input and output segments, resampling trajectories, and plotting them. This is useful for training models for trajectory prediction in 3D.

![traj1](resources/Figure_1.png)
![traj2](resources/Figure_2.png)


# Installation

Before running the scripts, you need to install the required Python packages. You can install them using `pip`:

```bash
pip install numpy scipy pandas matplotlib
```

Or if you prefer using a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

In this case, the `requirements.txt` file should contain:

```
numpy
scipy
pandas
matplotlib
```

# Trajectory File Formats

The expected file format for the trajectory files is CSV or TXT with the following columns:

- `timestamp`: The time at which the sample was taken.
- `tx`: The x-coordinate of the drone at the given timestamp.
- `ty`: The y-coordinate of the drone at the given timestamp.
- `tz`: The z-coordinate of the drone at the given timestamp.

# Terminology
* **Segment** Array of points in 3D, equally spaced in time.

* **Input segment** A segment that precedes an output segment. Can be used as an input to a model to be trained.

* `inp_seg_len` Input segment lenght. The number of points that constitute an input segment.

* **Output segment** A segment that comes after another. This can be the output of a model, given the corresponding input segment`.

* `out_seg_len` Input segment lenght. The number of points that constitute an output segment.

# Scripts

## 1. `process_single_trajectory.py`

This script processes a single drone trajectory to create input and output segments. The segments are saved in `.npz` format.

### Usage

```bash
python process_single_trajectory.py <trajectory_file> <input_segment_length> <output_segment_length> [--compute_velocity]
```

### Arguments

- `trajectory_file`: Path to the CSV or TXT file containing the drone position trajectory.
- `input_segment_length`: Length of each input segment.
- `output_segment_length`: Length of each output segment.
- `--compute_velocity`: Optional flag to compute velocity segments instead of position.



## 2. `process_multiple_trajectories.py`

This script processes multiple drone trajectories in a directory to create input and output segments for each trajectory. The segments are concatenated and saved in a single `.npz` file.

### Usage

```bash
python process_multiple_trajectories.py <directory_path> <input_segment_length> <output_segment_length> [--compute_velocity]
```

### Arguments

- `directory_path`: Path to the directory containing multiple drone trajectory files.
- `input_segment_length`: Length of each input segment.
- `output_segment_length`: Length of each output segment.
- `--compute_velocity`: Optional flag to compute velocity segments instead of position.

### Content of the `.npz` file:

1. **input_segments**:
    - Shape: `(3, inp_seg_len, total_num_input_segments)`
    - Description: This is a 3D array where each "slice" along the third dimension represents a segment of the input trajectory. The first dimension corresponds to the three coordinates `tx`, `ty`, and `tz`. The second dimension corresponds to the time steps in each segment.

2. **output_segments**:
    - Shape: `(3, out_seg_len, total_num_output_segments)`
    - Description: Similar to `input_segments`, but for the output segments.

3. **num_input_segments**:
    - Shape: Scalar
    - Description: Total number of input segments processed across all files.

4. **num_output_segments**:
    - Shape: Scalar
    - Description: Total number of output segments processed across all files.

5. **inp_seg_len**:
    - Shape: Scalar
    - Description: The length of each input segment.

6. **out_seg_len**:
    - Shape: Scalar
    - Description: The length of each output segment.

7. **knots_input_i** (for each segment i):
    - Shape: `(inp_seg_len + k + 1,)` where `k` is the degree of the spline (3 in our case).
    - Description: Knots of the spline representation for the i-th input segment.

8. **coeffs_input_i** (for each segment i):
    - Shape: `(inp_seg_len,)`
    - Description: Coefficients of the spline representation for the i-th input segment.

9. **knots_output_i** (for each segment i):
    - Shape: `(out_seg_len + k + 1,)`
    - Description: Knots of the spline representation for the i-th output segment.

10. **coeffs_output_i** (for each segment i):
    - Shape: `(out_seg_len,)`
    - Description: Coefficients of the spline representation for the i-th output segment.

## 3. `trajectory_to_segmetns.py`

This script takes a directory of drone trajectories and divides each trajectory into equal segments of a given length. Note that there are no input/output segments here. the script simply divides the trajectory into consecutive segments (think of a sequence of words in a sentence!).

### Usage

```bash
python divide_into_segments_multiple.py <directory_path> <segment_length> [--compute_velocity]
```

### Arguments

- `directory_path`: Path to the directory containing multiple drone trajectory files.
- `segment_length`: Length of each segment.
- `--compute_velocity`: Optional flag to compute velocity segments instead of position.

### `.npz` File Contents

The `.npz` file contains multiple arrays, each corresponding to a different trajectory file. The naming convention is `<filename>_segments`.

- `segment_length`: A scalar indicating the length of each segment.

## 4. `resample_trajectory.py`

This script resamples each drone trajectory in a directory at a given sampling time. The resampled trajectories are saved in a new directory.

### Usage

```bash
python resample_trajectory.py <directory_path> <sampling_time_in_seconds>
```

### Arguments

- `directory_path`: Path to the directory containing multiple drone trajectory files.
- `sampling_time_in_seconds`: The time interval for resampling in seconds.

## 5. `plot_trajectory.py`

This script plots a single drone trajectory from a CSV or TXT file. It also has an option to plot velocity vectors.

### Usage

```bash
python plot_trajectory.py <trajectory_file> [--plot_velocity]
```

### Arguments

- `trajectory_file`: Path to the CSV or TXT file containing the drone position trajectory.
- `--plot_velocity`: Optional flag to plot velocity vectors.

## 6. `compute_stats.py`

Script for Computing Position and Velocity Statistics from Trajectory Data.

This script reads trajectory data in CSV or TXT format from a specified directory.
Each file should contain timestamp, tx, ty, and tz columns, representing time and
3D position data. The script computes the mean and standard deviation of positions (tx, ty, tz),
calculates the velocity components (vx, vy, vz) and their magnitudes, and then computes
the mean and standard deviation of the velocity magnitudes.

Additionally, it computes and prints the maximum length of all position vectors and
the maximum velocity magnitudes from all trajectory files. These values are also saved
in the respective .npz files.

The script also computes, saves, and prints the covariance matrices and their inverses
for both position and velocity datasets, and performs a whitening transformation on the data.

The results, including position and velocity statistics and covariance matrices, are saved 
in two .npz files: `pos_stats.npz` and `vel_stats.npz`. It also generates histograms for the positions 
and velocity magnitudes.

The script also normalizes the original trajectories (using max norm, and whitening) and saves the normalized trajectories in CSV/TXT files in the parent directory of the provided path. These normalized trajectories can then be processed by `process_multiple_trajectories.py` to generate normalized position and velocity datasets for direct training.

### Usage:
    python compute_stats.py <directory_path>

Example:
    python compute_stats.py /path/to/directory

Where '/path/to/directory' is the path to the directory containing your CSV/TXT files.



# Ignored Files and Directories

The `.gitignore` file is set to ignore any `.npz` files and directories that start with "resampled".
