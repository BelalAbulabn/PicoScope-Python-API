from flask import Flask, request, jsonify, render_template
import ctypes
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import assert_pico_ok
from flask_cors import CORS  # Import this
import sys

sys.path.append('..')
from GUI.ps4000aSigGen import PicoScope4000a
from picosdk.errors import PicoSDKCtypesError
from GUI.PicoScopeStreamer import PicoScopeStreamer
from GUI.PicoScope import PicoScope

app = Flask(__name__)
CORS(app)  
try:
    picoscope = PicoScope4000a()
    picoscope.open_device()
    device_connected = True
except PicoSDKCtypesError:
    device_connected = False


@app.route('/')
def home():
    return render_template('index.html',device_connected=device_connected)

@app.route('/fetch-data')
def fetch_data():
    print("fetch_data route is being executed") # Add this lin

    try:
        print("Inside the try block") # Add this line
        # Get parameters from the query string
        channel_range = request.args.get('channelRange', default=5, type=int)
        buffer_size = request.args.get('bufferSize', default=500, type=int)
        num_buffers_to_capture = 10  # This can also be parameterized
        sample_interval = request.args.get('sampleInterval', default=250, type=int)

        # Pass the parameters to the PicoScopeStreamer
        streamer = PicoScopeStreamer(
            channel_range=channel_range,
            size_of_one_buffer=buffer_size,
            num_buffers_to_capture=num_buffers_to_capture,
            sample_interval=sample_interval
        )
        
        # Fetch the data
        time_array, adc2mVChAMax, adc2mVChBMax = streamer.fetch_data()
                # Print fetched data to console
        print("Time array:", time_array)
        print("Channel A data:", adc2mVChAMax)
        print("Channel B data:", adc2mVChBMax)

        # Return the data as JSON
        return jsonify({'time': time_array.tolist(), 'channelA': adc2mVChAMax.tolist(), 'channelB': adc2mVChBMax.tolist()})
    
    except Exception as e:
        print("An error occurred:", e) # Add this line
        return jsonify({'error': str(e)})
    
@app.route('/set_signal_generator', methods=['POST'])
def set_signal_generator():
    if not device_connected:
        return jsonify({'status': 'error', 'message': 'Device not connected'})

    data = request.json
    wavetype = data['wavetype']
    start_freq = data['start_freq']
    stop_freq = data['stop_freq']
    increment = data['increment']
    dwell_time = data['dwell_time']
    sweep_type = data['sweep_type']
    pk_to_pk = data['pk_to_pk']

    picoscope.set_signal_generator(wavetype, start_freq, stop_freq, increment, dwell_time, sweep_type, pk_to_pk)

    return jsonify({'status': 'success'})


@app.route('/connect_device', methods=['POST'])
def connect_device():
    global device_connected
    try:
        picoscope = PicoScope()

        picoscope.open_device()
        device_connected = True
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



if __name__ == '__main__':
    app.run(debug=True)
