import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def process_files(directory_path, figure_title="Data Distribution of Axes"):
    # List all files in the directory with .csv or .txt extensions
    files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f)) and (f.endswith('.csv') or f.endswith('.txt'))]

    # Check if there are any CSV or TXT files in the directory
    if not files:
        print("No CSV or TXT files found in the specified directory.")
        return

    # Initialize lists to store data from all files
    tx_values = []
    ty_values = []
    tz_values = []

    # Process each file
    for file in files:
        file_path = os.path.join(directory_path, file)
        try:
            # Read file (assuming comma-separated values for both .csv and .txt)
            df = pd.read_csv(file_path, sep=',')

            # Append data to the lists
            tx_values.extend(df['tx'].tolist())
            ty_values.extend(df['ty'].tolist())
            tz_values.extend(df['tz'].tolist())
        except Exception as e:
            print(f"Error processing file {file}: {e}")

    # Calculate mean and variance for each column
    tx_mean, tx_var = pd.Series(tx_values).mean(), pd.Series(tx_values).var()
    ty_mean, ty_var = pd.Series(ty_values).mean(), pd.Series(ty_values).var()
    tz_mean, tz_var = pd.Series(tz_values).mean(), pd.Series(tz_values).var()

    print("Mean and Variance for each axis (in meters):")
    print(f"tx: Mean = {tx_mean} m, Variance = {tx_var} m^2")
    print(f"ty: Mean = {ty_mean} m, Variance = {ty_var} m^2")
    print(f"tz: Mean = {tz_mean} m, Variance = {tz_var} m^2")

    # Visualize data distribution using histograms
    plt.figure(figsize=(15, 5))
    plt.suptitle(figure_title, fontsize=16)

    plt.subplot(1, 3, 1)
    plt.hist(tx_values, bins=50, color='blue', alpha=0.7)
    plt.title(f'Distribution of tx\nMean: {tx_mean:.2f} m, Variance: {tx_var:.2f} m^2')
    plt.xlabel('tx values (m)')
    plt.ylabel('Frequency')

    plt.subplot(1, 3, 2)
    plt.hist(ty_values, bins=50, color='green', alpha=0.7)
    plt.title(f'Distribution of ty\nMean: {ty_mean:.2f} m, Variance: {ty_var:.2f} m^2')
    plt.xlabel('ty values (m)')
    plt.ylabel('Frequency')

    plt.subplot(1, 3, 3)
    plt.hist(tz_values, bins=50, color='red', alpha=0.7)
    plt.title(f'Distribution of tz\nMean: {tz_mean:.2f} m, Variance: {tz_var:.2f} m^2')
    plt.xlabel('tz values (m)')
    plt.ylabel('Frequency')

    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
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
