from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.db import models
from api.interact import get_ip
from api.latest import latest
from api.account import pre_load
from api.config import config

def home(request):
	if 'teamid' not in request.session:
		return render(request, 'home_out.html', latest())
		
	return render(request, 'home.html', latest())

def challenge(request):
	if 'teamid' not in request.session or not config.comp_started():
		return HttpResponseRedirect('/')

	return render(request, 'challenge.html') 
	
def scoreboard(request):
	return render(request, 'scoreboard.html')
	
def interact(request):
	if 'teamid' not in request.session or not config.comp_started():
		return HttpResponseRedirect('/')

	return render(request, 'interact.html', {'ip': get_ip(request)})
	
def stats(request):
	return render(request, 'stats.html')
	
def account(request):
	if 'teamid' not in request.session:
		return HttpResponseRedirect('/')

	return render(request, 'account.html', pre_load(request))
	
def login(request):
	if 'teamid' in request.session:
		return HttpResponseRedirect('/')
		
	return render(request, 'login.html')
	
def register(request):
	if 'teamid' in request.session:
		return HttpResponseRedirect('/')

	return render(request, 'register.html')
	
def forgot(request):
	if 'teamid' in request.session:
		return HttpResponseRedirect('/')
	
	return render(request, 'forgot.html')
	
def license(request):
	return render(request, 'license.html')
	
def irc(request):
	return render(request, 'irc.html')
	
def readme(request):
	return render(request, 'readme.html')
	
def handler500(request):
	return render(request, '500.html')
	
def handler404(request):
	return render(request, '404.html')
	
def handler403(request):
	return render(request, '403.html')
	
def handler400(request):
	return render(request, '400.html')