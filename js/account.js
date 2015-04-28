$(document).ready(function() {
	//Initialize the sideNav
	$(".button-collapse").sideNav();
	//Initialize the modal
	$('.modal-trigger').leanModal();
	
	//Send new info to server
	$('form').submit(function() {
		form = $(this)
		$.ajax({
			type: 'POST',
			url: $(this).attr('action'),
			data: $(this).serialize(),
			success: function(data) {
				//On completion blur and remove active class of the parent label
				if (data.success == 1) {
					form.find('input:password').val('').blur().parent().find('i, label').removeClass('active');
				}
				//Toast info
				Materialize.toast(data.message, data.message.length * 150);
			}
		});
		return false;
	});
	
	//Logout info to server
	$('#logout').click(function() {
		$.ajax({
			type: 'GET',
			url: '/api/logout',
			success: function(data) {
				//On completion redirect to home page
				if (data.success == 1) {
					window.location.href = '/';
				} else {
				//On failure display toast with a message
					Materialize.toast(data.message, data.message.length * 150);
				}
			}
		});
	});
});