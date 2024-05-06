import pandas as pd
import matplotlib.pyplot as plt
import numpy as np  # For numerical operations

def plot_comparison_with_factors(frequencies, magnitudes1, magnitudes2, factors):
    """
    Plots the frequency responses for two datasets across different factors.
    :param frequencies: Frequencies from the datasets.
    :param magnitudes1: Magnitudes from the first dataset.
    :param magnitudes2: Magnitudes from the second dataset.
    :param factors: A list of factors to apply to the magnitudes.
    """
    for factor in factors:
        # Adjust magnitudes1 or magnitudes2 by the current factor
        adjusted_magnitudes1 = [mag * factor for mag in magnitudes1]
        # or adjusted_magnitudes2 = [mag * factor for mag in magnitudes2] depending on your requirement

        # Now, you can plot these adjusted magnitudes in comparison to the original ones
        plt.figure(figsize=(12, 6))
        plt.plot(frequencies, adjusted_magnitudes1, label=f'Factor {factor}')
        plt.xlabel('Frequency / Hz')
        plt.ylabel('Magnitude / dB')
        plt.xscale('log')
        plt.title(f'Frequency Response for Factor {factor}')
        plt.legend()
        plt.grid(True)

        # If you wish to compare both datasets with the factor applied, repeat the plotting for magnitudes2 as well

    plt.tight_layout()
    plt.show()

def read_data_from_csv(file_path):
    """
    Reads frequency and magnitude data from a CSV file.
    :param file_path: Path to the CSV file.
    :return: Two lists - frequencies and magnitudes.
    """
    use_cols = ['Frequency (Hz)', 'TR1: Gain (dB)']
    data = pd.read_csv(file_path, usecols=use_cols)
    frequencies = data['Frequency (Hz)'].tolist()
    magnitudes = data['TR1: Gain (dB)'].tolist()
    return frequencies, magnitudes

def calculate_error(magnitudes1, magnitudes2):
    """
    Calculates the percentage error between two sets of magnitudes.
    :param magnitudes1: Magnitudes from the first dataset.
    :param magnitudes2: Magnitudes from the second dataset.
    :return: List of percentage errors.
    """
    # Calculate percentage error
    errors = []
    for mag1, mag2 in zip(magnitudes1, magnitudes2):
        error = abs(mag1 - mag2) / abs(mag1) * 100 if mag1 != 0 else 0
        errors.append(error)
    return errors

def plot_comparison_and_error(frequencies, magnitudes1, magnitudes2):
    """
    Plots the frequency responses and errors between two datasets.
    :param frequencies: Frequencies from the datasets.
    :param magnitudes1: Magnitudes from the first dataset.
    :param magnitudes2: Magnitudes from the second dataset.
    """
    errors = calculate_error(magnitudes1, magnitudes2)

    # Plotting frequency response
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(frequencies, magnitudes1, marker='o', label='OMICRON Gerät')
    plt.plot(frequencies, magnitudes2, marker='x', label='Picoscope Gerät')
    plt.xlabel('Frequency / Hz')
    plt.ylabel('Magnitude / dB')
    plt.xscale('log')
    plt.title('Frequency Response Comparison')
    plt.legend()
    plt.grid(True)

    # Plotting error
    plt.subplot(1, 2, 2)
    plt.plot(frequencies, errors, marker='^', label='Percentage Error', color='red')
    plt.xlabel('Frequency / Hz')
    plt.ylabel('Error / %')
    plt.xscale('log')
    plt.title('Percentage Error Between Devices')
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# Paths to the CSV files are specified
# Read the data from the CSV files
# Paths to the CSV files
# file_path1 = 'C:\\pico\\PicoScope-Python-API\\100Hz-10MHz-9kHz.csv'
# file_path1 = 'C:\\pico\\PicoScope-Python-API\\100Hz-10MHz-9kHz.csv'
# file_path1 = 'C:\\pico\\PicoScope-Python-API\\100Hz-10MHz-9kHz.csv'
file_path1 = 'C:\\pico\\PicoScope-Python-API\\100Hz-700kHz-9kHz.csv'
# file_path1 = 'C:\\pico\\PicoScope-Python-API\\100Hz-700kHz-220kHz.csv' # OMICRON
# file_path2 = 'C:\\pico\\PicoScope-Python-API\\100Hz-10MHz-220kHz.csv'
# file_path2 = 'C:\\pico\\PicoScope-Python-API\\dut_values90kHz20db.csv' # Picoscope
file_path2 = 'C:\\pico\\PicoScope-Python-API\\Picoscope_100Hz_700kHz_9kHz.csv'


# Read the data from the CSV files
frequencies1, magnitudes1 = read_data_from_csv(file_path1)
frequencies2, magnitudes2 = read_data_from_csv(file_path2)

# Ensure the frequencies from both datasets match if they don't adjust accordingly
# For simplicity, this example assumes they are the same.

# Plot the frequency responses and errors
plot_comparison_and_error(frequencies1, magnitudes1, magnitudes2)

factors = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4]
# Assume frequencies, magnitudes1, and magnitudes2 are already read from the files
plot_comparison_with_factors(frequencies1, magnitudes1, magnitudes2, factors)

# Assuming file_path1 and file_path2 are defined as before


# Read the data from the CSV files
# frequencies1, magnitudes1 = read_data_from_csv(file_path1)
# frequencies2, magnitudes2 = read_data_from_csv(file_path2)

# Plot the frequency responses with variations
# plot_frequency_response_with_variations(frequencies1, magnitudes1, frequencies2, magnitudes2)



# Plot the frequency responses
# plot_frequency_response(frequencies1, magnitudes1, frequencies2, magnitudes2)
