import ctypes
import time
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import assert_pico_ok


class PicoScope4000a:
    def __init__(self):
        self.status = {}
        self.chandle = ctypes.c_int16()

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

    def set_signal_generator(self, wavetype, start_freq, stop_freq, increment=0, dwell_time=1, sweep_type='UP', pk_to_pk=2000000):
        wavetype_dict = ps.PS4000A_WAVE_TYPE
        sweep_type_dict = {'UP': ps.PS4000A_SWEEP_TYPE['PS4000A_UP'], 'UPDOWN': ps.PS4000A_SWEEP_TYPE['PS4000A_UPDOWN']}
        triggertype = ps.PS4000A_SIGGEN_TRIG_TYPE['PS4000A_SIGGEN_RISING']
        trigger_source = ps.PS4000A_SIGGEN_TRIG_SOURCE['PS4000A_SIGGEN_NONE']
        ext_in_threshold = ctypes.c_int16(0)

        self.status["SetSigGenBuiltIn"] = ps.ps4000aSetSigGenBuiltIn(
            self.chandle, 0, pk_to_pk, wavetype_dict[wavetype], start_freq, stop_freq, increment, dwell_time,
            sweep_type_dict[sweep_type], 0, 0, 0, triggertype, trigger_source, ext_in_threshold)
        assert_pico_ok(self.status["SetSigGenBuiltIn"])

    def close(self):
        self.status["close"] = ps.ps4000aCloseUnit(self.chandle)
        assert_pico_ok(self.status["close"])
        return self.status
