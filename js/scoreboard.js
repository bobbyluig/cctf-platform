var cache = [];
var last_th = '';
var selfid = -1;

function objsort(array, key) {
	array.sort(function(a, b) {
		return (a[key] > b[key]) ? 1 : ((b[key] > a[key]) ? -1 : 0);
	});
}

function table(data) {
	$('table tbody').empty();
	$(data).each(function(key, value) {
		if ($('#self b').length && value['id'] == selfid) {
			$('#self b').eq(0).text(value['team']);
			$('#self b').eq(1).text('#' + value['rank']);
			$('#self b').eq(2).text(value['score']);
		}
		tr = $('<tr>').data('id', value['id']).appendTo($('tbody'));
		$('<td>').appendTo(tr).text(value['rank']);
		$('<td>').appendTo(tr).text(value['team']);
		$('<td>').appendTo(tr).text(value['school']);
		$('<td>').appendTo(tr).text(value['score']);
	});
}

$(document).ready(function() {
	$('.button-collapse').sideNav();
	$('.modal-trigger').leanModal();

	$.ajax({
		type: 'GET',
		url: '/api/scoreboard/',
		success: function(data) {
			if (data.success == false) {
				Materialize.toast(data.message, 3000);
				return false;
			}
			cache = data;
			selfid = cache.pop(); 
			objsort(cache, 'rank');
			table(cache);
			$('table th').first().addClass('green lighten-3');

			$('.valign-wrapper').hide();
			$('#self').show();
			$('table').show();
		}
	});

	$('body').on('click', 'tbody tr', function() {
		link = $(this).data('id');
		window.location.href = '/team/?t=' + encodeURIComponent(link);
	});

	$('body').on('click', 'table th', function() {
		$(this).siblings().removeClass('green lighten-3');
		$(this).addClass('green lighten-3');
		if (last_th === $(this).data('sort')) {
			cache.reverse();
		} else {
			objsort(cache, $(this).data('sort'));
		}
		last_th = $(this).data('sort');
		table(cache);
	});
});