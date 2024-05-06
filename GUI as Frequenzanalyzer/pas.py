import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def read_data_from_csv(file_path, frequency_column='Frequency (Hz)', magnitude_column='TR1: Gain (dB)'):
    """
    Reads frequency and magnitude data from a CSV file.
    :param file_path: Path to the CSV file.
    :param frequency_column: Name of the column containing frequency data.
    :param magnitude_column: Name of the column containing magnitude data.
    :return: Two lists - frequencies and magnitudes.
    """
    data = pd.read_csv(file_path, usecols=[frequency_column, magnitude_column])
    frequencies = data[frequency_column].tolist()
    magnitudes = data[magnitude_column].tolist()
    return frequencies, magnitudes

def apply_correction_factor(magnitudes, factor):
    """
    Applies a correction factor to magnitude data.
    :param magnitudes: List of magnitude values.
    :param factor: Correction factor to be applied.
    :return: Corrected magnitudes.
    """
    return [magnitude * factor for magnitude in magnitudes]

def plot_with_correction_factors(frequencies, original_magnitudes, correction_factors, frequencies_omicron, magnitudes_omicron):
    """
    Plots OMICRON data, original Picoscope data, and Picoscope data with correction factors.
    :param frequencies: List of Picoscope frequencies.
    :param original_magnitudes: List of original Picoscope magnitude values.
    :param correction_factors: List of correction factors to apply to Picoscope data.
    :param frequencies_omicron: List of OMICRON frequencies.
    :param magnitudes_omicron: List of OMICRON magnitude values.
    """
    plt.figure(figsize=(14, 8))

    # Plot OMICRON data
    plt.plot(frequencies_omicron, magnitudes_omicron, label='OMICRON Data', marker='s', linestyle='-', color='black')

    # Plot original Picoscope data
    plt.plot(frequencies, original_magnitudes, label='Original Picoscope Data', marker='o', linestyle='-', color='blue')

    # Plot data with correction factors
    for factor in correction_factors:
        corrected_magnitudes = apply_correction_factor(original_magnitudes, factor)
        plt.plot(frequencies, corrected_magnitudes, label=f'Factor {factor}', linestyle='--')

    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.xscale('log')
    plt.title('Comparison of OMICRON and Picoscope Data with Correction Factors')
    plt.legend()
    plt.grid(True)
    plt.show()

# Specify the path to your CSV files
# Specify the path to your CSV files
file_path_omicron = 'C:\\pico\\PicoScope-Python-API\\100Hz-700kHz-9kHz.csv'  # Update this path
file_path_picoscope = 'C:\\pico\\PicoScope-Python-API\\Picoscope_100Hz_700kHz_9kHz.csv'  # Update this path

# Read the data from the CSV files
frequencies_omicron, magnitudes_omicron = read_data_from_csv(file_path_omicron)
frequencies_picoscope, magnitudes_picoscope = read_data_from_csv(file_path_picoscope)

# List of correction factors to apply
correction_factors = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4]

# Plot the OMICRON, original, and corrected Picoscope data
plot_with_correction_factors(frequencies_picoscope, magnitudes_picoscope, correction_factors, frequencies_omicron, magnitudes_omicron)


# # Read the data from the CSV files
# frequencies_omicron, magnitudes_omicron = read_data_from_csv(file_path_omicron)
# frequencies_picoscope, magnitudes_picoscope = read_data_from_csv(file_path_picoscope)

# # List of correction factors to apply
# correction_factors = [0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3, 4]

# # Plot the original and corrected Picoscope data
# plot_with_correction_factors(frequencies_picoscope, magnitudes_picoscope, correction_factors)
