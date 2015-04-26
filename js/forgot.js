$(document).ready(function() {
	$(".button-collapse").sideNav();
	$('.modal-trigger').leanModal();

	$('form').submit(function() {
		form = $(this);
		$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', true);
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				form[0].reset();
				form.find('i, label').removeClass('active');
				form.find('input').blur();
				Materialize.toast(data.message, data.message.length * 150);
				setTimeout(function() {
					$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', false);
				}, 500);
			}
		});
		return false;
	});
});