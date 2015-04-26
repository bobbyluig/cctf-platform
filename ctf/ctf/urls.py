from django.conf.urls import url
from ctf import views
from api import stats, challenge, attack, interact, account, auth, test

handler500 = views.handler500
handler404 = views.handler404
handler403 = views.handler403
handler400 = views.handler400

urlpatterns = [
    # Examples:
    # url(r'^$', 'ctf.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	# License
	url(r'^license/$', views.license),
	
	# Readme
	url(r'^readme/$', views.readme),
	
	# Home
	url(r'^$', views.home, name='home'),
	url(r'^api/home/graph/$', stats.home_graph),
	
	# IRC
	url(r'^irc/$', views.irc),
	
	# Challenges
	url(r'^challenges/$', views.challenge),
	url(r'^api/challenges/get_challenge/$', challenge.get_challenge),
	url(r'^api/challenges/name_list/$', challenge.name_list),
	url(r'^api/challenges/submit/$', attack.submit_flag),
	
	# Scoreboard
	url(r'^scoreboard/$', views.scoreboard),
	url(r'^api/scoreboard/$', stats.scoreboard),
	
	# Interact
	url(r'^interact/$', views.interact),
	url(r'^api/interact/list_teams/$', interact.list_teams),
	url(r'^api/interact/attack/$', interact.interact),
	
	# Account
	url(r'^account/$', views.account),
	url(r'^api/account/u_basic/$', account.u_basic),
	url(r'^api/account/u_password/$', account.u_password),
	# Logout
	url(r'^api/logout/$', auth.logout),
	
	# Login
	url(r'^login/$', views.login),
	url(r'^api/login/$', auth.login),
	
	# Register
	url(r'^register/$', views.register),
	
	# Forgot Password
	url(r'^forgot/$', views.forgot),
	
	# Team Stats
	url(r'^team/', views.stats),
	url(r'^api/team/stats/', stats.team_stats),
	url(r'^api/team/graph/', stats.graph),
	
	# Register
	url(r'^api/register/$', account.create_account),
	
	# Forgot Password
	url(r'^api/forgot/$', auth.forgot),
	
	# url(r'^api/contact/$', 'api.contact.contact'),
]