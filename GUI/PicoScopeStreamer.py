import ctypes
import numpy as np
import time
import matplotlib.pyplot as plt
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.errors import PicoSDKCtypesError



class PicoScopeStreamer:

    def __init__(self, channel_range=5, size_of_one_buffer=500, num_buffers_to_capture=10, sample_interval=250):
        self.chandle = ctypes.c_int16()
        self.status = {}



        # Set up channel A and B
        self.set_channel('A', channel_range)
        self.set_channel('B', channel_range)

        # Size of capture
        self.total_samples = size_of_one_buffer * num_buffers_to_capture

        # Setup buffers for data collection
        self.buffer_a_max = np.zeros(shape=size_of_one_buffer, dtype=np.int16)
        self.buffer_b_max = np.zeros(shape=size_of_one_buffer, dtype=np.int16)
        self.set_data_buffers('A', self.buffer_a_max)
        self.set_data_buffers('B', self.buffer_b_max)

        # Begin streaming mode
        self.actual_sample_interval_ns = self.start_streaming(sample_interval, self.total_samples)

        # Buffer to keep the complete capture in
        self.buffer_complete_a = np.zeros(shape=self.total_samples, dtype=np.int16)
        self.buffer_complete_b = np.zeros(shape=self.total_samples, dtype=np.int16)

    def set_channel(self, channel, channel_range):
        enabled = 1
        analogue_offset = 0.0
        self.status[f"setCh{channel}"] = ps.ps4000aSetChannel(self.chandle,
                                                              ps.PS4000A_CHANNEL[f'PS4000A_CHANNEL_{channel}'],
                                                              enabled,
                                                              ps.PS4000A_COUPLING['PS4000A_DC'],
                                                              channel_range,
                                                              analogue_offset)
        assert_pico_ok(self.status[f"setCh{channel}"])

    def set_data_buffers(self, channel, buffer):
        memory_segment = 0
        self.status[f"setDataBuffers{channel}"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                                           ps.PS4000A_CHANNEL[f'PS4000A_CHANNEL_{channel}'],
                                                                           buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                                           None,
                                                                           len(buffer),
                                                                           memory_segment,
                                                                           ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        assert_pico_ok(self.status[f"setDataBuffers{channel}"])

    def start_streaming(self, sample_interval, total_samples):
        sample_interval = ctypes.c_int32(sample_interval)
        max_pre_trigger_samples = 0
        auto_stop_on = 1
        downsample_ratio = 1
        self.status["runStreaming"] = ps.ps4000aRunStreaming(self.chandle,
                                                             ctypes.byref(sample_interval),
                                                             ps.PS4000A_TIME_UNITS['PS4000A_US'],
                                                             max_pre_trigger_samples,
                                                             total_samples,
                                                             auto_stop_on,
                                                             downsample_ratio,
                                                             ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'],
                                                             int(total_samples ** 0.5))
        assert_pico_ok(self.status["runStreaming"])
        return sample_interval.value * 1000

    def streaming_callback(self, handle, no_of_samples, start_index, overflow, trigger_at, triggered, auto_stop, param):
        dest_end = self.next_sample + no_of_samples
        source_end = start_index + no_of_samples
        self.buffer_complete_a[self.next_sample:dest_end] = self.buffer_a_max[start_index:source_end]
        self.buffer_complete_b[self.next_sample:dest_end] = self.buffer_b_max[start_index:source_end]
        self.next_sample += no_of_samples
        if auto_stop:
            self.auto_stop_outer = True

    def fetch_data(self):
        # Initialize values
        self.next_sample = 0
        self.auto_stop_outer = False
        c_func_ptr = ps.StreamingReadyType(self.streaming_callback)

        # Fetch data from the driver
        while self.next_sample < self.total_samples and not self.auto_stop_outer:
            self.status["getStreamingLastestValues"] = ps.ps4000aGetStreamingLatestValues(self.chandle, c_func_ptr, None)
            time.sleep(0.01)

        # Convert ADC counts data to mV
        max_adc = ctypes.c_int16()
        self.status["maximumValue"] = ps.ps4000aMaximumValue(self.chandle, ctypes.byref(max_adc))
        assert_pico_ok(self.status["maximumValue"])

        adc2mVChAMax = adc2mV(self.buffer_complete_a, channel_range, max_adc)
        adc2mVChBMax = adc2mV(self.buffer_complete_b, channel_range, max_adc)

        # Create time data
        time_array = np.linspace(0, (self.total_samples - 1) * self.actual_sample_interval_ns, self.total_samples)


        # Stop the scope
        self.status["stop"] = ps.ps4000aStop(self.chandle)
        assert_pico_ok(self.status["stop"])

        # Close the device
        self.status["close"] = ps.ps4000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])

        print(self.status) 
        return time_array, adc2mVChAMax, adc2mVChBMax

# Example usage
if __name__ == "__main__":
    try:
        streamer = PicoScopeStreamer(channel_range=5, size_of_one_buffer=500, num_buffers_to_capture=10, sample_interval=250)
        streamer.fetch_data()
    except PicoSDKCtypesError as e:
        print(f"PicoSDK Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
