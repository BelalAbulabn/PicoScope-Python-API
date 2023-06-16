
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
