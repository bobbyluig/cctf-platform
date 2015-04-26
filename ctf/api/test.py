from api.models import *
from django.http import HttpResponse
from django.contrib.auth.hashers import *
import json, names, random, time
import numpy as np
from django.db import connection
from api.config import config
from api.account import insert_team
from api.attack import insert_attack, update_cache

def test(request):
	for team in range(1, 64):
		update_cache(team)
		
	return HttpResponse('hello')

def test1(request):
	for i in range(1, 70):
		category = random.randint(1, 6)
		title = "Challenge " + str(i)
		score = max(int(np.random.normal(300, 200, 1)[0]), 0)
		description = "<p>This is challenge %d.</p>" % (i)
		
		challenge = db_challenges(title=title, score=score, file='web_f.py', category=category, deactivated=0, hidden=0)
		challenge.save()
		
	return HttpRespone('hello')

def submit_flag(challenge, teamid):
		
	cursor = connection.cursor()
	cursor.execute("SELECT challenges.title, challenges.score, challenges.deactivated, challenges.file, challenges.solves FROM challenges WHERE challenges.id = %s AND challenges.hidden != 1", [challenge])
	result = cursor.fetchone()

	if result[4] == 0:
		bonus = 3 if 3 > int(result[1]*0.03) else int(result[1]*0.03)
	elif result[4] == 1:
		bonus = 2 if 2 > int(result[1]*0.02) else int(result[1]*0.02)
	elif result[4] == 2:
		bonus = 1 if 1 > int(result[1]*0.01) else int(result[1]*0.01)
	else:
		bonus = 0
	
	ip_percent = config.IP_PERCENT + random.uniform(-0.05, 0.05)
	ip = 2 if 2 > result[1] * ip_percent else result[1] * ip_percent
	
	attack = db_attacks(team=teamid, challenge=challenge, additional=bonus, ip_earned=ip, time=time.time())
	attack.save()
	
def test2(request):
	for i in range(1, 500):
		num = max(int(np.random.normal(35, 30, 1)[0]), 0)
		if num >= 70:
			num = 69
		completed = random.sample(set(range(1,70)), num)
		for a in completed:
			submit_flag(a, i)
			