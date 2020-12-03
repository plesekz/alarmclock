import logging
import json
data = {'P_A': 'alarms.txt',
        'P_N': 'notifications.txt',
        'A_A_A': True,
        'U_A_A': True,
        'F_F_K' : [],
        'N_A' : 0,
        'W_API_KEY': "",
        'C_N' : 'Exeter',
        'N_API_KEY' : "",
        'C':"gb",
        "P_R":"routines.txt",
        "FAV": "static/images/favicon.png",
        "IM": "image.jpg"}

with open('config.txt', 'w') as f:
    data['P_A'] = input('File to store alarms: ')
    data['P_N'] = input('File to store notifications: ')
    while not (data['N_A']>0 and data['N_A']<10):
        data['N_A'] = int(input('Number of news articles to display [1-10] :'))
    data['W_API_KEY'] = input('Your weather API key: ')
    data['N_API_KEY'] = input('Your news API key: ')
    data['C_N'] = input('Your city: ')
    f.seek(0)
    f.write(json.dumps(data, indent=4, sort_keys=True))
with open(data['P_A'], 'w') as f:
    f.seek(0)
    f.write('[]')
    f.truncate()
with open(data['P_N'], 'w') as f:
    f.seek(0)
    f.write('[]')
    f.truncate()
with open(data['P_R'], 'w') as f:
    f.seek(0)
    txt = """[
	{
	"time":
		{
		"year":"",
		"month":"",
		"day":"",
		"hour":"7",
		"minute":"0",
		"second":"0"
		},
	"title": "ROUTINE",
	"news": "news",
	"weather":"weather",
	"covid":"covid",
	"content":"Good morning."
	}
]"""
    f.write()
    f.truncate()
