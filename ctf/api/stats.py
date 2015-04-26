from api.models import db_team
import json, time, math
from collections import OrderedDict
from django.http import HttpResponse
from django.db import connection
from api.config import config
from django.core.cache import cache
from django.views.decorators.cache import cache_page

def team_stats(request):
	if not config.comp_started():
		response = {'success': False, 'message': 'Competition has not started! There is nothing to show.'}
		return HttpResponse(json.dumps(response), content_type="application/json")

	# Cache exists.
	team_cache = cache.get('team_' + request.GET['t'] + '_stats')

	if team_cache is not None:
		return HttpResponse(json.dumps(team_cache), content_type="application/json")
		
	# Non cache.
	try:
		id = request.GET['t']
		team = db_team.objects.get(id=id)
		name = team.name
	except:
		response = {'success': False, 'message': 'The team you have requested does not exist.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	cursor = connection.cursor()
	cursor.execute( 'SELECT profile.score, ' #Score
					'profile.fails, ' #Fails
					'profile.completed, ' #Completed
					'(SELECT COALESCE(SUM(attacks.additional), 0) FROM attacks WHERE attacks.team = %s) AS bonus, ' #Bonus
					'(SELECT COALESCE(SUM(interact.value) * -1, 0) FROM interact WHERE interact.destination = %s AND interact.success = 1) AS loss, ' #Total buffer+points lost
					'(SELECT COALESCE((SUM(interact.value) * -1), 0) FROM interact WHERE interact.origin = %s) AS usedip, ' #Used interact points
					'(SELECT COALESCE((SUM(interact.value) * -1), 0) FROM interact WHERE interact.origin = %s AND interact.success = 1) AS success ' #Successful interact points
					'FROM profile WHERE profile.team = %s'
					, [id, id, id, id, id])
	result = cursor.fetchone()

	score = int(result[0])
	fails = int(result[1])
	completed = result[2]
	bonus = int(result[3])
	lost = int(result[4])
	usedip = int(result[5])
	success = int(result[6])
	fail = usedip-success
	
	if score == 0:
		response = {'success': False, 'message': 'This is a boring team. There are no statistics to show.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	# Cache exists.
	challenges_cache = cache.get('system_challenges')
	
	if challenges_cache is None:
		cursor = connection.cursor()
		cursor.execute("SELECT categories.name, challenges.title, challenges.id, challenges.score, challenges.deactivated, challenges.solves, challenges.type FROM challenges INNER JOIN categories ON challenges.category = categories.id WHERE hidden != 1 ORDER BY categories.name ASC, challenges.score ASC, challenges.title ASC")
			
		challenges_cache = cursor.fetchall()
		cache.set('system_challenges', challenges_cache)
	
	response = OrderedDict({})
	
	challenges = OrderedDict({})
	for challenge in challenges_cache:
		solved = 1 if int(challenge[2]) in completed else 0
	
		if challenge[0] in challenges:
			challenges[challenge[0]].append({'title': challenge[1], 'score': challenge[3], 'deactivated': challenge[4], 'solved': solved})
		else:
			challenges[challenge[0]] = []
			challenges[challenge[0]].append({'title': challenge[1], 'score': challenge[3], 'deactivated': challenge[4], 'solved': solved})
	
	destination = []
	#cursor = connection.cursor()
	cursor.execute('SELECT team.id, team.name, (SELECT COALESCE((SUM(interact.value) * -1), 0) FROM interact WHERE interact.destination = %s AND interact.success = 1 AND interact.origin = team.id), (SELECT COALESCE((SUM(interact.value) * -1), 0) FROM interact WHERE interact.destination = %s AND interact.origin = team.id) AS total FROM team ORDER BY 3 DESC, team.name ASC', [id, id]) # Attacked by
	for row in cursor.fetchall():
		if int(row[3]) != 0:
			destination.append([row[1], int(row[2]), int(row[3])])
	
	origin = []
	#cursor = connection.cursor()
	cursor.execute('SELECT team.id, team.name, (SELECT COALESCE((SUM(interact.value) * -1), 0) FROM interact WHERE interact.destination = team.id AND interact.success = 1 AND interact.origin = %s), (SELECT COALESCE((SUM(interact.value) * -1), 0) FROM interact WHERE interact.destination = team.id AND interact.origin = %s) AS total FROM team ORDER BY 3 DESC, team.name ASC', [id, id])
	for row in cursor.fetchall():
		if int(row[3]) != 0:
			origin.append([row[1], int(row[2]), int(row[3])])
	
	response = {'score': score, 'fails': fails, 'bonus': bonus, 'lost': lost, 'usedip': usedip, 'success': success, 'fail': fail, 'challenges': challenges, 'origin': origin, 'destination': destination, 'team': name}
	cache.set('team_' + id + '_stats', response)
	
	return HttpResponse(json.dumps(response), content_type="application/json")
	
@cache_page(60)
def graph(request):
	'''Returns points to plot. Accepts get parameter [t]. Returns dict.'''
	if not config.comp_started():
		response = {'success': False, 'message': 'Competition has not started!'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	NUM_POINTS = config.NUM_POINTS

	try:
		id = request.GET['t']
		team = db_team.objects.get(id=id)
		team_name = team.name
	except:
		response = {'success': False, 'message': 'Team does not exist.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
		
	cursor = connection.cursor()
	cursor.execute('SELECT time FROM attacks WHERE attacks.team = %s ORDER BY attacks.time ASC LIMIT 1', [id])
	data = cursor.fetchone()
	
	if not data:
		response = {'success': False, 'message': 'Sorry, no data to show.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	else:
		start = int(data[0])
		current = int(time.time()) 
		current = current if current < config.END_TIME else config.END_TIME
	
	step = math.ceil((current - start) / (NUM_POINTS - 1))
	
	base_score = []
	used_ip = []
	successful_ip = []
	total_lost = []
	total_attempted = []
	
	for i in range(0, NUM_POINTS):
		cursor = connection.cursor()
		
		epoch = start + i*step
		
		cursor.execute(	'SELECT a + b, c, d, e, f FROM '
						'(SELECT COALESCE( SUM( challenges.score ), 0 ) + COALESCE( SUM( attacks.additional ), 0 ) AS a FROM challenges, attacks WHERE attacks.team = %s AND attacks.challenge = challenges.id AND attacks.time <= %s) first, '
						'(SELECT COALESCE( SUM( interact.bp_lost ), 0 ) AS b, COALESCE( SUM( interact.value ), 0 ) AS c FROM interact WHERE interact.destination = %s AND interact.success = 1 AND interact.time <= %s) second, '
						'(SELECT COALESCE( SUM( interact.value ), 0 ) AS d FROM interact WHERE interact.destination = %s AND interact.time <= %s) third, '
						'(SELECT COALESCE( SUM( interact.value ), 0 ) AS e FROM interact WHERE interact.origin = %s AND interact.success = 1 AND interact.time <= %s) fourth, '
						'(SELECT COALESCE( SUM( interact.value ), 0 ) AS f FROM interact WHERE interact.origin = %s AND interact.time <= %s) fifth ', 
						[id, epoch, id, epoch, id, epoch, id, epoch, id, epoch] )
		data = cursor.fetchone()
		
		base_score.append(int(data[0]))
		used_ip.append(int(data[4]) * -1)
		successful_ip.append(int(data[3]) * -1)
		total_lost.append(int(data[1]) * -1)
		total_attempted.append(int(data[2]) * -1)
		
	response = {'name': team_name, 'start': start, 'interval': step, 'base_score': base_score, 'used_ip': used_ip, 'successful_ip': successful_ip, 'total_lost': total_lost, 'total_attempted': total_attempted}
	return HttpResponse(json.dumps(response), content_type="application/json")
	
@cache_page(60)
def home_graph(request):
	'''Returns points to plot. Returns dict.'''
	if not config.comp_started():
		response = {'success': False, 'message': 'Competition has not started! There is nothing to show.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	
	NUM_POINTS = config.NUM_POINTS
		
	cursor = connection.cursor()
	cursor.execute('SELECT time FROM attacks ORDER BY attacks.time ASC LIMIT 1')
	data = cursor.fetchone()
	
	if not data:
		response = {'success': False, 'message': 'Sorry, no data to show.'}
		return HttpResponse(json.dumps(response), content_type="application/json")
	else:
		start = int(data[0])
		current = int(time.time()) 
		current = current if current < config.END_TIME else config.END_TIME
	
	step = math.ceil((current - start) / (NUM_POINTS - 1))

	total_score = []
	total_ip = []
	successful_ip = []
	
	for i in range(0, NUM_POINTS):
		cursor = connection.cursor()
		
		epoch = start + i*step
		
		cursor.execute(	'SELECT a, b, c FROM '
						'(SELECT COALESCE( SUM( challenges.score ), 0 ) + COALESCE( SUM( attacks.additional ), 0 ) AS a FROM challenges, attacks WHERE attacks.challenge = challenges.id AND attacks.time <= %s) first, '
						'(SELECT COALESCE( SUM( interact.value ), 0 ) AS b FROM interact WHERE interact.success = 1 AND interact.time <= %s) second, '
						'(SELECT COALESCE( SUM( interact.value ), 0 ) AS c FROM interact WHERE interact.time <= %s) third',
						[epoch, epoch, epoch])
		data = cursor.fetchone()

		total_score.append(int(data[0]))
		total_ip.append(int(data[2]) * -1)
		successful_ip.append(int(data[1]) * -1)
	
	response = {'start': start, 'interval': step, 'total_score': total_score, 'total_ip': total_ip, 'successful_ip': successful_ip}
	return HttpResponse(json.dumps(response), content_type="application/json")	

def scoreboard(request):
	'''Returns Scoreboard information'''
	system_scoreboard = cache.get('system_scoreboard')
	
	# If cache exists.
	if system_scoreboard is not None:
		if 'teamid' in request.session:
			system_scoreboard.append(request.session['teamid'])
		else:
			system_scoreboard.append(-1)
			
		return HttpResponse(json.dumps(system_scoreboard), content_type="application/json")
		
	# Non cache.
	cursor = connection.cursor()
	cursor.execute("SELECT team.id, team.name, team.school, profile.score, profile.last_solve_time FROM team INNER JOIN profile ON profile.team = team.id ORDER BY profile.score DESC, profile.last_solve_time ASC,  team.name ASC")
	
	rank = 0	
	response = []
	for row in cursor.fetchall():
		rank += 1
		response.append({'team': row[1], 'school': row[2], 'score': row[3], 'id': row[0], 'rank': rank})
		
	cache.set('system_scoreboard', response)
	
	if 'teamid' in request.session:
		response.append(request.session['teamid'])
	else:
		response.append(-1)

	return HttpResponse(json.dumps(response), content_type="application/json")