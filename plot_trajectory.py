import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse
import os
import numpy as np

def read_trajectory(file_path):
    df = pd.read_csv(file_path)
    return df

# Define the modified functions to compute velocity and plot the trajectory

def compute_velocity(df):

    # Compute the velocity components

    df_velocity = df[['tx', 'ty', 'tz']].diff() / df['timestamp'].diff().values[:, None]

    # Combine the original position data with the velocity components

    df_combined = pd.concat([df[['tx', 'ty', 'tz']], df_velocity], axis=1)

    df_combined.columns = ['tx', 'ty', 'tz', 'vx', 'vy', 'vz']

    return df_combined.dropna()



def plot_trajectory(df, title, plot_velocity=False):

    if plot_velocity:

        # Two subplots: one for position and one for velocity

        fig, axs = plt.subplots(2, 1, subplot_kw={'projection': '3d'})

        ax1, ax2 = axs

    else:

        # Only one plot for position

        fig = plt.figure()

        ax1 = fig.add_subplot(111, projection='3d')

    

    # Plot position trajectory

    ax1.scatter(df['tx'], df['ty'], df['tz'], c='g', marker='o', label='Trajectory')

    ax1.set_xlabel('tx')

    ax1.set_ylabel('ty')

    ax1.set_zlabel('tz')

    ax1.set_title(f"{title} - Position")

    

    if plot_velocity:

        # Compute and plot velocity vectors

        df_combined = compute_velocity(df)

        ax2.quiver(df_combined['tx'], df_combined['ty'], df_combined['tz'],

                   df_combined['vx'], df_combined['vy'], df_combined['vz'],

                   color='r', length=0.1, normalize=True, label='Velocity')

        

        ax2.set_xlabel('tx')

        ax2.set_ylabel('ty')

        ax2.set_zlabel('tz')

        ax2.set_title(f"{title} - Velocity")

    

    plt.legend()

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Visualize drone trajectory from a CSV or TXT file.')
    parser.add_argument('file_path', type=str, help='Path to the CSV or TXT file containing the drone position trajectory')
    parser.add_argument('--plot_velocity', action='store_true', help='Plot velocity vectors along with position')
    
    args = parser.parse_args()
    
    file_path = args.file_path
    plot_velocity = args.plot_velocity
    title = os.path.basename(file_path)
    
    df = read_trajectory(file_path)
    
    plot_trajectory(df, title, plot_velocity)
