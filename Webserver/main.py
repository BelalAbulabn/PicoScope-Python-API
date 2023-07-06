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

from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime
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

"""
Background Thread
"""
thread = None
thread_lock = Lock()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'donsky!'
socketio = SocketIO(app, cors_allowed_origins='*')

"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

"""
Generate random sequence of dummy sensor values and send it to our clients
"""
def background_thread():
    print("Generating random sensor values")
    while True:
        # Assuming you have 3 channels.
        dummy_sensor_value1 = round(random() * 100, 50)
        dummy_sensor_value2 = round(random() * 100, 50)
        dummy_sensor_value3 = round(random() * 100, 50)
        socketio.emit('updateSensorData', 
                      {'channel1': dummy_sensor_value1, 
                       'channel2': dummy_sensor_value2, 
                       'channel3': dummy_sensor_value3, 
                       "date": get_current_datetime()})
        socketio.sleep(1)


"""
Serve root index file
"""
@app.route('/')
def index():
    return render_template('index.html',device_connected=device_connected)

"""
Decorator for connect
"""
@socketio.on('connect')
def connect():
    global thread
    print('Client connected')

    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

      
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
    socketio.run(app)