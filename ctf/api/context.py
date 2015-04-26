import time
from api.config import config

def comp_started(request):
	return {'comp_started': time.time() >= config.START_TIME}