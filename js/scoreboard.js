//Create a cache
var cache = [];
//Create var for storing last setting on scoreboard
var last_th = '';
//Create var for self identification
var selfid = -1;

//Sort an array based on object key value
function objsort(array, key) {
	array.sort(function(a, b) {
		return (a[key] > b[key]) ? 1 : ((b[key] > a[key]) ? -1 : 0);
	});
}

//Load data to table
function table(data) {
	//Empty the table
	$('table tbody').empty();
	//Show data of self at top
	$(data).each(function(key, value) {
		if ($('#self b').length && value['id'] == selfid) {
			$('#self b').eq(0).text(value['team']);
			$('#self b').eq(1).text('#' + value['rank']);
			$('#self b').eq(2).text(value['score']);
		}
		//Truncate any huge values
		tr = $('<tr>').data('id', value['id']).appendTo($('tbody'));
		//Load in values of team's Rank, Team, School, and Score
		$('<td>').appendTo(tr).text(value['rank']);
		$('<td>').appendTo(tr).text(value['team']);
		$('<td>').appendTo(tr).text(value['school']);
		$('<td>').appendTo(tr).text(value['score']);
	});
}

$(document).ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	
	//Get info from server
	$.ajax({
		type: 'GET',
		url: '/api/scoreboard/',
		success: function(data) {
			//On completion toast
			if (data.success == false) {
				Materialize.toast(data.message, 3000);
				return false;
			}
			//Cache
			cache = data;
			selfid = cache.pop(); 
			objsort(cache, 'rank');
			table(cache);
			//Add class to selected sorter
			$('table th').first().addClass('green lighten-3');
			//Hide vertical align wrapper
			$('.valign-wrapper').hide();
			//Show self element
			$('#self').show();
			//Show table element
			$('table').show();
		}
	});
	//On click of a team redirect to a URL for that team
	$('body').on('click', 'tbody tr', function() {
		link = $(this).data('id');
		window.location.href = '/team/?t=' + encodeURIComponent(link);
	});
	
	//Add class to the sorter of choice
	$('body').on('click', 'table th', function() {
		//Remove class on previous sorter
		$(this).siblings().removeClass('green lighten-3');
		//Add onto desired sorter
		$(this).addClass('green lighten-3');
		//Sort the scoreboard
		if (last_th === $(this).data('sort')) {
			cache.reverse();
		} else {
			objsort(cache, $(this).data('sort'));
		}
		last_th = $(this).data('sort');
		//Cache
		table(cache);
	});
});