function subarray(a, b) {
	var temp = [];
	for (i = 0; i < a.length; i++) {
		temp[i] = a[i] - b[i];
	}
	return temp;
}

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
	$('.button-collapse').sideNav();
	$('.modal-trigger').leanModal();

	countdown();
	
	if(typeof(Storage) !== 'undefined') {
		if(!localStorage['home_new']) {
			localStorage.setItem('home_new', 'false');
			$('#helpmodal').openModal();
		}
	} else {
		$('#helpmodal').openModal();
	}

	var $list = $('#system p').hide();
	$list.slice(0, 5).show();
	var list_size = $list.length;
	var x = 5;
	var start = 0;
	var running = false;

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

	$.ajax({
		type: 'GET',
		url: '/api/home/graph/',
		success: function(data) {
			if (data.success === false) {
				$('.valign-wrapper').empty();
				$('.valign-wrapper').html('<h5 class="center light">' + data.message + '</h5>');
				return false;
			}
			var options = {
				chart: {
					renderTo: 'graph'
				},
				xAxis: {
					type: 'datetime'
				},
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
				credits: {
					enabled: false
				},
				title: {
					text: 'System Statistics'
				},
				yAxis: {
					title: 'Value',
					floor: 0
				}
			}
			
			var d = new Date();
			Highcharts.setOptions({
				global: {
					timezoneOffset: d.getTimezoneOffset()
				}
			});
			
			var chart = new Highcharts.Chart(options);
		}
	});
});