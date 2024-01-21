from flask import Flask, render_template, request,jsonify
from flask import Flask, render_template, jsonify
import threading
import numpy as np
from flask import jsonify, current_app
import traceback
from FrequencyAnalyser import PicoScopeController
import logging
app = Flask(__name__)

pico_controller = PicoScopeController()
frequencies = np.logspace(2, np.log10(7*10**5), 50)  # Define your frequency range




# open page
@app.route('/')
def display_page():
    return render_template('index.html', frequency = [0], total_spectrum = [0])


# signal generator
@app.route('/submit-form1', methods=['POST'])
def handle_form1_submission():
    json_data = request.get_json()
    amplitude = json_data.get('amplitude')
    frequency = json_data.get('frequency')
    waveform = json_data.get('waveform')
    
    json_return_data = {
        "message": "POST1 data received",
        "status": "success",
        "waveform": waveform,
        "amplitude": amplitude,
        "frequency": frequency,
        # "freq": [100, 1100, 5100, 6100, 9100, 10100, 12100],
        "freq":  [ 10, 100, 500, 1000, 10000],
        "freq_response": [10, 20, 30, 20, 10],
    }    
    return jsonify(json_return_data)


@app.route('/submit-form3', methods=['POST'])
def frequency_response_analyzer():
    json_data = request.get_json()
    startFrequency = json_data.get('startfrequency')
    stopFrequency = json_data.get('stopfrequency')
    RBW = json_data.get('resolutionbandwidth')

    freqstep = RBW
    freq = [hz for hz in range(int(startFrequency), int(stopFrequency) + int(freqstep), int(freqstep))]
    
    json_return_data = {
        "message": "POST3 data received",
        "startHz": startFrequency,
        "stopHz": stopFrequency,
        "stepHz": freqstep,
        "resolution": RBW,
        "freq": freq, # x-axis value
        "freq_response": [20] * len(freq), # y-axis value
    }    
    return jsonify(json_return_data)



@app.route('/calibrate', methods=['POST'])
def calibrate():
    try:
        pico_controller.run_calibration(frequencies)
        return jsonify({'status': 'success', 'message': 'Calibration ended'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/measure', methods=['POST'])
def measure():
    try:
        pico_controller.run_measurement(frequencies)
        return jsonify({'status': 'success', 'message': 'Measurement ended'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# @app.route('/calculate_attenuation', methods=['POST'])
# def calculate_attenuation():
#     try:
#         attenuation = pico_controller.calculate_and_plot_attenuation(frequencies)
#         return jsonify({'status': 'success', 'message': 'Attenuation calculated'})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/calculate_attenuation', methods=['POST'])
def calculate_attenuation():
    try:
        attenuation_dB = pico_controller.calculate_and_plot_attenuation(frequencies)

        attenuation_dB_list = [float(db[0]) for db in attenuation_dB]
        data_to_send = [{"frequency": freq, "dB": db} for freq, db in zip(frequencies, attenuation_dB_list)]
        app.logger.info(f"Sending data: {data_to_send}")
        return jsonify({'status': 'success', 'attenuation': data_to_send})
    except Exception as e:
        app.logger.error(f"Error in calculate_attenuation: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)
    # pico_controller = PicoScopeController()
    



