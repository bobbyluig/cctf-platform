import json
from django.http import HttpResponse
from django.db import connection
from django.utils.html import format_html
from django.core.cache import cache

def latest():
	'''Returns latest system message, submission, and interaction.'''
	
	system = cache.get('system_latest_messages')
	
	if system is None:
		cursor = connection.cursor()
		cursor.execute('SELECT * FROM system ORDER BY id DESC LIMIT 50')
		system = []
		for data in cursor.fetchall():
			system.append('%s > %s' % (str(data[2]).split()[0], data[1]))
		if len(system) == 0:
			system = ['No system messages.']
			
		cache.set('system_latest_messages', system)
	
	submit = cache.get('system_latest_attacks')
	
	if submit is None:
		cursor = connection.cursor()
		cursor.execute('SELECT attacks.id, team.name, challenges.title FROM attacks JOIN team ON attacks.team = team.id JOIN challenges ON attacks.challenge = challenges.id ORDER BY attacks.id DESC LIMIT 5')
		submit = []
		for data in cursor.fetchall():
			submit.append(format_html(u'<b>{0}</b> recently completed <b>{1}</b>.', data[1], data[2]))
		if len(submit) == 0:
			submit = ['No flag submissions.']
		
		cache.set('system_latest_attacks', submit)
	
	interact = cache.get('system_latest_interacts')
	
	if interact is None:
		cursor = connection.cursor()
		cursor.execute('SELECT origin, destination, success, value * -1 FROM (SELECT interact.id, team.name AS origin FROM team JOIN interact ON interact.origin = team.id ORDER BY interact.id DESC LIMIT 5) a JOIN (SELECT interact.id, interact.success, interact.value, team.name AS destination FROM team JOIN interact ON interact.destination = team.id ORDER BY interact.id DESC LIMIT 5) b ON a.id = b.id')
		interact = []
		for data in cursor.fetchall():
			if data[2] == 1:
				interact.append(format_html('<b>{0}</b> successfully used <b>{1}</b> interact point(s) on <b>{2}</b>.', data[0], data[3], data[1]))
			elif data[2] == 0:
				interact.append(format_html('<b>{0}</b> failed to use <b>{1}</b> interact point(s) on <b>{2}</b>.', data[0], data[3], data[1]))		
		if len(interact) == 0:
			interact = ['No interactions.']
		
		cache.set('system_latest_interacts', interact)

	return {'system': system, 'submit': submit, 'interact': interact}
			