# from Open4000SeriesPicoScope import PicoScopeSetup, SetChannel
from ps4000aSigGen import PicoScope4000a
# import time
# # Initialize the PicoScope
# pico_scope = PicoScopeSetup()
# pico_scope.open_unit()

# # Initialize the SetChannel
# set_channel = SetChannel(pico_scope)

# # Call setup_channels function
# set_channel.setup_channels()

# # Close the PicoScope when done
# pico_scope.close_unit()
import time
# from picoscope_4000a import PicoScope4000a

# Create an instance of the PicoScope4000a class
picoscope = PicoScope4000a()

# Open the device
picoscope.open_device()

# Use the set_signal_generator method to set various signal outputs
picoscope.set_signal_generator('PS4000A_SINE', 10000, 10000)
time.sleep(10)
picoscope.set_signal_generator('PS4000A_SQUARE', 10000, 10000)
time.sleep(10)
picoscope.set_signal_generator('PS4000A_SQUARE', 10000, 100000, 5000, 1, 'UPDOWN')
time.sleep(36)

# Close the PicoScope
status = picoscope.close()

# Print the status
print(status)
