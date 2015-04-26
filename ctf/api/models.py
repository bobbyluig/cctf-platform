from django.db import models
from django.contrib.postgres.fields import ArrayField

class db_attacks(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.IntegerField()
	challenge = models.IntegerField()
	time = models.IntegerField()
	additional = models.IntegerField()
	ip_earned = models.IntegerField()
	
	class Meta:
		db_table = 'attacks'
		unique_together = ('team', 'challenge')

class db_categories(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.TextField()
	
	class Meta:
		db_table= 'categories'
	
class db_challenges(models.Model):
	id = models.AutoField(primary_key=True)
	title = models.TextField()
	score = models.IntegerField()
	file = models.TextField()
	category = models.IntegerField()
	type = models.IntegerField()
	solves = models.IntegerField()
	deactivated = models.IntegerField()
	hidden = models.IntegerField()
	
	class Meta:
		db_table = 'challenges'
	
class db_interact(models.Model):
	id = models.AutoField(primary_key=True)
	origin = models.IntegerField() 
	destination = models.IntegerField()
	success = models.IntegerField()
	value = models.IntegerField()
	bp_lost = models.IntegerField()
	time = models.IntegerField()
	
	class Meta:
		db_table = 'interact'

class db_team(models.Model):
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=50, unique=True)
	registration = models.IntegerField()
	local = models.IntegerField()
	school = models.CharField(max_length=100)
	password = models.TextField()
	email = models.EmailField()
	lastlogin = models.IntegerField()
	
	class Meta:
		db_table = 'team'
		
class db_profile(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.IntegerField(unique=True)
	members = ArrayField(models.TextField(), blank=True)
	score = models.IntegerField()
	ip = models.IntegerField()
	fails = models.IntegerField()
	completed = ArrayField(models.IntegerField(), blank=True)
	last_solve_time = models.IntegerField()
	track = models.GenericIPAddressField()
	
	class Meta:
		db_table = 'profile'

class db_system(models.Model):
	id = models.AutoField(primary_key=True)
	text = models.TextField()
	time = models.DateTimeField(auto_now_add=True)
	
	class Meta:
		db_table = 'system'
		
class db_fails(models.Model):
	id = models.AutoField(primary_key=True)
	team = models.IntegerField()
	challenge = models.IntegerField()
	flag = models.CharField(max_length=100)
	track = models.GenericIPAddressField()
	time = models.IntegerField()
	
	class Meta:
		db_table = 'fails'