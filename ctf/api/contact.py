from api.models import *
import hashlib, json
from time import gmtime, strftime
from django.http import HttpResponse
from django.core.mail import send_mail
from django import forms
from api.config import config

def contact(request):
	'''Handles contacts. Sends email to administrator. Accepts post parameters [first], [last], [message], and [email].'''
	if (request.method != 'POST') or not all(x in request.POST for x in ['first', 'last', 'message', 'email']):
		return HttpResponse()
		
	f = forms.EmailField()
		
	first = request.POST['first']
	last = request.POST['last']
	message = request.POST['message']
	try:
		email = f.clean(request.POST['email'])
	except:
		email = False
		
	if len(message) < 1:
		response = {'success': False, 'message': 'You must have a message!'}
	elif len(first) < 1 or len(last) < 1:
		response = {'success': False, 'message': 'Your name is invalid.'}
	elif not email:
		response = {'success': False, 'message': 'Please enter a valid email!'}
	else:
		time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
		mail_message = 'Dear maintainer,\n\nThe following message was sent by %s %s on %s.\n\n"%s"\n\nPlease respond to his/her email: %s.' % (first, last, time, message, email)
		
		try:
			send_mail('Contact Us', mail_message, 'admin@ctf.camscsc.org', [config.ADMIN_EMAIL], fail_silently=False)
			response = {'success': True, 'message': 'Your messsage has been sent successfully!'}
		except:
			response = {'success': False, 'message': 'Your message was not sent. Please try again later.'}
		
	return HttpResponse(json.dumps(response), content_type="application/json")
	
	