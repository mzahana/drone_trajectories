import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def compute_velocity(data):
    # Compute velocities using finite differences
    data['vx'] = data['tx'].diff() / data['timestamp'].diff()
    data['vy'] = data['ty'].diff() / data['timestamp'].diff()
    data['vz'] = data['tz'].diff() / data['timestamp'].diff()
    # Drop the first row as it will have NaN values for velocities
    data = data.iloc[1:]
    return data

def process_files(directory_path, figure_title="Data Distribution of Axes"):
    # List all files in the directory with .csv or .txt extensions
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f)) and (f.endswith('.csv') or f.endswith('.txt'))]

    # Check if there are any CSV or TXT files in the directory
    if not files:
        print("No CSV or TXT files found in the specified directory.")
        return

    # Initialize lists to store data from all files
    tx_values, ty_values, tz_values = [], [], []
    vx_values, vy_values, vz_values = [], [], []

    # Process each file
    for file in files:
        file_path = os.path.join(directory_path, file)
        try:
            # Read file (assuming comma-separated values for both .csv and .txt)
            df = pd.read_csv(file_path, sep=',')
            
            # Compute velocities
            df = compute_velocity(df)

            # Append data to the lists
            tx_values.extend(df['tx'].tolist())
            ty_values.extend(df['ty'].tolist())
            tz_values.extend(df['tz'].tolist())
            vx_values.extend(df['vx'].tolist())
            vy_values.extend(df['vy'].tolist())
            vz_values.extend(df['vz'].tolist())
        except Exception as e:
            print(f"Error processing file {file}: {e}")

    # Calculate mean and variance for each column
    stats = {
        'tx': (pd.Series(tx_values).mean(), pd.Series(tx_values).var()),
        'ty': (pd.Series(ty_values).mean(), pd.Series(ty_values).var()),
        'tz': (pd.Series(tz_values).mean(), pd.Series(tz_values).var()),
        'vx': (pd.Series(vx_values).mean(), pd.Series(vx_values).var()),
        'vy': (pd.Series(vy_values).mean(), pd.Series(vy_values).var()),
        'vz': (pd.Series(vz_values).mean(), pd.Series(vz_values).var())
    }

    for key, (mean, var) in stats.items():
        unit = 'm' if 't' in key else 'm/s'
        print(f"{key}: Mean = {mean} {unit}, Variance = {var} {unit}^2")

    # Visualize data distribution using histograms
    plt.figure(figsize=(20, 10))
    plt.suptitle(figure_title, fontsize=16)

    axes = ['tx', 'ty', 'tz', 'vx', 'vy', 'vz']
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow']
    for i, (ax, color) in enumerate(zip(axes, colors)):
        row = 1 if i < 3 else 2  # Position figures on the first row, velocity on the second
        col = i % 3 + 1
        plt.subplot(2, 3, (row-1)*3 + col)
        values = eval(f"{ax}_values")
        unit = 'm' if 't' in ax else 'm/s'
        plt.hist(values, bins=50, color=color, alpha=0.7)
        plt.title(f'Distribution of {ax}\nMean: {stats[ax][0]:.2f} {unit}, Variance: {stats[ax][1]:.2f} {unit}^2')
        plt.xlabel(f'{ax} values ({unit})')
        plt.ylabel('Frequency')

    plt.tight_layout()
    plt.subplots_adjust(top=0.90)
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 script_name.py <directory_path> [figure_title]")
        sys.exit(1)

    directory_path = sys.argv[1]
    if not os.path.exists(directory_path):
        print("The specified directory does not exist.")
        sys.exit(1)

    # Check if a title is provided, otherwise use the default
    title = sys.argv[2] if len(sys.argv) > 2 else "Data Distribution of Axes"

    process_files(directory_path, title)
