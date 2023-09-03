import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse
import os
import numpy as np

def read_trajectory(file_path):
    df = pd.read_csv(file_path)
    return df

def compute_velocity(df):
    df_velocity = df[['tx', 'ty', 'tz']].diff() / df['timestamp'].diff().values[:, None]
    return df_velocity.dropna()

def plot_trajectory(df, title, plot_velocity=False):
    if plot_velocity:
        fig, axs = plt.subplots(2, 1, subplot_kw={'projection': '3d'})
        ax1, ax2 = axs
    else:
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
        df_velocity = compute_velocity(df)
        ax2.quiver(df_velocity['tx'].iloc[:-1], df_velocity['ty'].iloc[:-1], df_velocity['tz'].iloc[:-1],
                   df_velocity['tx'].diff().iloc[1:], df_velocity['ty'].diff().iloc[1:], df_velocity['tz'].diff().iloc[1:],
                   color='r', label='Velocity')
        
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
