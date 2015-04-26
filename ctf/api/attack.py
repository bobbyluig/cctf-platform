from api.models import *
import json, hashlib, random, time
from datetime import datetime
from django.http import HttpResponse
from django.db import connection, transaction
from api.config import config
from django.db.models import F
from importlib import import_module
from django.core.cache import cache

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@transaction.atomic
def update_cache(id):
	'''Updates profile cache specific to current file. 99.99% guarantee to be safe from race conditions. Pessimistic locking! :D'''
	profile = db_profile.objects.select_for_update().get(team=id)
	
	cursor = connection.cursor()
	cursor.execute('SELECT a + b, c + d + e - b, completed, last FROM (SELECT COALESCE( SUM( challenges.score ), 0 ) + COALESCE( SUM( attacks.additional ), 0 ) AS a, COALESCE( SUM( attacks.ip_earned ), 0 ) AS c, array_agg( attacks.challenge ) as completed, max(attacks.time) AS last FROM challenges, attacks WHERE attacks.team = %s AND attacks.challenge = challenges.id) first, (SELECT COALESCE( SUM( interact.bp_lost ), 0 ) AS b, COALESCE( SUM( interact.value ), 0 ) AS d FROM interact WHERE interact.destination = %s AND interact.success = 1) second, (SELECT COALESCE( SUM( interact.value ), 0) AS e FROM interact WHERE interact.origin = %s) third', [id, id, id])
	result = cursor.fetchone()
	
	profile.score = result[0]
	profile.ip = result[1]
	profile.last_solve_time = result[3]
	profile.completed = result[2]
	profile.save()
	
@transaction.atomic	
def insert_attack(team, challenge, bonus, ip):
	'''
	Inserts attack row and returns false if challenge is already solved.
	It also increments solve cache. This prevents all flag submission race conditions.
	Note that unique_together = ('team', 'challenge') must be specified in table meta for concurrency protection.
	'''
	
	db_challenges.objects.filter(id=challenge).update(solves=F('solves')+1) # Prevent race conditions
	
	try:
		attack = db_attacks(team=team, challenge=challenge, additional=bonus, ip_earned=ip, time=time.time())
		attack.save()
		
		# Invalidate cache.
		cache.set('system_scoreboard', '', 0)
		cache.set('system_challenges', '', 0)
		cache.set('system_latest_attacks', '', 0)
		cache.set('team_' + str(team) + '_stats', '', 0)
		cache.set('team_' + str(team) + '_completed', '', 0)
		cache.incr('challenge_solves_' + str(challenge))
		
		return True
	except:
		return False
	
def submit_flag(request):
	'''Handles flag submissions. Accepts post parameter [flag]'''
	if (request.method != 'POST') or not all(x in request.POST for x in ['id', 'flag']):
		return HttpResponse()
		
	if 'teamid' not in request.session:
		response = {'success': False, 'message': 'You must be logged in to view this resource.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
		
	if not config.comp_started():
		response = {'success': False, 'message': 'Competition has not started!'}
		return HttpResponse(json.dumps(response), content_type="application/json")
		
	# Cache exists.
		
	cache_solves = cache.get('challenge_solves_' + request.POST['id'])
	cache_info = cache.get('challenge_info_' + request.POST['id'])
		
	if cache_solves is None or cache_info is None:
		cursor = connection.cursor()
		cursor.execute("SELECT challenges.title, challenges.score, challenges.deactivated, challenges.file, challenges.solves FROM challenges WHERE challenges.id = %s AND challenges.hidden != 1", [request.POST['id']])
		result = cursor.fetchone()
		
		if result is None:
			response = {'success': False, 'message': 'The challenge does not exist.'}
			return HttpResponse(json.dumps(response), content_type="application/json")
		
		cache_solves = int(result[4])
		cache_info = {'title': result[0], 'score': int(result[1]), 'deactivated': result[2], 'file': result[3], 'solves': result[4]}
		
		cache.set('challenge_solves_' + request.POST['id'], cache_solves)
		cache.set('challenge_info_' + request.POST['id'], cache_info)

	if cache_solves == 0:
		bonus = 3 if 3 > round(cache_info['score']*0.03) else round(cache_info['score']*0.03)
	elif cache_solves == 1:
		bonus = 2 if 2 > round(cache_info['score']*0.02) else round(cache_info['score']*0.02)
	elif cache_solves == 2:
		bonus = 1 if 1 > round(cache_info['score']*0.01) else round(cache_info['score']*0.01)
	else:
		bonus = 0
	
	ip_percent = config.IP_PERCENT + random.uniform(-0.05, 0.05)
	ip = 2 if 2 > round(cache_info['score'] * ip_percent) else round(cache_info['score'] * ip_percent)

	try:
		grader = cache_info['file'][:-3]
		grade = getattr(import_module('%s.%s' % (config.CHALLENGE_FOLDER, grader)), 'grade')
		(correct, mock) = grade(request.POST['flag'][:100]) # Flags should not be over 100 characters.
	except:
		response = {'success': False, 'message': 'Error.'}
	else:
		if not correct:
			if not config.comp_ended():
				flag = request.POST['flag'][:100] # Don't have them waste space in the database.
				fails = db_fails(team=request.session['teamid'], flag=flag, challenge=request.POST['id'] ,track=get_client_ip(request), time=time.time())
				fails.save()
				
				db_profile.objects.filter(team=request.session['teamid']).update(fails=F('fails')+1)
				
				# Invalidate cache.
				cache.set('team_' + str(request.session['teamid']) + '_stats', '', 0)
				
			response = {'success': False, 'message': mock}
		elif config.comp_ended():
			response = {'success': False, 'message': 'Correct flag. However, competition has ended.'}
		elif cache_info['deactivated'] == 1:
			response = {'success': False, 'message': 'Correct flag. However, the challenge is disabled.'}
		elif not insert_attack(request.session['teamid'], request.POST['id'], bonus, ip):
			response = {'success': False, 'message': 'Correct flag. However, you have already completed this challenge.'}
		else:
			message = '<span>%s</span>&nbsp;<span class="indigo-text text-accent-2">(+%d, +%d)</span>' % (mock, cache_info['score'] + bonus, ip)
			response = {'success': True, 'message': message, 'solves': cache_solves + 1}
			
			update_cache(request.session['teamid'])
		
	return HttpResponse(json.dumps(response), content_type="application/json")