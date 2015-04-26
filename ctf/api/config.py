import time

class config:
	IP_PERCENT = 0.20 # Base IP percent +- 5% for completed challenges.
	SUCCESS_RATE = 0.50 # Max success rate for Interact.
	MIN_INTERACT_SCORE = 100 # Minimum score for interact.
	MIN_RATE = 0.005 # Minimum success rate for Interact.
	SYSTEM_EMAIL = 'CCTF System <system@camsctf.com>' # System alias.
	NUM_POINTS = 20 # Number of points to plot.
	START_TIME = 1429315200 # Competition start time.
	END_TIME = 1429938060 # Competition end time.
	CHALLENGE_FOLDER = 'challenges' # Challenges folder
	GCAPTCHA_SECRET = '' # reCAPTCHA Secret

	@staticmethod
	def comp_started():
		if time.time() >= config.START_TIME:
			return True
		else:
			return False
		
	@staticmethod
	def comp_ended():
		if time.time() >= config.END_TIME:
			return True
		else:
			return False