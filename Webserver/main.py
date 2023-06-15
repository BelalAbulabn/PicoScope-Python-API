from flask import Flask, request, jsonify, render_template
import ctypes
from picosdk.ps4000a import ps4000a as ps
from picosdk.functions import assert_pico_ok
import sys
sys.path.append('..')
from GUI.ps4000aSigGen import PicoScope4000a

app = Flask(__name__)

picoscope = PicoScope4000a()
picoscope.open_device()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set_signal_generator', methods=['POST'])
def set_signal_generator():
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

if __name__ == '__main__':
    app.run(debug=True)
