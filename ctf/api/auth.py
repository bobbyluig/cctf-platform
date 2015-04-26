import os, random, string
from api.models import *
import json, time
from django.http import HttpResponse
from django.core.mail import send_mail
from api.config import config
from django.contrib.auth.hashers import *
from django.conf import settings

def login(request):
	'''Handles all login requests. Accepts post parameters [name] and [password].'''
	
	if (request.method != 'POST') or not all(x in request.POST for x in ['name', 'password']):
		return HttpResponse()

	if 'teamid' in request.session:
		response = {'success': False, 'message': 'You are already logged in.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	try:
		m = db_team.objects.get(name=request.POST['name'])
	except:
		m = False
	
	if hasattr(m, 'password') and check_password(request.POST['password'], m.password):
		request.session['teamid'] = m.id
		m.lastlogin = time.time()
		m.save() # Update last login.
		response = {'success': True, 'message': 'You have logged in.'}
	else:
		response = {'success': False, 'message': 'Log in failed.'}
		time.sleep(0.5) # Prevent brute-forcing.
		
	return HttpResponse(json.dumps(response), content_type="application/json")
	
def logout(request):
	'''Handles logout requests. Accepts no post parameters'''
	
	if 'teamid' not in request.session:
		response = {'success': False, 'message': 'You are not logged in.'}
	else:
		request.session.flush()
		response = {'success': True, 'message': 'You have been logged out.'}
		
	return HttpResponse(json.dumps(response), content_type="application/json")

def generate_password():
	length = 10
	chars = string.ascii_letters + string.digits
	random.seed = os.urandom(1024) + '5XSqWTf89BTw2VJzmKf4RkGM'.encode()
	return ''.join(random.choice(chars) for i in range(length))
	
def forgot(request):
	'''Handles forget password requests. Accepts the post parameter [email]'''
	
	if (request.method != 'POST') or ('email' not in request.POST):
		return HttpResponse()
		
	if 'teamid' in request.session:
		response = {'success': False, 'message': 'You are already logged in.'}
	else:
		response = {'success': True, 'message': 'If your email is associated with an account, a temporary password has been sent to you.'}
		try:
			team = db_team.objects.get(email=request.POST['email'])
			password = generate_password()
			team.password = make_password(password)
			email = team.email
			team.save()
			message = "Dear %s,\n\nYour team has requested a password reset. Your temporary password is %s. Please log in and change the provided password.\n\nThank you,\nCAMS CTF" % (team.name, password)
			
			SYSTEM_EMAIL = config.SYSTEM_EMAIL
			send_mail('CTF Password Recovery', message, SYSTEM_EMAIL, [email], fail_silently=True)
		except:
			pass
	
	return HttpResponse(json.dumps(response), content_type="application/json")