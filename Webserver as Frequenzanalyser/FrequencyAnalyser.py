
import ctypes
import numpy as np
from picosdk.ps4000a import ps4000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok
import pandas as pd
import csv
import os
import tkinter as tk
from tkinter import messagebox
import threading
class PicoScopeController:
    def __init__(self):
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.maxADC = ctypes.c_int16(32767)
        self.open_unit()
        self.listofvalues = []
        self.calibration_values = []  # Liste für Kalibrierungswerte
        self.dut_values = [] # Liste für DUT-Messwerte
        self.script_dir = os.path.dirname(os.path.realpath(__file__))  # Directory of the script

    def open_unit(self):
        self.status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self.chandle), None)
        assert_pico_ok(self.status["openunit"])

    def setup_signal_generator(self, frequency):
        wavetype = ps.PS4000A_WAVE_TYPE['PS4000A_SINE']
        sweepType = ps.PS4000A_SWEEP_TYPE['PS4000A_UP']
        triggertype = ps.PS4000A_SIGGEN_TRIG_TYPE['PS4000A_SIGGEN_RISING']
        triggerSource = ps.PS4000A_SIGGEN_TRIG_SOURCE['PS4000A_SIGGEN_NONE']
        extInThreshold = ctypes.c_int16(0)

        self.status["SetSigGenBuiltIn"] = ps.ps4000aSetSigGenBuiltIn(
            self.chandle, 0, 100000, wavetype, frequency, frequency, 0, 1, sweepType, 0, 0, 0,
            triggertype, triggerSource, extInThreshold
        )
        assert_pico_ok(self.status["SetSigGenBuiltIn"])

    def setup_channel_and_trigger(self):
        chARange = 7
        self.status["setChA"] = ps.ps4000aSetChannel(self.chandle, 0, 1, 1, chARange, 0)
        assert_pico_ok(self.status["setChA"])
        self.status["trigger"] = ps.ps4000aSetSimpleTrigger(self.chandle, 1, 0, 1024, 2, 0, 100)
        assert_pico_ok(self.status["trigger"])

    def collect_data(self,timestep):
            preTriggerSamples = 16*16*16*4
            postTriggerSamples = 16*16*16*4
            maxSamples = preTriggerSamples + postTriggerSamples
            # print(timestep/10)
            timebase = int (timestep/100)
            # timebase = maxSamples
            timeIntervalns = ctypes.c_float()
            returnedMaxSamples = ctypes.c_int32()
            oversample = ctypes.c_int16(1)
            self.status["getTimebase2"] = ps.ps4000aGetTimebase2(self.chandle, timebase, maxSamples, ctypes.byref(timeIntervalns), ctypes.byref(returnedMaxSamples), 0)
            assert_pico_ok(self.status["getTimebase2"])
            # Berechnen der Abtastrate
            sampling_rate_hz = 1 / (timeIntervalns.value * 1e-9)
            self.status["runBlock"] = ps.ps4000aRunBlock(self.chandle, preTriggerSamples, postTriggerSamples, timebase, None, 0, None, None)
            assert_pico_ok(self.status["runBlock"])

            ready = ctypes.c_int16(0)
            check = ctypes.c_int16(0)
            while ready.value == check.value:
                self.status["isReady"] = ps.ps4000aIsReady(self.chandle, ctypes.byref(ready))

            bufferAMax = (ctypes.c_int16 * maxSamples)()
            bufferAMin = (ctypes.c_int16 * maxSamples)()
            bufferBMax = (ctypes.c_int16 * maxSamples)()
            bufferBMin = (ctypes.c_int16 * maxSamples)()

            self.status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(self.chandle, 0, ctypes.byref(bufferAMax), ctypes.byref(bufferAMin), maxSamples, 0 , 0)
            assert_pico_ok(self.status["setDataBuffersA"])

            self.status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(self.chandle, 1, ctypes.byref(bufferBMax), ctypes.byref(bufferBMin), maxSamples, 0 , 0)
            assert_pico_ok(self.status["setDataBuffersB"])

            overflow = ctypes.c_int16()
            cmaxSamples = ctypes.c_int32(maxSamples)

            self.status["getValues"] = ps.ps4000aGetValues(self.chandle, 0, ctypes.byref(cmaxSamples), 0, 0, 0, ctypes.byref(overflow))
            assert_pico_ok(self.status["getValues"])

            chARange = 7  # Assume chARange is 7 as in your script
            chBRange = 7  # Assume chBRange is 7, you might want to change this

            adc2mVChAMax = adc2mV(bufferAMax, chARange, self.maxADC)
            adc2mVChBMax = adc2mV(bufferBMax, chBRange, self.maxADC)

            time = np.linspace(0, (cmaxSamples.value - 1) * timeIntervalns.value, cmaxSamples.value)

            return time, adc2mVChAMax, adc2mVChBMax, sampling_rate_hz
    def run_experiment(self, frequencies):
        for frequency in frequencies:
            self.setup_signal_generator(frequency)
            time, chA_data, chB_data, = self.collect_data(self.get_timebase(desired_frequency=frequency))

    def close_unit(self):
        self.status["stop"] = ps.ps4000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])
        self.status["close"] = ps.ps4000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])
        print(self.status)



    def run_calibration(self, frequencies):
        self.listofvalues = []  # Reset the list of values for each calibration run
        for frequency in frequencies:
            self.setup_signal_generator(frequency)
            self.setup_channel_and_trigger()
            sampling_rate = 1 * frequency  # Assuming this is how you determine the sampling rate

            time, chA_data, chB_data, sampling_rate = self.collect_data(self.get_timebase(desired_frequency=sampling_rate))
            self.plot_frequency_response(chA_data, chB_data, sampling_rate)

            # Process and store the response values (this needs to be defined based on your requirements)
            # Example: self.listofvalues.append(some_processed_value)

        # After collecting data for all frequencies
        response_values = self.listofvalues
        # Plot the overall frequency response
        self.calibration_values = response_values
        # self.plot_frequency_response1(frequencies, response_values)
        # Cleanup
        print("Kalibrierung abgeschlossen")
    def calculate_and_plot_attenuation(self, frequencies):
        print("Berechnung der Dämpfung")
        if len(self.calibration_values) != len(self.dut_values):
            print("Error: Calibration and DUT values lengths do not match")
            return []

        attenuation_dB = [5 * np.log10( calib/ dut ) if dut != 0 else 0 for dut, calib in zip(self.calibration_values, self.dut_values)]
        print("   plot" + str(attenuation_dB))

        return attenuation_dB


        

    def run_measurement(self, frequencies):
        self.listofvalues = []  # Reset the list of values for each calibration run
        for frequency in frequencies:
            self.setup_signal_generator(frequency)
            self.setup_channel_and_trigger()
            sampling_rate = 1 * frequency  # Assuming this is how you determine the sampling rate

            time, chA_data, chB_data, sampling_rate = self.collect_data(self.get_timebase(desired_frequency=sampling_rate))
            self.plot_frequency_response(chA_data, chB_data, sampling_rate)

            # Process and store the response values (this needs to be defined based on your requirements)
            # Example: self.listofvalues.append(some_processed_value)

        # After collecting data for all frequencies
        response_values = self.listofvalues
        # Plot the overall frequency response
        self.dut_values = response_values
        # self.plot_frequency_response1(frequencies, response_values)
        # Cleanup
        print("Messung gestartet")

  
    def plot_frequency_response(self, chA_data, chB_data, sampling_rate):
    # Fensterfunktion anwenden
        window = np.hanning(len(chA_data))
        chA_data_windowed = chA_data * window
        chB_data_windowed = chB_data * window

        # FFT anwenden
        A_freq_windowed = np.fft.fft(chA_data_windowed)
        B_freq_windowed = np.fft.fft(chB_data_windowed)

        # Frequenzen berechnen
        N = len(chA_data_windowed)
        freq = np.fft.fftfreq(N, d=1/sampling_rate)

        # Nur die Hälfte der FFT und Frequenzen (die andere Hälfte ist symmetrisch)
        A_magnitude = np.abs(A_freq_windowed)[:N // 2]
        B_magnitude = np.abs(B_freq_windowed)[:N // 2]
        freq = freq[:N // 2]
        # Berechnung der Top-Frequenzen und Durchschnitt
        sorted_indices = np.argsort(A_magnitude)[::-1]  # Sortieren in absteigender Reihenfolge
        top_one_indices = sorted_indices[:1] 
        self.listofvalues.append(A_magnitude[top_one_indices])


    def run_experiment(self, frequencies):
        for frequency in frequencies:
            self.setup_signal_generator(frequency)
            time, chA_data, chB_data,sampling_rate = self.collect_data(self.get_timebase(desired_frequency=frequency))
            # self.save_to_csv(time, chA_data, chB_data, frequency)
            self.plot_frequency_response(chA_data, chB_data, sampling_rate)

    def get_timebase(self,desired_interval=None, desired_frequency=None):
        if desired_interval:
            # Calculate the timebase using the interval formula
            n = (desired_interval / 12.5e-9) - 1
        elif desired_frequency:
            # Calculate the timebase using the frequency formula
            n = (80e6 / desired_frequency) - 1
            print(desired_frequency)
            print(n)
        else:
            raise ValueError("Please provide either a desired interval or a desired frequency.")
        
        # Round to the nearest whole number and check the bounds
        n = round(n)
        if 0 <= n < 2**32:
            return n
        else:
            return None  # Desired value is out of range

 
    def plot_frquancy_response(self,magnitude,frequency):   
        # Creating the plot
        plt.figure(figsize=(10, 5))
        plt.plot(frequency, magnitude, marker='o') # 'o' creates a circular marker at each data point









