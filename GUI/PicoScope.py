import ctypes
import numpy as np
import time
import matplotlib.pyplot as plt
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import adc2mV, assert_pico_ok
from picosdk.errors import PicoSDKCtypesError


class PicoScope:
    def __init__(self):
        self.status = {}
        self.chandle = ctypes.c_int16()
        self.channel_range = 7
        self.size_of_one_buffer = 500
        self.num_buffers_to_capture = 10
        self.total_samples = self.size_of_one_buffer * self.num_buffers_to_capture
        self.buffer_a_max = np.zeros(shape=self.size_of_one_buffer, dtype=np.int16)
        self.buffer_b_max = np.zeros(shape=self.size_of_one_buffer, dtype=np.int16)

        self.next_sample = 0
        self.buffer_complete_a = np.zeros(shape=self.total_samples, dtype=np.int16)
        self.buffer_complete_b = np.zeros(shape=self.total_samples, dtype=np.int16)
        self.auto_stop_outer = False

    def open_device(self):
        self.status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self.chandle), None)
        try:
            assert_pico_ok(self.status["openunit"])
        except:
            powerstate = self.status["openunit"]
            if powerstate == 282:
                self.status["ChangePowerSource"] = ps.ps4000aChangePowerSource(self.chandle, 282)
            elif powerstate == 286:
                self.status["ChangePowerSource"] = ps.ps4000aChangePowerSource(self.chandle, 286)
            else:
                raise
            assert_pico_ok(self.status["ChangePowerSource"])

    def set_channels(self, channel_range):
        enabled = 1
        analogue_offset = 0.0

        # Set up channel A
        self.status["setChA"] = ps.ps4000aSetChannel(self.chandle,
                                                ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'],
                                                enabled,
                                                ps.PS4000A_COUPLING['PS4000A_DC'],
                                                self.channel_range,
                                                analogue_offset)
        assert_pico_ok(self.status["setChA"])

        # Set up channel B
        self.status["setChB"] = ps.ps4000aSetChannel(self.chandle,
                                                ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'],
                                                enabled,
                                                ps.PS4000A_COUPLING['PS4000A_DC'],
                                                self.channel_range,
                                                analogue_offset)
        assert_pico_ok(self.status["setChB"])

    def streaming_callback(self, handle, no_of_samples, start_index, overflow, triggerAT, triggered, autoStop, param):
        dest_end = self.next_sample + no_of_samples
        source_end = start_index + no_of_samples
        self.buffer_complete_a[self.next_sample:dest_end] = self.buffer_a_max[start_index:source_end]
        self.buffer_complete_b[self.next_sample:dest_end] = self.buffer_b_max[start_index:source_end]
        self.next_sample += no_of_samples
        if autoStop:
            self.auto_stop_outer = True
    # Convert the python function into a C function pointer.

    def set_signal_generator(self, wavetype, start_freq, stop_freq, increment=0.0, dwell_time=1.0, sweep_type='UP', pk_to_pk=2000000):
        wavetype_dict = ps.PS4000A_WAVE_TYPE
        sweep_type_dict = {'UP': ps.PS4000A_SWEEP_TYPE['PS4000A_UP'], 'UPDOWN': ps.PS4000A_SWEEP_TYPE['PS4000A_UPDOWN']}
        triggertype = ps.PS4000A_SIGGEN_TRIG_TYPE['PS4000A_SIGGEN_RISING']
        trigger_source = ps.PS4000A_SIGGEN_TRIG_SOURCE['PS4000A_SIGGEN_NONE']
        ext_in_threshold = ctypes.c_int16(0)
        pk_to_pk = int(pk_to_pk)
        start_freq = float(start_freq)
        stop_freq = float(stop_freq)
        increment = float(increment)
        dwell_time = float(dwell_time)
        print("Setting Signal Generator...")
        self.status["SetSigGenBuiltIn"] = ps.ps4000aSetSigGenBuiltIn(
            self.chandle, 0, pk_to_pk, wavetype_dict[wavetype], start_freq, stop_freq, increment, dwell_time,
            sweep_type_dict[sweep_type], 0, 0, 0, triggertype, trigger_source, ext_in_threshold)
        assert_pico_ok(self.status["SetSigGenBuiltIn"])

    def set_data_buffers(self, size_of_one_buffer):
        memory_segment = 0
        # Set data buffer for channel A
        self.status["setDataBuffersA"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                     ps.PS4000A_CHANNEL['PS4000A_CHANNEL_A'],
                                                     self.buffer_a_max.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     self.size_of_one_buffer,
                                                     memory_segment,
                                                     ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        assert_pico_ok(self.status["setDataBuffersA"])
        
        # Set data buffer for channel B
        self.status["setDataBuffersB"] = ps.ps4000aSetDataBuffers(self.chandle,
                                                     ps.PS4000A_CHANNEL['PS4000A_CHANNEL_B'],
                                                     self.buffer_b_max.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                                     None,
                                                     self.size_of_one_buffer,
                                                     memory_segment,
                                                     ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
        assert_pico_ok(self.status["setDataBuffersB"])

    def run_streaming(self, sample_interval=1, sample_units=ps.PS4000A_TIME_UNITS['PS4000A_US'], max_pre_trigger_samples=0):
        # Set the sample interval, sample units, and the maximum pre- and post-trigger samples
        self.status["runStreaming"] = ps.ps4000aRunStreaming(self.chandle,
                                                            ctypes.byref(ctypes.c_int32(sample_interval)),
                                                            sample_units,
                                                            max_pre_trigger_samples,
                                                            self.total_samples,
                                                            1,  # autostop
                                                            self.size_of_one_buffer)

        assert_pico_ok(self.status["runStreaming"])

        cFuncPtr = ps.StreamingReadyType(self.streaming_callback)


        # Retrieve streaming data
        was_called_back = False
        total_samples = 0
        while total_samples < self.total_samples:
            ready = False
            while not ready:
                self.status["isReady"] = ps.ps4000aIsReady(self.chandle, ctypes.byref(ctypes.c_int16(ready)))
                assert_pico_ok(self.status["isReady"])
                time.sleep(0.01)  # sleep to lower CPU usage
            self.status["getStreamingLatestValues"] = ps.ps4000aGetStreamingLatestValues(self.chandle, cFuncPtr, None)
            assert_pico_ok(self.status["getStreamingLatestValues"])
            total_samples += self.size_of_one_buffer
            was_called_back = True

        # Confirm that the callback has been called
        assert was_called_back is True

        # Retrieve the maximum ADC count value
        max_adc_value = ctypes.c_int16(32767)

        # Convert ADC counts data to millivolts
        buffer_a_mv = adc2mV(self.buffer_a_max, self.channel_range, max_adc_value)
        buffer_b_mv = adc2mV(self.buffer_b_max, self.channel_range, max_adc_value)

        # Return the retrieved data
        return buffer_a_mv, buffer_b_mv


    def close(self):
        self.status["close"] = ps.ps4000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])
        return self.status

    # def __init__(self, channel_range, size_of_one_buffer, num_buffers_to_capture, sample_interval):
    #     self.chandle = ctypes.c_int16()
    #     self.status = {}

    #     # Set up channel A and B
    #     self.set_channel('A', channel_range)
    #     self.set_channel('B', channel_range)

    #     # Size of capture
    #     self.total_samples = size_of_one_buffer * num_buffers_to_capture

    #     # Setup buffers for data collection
    #     self.buffer_a_max = np.zeros(shape=size_of_one_buffer, dtype=np.int16)
    #     self.buffer_b_max = np.zeros(shape=size_of_one_buffer, dtype=np.int16)
    #     self.set_data_buffers('A', self.buffer_a_max)
    #     self.set_data_buffers('B', self.buffer_b_max)

    #     # Begin streaming mode
    #     self.actual_sample_interval_ns = self.start_streaming(sample_interval, self.total_samples)

    #     # Buffer to keep the complete capture in
    #     self.buffer_complete_a = np.zeros(shape=self.total_samples, dtype=np.int16)
    #     self.buffer_complete_b = np.zeros(shape=self.total_samples, dtype=np.int16)

    # # Method from PicoScope4000a
    # def open_device(self):
    #     self.status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self.chandle), None)
    #     try:
    #         assert_pico_ok(self.status["openunit"])
    #     except:
    #         powerstate = self.status["openunit"]
    #         if powerstate == 282:
    #             self.status["ChangePowerSource"] = ps.ps4000aChangePowerSource(self.chandle, 282)
    #         elif powerstate == 286:
                
    #             self.status["ChangePowerSource"] = ps.ps4000aChangePowerSource(self.chandle, 286)
    #         else:
    #             raise
    #         assert_pico_ok(self.status["ChangePowerSource"])
    
    # def set_signal_generator(self, wavetype, start_freq, stop_freq, increment=0.0, dwell_time=1.0, sweep_type='UP', pk_to_pk=2000000):
    #     wavetype_dict = ps.PS4000A_WAVE_TYPE
    #     sweep_type_dict = {'UP': ps.PS4000A_SWEEP_TYPE['PS4000A_UP'], 'UPDOWN': ps.PS4000A_SWEEP_TYPE['PS4000A_UPDOWN']}
    #     triggertype = ps.PS4000A_SIGGEN_TRIG_TYPE['PS4000A_SIGGEN_RISING']
    #     trigger_source = ps.PS4000A_SIGGEN_TRIG_SOURCE['PS4000A_SIGGEN_NONE']
    #     ext_in_threshold = ctypes.c_int16(0)
    #     pk_to_pk = int(pk_to_pk)
    #     start_freq = float(start_freq)
    #     stop_freq = float(stop_freq)
    #     increment = float(increment)
    #     dwell_time = float(dwell_time)
    #     print("Setting Signal Generator...")
    #     self.status["SetSigGenBuiltIn"] = ps.ps4000aSetSigGenBuiltIn(
    #         self.chandle, 0, pk_to_pk, wavetype_dict[wavetype], start_freq, stop_freq, increment, dwell_time,
    #         sweep_type_dict[sweep_type], 0, 0, 0, triggertype, trigger_source, ext_in_threshold)
    #     assert_pico_ok(self.status["SetSigGenBuiltIn"])

    # # Methods from PicoScopeStreamer
    # def set_channel(self, channel, channel_range):
    #     enabled = 1
    #     analogue_offset = 0.0
    #     self.status[f"setCh{channel}"] = ps.ps4000aSetChannel(self.chandle,
    #                                                           ps.PS4000A_CHANNEL[f'PS4000A_CHANNEL_{channel}'],
    #                                                           enabled,
    #                                                           ps.PS4000A_COUPLING['PS4000A_DC'],
    #                                                           channel_range,
    #                                                           analogue_offset)
    #     assert_pico_ok(self.status[f"setCh{channel}"])

    # def set_data_buffers(self, channel, buffer):
    #     memory_segment = 0
    #     self.status[f"setDataBuffers{channel}"] = ps.ps4000aSetDataBuffers(self.chandle,
    #                                                                        ps.PS000A_CHANNEL[f'PS4000A_CHANNEL_{channel}'],
    #                                                                        buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
    #                                                                        None,
    #                                                                        len(buffer),
    #                                                                        memory_segment,
    #                                                                        ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'])
    #     assert_pico_ok(self.status[f"setDataBuffers{channel}"])

    # def start_streaming(self, sample_interval, total_samples):
    #     sample_interval = ctypes.c_int32(sample_interval)
    #     max_pre_trigger_samples = 0
    #     auto_stop_on = 1
    #     downsample_ratio = 1
    #     self.status["runStreaming"] = ps.ps4000aRunStreaming(self.chandle,
    #                                                          ctypes.byref(sample_interval),
    #                                                          ps.PS4000A_TIME_UNITS['PS4000A_US'],
    #                                                          max_pre_trigger_samples,
    #                                                          total_samples,
    #                                                          auto_stop_on,
    #                                                          downsample_ratio,
    #                                                          ps.PS4000A_RATIO_MODE['PS4000A_RATIO_MODE_NONE'],
    #                                                          int(total_samples ** 0.5))
    #     assert_pico_ok(self.status["runStreaming"])
    #     return sample_interval.value * 1000


    # def streaming_callback(self, handle, no_of_samples, start_index, overflow, trigger_at, triggered, auto_stop, param):
    #     dest_end = self.next_sample + no_of_samples
    #     source_end = start_index + no_of_samples
    #     self.buffer_complete_a[self.next_sample:dest_end] = self.buffer_a_max[start_index:source_end]
    #     self.buffer_complete_b[self.next_sample:dest_end] = self.buffer_b_max[start_index:source_end]
    #     self.next_sample += no_of_samples
    #     if auto_stop:
    #         self.auto_stop_outer = True

    #     # Print every sample
    #     for i in range(start_index, source_end):
    #         print(f'Sample A: {self.buffer_a_max[i]}, Sample B: {self.buffer_b_max[i]}')
        




    # def fetch_data(self):
    #     # Initialize values
    #     print("Fetching data...")
    #     self.next_sample = 0
    #     self.auto_stop_outer = False
    #     c_func_ptr = ps.StreamingReadyType(self.streaming_callback)
    #     print("StreamingReadyType: ", c_func_ptr)

    #     # Fetch data from the driver
    #     while self.next_sample < self.total_samples and not self.auto_stop_outer:
    #         self.status["getStreamingLastestValues"] = ps.ps4000aGetStreamingLatestValues(self.chandle, c_func_ptr, None)
    #         time.sleep(0.01)
    #     print("Done fetching data.")

    #     # Convert ADC counts data to mV
    #     max_adc = ctypes.c_int16()
    #     self.status["maximumValue"] = ps.ps4000aMaximumValue(self.chandle, ctypes.byref(max_adc))
    #     assert_pico_ok(self.status["maximumValue"])

    #     adc2mVChAMax = adc2mV(self.buffer_complete_a, channel_range, max_adc)
    #     adc2mVChBMax = adc2mV(self.buffer_complete_b, channel_range, max_adc)

    #     # Create time data
    #     time_array = np.linspace(0, (self.total_samples - 1) * self.actual_sample_interval_ns, self.total_samples)


    #     print(self.status) 
    #     return time_array, adc2mVChAMax, adc2mVChBMax
