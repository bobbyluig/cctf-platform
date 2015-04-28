$(document).ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	
	//Get data to confirm login
	$('form').submit(function() {
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				//On completion redirect to home page
				if (data.success == 1) {
					window.location.href = '/';
				} else {
				//On failure display a toast with error message
					Materialize.toast(data.message, data.message.length * 150);
				}
			}
		});
		return false;
	});
});