from api.models import db_team, db_profile
import json, re, time, requests
from django.http import HttpResponse
from django import forms
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.hashers import *
from api.config import config
from django.core.cache import cache

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@transaction.atomic
def insert_team(name, school, password, email, members, ip):
	try:
		team = db_team(name=name, local=1, school=school, password=password, email=email, registration=time.time(), lastlogin=time.time())
		team.save()
		profile = db_profile(team=team.id, members=members, score=0, ip=0, completed=[], track=ip, fails=0, last_solve_time=time.time())
		profile.save()
		
		cache.set('system_scoreboard', '', 0)
		return True
	except:
		return False
	
def create_account(request):
	'''Creates a new team with post parameters [name], [school], [m1], [m2], [m3], [m4], [email], and [password].'''
	
	if (request.method != 'POST') or not all(x in request.POST for x in ['name', 'school', 'm1', 'm2', 'm3', 'm4', 'email', 'password', 'confirm', 'g-recaptcha-response']):
		return HttpResponse()
	
	'''
	if config.comp_ended():
		response = {'success': False, 'message': 'Competition has ended!'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	'''
	
	f = forms.EmailField()
	
	name = request.POST['name']
	school = request.POST['school']
	members = [request.POST['m1'][:50], request.POST['m2'][:50], request.POST['m3'][:50], request.POST['m4'][:50]]
	password = request.POST['password']
	confirm = request.POST['confirm']
	
	try:
		email = f.clean(request.POST['email'])
	except:
		email = False
	try:
		repeat_name = True
		db_team.objects.get(name=name)
	except:
		repeat_name = False
	try:
		repeat_email = True
		db_team.objects.get(email=email)
	except:
		repeat_email = False
	
	payload = {'secret': config.GCAPTCHA_SECRET, 'response': request.POST['g-recaptcha-response'], 'remoteip': get_client_ip(request)}
	url = 'https://www.google.com/recaptcha/api/siteverify'
	r = requests.post(url, data=payload)
	captcha = json.loads(r.text)
	
	if captcha['success'] != True:
		response = {'success': False, 'message': 'Please, stop being a robot.'}
	elif len(name) == 0 or len(school) == 0 or len(email) == 0 or len(password) == 0:
		response = {'success': False, 'message': 'All fields must be filled out.'}
	elif repeat_name:
		response = {'success': False, 'message': 'It looks like your team name is already taken.'}
	elif repeat_email:
		response = {'success': False, 'message': 'It looks like your email is already associated with a team.'}
	elif len(name) > 40:
		response = {'success': False, 'message': 'Your team name cannot exceed 40 characters in length!'}
	elif re.search('[ -~]{1,40}', name).group() != name:
		response = {'success': False, 'message': 'Your username is not within the ASCII printable range!'}
	elif name.startswith(' ') or name.endswith(' '):
		response = {'success': False, 'message': 'Team names cannot start or end with a space!'}
	elif all(len(m) == 0 for m in members):
		response = {'success': False, 'message': 'You cannot have a team with 0 members!'}
	elif not email:
		response = {'success': False, 'message': 'Please enter a valid email!'}
	elif len(school) > 100:
		response = {'success': False, 'message': 'Come on. Your school name is not that long.'}
	elif len(password) < 6:
		response = {'success': False, 'message': 'Use a secure password at least 6 characters long!'}
	elif password != confirm:
		response = {'success': False, 'message': 'Passwords do not match!'}
	else:
		success = insert_team(name, school, make_password(password), email, members, get_client_ip(request))
		
		if success:
			response = {'success': True, 'message': 'Registration successful!'}
		else:
			response = {'success': False, 'message': 'Error. Try again in a few seconds.'}
	
	return HttpResponse(json.dumps(response), content_type="application/json")
	
def u_basic(request):
	'''Updates basic information. Accepts post parameters [m1], [m2], [m3], [m4], [email], [email].'''
	
	if (request.method != 'POST') or not all(x in request.POST for x in ['m1', 'm2', 'm3', 'm4', 'email', 'password']):
		return HttpResponse()
		
	if 'teamid' not in request.session:
		response = {'success': False, 'message': 'You must be logged in to view this resource.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	f = forms.EmailField()
	
	try:
		email = f.clean(request.POST['email'])
	except:
		email = False

	members = [request.POST['m1'][:50], request.POST['m2'][:50], request.POST['m3'][:50], request.POST['m4'][:50]]
	password = request.POST['password']
	team = db_team.objects.get(id=request.session['teamid'])
	
	if not check_password(password, team.password):
		response = {'success': False, 'message': 'Your current password does not match our records.'}
	else:
		repeat = db_team.objects.filter(Q(email=email), ~Q(id=request.session['teamid']))
		
		if all(m == '' for m in members):
			response = {'success': False, 'message': 'You cannot have a team with 0 members!'}
		elif not email:
			response = {'success': False, 'message': 'Please enter a valid email!'}
		elif len(repeat) > 0:
			response = {'success': False, 'message': 'That email address is used!'}
		else:
			profile = db_profile.objects.get(team=request.session['teamid'])
			
			if profile.members != members:
				profile.members=members
				profile.save()
			
			if team.email != email:
				team.email=email
				team.save()
			
			response = {'success': True, 'message': 'Basic information updated successfully!'}
	
	return HttpResponse(json.dumps(response), content_type="application/json")
	
def u_password(request):
	'''Updates password. Accepts post parameters [current], [new], [confirm]'''

	if (request.method != 'POST') or not all(x in request.POST for x in ['current', 'new', 'confirm']):
		return HttpResponse()
		
	if 'teamid' not in request.session:
		response = {'success': False, 'message': 'You must be logged in to view this resource.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	new = request.POST['new']
	confirm = request.POST['confirm']
	
	team = db_team.objects.get(id=request.session['teamid'])
	
	if not check_password(request.POST['current'], team.password):
		response = {'success': False, 'message': 'Your current password does not match our records.'}
	else:
		if len(new) < 6:
			response = {'success': False, 'message': 'Use a secure password at least 6 characters long!'}
		elif new != confirm:
			response = {'success': False, 'message': 'Passwords do not match!'}
		else:
			team.password = make_password(new)
			team.save()
			response = {'success': True, 'message': 'Password updated!'}
	
	return HttpResponse(json.dumps(response), content_type="application/json")

def pre_load(request):
	'''For internal calls only. Retrieves member names + email and returns a dict.'''
	
	try:
		team = db_team.objects.get(id=request.session['teamid'])
	except:
		return False
	else:
		email = team.email
		profile = db_profile.objects.get(team=team.id)
		members = profile.members
		m1 = members[0]
		m2 = members[1]
		m3 = members[2]
		m4 = members[3]
		
		return {'m1': m1, 'm2': m2, 'm3': m3, 'm4': m4, 'email': email}
			
		