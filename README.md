# CCTF Platform
This is a CTF platform built using Django and Materialize used in the CCTF 2015 competition. We wanted to create a unique platform that can accomodate both novice and veteran CTF players alike. The CCTF Platform tried many experimental things such as Interact Points, AJAX challenge loading system, and dynamic graphs. Most of them turned out nicely but some features still require significant polishing. Also, the platform lacked an integrated administrative system. We are starting work on improving the platform for next year!

### Prerequisites
The following prerequisites are needed for the platform to run.

1. Python 3 (latest version preferable).
2. Django ```pip install django```.
3. Psycopg2 ```pip install psycopg2```.
4. PostgreSQL (latest version preferable, 8.4 minimum).
5. Memcached (latest version preferable).
5. A deployment method (uwsgi preferable).

### Development
Development of the CCTF platform can be done using any IDE or Notepad++. [Koala](http://koala-app.com/) was used for SASS compilation and JavaScript minification. All JS and CSS files in the static folder are minified.

### Challenge Files
Challenges are made of three components: a descriptor, a grader, and an adder.

Descriptors are Python functions that return the data to be displayed for the challenge. Graders are Python functions that are used to determine the correct "flag" for each challenge. Each grader should return a tuple. The first item in the tuple should indicate whether the user's submission was correct. The second item should be a message to display back to the user. Adders are Python functions that add the challenge into the database. They contain the title, category, value, and type (if necessary).

All challenge files should contain three functions: ```def grade(flag)```, ```def description()```, and ```def add()```. They should be placed in the challenges folder (or whichever folder you choose in the config file). There should be one file per challenge. Challenge files can be named arbitrarily.

Example: Challenge 1

	python

     def grade(flag):
    	if flag == '{this_is_a_flag}':
    		return (True, 'Success!')
    	else:
    		return (False, 'You are a failure.')
    
    def description():
    	data = "<p>Are you ready for challenge 1?</p>"
    	return data
    	
    def add():
    	data = {
    		'title': 'Web 1',
    		'category': 2,
    		'value': 15,
    		'type': 0, # Optional. If 1, tells browser not to cache challenge.
    	}
    	
    return data


The file in this case should be named ```challenge_1.py```.

### Administration
Challenges can be automatically added using ```admin.py```. Simply run the following:
```
python -c "from admin import add_challenges; add_challenges()"
```

Other administrative tasks can be done by calling functions in ```admin.py```. This will be improved in the next version of the platform.

### Deployment
The preferable method for deploying the CCTF Platform if using [uwsgi](https://github.com/unbit/uwsgi). Other methods include ```mod_python```, ```gunicorn```, or the deprecated ```FastCGI``` (highly not recommended but possible).
