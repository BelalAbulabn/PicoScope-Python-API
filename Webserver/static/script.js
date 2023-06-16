
function setSignalGenerator() {
	var data = {
		wavetype: document.getElementById("waveType").value,
		start_freq: document.getElementById("startFreq").value,
		stop_freq: document.getElementById("stopFreq").value,
		increment: document.getElementById("increment").value,
		dwell_time: document.getElementById("dwellTime").value,
		sweep_type: document.getElementById("sweepType").value,
		pk_to_pk: document.getElementById("peakToPeakVoltage").value
	};

	$.ajax({
		url: '/set_signal_generator',
		type: 'post',
		contentType: 'application/json',
		data: JSON.stringify(data),
		success: function(response) {
			console.log(response);
		}
	});
}

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

document.addEventListener("DOMContentLoaded", function() {
    var button = document.querySelector("button");
    if (button) {
        button.addEventListener("click", attemptConnection);
    }
});


// document.addEventListener("DOMContentLoaded", function() {
//     var ctx = document.getElementById('signalChart').getContext('2d');
    
//     // Generate sine wave data
//     var labels = [];
//     var data = [];
//     for (var i = 0; i < 360; i += 10) { // 360 degrees, incrementing by 10 degrees
//         var radians = i * (Math.PI / 180); // Convert degrees to radians
//         var sineValue = Math.sin(radians);
//         labels.push(i);
//         data.push(sineValue);
//     }

//     var signalChart = new Chart(ctx, {
//         type: 'line', // Line chart
//         data: {
//             labels: labels, // X-axis labels
//             datasets: [{
//                 label: 'Sine Wave',
//                 data: data, // Y-axis data points
//                 borderColor: 'rgba(75, 192, 192, 1)',
//                 borderWidth: 1
//             }]
//         },
//         options: {
//             scales: {
//                 x: {
//                     title: {
//                         display: true,
//                         text: 'Time' // Label for X-axis
//                     }
//                 },
//                 y: {
//                     title: {
//                         display: true,
//                         text: 'Spannung' // Label for Y-axis
//                     },
//                     beginAtZero: false
//                 }
//             }
//         }
//     });
// });



document.addEventListener("DOMContentLoaded", function() {
    var ctx = document.getElementById('signalChart').getContext('2d');
	// Generate sine wave data
	var labels = [];
	var data = [];
	for (var i = 0; i < 360; i += 10) { // 360 degrees, incrementing by 10 degrees
		var radians = i * (Math.PI / 180); // Convert degrees to radians
		var sineValue = Math.sin(radians);
		labels.push(i);
		data.push(sineValue);
	}
    
    var timeScale = 's'; // You can change this to 'us' or 'ns' or have this set through UI
    var voltageScale = 'V'; // You can change this to 'uV' or have this set through UI

    // Sample data
    var timeData = []; // Assume this is in seconds
    var voltageData = []; // Assume this is in volts

    // Convert time data based on scale
    var convertedTimeData = timeData.map(function(time) {
        switch (timeScale) {
            case 'us':
                return time * 1000000;
            case 'ns':
                return time * 1000000000;
            default:
                return time;
        }
    });

    // Convert voltage data based on scale
    var convertedVoltageData = voltageData.map(function(voltage) {
        switch (voltageScale) {
            case 'uV':
                return voltage * 1000000;
            default:
                return voltage;
        }
    });

    var signalChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Signal',
                data: data,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time (' + timeScale + ')'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Voltage (' + voltageScale + ')'
                    },
                    beginAtZero: false
                }
            }
        }
    });
});

