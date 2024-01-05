"""
Plot specific traj:
    python plot_trajectory.py --file_path "path/to/your/trajectory.csv" --plot_velocity

Plot random number o trajectories
    python plot_trajectory.py --directory "path/to/trajectory/directory" --num_trajectories 3 --plot_velocity

"""
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse
import os
import numpy as np
import random

def read_trajectory(file_path):
    df = pd.read_csv(file_path)
    return df

def compute_velocity(df):
    df_velocity = df[['tx', 'ty', 'tz']].diff() / df['timestamp'].diff().values[:, None]
    df_combined = pd.concat([df[['tx', 'ty', 'tz']], df_velocity], axis=1)
    df_combined.columns = ['tx', 'ty', 'tz', 'vx', 'vy', 'vz']
    return df_combined.dropna()

def plot_trajectory(df, title, plot_velocity, ax):
    ax.scatter(df['tx'], df['ty'], df['tz'], c='g', marker='o', label='Trajectory')
    ax.set_xlabel('tx')
    ax.set_ylabel('ty')
    ax.set_zlabel('tz')
    ax.set_title(f"{title}")

    if plot_velocity:
        df_combined = compute_velocity(df)
        ax.quiver(df_combined['tx'], df_combined['ty'], df_combined['tz'],
                  df_combined['vx'], df_combined['vy'], df_combined['vz'],
                  color='r', length=0.1, normalize=False)

def get_trajectory_files(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and (f.endswith('.csv') or f.endswith('.txt'))]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize drone trajectory from a CSV or TXT file.')
    parser.add_argument('--file_path', type=str, help='Path to the CSV or TXT file containing the drone position trajectory')
    parser.add_argument('--directory', type=str, help='Directory containing multiple trajectory files')
    parser.add_argument('--num_trajectories', type=int, default=1, help='Number of random trajectories to plot from the directory')
    parser.add_argument('--plot_velocity', action='store_true', help='Plot velocity vectors along with position')
    
    args = parser.parse_args()

    if args.directory:
        files = get_trajectory_files(args.directory)
        if len(files) < args.num_trajectories:
            print("Number of trajectories requested exceeds the available files. Plotting all available trajectories.")
            num_to_plot = len(files)
        else:
            num_to_plot = args.num_trajectories

        # Determine the number of rows and columns for the subplots
        cols = 3
        rows = (num_to_plot + cols - 1) // cols

        fig = plt.figure(figsize=(cols * 5, rows * 5))
        random_files = random.sample(files, num_to_plot)

        for i, file in enumerate(random_files, 1):
            ax = fig.add_subplot(rows, cols, i, projection='3d')
            file_path = os.path.join(args.directory, file)
            df = read_trajectory(file_path)
            plot_trajectory(df, file, args.plot_velocity, ax)

        plt.tight_layout()
        plt.show()

    elif args.file_path:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        df = read_trajectory(args.file_path)
        title = os.path.basename(args.file_path)
        plot_trajectory(df, title, args.plot_velocity, ax)
        plt.show()
    else:
        print("Please provide either a file path or a directory.")
