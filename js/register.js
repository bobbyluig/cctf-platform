$(document).ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	$('select').material_select();

	$('form').submit(function() {
		if (!$('#agree').is(':checked')) {
			Materialize.toast('Please agree to the Terms and Conditions.', 3000);
			return false;
		}
		if (!$('#g-recaptcha-response').val()) {
			Materialize.toast('Please verify your non-bot status.', 3000);
			return false;
		}

		form = $(this);
		$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', true);
		
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				if (data.success == 1) {
					form[0].reset();
					form.find('i, label').removeClass('active');
					form.find('input').blur();
				}
				grecaptcha.reset();
				Materialize.toast(data.message, data.message.length * 150);
				setTimeout(function() {
					$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', false);
				}, 500);
			}
		});
		return false;
	});
});