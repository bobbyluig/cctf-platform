$(document).ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	
	//When the submit button is hit
	$('form').submit(function() {
		form = $(this);
		//Disable submit button
		$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', true);
		//Send data to server
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				//Reset form
				form[0].reset();
				//Deactivate the labels
				form.find('i, label').removeClass('active');
				//Blur the input fields
				form.find('input').blur();
				//Toast a confirmation
				Materialize.toast(data.message, data.message.length * 150);
				//Enable the submit button after a period of time
				setTimeout(function() {
					$('button', form).toggleClass('disabled waves-effect waves-light').attr('disabled', false);
				}, 500);
			}
		});
		return false;
	});
});