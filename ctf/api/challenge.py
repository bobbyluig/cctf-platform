from api.models import *
import json
from django.http import HttpResponse
from django.db import connection
from collections import OrderedDict
from api.config import config
from importlib import import_module
from django.core.cache import cache

def name_list(request):
	'''Returns the same as full_list without descriptions but with ids.'''
	
	if 'teamid' not in request.session:
		response = {'success': False, 'message': 'You must be logged in to view this resource.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	if not config.comp_started():
		response = {'success': False, 'message': 'Competition has not started!'}
		return HttpResponse(json.dumps(response), content_type="application/json")
		
	completed = cache.get('team_' + str(request.session['teamid']) + '_completed')
	
	if completed is None:
		cursor = connection.cursor()
		cursor.execute("SELECT profile.completed FROM profile WHERE profile.team = %s", [request.session['teamid']])
		completed = cursor.fetchone()[0]
		cache.set('team_' + str(request.session['teamid']) + '_completed', completed)
	
	challenges = cache.get('system_challenges')
	
	if challenges is None:
		cursor = connection.cursor()
		cursor.execute("SELECT categories.name, challenges.title, challenges.id, challenges.score, challenges.deactivated, challenges.solves, challenges.type FROM challenges INNER JOIN categories ON challenges.category = categories.id WHERE hidden != 1 ORDER BY categories.name ASC, challenges.score ASC, challenges.title ASC")
		
		if cursor.rowcount == 0:
			response = {'success': False, 'message': 'This is embarrassing. There are no challenges.'}
			return HttpResponse(json.dumps(response), content_type="application/json")
			
		challenges = cursor.fetchall()
		cache.set('system_challenges', challenges)
	
	response = OrderedDict({})
	
	for challenge in challenges:
		solved = 1 if int(challenge[2]) in completed else 0
	
		if challenge[0] in response:
			response[challenge[0]].append({'title': challenge[1], 'id': challenge[2], 'score': challenge[3], 'deactivated': challenge[4], 'solved': solved, 'solves': challenge[5], 'type': challenge[6]})
		else:
			response[challenge[0]] = []
			response[challenge[0]].append({'title': challenge[1], 'id': challenge[2], 'score': challenge[3], 'deactivated': challenge[4], 'solved': solved, 'solves': challenge[5], 'type': challenge[6]})

	return HttpResponse(json.dumps(response), content_type="application/json")
	
def get_challenge(request):
	'''Returns data for a specific challenge. Accepts get parameter [id]'''
	if 'id' not in request.GET:
		return HttpResponse()

	if 'teamid' not in request.session:
		response = {'success': False, 'message': 'You must be logged in to view this resource.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
		
	if not config.comp_started():
		response = {'success': False, 'message': 'Competition has not started!'}
		return HttpResponse(json.dumps(response), content_type="application/json")
		
	cache_solves = cache.get('challenge_solves_' + request.GET['id'])
	cache_info = cache.get('challenge_info_' + request.GET['id'])
		
	if cache_solves is None or cache_info is None:
		cursor = connection.cursor()
		cursor.execute("SELECT challenges.title, challenges.score, challenges.deactivated, challenges.file, challenges.solves FROM challenges WHERE challenges.id = %s AND challenges.hidden != 1", [request.GET['id']])
		result = cursor.fetchone()
		
		cache_solves = int(result[4])
		cache_info = {'title': result[0], 'score': result[1], 'deactivated': result[2], 'file': result[3], 'solves': result[4]}
		
		cache.set('challenge_solves_' + request.GET['id'], int(cache_solves))
		cache.set('challenge_info_' + request.GET['id'], cache_info)
	
	try:
		descriptor = cache_info['file'][:-3]
		print(config.CHALLENGE_FOLDER)
		description = getattr(import_module('%s.%s' % (config.CHALLENGE_FOLDER, descriptor)), 'description')
		description = description()
	except:
		response = {'success': False, 'message': 'The challenge does not exist.'}
	else:
		response = {'description': description, 'solves': cache_solves}
	
	return HttpResponse(json.dumps(response), content_type="application/json")