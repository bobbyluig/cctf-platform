from api.models import *
import json, os, random, time
from django.http import HttpResponse
from django.db import connection, transaction, IntegrityError
from django.db.models import F, Sum
from api.config import config
from django.core.cache import cache

def is_int(s):
    try:
        int(s)
        return True
    except:
        return False

@transaction.atomic
def stop_the_race(id, v_id, value, bp_loss, success):
	attack = db_interact(origin=id, destination=v_id, value=value, bp_lost=bp_loss, success=success, time=time.time())
	attack.save()

	# Attacker
	try:
		profile = db_profile.objects.select_for_update(nowait=True).get(team=id)
	except:
		raise IntegrityError('Race condition detected.')
			
	cursor = connection.cursor()
	cursor.execute('SELECT a + b, c + d + e - b FROM (SELECT COALESCE( SUM( challenges.score ), 0 ) + COALESCE( SUM( attacks.additional ), 0 ) AS a, COALESCE( SUM( attacks.ip_earned ), 0 ) AS c FROM challenges, attacks WHERE attacks.team = %s AND attacks.challenge = challenges.id) first, (SELECT COALESCE( SUM( interact.bp_lost ), 0 ) AS b, COALESCE( SUM( interact.value ), 0 ) AS d FROM interact WHERE interact.destination = %s AND interact.success = 1) second, (SELECT COALESCE( SUM( interact.value ), 0) AS e FROM interact WHERE interact.origin = %s) third', [id, id, id])
	result = cursor.fetchone()		
	
	ip = result[1]
	
	if ip < 0:
		raise IntegrityError('Oops.')
	
	profile.ip = ip
	profile.score = result[0]
	profile.save()

	if success == 1:
		try:
			profile = db_profile.objects.select_for_update(nowait=True).get(team=v_id)
		except:
			raise IntegrityError('Race condition detected.')
				
		cursor = connection.cursor()
		cursor.execute('SELECT a + b, c + d + e - b FROM (SELECT COALESCE( SUM( challenges.score ), 0 ) + COALESCE( SUM( attacks.additional ), 0 ) AS a, COALESCE( SUM( attacks.ip_earned ), 0 ) AS c FROM challenges, attacks WHERE attacks.team = %s AND attacks.challenge = challenges.id) first, (SELECT COALESCE( SUM( interact.bp_lost ), 0 ) AS b, COALESCE( SUM( interact.value ), 0 ) AS d FROM interact WHERE interact.destination = %s AND interact.success = 1) second, (SELECT COALESCE( SUM( interact.value ), 0) AS e FROM interact WHERE interact.origin = %s) third', [v_id, v_id, v_id])
		result = cursor.fetchone()

		v_score = result[0]
		
		if v_score <= config.MIN_INTERACT_SCORE:
			raise IntegrityError('Oops.')
		
		profile.score = v_score
		profile.ip = result[1]
		profile.save()
		
		return [ip, v_score]
	else:
		return [ip]
		
def interact(request):
	'''Handles team interactions. Accepts post parameter [team] and [value].'''
	if (request.method != 'POST') or not all(x in request.POST for x in ['team', 'value']):
		return HttpResponse()
		
	if 'teamid' not in request.session:
		response = {'success': False, 'message': 'You must be logged in to view this resource.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
				
	if not config.comp_started():
		response = {'success': False, 'message': 'Competition has not started!'}
		return HttpResponse(json.dumps(response), content_type="application/json")
		
	if config.comp_ended():
		response = {'success': False, 'message': 'Competition has ended!'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	try:
		team = db_team.objects.get(name=request.POST['team'])
		v_id = team.id
		v_name = team.name
	except:
		response = {'success': False, 'message': 'The team you have entered does not exist.'}
	else:
		cursor = connection.cursor()
		cursor.execute("SELECT profile.score, profile.ip, (SELECT COALESCE(SUM(interact.value) * -1, 0) FROM interact WHERE interact.destination = %s AND interact.success = 1) AS v_lost, (SELECT SUM(ip) FROM profile) AS total_ip FROM profile WHERE profile.team = %s", [v_id, v_id]) # Not important. Use cache.
		result = cursor.fetchone()
		
		value = int(request.POST['value']) if is_int(request.POST['value']) else False
		v_score = int(result[0])
		v_ip = int(result[1])
		v_lost = int(result[2])
		total_ip = int(result[3])
		
		if v_id == request.session['teamid']:
			response = {'success': False, 'message': 'It is highly recommended that you avoid doing this to your own team.'}
		elif not value:
			response = {'success': False, 'message': 'Value must be an integer.'}
		elif v_score <= config.MIN_INTERACT_SCORE:
			response = {'success': False, 'message': 'Please attack a more affluent team.'}
		elif value < 1:
			response = {'success': False, 'message': 'The minimum attack value is 1 point.'}
		elif v_score-value <= config.MIN_INTERACT_SCORE:
			response = {'success': False, 'message': "Please try to keep the team's base score above 100 points."}
		elif len(db_profile.objects.filter(team=request.session['teamid'], ip__gte=value)) == 0:
			response = {'success': False, 'message': 'You are too poor to perform that action.'}
		else:
			luck = random.random()
			bp_loss = 0
			value *= -1
			SUCCESS_RATE = config.SUCCESS_RATE
			MIN_RATE = config.MIN_RATE + (v_ip / total_ip)

			# Magical algorithm of r = SUCCESS_RATE - (lost / (IP_PERCENT * score) * SUCCESS_RATE) for r >= MIN_RATE
			r = SUCCESS_RATE - (v_lost / (config.IP_PERCENT * v_score) * SUCCESS_RATE)
			r = r if r > MIN_RATE else MIN_RATE		
			
			if luck >= r:
				success = 0
			else:
				success = 1
				
				# Set new data using interact point buffer.
				new_score = v_score if v_ip+value >= 0 else v_score+v_ip+value
				# new_ip = v_ip+value if v_ip+value >= 0 else 0
				bp_loss = (v_score - new_score) * -1
				
			# Handle race conditions.
			try:
				result = stop_the_race(request.session['teamid'], v_id, value, bp_loss, success)
			except IntegrityError:
				response = {'success': False, 'message': 'Slow down, grasshopper.'}
			else:
				if success == 0:
					response = {'success': True, 'message': "Attack failed!", 'ip': result[0]}
				else:
					message = '<span>%s</span>&nbsp;<span class="indigo-text text-accent-2">(%d)</span>' % ("Attack successful!", result[1])
					response = {'success': True, 'message': message, 'ip': result[0]}
					
					# Invalidate cache.
					cache.set('system_scoreboard', '', 0)
				
				# Invalidate cache.
				cache.set('team_' + str(request.session['teamid']) + '_stats', '', 0)
				cache.set('team_' + str(v_id) + '_stats', '', 0)
				cache.set('system_latest_interacts', '', 0)

	return HttpResponse(json.dumps(response), content_type="application/json")
	
def get_ip(request):
	'''Returns the number of interact points. Not for external calls.'''
	profile = db_profile.objects.get(team=request.session['teamid'])
	return profile.ip
	
def list_teams(request):
	if 'teamid' not in request.session or 'q' not in request.GET:
		response = {'success': False, 'message': 'You must be logged in to view this resource.'}
		return HttpResponse()
		
	team = db_team.objects.filter(name__contains=request.GET['q'])
	
	response = [t.name for t in team]

	return HttpResponse(json.dumps(response), content_type="application/json")
		