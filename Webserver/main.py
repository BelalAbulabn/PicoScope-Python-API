from flask import Flask, request, jsonify, render_template
import ctypes
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import assert_pico_ok
from flask_cors import CORS  # Import this
import sys

sys.path.append('..')
from GUI.ps4000aSigGen import PicoScope4000a
from picosdk.errors import PicoSDKCtypesError

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
        picoscope = PicoScope4000a()
        picoscope.open_device()
        device_connected = True
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})



if __name__ == '__main__':
    app.run(debug=True)
