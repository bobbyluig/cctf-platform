$(document).ready(function() {
	$(".button-collapse").sideNav();
	$('.modal-trigger').leanModal();

	$('form').submit(function() {
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				if (data.success == 1) {
					window.location.href = '/';
				} else {
					Materialize.toast(data.message, data.message.length * 150);
				}
			}
		});
		return false;
	});
});