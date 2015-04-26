$(document).ready(function() {
	$(".button-collapse").sideNav();
	$('.modal-trigger').leanModal();

	$('form').submit(function() {
		form = $(this)
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				if (data.success == 1) {
					form.find('input:password').val('').blur().parent().find('i, label').removeClass('active');
				}
				Materialize.toast(data.message, data.message.length * 150);
			}
		});
		return false;
	});

	$('#logout').click(function() {
		$.ajax({
			type: 'GET',
			url: '/api/logout',
			success: function(data) {
				if (data.success == 1) {
					window.location.href = '/';
				} else {
					Materialize.toast(data.message, data.message.length * 150);
				}
			}
		});
	});
});