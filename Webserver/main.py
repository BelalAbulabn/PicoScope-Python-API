from flask import Flask, request, jsonify, render_template
import ctypes
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import assert_pico_ok
from flask_cors import CORS  # Import this
import sys
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

sys.path.append('..')
from GUI.ps4000aSigGen import PicoScope4000a
from picosdk.errors import PicoSDKCtypesError
from GUI.PicoScopeStreamer import PicoScopeStreamer
from GUI.PicoScope import PicoScope


app = Flask(__name__)

CORS(app)  
try:
    picoscope = PicoScope()
    picoscope.open_device()
    device_connected = True
except PicoSDKCtypesError:
    device_connected = False
now = datetime.now()
configs = {
	'Y1': (0, 250),
	'Y2': (0, 500),
	'Y3': (0, 750),
}

df_num_rows = 10000
y_vals = {i: [random.randint(*configs[i]) for j in range(df_num_rows)] for i in configs}
df = pd.DataFrame({
	'X': ['{:%Y-%m-%d %H:%M:%S}'.format(now + timedelta(seconds=i)) for i in range(df_num_rows)],
	**y_vals
})

df.to_csv('test_data.csv', index=False)

@app.route('/')
def home():
    return render_template('index.html',device_connected=device_connected)
# Ensure picoscope is initialized and open before use


@app.route('/fetch-data')
def fetch_data():
    print("fetch_data route is being executed")
    try:
        print("Inside the try block")
        # Get parameters from the query string
        channel_range = request.args.get('channelRange', default=5, type=int)
        print("Channel range:", channel_range)
        buffer_size = request.args.get('bufferSize', default=500, type=int)
        print("Buffer size:", buffer_size)
        sample_interval = request.args.get('sampleInterval', default=250, type=int)
        print("Sample interval:", sample_interval)

        # Set channel A and B
        picoscope.set_channels(channel_range)
        print("Channels set")
 
        # Set buffer size for streaming
        picoscope.set_data_buffers(buffer_size)
        print("Buffers set")

        # Get sample units and max pre-trigger samples
        sample_units = ps.PS4000A_TIME_UNITS['PS4000A_US']
        max_pre_trigger_samples = 0

        # Run streaming with sample_interval and fetch the data
        adc2mVChAMax, adc2mVChBMax = picoscope.run_streaming(sample_interval=sample_interval, 
                                                             sample_units=sample_units, 
                                                             max_pre_trigger_samples=max_pre_trigger_samples)
        print("Streaming done")

        # Print fetched data to console
        print("Channel A data:", adc2mVChAMax)
        print("Channel B data:", adc2mVChBMax)

        # Create time array based on the sample interval and number of samples
        total_samples = len(adc2mVChAMax)  # assuming both channels return same number of samples
        time_array = np.linspace(0, (total_samples - 1) * sample_interval, total_samples)

        # Return the data as JSON
        return jsonify({'time': time_array.tolist(), 'channelA': adc2mVChAMax.tolist(), 'channelB': adc2mVChBMax.tolist()})

    except Exception as e:
        print("Error in fetch_data:", str(e))
        return str(e), 500


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

@app.route('/fetchig_data')
def fetchig_data():
	offset = request.args.get('offset', default = 1, type = int) # rows to skip
	limit = request.args.get('limit', default = 1, type = int) # number of rows
	df = pd.read_csv('test_data.csv', # here we just import the data we need from the csv, accordding with client parameters
		skiprows=range(1, offset+1), # ignore rows in the interval
      		nrows=limit, # limited to n rows, 1 after the first request
      		parse_dates=['X']) 

	cols = [col for col in df.columns if col.startswith('Y')]

	configs = {
		'Y1': {'color': '#483D8B', 'col_name': 'name_Y1'},
		'Y2': {'color': '#f87979', 'col_name': 'name_Y2'},
		'Y3': {'color': '#00BFFF', 'col_name': 'name_Y3'},
	}

	datasets = []
	for k, c in enumerate(cols):
		datasets.append({ # our datasets configs
			'label': configs[c]['col_name'],
			'borderColor': configs[c]['color'],
			'backgroundColor': configs[c]['color'],
			'borderWidth': 2,
			'pointBorderColor': '#000000',
			'lineTension': k*0.23, # line curve
			'pointRadius': 2,
			'pointBorderWidth': 1,
			'fill': False,
			'data': df[c].tolist()
		})

	chart = {
		'labels': df['X'].dt.strftime('%H:%M:%S').tolist(),
		'datasets': datasets
	}
        
    # return render_template('index.html',device_connected=device_connected)

	return jsonify({'chart_data': chart})
    




if __name__ == '__main__':
    app.run(debug=True)
