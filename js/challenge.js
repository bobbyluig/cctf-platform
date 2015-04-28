/*! jquery.finger - v0.1.2 - 2014-10-01
* https://github.com/ngryman/jquery.finger
* Copyright (c) 2014 Nicolas Gryman; Licensed MIT */
(function(e,t){function a(t){t.preventDefault(),e.event.remove(T,"click",a)}function n(e,t){return(p?t.originalEvent.touches[0]:t)["page"+e.toUpperCase()]}function r(t,n,r){var o=e.Event(n,b);e.event.trigger(o,{originalEvent:t},t.target),o.isDefaultPrevented()&&(~n.indexOf("tap")&&!p?e.event.add(T,"click",a):t.preventDefault()),r&&(e.event.remove(T,y+"."+D,i),e.event.remove(T,x+"."+D,d))}function o(t){var o=t.timeStamp||+new Date;v!=o&&(v=o,k.x=b.x=n("x",t),k.y=b.y=n("y",t),k.time=o,k.target=t.target,b.orientation=null,b.end=!1,u=!1,l=!1,c=setTimeout(function(){l=!0,r(t,"press")},e.Finger.pressDuration),e.event.add(T,y+"."+D,i),e.event.add(T,x+"."+D,d),w.preventDefault&&(t.preventDefault(),e.event.add(T,"click",a)))}function i(t){if(b.x=n("x",t),b.y=n("y",t),b.dx=b.x-k.x,b.dy=b.y-k.y,b.adx=Math.abs(b.dx),b.ady=Math.abs(b.dy),u=b.adx>w.motionThreshold||b.ady>w.motionThreshold){for(clearTimeout(c),b.orientation||(b.adx>b.ady?(b.orientation="horizontal",b.direction=b.dx>0?1:-1):(b.orientation="vertical",b.direction=b.dy>0?1:-1));t.target&&t.target!==k.target;)t.target=t.target.parentNode;return t.target!==k.target?(t.target=k.target,d.call(this,e.Event(x+"."+D,t)),void 0):(r(t,"drag"),void 0)}}function d(e){var t,a=e.timeStamp||+new Date,n=a-k.time;if(clearTimeout(c),u||l||e.target!==k.target)e.target=k.target,w.flickDuration>n&&r(e,"flick"),b.end=!0,t="drag";else{var o=g===e.target&&w.doubleTapInterval>a-s;t=o?"doubletap":"tap",g=o?null:k.target,s=a}r(e,t,!0)}var u,l,v,c,g,s,m=/chrome/i.exec(t),f=/android/i.exec(t),p="ontouchstart"in window&&!(m&&!f),h=p?"touchstart":"mousedown",x=p?"touchend touchcancel":"mouseup mouseleave",y=p?"touchmove":"mousemove",D="finger",T=e("html")[0],k={},b={},w=e.Finger={pressDuration:300,doubleTapInterval:300,flickDuration:150,motionThreshold:5};e.event.add(T,h+"."+D,o)})(jQuery,navigator.userAgent);

var cache = [];
var sort_order = 'title';

if(typeof(Storage) !== 'undefined') {
	if(!localStorage['challenge_cache']) {
		localStorage.setItem('challenge_cache', '[]');
	}
	if(!localStorage['challenge_sortorder']) {
		localStorage.setItem('challenge_sortorder', 'title');
	}
	cache = JSON.parse(localStorage['challenge_cache']);
	sort_order = localStorage['challenge_sortorder'];
}

if(sort_order === 'title') {
	$('#order1').prop('checked', true);
} else {
	$('#order2').prop('checked', true);
}

function objsort(array, key) {
	array.sort(function(a, b) {
		return (a[1][key] > b[1][key]) ? 1 : ((b[1][key] > a[1][key]) ? -1 : 0);
	});
}

//Initialize the sideNav
$(".button-collapse").sideNav();
//Initialize the modal
$('.modal-trigger').leanModal();

icon_map = {
	'Cryptography': 'mdi-communication-vpn-key',
	'Exploitation': 'mdi-hardware-security',
	'Forensics': 'mdi-action-search',
	'Programming': 'mdi-editor-mode-edit',
	'Reconnaissance': 'mdi-action-explore',
	'Miscellaneous': 'mdi-social-share'
}

