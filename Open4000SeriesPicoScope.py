
# import ctypes
import ctypes
from picosdk.ps4000a import ps4000a as ps
import numpy as np
# from picosdk.ps4000a import ps4000a as ps
import matplotlib.pyplot as plt
from picosdk.functions import adc2mV, assert_pico_ok

# Create chandle and status ready for use
chandle = ctypes.c_int16()
status = {}

# Open 4000 series PicoScope
# Returns handle to chandle for use in future API functions
status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(chandle), None)

try:
    assert_pico_ok(status["openunit"])
except:

    powerStatus = status["openunit"]

    if powerStatus == 286:
        status["changePowerSource"] = ps.ps4000aChangePowerSource(chandle, powerStatus)
    else:
        raise

    assert_pico_ok(status["changePowerSource"])



# from picosdk.functions import assert_pico_ok

class PicoScopeSetup:
    def __init__(self):
        self._chandle = ctypes.c_int16()
        self._status = {}
    
    def open_unit(self):
        # Open 4000 series PicoScope
        # Returns handle to _chandle for use in future API functions
        self._status["openunit"] = ps.ps4000aOpenUnit(ctypes.byref(self._chandle), None)
        self._check_status("openunit")
        
    def _check_status(self, status_key):
        try:
            assert_pico_ok(self._status[status_key])
        except:
            power_status = self._status[status_key]
            if power_status == 286:
                self._change_power_source(power_status)
            else:
                raise
                
    def _change_power_source(self, power_status):
        self._status["changePowerSource"] = ps.ps4000aChangePowerSource(self._chandle, power_status)
        self._check_status("changePowerSource")
        
    def close_unit(self):
        # Close unit
        self._status["close"] = ps.ps4000aCloseUnit(self._chandle)
        self._check_status("close")


class SetChannel:
    def __init__(self, pico_scope):
        self.pico_scope = pico_scope
        self.channels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        self.channel_ids = {name: idx for idx, name in enumerate(self.channels)}
        
    def set_channel(self, channel, enabled, coupling, rang, analog_offset):
        channel_id = self.channel_ids[channel]
        status_key = "setCh"+channel
        self.pico_scope.status[status_key] = ps.ps4000aSetChannel(self.pico_scope.chandle, channel_id, enabled, coupling, rang, analog_offset)
        self.pico_scope._check_status(status_key)
        
    def setup_channels(self):
        for channel in self.channels:
            self.set_channel(channel, 1, 1, 7, 0)