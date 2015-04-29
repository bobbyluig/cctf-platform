//Create a URL for the team
function getURLParameter(name) {
	return (new RegExp('[?|&]' + name + '=' + '([^&;]+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20') || null
}

//Subtract two arrays and return difference
function subarray(a, b) {
	var temp = [];
	for (i = 0; i < a.length; i++) {
		temp[i] = a[i] - b[i];
	}
	return temp;
}

//Map out the categories to the mdi
icon_map = {
	'Cryptography': 'mdi-communication-vpn-key',
	'Exploitation': 'mdi-hardware-security',
	'Forensics': 'mdi-action-search',
	'Programming': 'mdi-editor-mode-edit',
	'Reconnaissance': 'mdi-action-explore',
	'Miscellaneous': 'mdi-social-share'
}

//Function to get statistical data
function ajax_stats(data) {
	//On failure stop preload and display error message
	if(data.success == false) {
		$('#preload .container').empty();
		$('#preload .container').html('<h5 class="center light">' + data.message + '</h5>');
	}
	
	//Start at 0 solved
	var total_solved = 0;
	//Loop through data and mark solved and unsolved challenges
	for(var category in data['challenges']) {
		cat = category;
		category = data['challenges'][category];
		var total = category.length;
		var solved = 0;
		//Create a collection
		var list = $('<div class="collection">');
		category.forEach(function(challenge) {
			var cla = 'white';
			//Green for solved
			if (challenge.solved == 1) {
				cla = 'green lighten-5';
				solved += 1;
			//Red for unsolved
			} else if (challenge.deactivated == 1) {
				cla = 'red lighten-5';
			}
			//Add the class, name, score
			list.append('<a class="' + cla + ' collection-item">' + challenge['title'] + '<span class="badge">' + challenge['score'] + '</span></a>');
		});
		
		//Make it a list
		var a = $('<li>').appendTo($('#data'));
		//Add the mdi
		var b = $('<div class="collapsible-header"><i class="' + icon_map[cat] + '"></i>' + cat + ' - ' + solved + '/' + total + '</div>').appendTo(a);
		//Add green color
		if(total === solved) {
			b.addClass('green lighten-5');
		}
		//Make it collapsible
		$('<div>').attr('class', 'collapsible-body').append(list).appendTo(a);
		
		//Increase the total number of solved challenges
		total_solved += solved;
	}
	//Make #data collapsible
	$('#data').collapsible();
	//Embiggen the team
	$('h2').text(data['team']);
	//Add elements to data
	$('#1').text(data['score']);
	$('#2').text(data['lost']);
	$('#3').text(total_solved);
	$('#4').text(data['bonus']);
	$('#5').text(data['fails']);
	
	//Get the accuracy
	var sub_acc = parseFloat(total_solved/(total_solved+data['fails'])*100).toFixed(2);
	if(isNaN(sub_acc)) {
		sub_acc = 'Undefined';
	} else {
		sub_acc += '%';
	}
	//Add #6 to accuracy
	$('#6').text(sub_acc);
	//Add elements to data
	$('#7').text(data['usedip']);
	$('#8').text(data['success']);
	$('#9').text(data['fail']);
	
	//Get accuracy
	var int_acc = parseFloat(data['success']/(data['success']+data['fail'])*100).toFixed(2);
	if(isNaN(int_acc)) {
		int_acc = 'Undefined';
	} else {
		int_acc += '%';
	}
	//Add #10 to accuracy
	$('#10').text(int_acc);
	
	//Loop through and add data
	if(data['origin'].length > 0) {
		data['origin'].forEach(function(team) {
			var a = $('<tr>').appendTo($('#origin tbody'));
			$('<td>').appendTo(a).text(team[0]);
			$('<td>').appendTo(a).text(team[1]);
			$('<td>').appendTo(a).text(team[2]);
		});
	} else {
		$('#origin').remove();
	}
	
	//Loop through and add team data
	if(data['destination'].length > 0) {
		data['destination'].forEach(function(team) {
			var a = $('<tr>').appendTo($('#destination tbody'));
			$('<td>').appendTo(a).text(team[0]);
			$('<td>').appendTo(a).text(team[1]);
			$('<td>').appendTo(a).text(team[2]);
		});
	} else {
		$('#destination').remove();
	}
	
	//Remove preloader and show the stats
	$('#preload').hide();
	$('#main').show();
}

//Get data and make a graph
function ajax_graph(data) {
	//On failure stop preload and display error message
	if (data.success === false) {
		$('#graph .valign-wrapper').empty();
		$('#graph .valign-wrapper').html('<h5 class="center light">' + data.message + '</h5>');
		return false;
	}
	//Options for graph
	var options = {
		//Where to render
		chart: {
			renderTo: 'graph'
		},
		//X Axis type
		xAxis: {
			type: 'datetime'
		},
		//Data to plot
		series: [{
			pointStart: data.start * 1000,
			pointInterval: data.interval * 1000,
			name: 'Base Points',
			data: data.base_score
		}, {
			pointStart: data.start * 1000,
			pointInterval: data.interval * 1000,
			name: 'Offensive IP',
			data: data.used_ip
		}, {
			pointStart: data.start * 1000,
			pointInterval: data.interval * 1000,
			name: 'O. IP (S)',
			data: data.successful_ip
		}, {
			pointStart: data.start * 1000,
			pointInterval: data.interval * 1000,
			name: 'O. IP (F)',
			data: subarray(data.used_ip, data.successful_ip)
		}, {
			pointStart: data.start * 1000,
			pointInterval: data.interval * 1000,
			name: 'Defensive IP',
			data: data.total_attempted
		}, {
			pointStart: data.start * 1000,
			pointInterval: data.interval * 1000,
			name: 'D. IP (S) ',
			data: data.total_lost
		}, {
			pointStart: data.start * 1000,
			pointInterval: data.interval * 1000,
			name: 'D. IP (F)',
			data: subarray(data.total_attempted, data.total_lost)
		}, ],
		//Credits
		credits: {
			enabled: false
		},
		//Title
		title: {
			text: 'Team Progression Data'
		},
		//Y Axis type
		yAxis: {
			title: 'Value',
			floor: 0
		}
	}
	
	//TimeZone options
	var d = new Date();
	Highcharts.setOptions({
		global: {
			timezoneOffset: d.getTimezoneOffset()
		}
	});
	
	//Create a chart
	var chart = new Highcharts.Chart(options);
}
//Create dynamic URLs
var d1 = $.get('/api/team/stats/?t=' + getURLParameter('t'));
var d2 = $.get('/api/team/graph/?t=' + getURLParameter('t'));

$(document).ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	
	//Run Stats and Graph functions
	$.when(d1).done(function(data) {
		ajax_stats(data);
		$.when(d2).done(function(data) {
			ajax_graph(data);
		});
	});
});