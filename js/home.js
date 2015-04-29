//Function used to subtract arrays and return difference
function subarray(a, b) {
	var temp = [];
	for (i = 0; i < a.length; i++) {
		temp[i] = a[i] - b[i];
	}
	return temp;
}

//Function used to count down time with the target being customizable
function countdown() {
	var epoch = Math.floor((new Date).getTime()/1000);
	var target = 1429315200;
	if (target > epoch) {
		$('#countdown').text(Math.floor(target-epoch));
	} else {
		$('#countdown').text('0');
	}
	setTimeout(function() {
		countdown();
	}, 1000);
}

$('document').ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	
	//Initialize countdown
	countdown();
	
	//Check if this site has been accessed and if not open the help modal
	if(typeof(Storage) !== 'undefined') {
		if(!localStorage['home_new']) {
			localStorage.setItem('home_new', 'false');
			$('#helpmodal').openModal();
		}
	} else {
		$('#helpmodal').openModal();
	}
	
	//Create a var that selects an attribute and hides it
	var $list = $('#system p').hide();
	//Split and shoe the list
	$list.slice(0, 5).show();
	//Copy length to new var
	var list_size = $list.length;
	//Create a list with the size of 5
	var x = 5;
	//Start the list at 0
	var start = 0;
	//Start it off
	var running = false;
	
	//When the back button is hit, go back in time to previous messages
	$('#back').click(function() {
		if (start + x < list_size && !running) {
			running = true;
			$list.slice(start, start + x).fadeOut('medium', function() {
				$list.slice(start, start + x).fadeIn('medium', function() {
					running = false;
				});
			});
			start += x;
		}
		return false;
	});
	
	//When the forward button is hit, go forward in time to newer messages
	$('#forward').click(function() {
		if (start - x >= 0 && !running) {
			running = true;
			$list.slice(start, start + x).fadeOut('medium', function() {
				$list.slice(start, start + x).fadeIn('medium', function() {
					running = false;
				});
			});
			start -= x;
		}
		return false;
	});
	
	//Get data for the home graph
	$.ajax({
		type: 'GET',
		url: '/api/home/graph/',
		success: function(data) {
			if (data.success === false) {
				//Clear wrapper and add a heading and center it
				$('.valign-wrapper').empty();
				$('.valign-wrapper').html('<h5 class="center light">' + data.message + '</h5>');
				return false;
			}
			var options = {
				chart: {
					renderTo: 'graph'
				},
				//The X Axis type
				xAxis: {
					type: 'datetime'
				},
				//Data to graph
				series: [{
					pointStart: data.start * 1000,
					pointInterval: data.interval * 1000,
					name: 'Total Earned (Raw+Bonus)',
					data: data.total_score
				}, {
					pointStart: data.start * 1000,
					pointInterval: data.interval * 1000,
					name: 'Total IP',
					data: data.total_ip
				}, {
					pointStart: data.start * 1000,
					pointInterval: data.interval * 1000,
					name: 'Successful IP',
					data: data.successful_ip
				}, {
					pointStart: data.start * 1000,
					pointInterval: data.interval * 1000,
					name: 'Failed IP',
					data: subarray(data.total_ip, data.successful_ip)
				}, ],
				//Credits option
				credits: {
					enabled: false
				},
				//Title
				title: {
					text: 'System Statistics'
				},
				//The Y Axis type
				yAxis: {
					title: 'Value',
					floor: 0
				}
			}
			
			//New date adjusted to TimeZones
			var d = new Date();
			Highcharts.setOptions({
				global: {
					timezoneOffset: d.getTimezoneOffset()
				}
			});
			
			//Create a chart with the options
			var chart = new Highcharts.Chart(options);
		}
	});
});