import pkgutil, os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ctf.settings")

from django.db import connection
from api.attack import update_cache
from api.config import config
from importlib import import_module
from api.models import *
from django.core.cache import cache
import json, time

def flush():
	cursor = connection.cursor()
	cursor.execute("SELECT array_agg(id) FROM team")
	teams = cursor.fetchone()[0]

	for team in teams:
		print(team)
		try:
			update_cache(team)
		except:
			pass
			
	print('Success!')

def add_message(message):
	db = db_system(text=message)
	db.save()
	cache.set('system_latest_messages', '', 0)
	
	print('Success!')
	
def check_cache():
	cache.set('test_cache', '')
	if cache.get('test_cache') is None:
		print('Memcached is not working!')
	else:
		cache.set('test_cache', '', 0)
		print('Memcached is working!')
	
def clear_cache():	
	cache.clear()
	
	print('Success!')
	
def cache_test():
	cache.set('test_cache', 'abc')
	start = time.time()
	for i in range(0, 10000):
		cache.get('test_cache')
	print(time.time() - start)
	start = time.time()
	for i in range(0, 10000):
		cache.set('test_cache', 'aaaaaaaaaaaaaaaaaaa')
	print(time.time() - start)
	
		
def add_challenges():	
	cursor = connection.cursor()
	cursor.execute("TRUNCATE challenges RESTART IDENTITY")
	challenges = [name for _, name, _ in pkgutil.iter_modules([config.CHALLENGE_FOLDER])]
	for challenge in challenges:
		try:
			add = getattr(import_module('%s.%s' % (config.CHALLENGE_FOLDER, challenge)), 'add')
			data = add()
			
			if 'type' not in data:
				type = 0
			else:
				type = data['type']
				
			db = db_challenges(title=data['title'], score=data['score'], file=challenge + '.py', category=data['category'], solves=0, type=type, deactivated=0, hidden=0)
			db.save()
		except:
			pass
		
	print('Success!')
	
if __name__ == '__main__':
	while True:
		data = input('Function: ')
		eval(data)