$(document).ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	//Initialize the form
	$('select').material_select();

	$('form').submit(function() {
		//Check if terms and conditions are checked then display a toast if otherwise
		if (!$('#agree').is(':checked')) {
			Materialize.toast('Please agree to the Terms and Conditions.', 3000);
			return false;
		}
		//Check the captcha and display toast if not verified
		if (!$('#g-recaptcha-response').val()) {
			Materialize.toast('Please verify your non-bot status.', 3000);
			return false;
		}
		
		form = $(this);
		//Disable the submit as double registering is not wanted
		$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', true);
		
		//Send data to the server
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				//On completion reset the form and remove the active classes
				if (data.success == 1) {
					form[0].reset();
					form.find('i, label').removeClass('active');
					form.find('input').blur();
				}
				//Reset Google ReCaptcha
				grecaptcha.reset();
				//Toast a message
				Materialize.toast(data.message, data.message.length * 150);
				//Reenable submit button after a period of time
				setTimeout(function() {
					$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', false);
				}, 500);
			}
		});
		return false;
	});
});