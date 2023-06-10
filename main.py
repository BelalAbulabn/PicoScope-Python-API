from picoscope_module import PicoScopeSetup, SetChannel

# Initialize the PicoScope
pico_scope = PicoScopeSetup()
pico_scope.open_unit()

# Initialize the SetChannel
set_channel = SetChannel(pico_scope)

# Call setup_channels function
set_channel.setup_channels()

# Close the PicoScope when done
pico_scope.close_unit()
#gg 
#ghgg
