PRE-REQUISITS
	Python 3.9
	Python modules:
		sched
		time
		datatime
		logging
		json
		copy
		flask
		requests
		uk_covid19
		pyttsx3
SETUP
	(1) CREATE A DIRECTORY
	Create a directory which will host the server.

	(2) SETTING UP THE FILE STRUCTURE
	You need to create a folder in your directory and name it "static".
	You need to create a folder in your "static" folder and name it "images"
	You need to create a folder in your directory and name it "templates"

	directory
	    |- static
	    |   \ images
	    \- templates

	(3) SETTING UP THE FILES
	Put "setup.py" into your directory.
	Put "main.py" into your directory.
	Put your html template into the templates directory and name it
		template.html
		//html template provided separately by Matt Collinson.
	Put a "image.jpg" into your "images" folder. This will be an image
		welcoming you to the alarm clock.
	Put a "favicon.png" into your "images" folder. This will be an image
		used as an icon for your alarm clock.

	(4) RUNNING THE SETUP UTILITY
	Run the setup utility with
		python setup.py
	from console after navigating into the folder you have your program in
	and follow the inctructions.
		"File to store your alarms"
			specify a name for a file which will be used to store
			your alarms.
			
			!WARNING! The file will be overwritten. !WARNING!

		"File to store your notifications"
			specify a name for a file which will be used to store
			your notifications.

			!WARNING! The file will be overwritten. !WARNING!

		"Number of news articles to display:"
			Enter a number ranging from 0 to 10 which
			determines how many articles will be displayed
			during the news routine.

		"Your weather API key"
			Enter your openweathermap.org api key.

		"Your news API key"
			Enter your newsapi.org key.

		"Your city"
			Enter the name of city you wish to display weather
			for.
RUNNING
	Navigate console to your directory.
	Run the "main.py" with command
		python main.py
	Open browser and navigate to 127.0.0.1:5000/index
	Enjoy!

Config file structure
	P_A	name of a file which stores your alarms
	P_N	name of a file which stores your notification
	P_R	name of a file which stores your routines
	A_A_A	True/False - determines whether alarms are read out loud
	U_A_A	True False - determines whether notifications are read out loud
	N_A	Number of news articles in the news notification
	W_API_KEY	weather API key (openweathermap.org)
	N_API_KEY	news API key (newsapi.org)
	C_N	Your city
	C	Country to display news. See newsapi.org for valid values.
	FAV	Location of your favicon.
	IM	Name of your image.
Routine file structure

[						file starts with [
	{					each routine starts with {
	"time":
		{
		"year":"",
		"month":"",
		"day":"",
		"hour":"7",			which hour should the routine go off
		"minute":"0",			which minute should the routine go off
		"second":"0"			which second should the routine go off
		},
	"title": "ROUTINE",			if title is different than ROUTINE, it
							will trigger an alarm
	"news": "news",				any value/null - null means that news
							notification won't be triggered
	"weather":"weather",			any value/null - null means that weather
							notification won't be triggered
	"covid":"covid",			any value/null - null means that covid
							notification won't be triggered
	"content":"Good morning."		content of the routine, determines
							description
	}
]