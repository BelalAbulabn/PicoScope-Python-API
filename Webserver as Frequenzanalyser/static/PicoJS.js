//Define the keyup event handler.
function form1EventHandler(event) {
  if (event.key === "Enter") {
    event.preventDefault();

    const amplitude = +document.getElementById("amplitude").value;
    const frequency = +document.getElementById("frequency").value;
    const waveform = document.getElementById("waveform").value;
    const xaxistype1 = document.getElementById("xaxistype1").value;

    if (!amplitude || !frequency || !waveform || !xaxistype1) {
      alert("Please select or enter parameters for 'Signal Generator'.");
    } else {
      alert("Signal Generator Submission Completed");
      const data = {
        amplitude: amplitude,
        frequency: frequency,
        waveform: waveform
      };
    // Send data.
    fetch('http://127.0.0.1:5001/submit-form1', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
      })
      .then(response =>response.json())
      .then(data => {
        // Update frequency and total_spectrum. 
        const frequency = data.freq;
        const total_spectrum = data.freq_response;
        if(xaxistype1 === 'log'){
          //Update the x-axis of the Plotly chart.
          Plotly.relayout('chartContainer', {
            'xaxis.type':'log',
            'xaxis.tickvals': [0, 1, 2, 3, 4, 5, 6],
            'xaxis.ticktext': ['1', '10', '100', '1000', '10000', '100000', '1000000'],
            }
          );
          // Update Plotly chart.
          Plotly.update('chartContainer', {
            x: [frequency.map(element => Math.log10(element))],
            y: [total_spectrum],
            customdata: [frequency], 
            hovertemplate: 'Frequency:  %{customdata} Hz<br>Magnitude: %{y} dB'
            }
          );
        } 
        else if(xaxistype1 === 'linear'){
          // Update Plotly chart.
          Plotly.relayout('chartContainer', {
            'xaxis.type':'linear',
            'xaxis.tickvals': [1, 10, 100, 1000, 10000, 100000, 1000000],
            'xaxis.ticktext': ['1', '10', '100', '1000', '10000', '100000', '1000000'],
            }
          );
          Plotly.update('chartContainer', {x: [frequency], y: [total_spectrum]});
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });

    }
  }
}

function form2EventHandler(event) {
  if (event.key === "Enter") {
    event.preventDefault();

    const triggermode = document.getElementById("triggermode").value;
    const samplerate = +document.getElementById("samplerate").value;
    const triggerlevel = document.getElementById("triggerlevel").value;

    if (!triggermode || !samplerate || !triggerlevel) {
      alert("Please select or enter parameters dor Signal Measurement.");
    } else {
      alert("Signal Measurement Submission Completed");


      // 使用 fetch 提交表单数据
    fetch('http://127.0.0.1:5001/submit-form2', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        triggermode: triggermode,
        samplerate: samplerate,
        triggerlevel: triggerlevel
      })
    })
    .then(response => {
      if (response.ok) {
        alert('Form2 submitted successfully!');
      } else {
        alert('Form2 submission failed.');
      }
    })
    .catch(error => {
      alert('An error occurred during form2 submission.');
      console.error(error);
    });
    }
  }
}

function form3EventHandler(event) {
  if (event.key === "Enter") {
    event.preventDefault();

    const startfrequency = +document.getElementById("startfrequency").value;
    const stopfrequency = +document.getElementById("stopfrequency").value;
    const resolutionbandwidth = +document.getElementById("resolutionbandwidth").value;
    const xaxistype3 = document.getElementById("xaxistype3").value;

    if (!startfrequency || !stopfrequency || !resolutionbandwidth|| !xaxistype3) {
      alert("Please select parameters for 'Spectral Analysis'.");
    } else {
      alert("Spectral Analysis Submission Completed");

      const data = {
        startfrequency: startfrequency,
        stopfrequency: stopfrequency,
        resolutionbandwidth: resolutionbandwidth
      };

      fetch('http://127.0.0.1:5001/submit-form3', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      })
      .then(response =>response.json())
      .then(data => {
        const frequency = data.freq;
        const total_spectrum = data.freq_response;

        if(xaxistype3 === 'log'){
            Plotly.relayout('chartContainer', {
              'xaxis.type':'log',
              'xaxis.tickvals': [0, 1, 2, 3, 4, 5, 6],
              'xaxis.ticktext': ['1', '10', '10^2', '10^3', '10^4', '10^5', '10^6'],
              }
            );
            const logfreq = frequency.map(element => Math.log10(element));
    
            Plotly.update('chartContainer', {
              x: [logfreq],
              y: [total_spectrum],
              customdata: [frequency], // 使用 customdata 来传递自定义数据
              hovertemplate: 'Frequency:  %{customdata} Hz<br>Magnitude: %{y} dB'
              }
            );
        } 
        else if(xaxistype3 === 'linear'){
            Plotly.relayout('chartContainer', {
              'xaxis.type':'linear',
              'xaxis.tickvals': [1, 10, 100, 1000, 10000, 100000, 1000000],
              'xaxis.ticktext': ['1', '10', '100', '1000', '10000', '100000', '1000000'],
              }
            );
            Plotly.update('chartContainer', {x: [frequency], y: [total_spectrum], hovertemplate: 'Frequency: %{x} Hz<br>Magnitude: %{y} dB'});
        }
        })
      .catch(error => {
        console.error('Error:', error);
        });
    }
  }
}


document.addEventListener("keyup", function (event) {
  if (event.key === "Enter") {
    const signalGeneratorCheckbox = document.getElementById("signalGeneratorCheckbox");
    const signalMeasurementCheckbox = document.getElementById("signalMeasurementCheckbox");
    const spectralAnalysisCheckbox = document.getElementById("spectralAnalysisCheckbox");

    const isSignalGeneratorChecked = signalGeneratorCheckbox.checked;
    const isSignalMeasurementChecked = signalMeasurementCheckbox.checked;
    const isSpectralAnalysisChecked = spectralAnalysisCheckbox.checked;

    const checkedCount = [isSignalGeneratorChecked, isSignalMeasurementChecked, isSpectralAnalysisChecked].filter(Boolean).length;

    if (checkedCount === 1) {
      if (isSignalGeneratorChecked) {
        const form1 = document.getElementById("theForm1");
        form1.removeEventListener("keyup", form2EventHandler);
        form1.removeEventListener("keyup", form3EventHandler);
        form1.addEventListener("keyup", form1EventHandler, { once: true });

        const keyupEvent = new KeyboardEvent("keyup", {
          key: "Enter",
        });
        form1.dispatchEvent(keyupEvent);
      } else if (isSignalMeasurementChecked) {
        const form2 = document.getElementById("theForm2");
        form2.removeEventListener("keyup", form1EventHandler);
        form2.removeEventListener("keyup", form3EventHandler);
        form2.addEventListener("keyup", form2EventHandler, { once: true });
        const keyupEvent = new KeyboardEvent("keyup", {
          key: "Enter",
        });
        form2.dispatchEvent(keyupEvent);
      } else if (isSpectralAnalysisChecked) {
        const form3 = document.getElementById("theForm3");
        form3.removeEventListener("keyup", form1EventHandler);
        form3.removeEventListener("keyup", form2EventHandler);
        form3.addEventListener("keyup", form3EventHandler, { once: true });
        const keyupEvent = new KeyboardEvent("keyup", {
          key: "Enter",
        });
        form3.dispatchEvent(keyupEvent);
      }
    } if(checkedCount === 0) {
      alert("Please check one box");
    } else{"Please only check one box"}
  }
});

    