function list_challenges() {
	categories = [];
	data = {};
	cache.forEach(function(challenge){
		challenge = challenge[1];
		category = challenge.category;
		if (!(categories.indexOf(category) > -1)) {
			categories.push(category);
			data[category] = $('<div class="collection">');
		}
		
		var cla = 'white';
			if (challenge.solved == 1) {
			cla = 'green lighten-5';
		} else if (challenge.deactivated == 1) {
			cla = 'red lighten-5';
		}
		
		data[category].append('<a href="' + challenge['id'] + '" id="challenge" class="' + cla + ' collection-item">' + challenge['title'] + '<span class="badge">' + challenge['score'] + '</span></a>');
	});
	
	categories.sort();
	$('#chal-view ul').empty();
	var total_solved = 0;
	
	categories.forEach(function(category) {
		var total = data[category].children().length;
		var solved = data[category].children('.green').length;
		var a = $('<li>').appendTo($('#data'));
		var b = $('<div class="collapsible-header"><i class="' + icon_map[category] + '"></i>' + category + ' - ' + solved + '/' + total + '</div>').appendTo(a);
		$('<div>').attr('class', 'collapsible-body').append(data[category]).appendTo(a);
		if(total === solved) {
			b.addClass('green lighten-5');
		}
		total_solved += solved;
	});

	$('#data').collapsible();
	$('#chal-view ul').show();
	
	$({
		someValue: parseInt($('#count').text())
	}).animate({
		someValue: total_solved
	}, {
		duration: 2000,
		easing: 'swing',
		step: function() {
			$('#count').text(Math.ceil(this.someValue));
		}
	});
	
	$('.valign-wrapper').hide();
	$('#chal-view ul').show();
}

function refresh_challenges() {
	$('#chal-view ul').hide().empty();
	$('.valign-wrapper').show();
	$.ajax({
		type: 'GET',
		url: '/api/challenges/name_list/',
		success: function(data) {
			if (data.success == false) {
				Materialize.toast(data.message, 3000, '', function() {
					$('.challenge-nav').sideNav('hide');
				});
				return false;
			}

			$.each(data, function(key, challenges) {
				$.each(challenges, function(id, challenge) {
					var c_challenge = cache.filter(function(element){return element[1]['id'] == challenge['id']})[0];
					if (c_challenge !== undefined) {
						c_challenge[1].solved = challenge.solved;
						c_challenge[1].solves = challenge.solves;
					} else {
						challenge.category = key;
						cache.push([challenge.id, challenge]);
					}
				});
			});
			
			objsort(cache, sort_order);
			list_challenges(cache);
			$('.collapsible').collapsible();
			localStorage['challenge_cache'] = JSON.stringify(cache);
		}
	});
	
	return false;
}

function display_challenge(id) {
	// Super advanced and amazing reference variable. Took way too long...
	var challenge = cache.filter(function(element){return element[1]['id'] == id})[0];
	challenge = challenge[1];
	if (!('description' in challenge) || challenge['type'] == '1') {
		$.ajax({
			type: 'GET',
			url: '/api/challenges/get_challenge/',
			data: {
				'id': id
			},
			success: function(data) {
				if (data.success == false) {
					Materialize.toast(data.message, 3000);
					return;
				} else {
					challenge.description = data.description;
					challenge.solves = data.solves;
					update_display(challenge);
					localStorage['challenge_cache'] = JSON.stringify(cache);
				}
			}
		});
	} else {
		update_display(challenge);
	}
}

function update_display(challenge) {
	$('#title').text(challenge.title + ' - ' + challenge.score);
	$('#description').html(challenge.description);
	$('#solves').text(challenge.solves);
	$('input[name="id"]').val(challenge.id);
	
	$('ul.tabs').tabs('select_tab', 'solve-view');

	var distance = 0;
	if ($('.card').height() > $(window).height()) {
		distance = $('.card').offset()['top'];
	} else {
		distance = $('.card').offset()['top'] - ($(window).height() / 2) + ($('.card').height() / 2);
	}
	$('html, body').animate({
		scrollTop: distance
	}, 500);
}

$('body').on('click', '#challenge', function() {
	display_challenge($(this).attr('href'));
	return false;
});

$('form').submit(function() {
	if ($(this).find('input[type="hidden"]').val() == '0') {
		Materialize.toast('Select a challenge first!', 2000);
		return false;
	}

	form = $(this);
	$.ajax({
		type: 'POST',
		url: $(this).attr('action'),
		data: $(this).serialize(),
		success: function(data) {
			if (data.success) {
				refresh_challenges();
				$('#solves').text(data.solves);
			}
			form[0].reset();
			form.find('i, label').removeClass('active');
			form.find('input').blur();
			Materialize.toast(data.message, data.message.length * 150);
		}
	});
	return false;
});

$(document).ready(function() {
	refresh_challenges();
	
	$('input[name=sortorder]').change(function(){
		sort_order = $(this).data('sort');
		objsort(cache, sort_order);
		list_challenges();
		localStorage['challenge_sortorder'] = sort_order;
	});
	
	$('a[href="#chal-view"]').dblclick(function() {
		refresh_challenges();
	});
	
	$('a[href="#chal-view"]').on('doubletap', function(e) {
		refresh_challenges();
	});
	
	$('#clear-cache').click(function() {
		localStorage.clear();
		cache = [];
		refresh_challenges();
		return false;
	});
});