
function onButtonClick() {
	try {
		// Call the function that might throw an error
		setSignalGenerator();
	} catch (error) {
		// Display an alert box with the error message
		alert(error.message);
	}
}

function attemptConnection() {
	fetch('/connect_device', {
		method: 'POST'
	})
	.then(response => response.json())
	.then(data => {
		if (data.status === 'success') {
			location.reload();
		} else {
			document.getElementById('error').innerHTML = data.message;
		}
	})
}


    
// });


  var signalChart; // Declare signalChart here so it can be accessed in different functions

  // Function to set the signal generator
  function setSignalGenerator() {
      var waveTypeElement = document.getElementById("waveType");
      var startFreqElement = document.getElementById("startFreq");
      var stopFreqElement = document.getElementById("stopFreq");
      var incrementElement = document.getElementById("increment");
      var dwellTimeElement = document.getElementById("dwellTime");
      var sweepTypeElement = document.getElementById("sweepType");
      var peakToPeakVoltageElement = document.getElementById("peakToPeakVoltage");

      var data = {
          wavetype: waveTypeElement ? waveTypeElement.value : null,
          start_freq: startFreqElement ? startFreqElement.value : null,
          stop_freq: stopFreqElement ? stopFreqElement.value : null,
          increment: incrementElement ? incrementElement.value : null,
          dwell_time: dwellTimeElement ? dwellTimeElement.value : null,
          sweep_type: sweepTypeElement ? sweepTypeElement.value : null,
          pk_to_pk: peakToPeakVoltageElement ? peakToPeakVoltageElement.value : null
      };

      console.log("Data to be sent:", data);

      $.ajax({
          url: '/set_signal_generator',
          type: 'post',
          contentType: 'application/json',
          data: JSON.stringify(data),
          success: function (response) {
              console.log("Response from server:", response);
          }
      });
  }


  document.addEventListener("DOMContentLoaded", function(){
    // Event listener for the signal generator button
    var signalButton = document.getElementById("setSignalGeneratorButton");
    if (signalButton) {
      signalButton.addEventListener("click", setSignalGenerator);
    }
  });
  


$(document).ready(function () {
  const ctx = document.getElementById("myChart").getContext("2d");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        { label: "Channel 1", borderColor: 'rgba(255, 99, 132, 1)', data: [] },
        { label: "Channel 2", borderColor: 'rgba(75, 192, 192, 1)', data: [] },
        { label: "Channel 3", borderColor: 'rgba(153, 102, 255, 1)', data: [] }
      ],
    },
    options: {
      borderWidth: 3,
    },
  });

  function addData(label, data1, data2, data3) {
    myChart.data.labels.push(label);
    myChart.data.datasets[0].data.push(data1);  // data for channel 1
    myChart.data.datasets[1].data.push(data2);  // data for channel 2
    myChart.data.datasets[2].data.push(data3);  // data for channel 3
    myChart.update();
  }

  function removeFirstData() {
    myChart.data.labels.shift();
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }
  function getMaxDataCount() {
    var maxDataCountElement = document.getElementById('maxDataCount');
    return maxDataCountElement ? parseInt(maxDataCountElement.value) : 10;
    }
  var socket = io.connect();

  socket.on("updateSensorData", function (msg) {
    // console.log("Received sensorData :: " + msg.date + " :: " + msg.channel1 + ", " + msg.channel2 + ", " + msg.channel3);
    addData(msg.date, msg.channel1, msg.channel2, msg.channel3);

    if (myChart.data.labels.length > getMaxDataCount()) {
      removeFirstData();
    }

    addData(msg.date, msg.channel1, msg.channel2, msg.channel3);
  });
});
