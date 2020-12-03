"""This module creates and runs an internal host for an alarm clock."""
import sched
import time
from datetime import datetime, timedelta
import logging
import json
import copy
from flask import Flask
from flask import request
from flask import render_template
import requests
from uk_covid19 import Cov19API
import pyttsx3

#constanst
CONFIG_FILE = 'config.txt'
#configuring logging
logfile = str(time.localtime().tm_year)+str(time.localtime().tm_mon)+str(time.localtime().tm_mday)+'.log'
logging.basicConfig(filename=logfile, encoding='utf-8', level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)
#global definitions
logging.info("Initializing global definitions...")
PERSISTENT_ALARMS = 'events.txt'
PERSISTENT_NOTIFICATIONS = 'notifications.txt'
PERSISTENT_ROUTINES = 'routines.txt'
ALARMS_ARE_ANNOUNCEMENTS = True
UPDATES_ARE_ANNOUNCEMENTS = True
FILTER_FOR_KEYWORDS = [] # keywords that articles are filtered for
NEWS_ARTICLES = 5 # maximum number of news articles spok
WEATHER_API_KEY = "" # weather API key, loaded during set-up phase
CITY_NAME = 'Exeter' # city to get weather for
NEWS_API_KEY = ""
COUNTRY="gb"
FAVICON = "" # adress to the favicon picture.
IMAGE = ""
NOTIF_SAVE = False # set to true/false according to whether notification field allows HTML
#init
logging.info("Initializing global variables...")
notifications_list = []
events_list = []
routines = []
app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)
ENGINE = pyttsx3.init(debug=True)
ENGINE.startLoop(False)

#functions
logging.info("Initializing functions...")
def sec_s_mn(time_input:dict)->int:
    """Returns number of seconds that passed since midnight.

    Takes dictionary with 'hour', 'minute' and 'second' keys and returns an int
    representing seconds that passed since midnight."""
    logging.debug("sec_s_mn entered with:/n%s",str(time_input))
    seconds = 0
    seconds = int(time_input['hour'])*60**2
    seconds+= int(time_input['minute'])*60
    seconds+= int(time_input['second'])
    return seconds

def append_as_notification(notification: dict):
    """Creates a notification.

    Takes a dictionary with 'title' and 'content' keys."""
    logging.debug("append_as_notification entered with:%s", str(notification))
    notification['title'] = str(len(notifications_list)+1)+" "+notification['title']
    notifications_list.append(notification)
    save_notifications()

def announce(txt: str):
    """Reads string aloud.

    Takes string as an argument."""
    logging.debug("announce entered with:%s", str(txt))
    global ENGINE
    #try:
    #    engine.endLoop()
    #except:
    #    logging.error('PyTTSx3 Endloop error')
    #engine.stop()
    ENGINE.say(txt)
    ENGINE.runAndWait()
    #engine.stop()

def get_weather(): # add try/catch block
    """Returns dictionary object acquired from openweathermap.org"""
    logging.debug("get_weather entered")
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + WEATHER_API_KEY + "&q=" + CITY_NAME
    response = ""
    try:
        response = requests.get(complete_url)
    except:
        logging.error("An error occured while generating weather request.")
    w = ""
    try:
        w = response.json()
    except:
        logging.error("An error occured while interpreting weather request.\n%s",str(w))
    return w

def get_news(): # add try/catch block
    """Returns dictionary obect acquired from newsapi."""
    logging.debug("get_news entered")
    base_url = "http://newsapi.org/v2/top-headlines?"
    complete_url = base_url + "country=" + COUNTRY + "&apiKey=" + NEWS_API_KEY
    response = requests.get(complete_url)
    w = response.json()
    return w

def get_covid():
    """Returns dictionary object containing newst COVID stats."""
    logging.debug("get_covid entered")
    england_only = [
        'areaType=nation',
        'areaName=England'
    ]
    cases_and_deaths = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "newCasesByPublishDate": "newCasesByPublishDate",
        "cumCasesByPublishDate": "cumCasesByPublishDate",
        "newDeathsByDeathDate": "newDeathsByDeathDate",
        "cumDeathsByDeathDate": "cumDeathsByDeathDate"
    }
    try:
        api = Cov19API(filters=england_only, structure=cases_and_deaths)
        data = api.get_json()
    except:
        logging.error("Error occured in the COVID API.")
    return data

def digest_weather(raw_weather: dict)->str: # add try catch block
    """Turns weather API dict object into a human readable string.

    Takes a dict object created by openweathermap API and returns a string."""
    logging.debug("Digesting weather entered with:\n%s",str(raw_weather))
    digested_weather = "Weather is "
    for weather in raw_weather['weather']:
        digested_weather+= weather['main'] +', '
    digested_weather+= "and it is "+str(raw_weather['main']['temp'])+'K'
    digested_weather+=', but it feels like '+str(raw_weather['main']['feels_like'])+'K.'
    digested_weather+='The sunrise is at '+sec_t_times(raw_weather['sys']['sunrise'])+'.'
    digested_weather+='The sunset is at '+sec_t_times(raw_weather['sys']['sunset']) +'.'
    return digested_weather

def unsave_digest_news(raw_news: dict)->list: # add try catch block
    """Turns news API dict object into a string with HTML code.

    Takes a dict object and returns a string with HTML code."""
    logging.debug("unsave_digest_news entered with:\n%s",str(raw_news))
    digested_news = ["Top headlines:\n","Top healdines:"]
    i = 0
    for article in raw_news['articles']:
        ar_st = '<a href="'
        ar_st+= article['url']+'">'
        ar_st+= article['title']+'</a>\n'
        ar_st+= '<img src="'+article['urlToImage']+'">\n'
        digested_news[0]+= ar_st
        digested_news[1]+= article['title']+', '
        # limiting a number of articles displayed v
        i+=1
        if i == NEWS_ARTICLES:
            break
    return digested_news

def save_digest_news(raw_news: dict)->list: # add try catch block
    """Turns news API dict object into a human readble code.

    Takes a dict object and returns a list with human readable strings
    containing headlines."""
    logging.debug("save_digest_news entered with:\n%s",str(raw_news))
    digested_news = [[],"Top headlines: "]
    i = 0
    for article in raw_news['articles']:
        ar_st = ''
        ar_st+= article['title']
        digested_news[0].append(ar_st)
        digested_news[1]+= article['title']+', '
        # limiting a number of articles displayed v
        i+=1
        if i == NEWS_ARTICLES:
            break
    return digested_news

def digest_covid(raw_covid: dict)->str:
    """Takes a dictionary object returned by the COVID API and returns a human readble string."""
    logging.debug("digest_covid entered with:\n%s",str(raw_covid))
    today = raw_covid['data'][0]['newCasesByPublishDate']
    yesterday = raw_covid['data'][1]['newCasesByPublishDate']
    the_day_before = raw_covid['data'][2]['newCasesByPublishDate']
    digested_covid = "There were "
    digested_covid+= str(raw_covid['data'][1]['newCasesByPublishDate'])
    digested_covid+= " new cases yesterday."
    digested_covid+= " Which makes "
    digested_covid+= str(round((yesterday/the_day_before)*100-100,2))
    digested_covid+= "% increase."
    digested_covid+= " There are "
    digested_covid+= str(today)
    digested_covid+= " cases today as of now."
    return digested_covid

def sec_t_times(sec: int)-> str:
    """Takes seconds in the int form and returns HH:MM string since the midnight."""
    logging.debug("sec_t_times entered with:\n%s", sec)
    d = timedelta(seconds=sec)
    logging.debug(d)
    #dtime.tm_day = 0
    string = str(d)
    string = string.split(' ')
    return string[-1]

def make_alarm_notif(event_data: dict):
    """Creates an alarm notification."""
    logging.debug("make_alarm_notif entered with:\n%s",str(event_data))
    content = 'has gone off at '
    content+= str(time.localtime().tm_hour)+":"+str(time.localtime().tm_min)
    append_as_notification({'title': event_data['title'],
                            'content': content
                            })

def make_weather_notif():
    """Creates weather notification."""
    logging.debug("make_weather_notif entered")
    raw_weather = get_weather()
    digested_weather = digest_weather(raw_weather)
    weather_notification = { 'title': 'Weather',
                             'content': digested_weather}
    append_as_notification(weather_notification)
    if UPDATES_ARE_ANNOUNCEMENTS == True:
        announce(digested_weather)

def make_news_notif():
    """Creates news notification."""
    logging.debug("make_news_notif entered.")
    raw_news = get_news()
    digested_news = None
    if NOTIF_SAVE == True:
        digested_news = unsave_digest_news(raw_news)
        news_notification = { 'title': 'News',
                              'content': digested_news[0]}
        append_as_notification(news_notification)
    else:
        digested_news = save_digest_news(raw_news)
        for article in digested_news[0]:
            news_notification = { 'title': 'News',
                                  'content': article}
            append_as_notification(news_notification)
    if UPDATES_ARE_ANNOUNCEMENTS == True:
        announce(digested_news[1])

def make_covid_notif():
    """Creates COVID notification."""
    logging.debug("make_covid_notif entered.")
    raw_covid = get_covid()
    digested_covid = digest_covid(raw_covid)
    covid_notification = {'title':'COVID',
                          'content': digested_covid}
    append_as_notification(covid_notification)
    if UPDATES_ARE_ANNOUNCEMENTS == True:
        announce(digested_covid)

def notifications(event_data: dict):
    """Notifications routine.

       Accepts the calling event as its arguments."""
    logging.debug("notifications entered with:\n%s",str(event_data))
    if (event_data['title']=="ROUTINE")==False:
        make_alarm_notif(event_data)
    if event_data['weather'] == 'weather':
        make_weather_notif()
    if event_data['news'] == 'news':
        make_news_notif()
    if event_data['covid']:
        make_covid_notif()

def event(event_data):
    """Alarm routine.

    Trigerred whenever an event happens. Accepts the calling event structure as args."""
    logging.debug("event entered with:\n%s\n arguments.",str(event_data))
    time_str = "It's "
    time_str+= str(time.localtime().tm_hour)+' hours and '
    time_str+= str(time.localtime().tm_min)+"minutes."
    if ALARMS_ARE_ANNOUNCEMENTS == True:
        announce(time_str)
    notifications(event_data)
    logging.debug("events_list before being popped in event:\n%s",str(events_list))
    events_list.pop(0)
    for i in range(len(events_list)):
        events_list[i]['title'] = events_list[i]['title'].split(' ')
        events_list[i]['title'][0] = str(i+1)
        events_list[i]['title'] = " ".join(events_list[i]['title'])
    save_events()

def schedule_an_event(event_data: dict):
    """Schedules an event for today."""
    logging.debug("schedule_an_event entered with:\n%s",str(event_data))
    raw_time = time.localtime()
    raw_time = { 'hour':raw_time.tm_hour,
                 'minute':raw_time.tm_min,
                 'second':raw_time.tm_sec}
    delay = sec_s_mn(event_data['time'])-sec_s_mn(raw_time)
    if delay > 0:
        s.enter(delay, 1, event, argument = [event_data,])
        logging.debug("An event was scheduled.\nIn: %s",str(delay))
        logging.debug(event_data)
    else:
        logging.debug("Alarm had a time set in the past; firing away.")
        event(event_data) # this line is here for debug purposes, should be removed before release

def rel_t(i):
    """Calculates a number which represents relative position of an event
    on a chronological axis."""
    logging.debug("rel_t entered with:\n%s",str(i))
    relt=0
    relt = int(i['time']['minute'])
    relt = int(i['time']['hour'])*10**2+relt
    relt = int(i['time']['day'])*10**4+relt
    relt = int(i['time']['month'])*10**6+relt
    relt = int(i['time']['year'])*10**8+relt
    return relt

def save_events():
    """"Routine which saves current event list into a file."""
    logging.debug("save_events entered")
    with open(PERSISTENT_ALARMS, 'w') as f:
        f.seek(0)
        f.write(json.dumps(events_list, indent=4, sort_keys=True))

def save_notifications():
    """"Routine which saves current event list into a file."""
    logging.debug("save_notification entered")
    with open(PERSISTENT_NOTIFICATIONS, 'w') as f:
        f.seek(0)
        f.write(json.dumps(notifications_list, indent=4, sort_keys=True))

def add_event(new_event: dict):
    """Adds the event to the list of all events."""
    logging.debug("add_event entered with:\n%s",str(new_event))
    global events_list
    new_event = copy.deepcopy(new_event)
    new_event['title'] ="New " + new_event['title']
    new_event['relt'] = rel_t(new_event)
    events_list.append(new_event)
    #logging.debug(events_list)
    events_list = sorted(events_list, key = lambda i : i['relt'])
    logging.debug('  Alarms list:/n%s',str(events_list))
    for i in range(len(events_list)):
        events_list[i]['title'] = events_list[i]['title'].split(' ')
        events_list[i]['title'][0] = str(i+1)
        events_list[i]['title'] = " ".join(events_list[i]['title'])
    save_events()

def is_today(date: dict) -> bool:
    """Checks whether a specific date is today."""
    logging.debug("is_today entered with:\n%s",str(date))
    raw_time = time.localtime()
    logging.debug("raw time is: %s",str(raw_time))
    logging.debug("time to check is: %s",str(date))
    if int(raw_time.tm_year) == int(date['year']):
        if int(raw_time.tm_mon) == int(date['month']):
            if int(raw_time.tm_mday) == int(date['day']):
                return True
    return False

def set_up_new_event() -> dict:
    """Creates new event dictionary structure based on query arguments."""
    logging.debug("set_up_new_event entered")
    logging.info('New request received:')
    logging.info(request)
    new_event={}
    new_event['time'] = request.args.get("alarm")
    new_event['time'] = datetime.strptime(new_event['time'], '%Y-%m-%dT%H:%M')#2020-11-30T21:01
    new_event['time'] = {'year': str(new_event['time'].year),
                         'month': str(new_event['time'].month),
                         'day': str(new_event['time'].day),
                         'hour': str(new_event['time'].hour),
                         'minute': str(new_event['time'].minute),
                         'second': 0}
    new_event['title'] = request.args.get("two")
    new_event['news'] = request.args.get("news")
    new_event['weather'] = request.args.get("weather")
    new_event['covid'] = request.args.get("covid")
    new_event['content'] = new_event['time']['year']
    new_event['content']+= '-'+new_event['time']['month']
    new_event['content']+= '-'+new_event['time']['day']
    new_event['content']+= ' '+new_event['time']['hour']
    new_event['content']+= ':'+new_event['time']['minute']
    if new_event['news']:
        new_event['content']+=' + news'
    if new_event['weather']:
        new_event['content']+=' + weather'
    if new_event['covid']:
        new_event['content']+=' + covid'
    logging.info('Alarm set:')
    logging.info(new_event)
    return new_event

def new_day():
    """New day routine. Schedules itself for tomorow
    and schedules any events for today."""
    logging.debug("new_day entered")
    s.enter(60**3,1, new_day)
    for instance in events_list:
        if is_today(instance['time'])==True:
            schedule_an_event(instance)
        else:
            break
    set_up_routines()

def remove_notification():
    """Removes a notification from the queue."""
    logging.debug("remove_notification entered")
    global notifications_list
    logging.info('New request received:\n%s',str(request))
    removed_title = request.args.get("notif")
    for i in range(len(notifications_list)):
        if notifications_list[i]['title']==removed_title:
            notifications_list.pop(i)
            break
    for i in range(len(notifications_list)):
        notifications_list[i]['title'] = notifications_list[i]['title'].split(' ')
        notifications_list[i]['title'][0] = str(i+1)
        notifications_list[i]['title'] = " ".join(notifications_list[i]['title'])
    save_notifications()

    seconds = sec_s_mn(time_now)
    s.enter(60**3-seconds,1, new_day)

def remove_events():
    """Removes an event from the queue."""
    logging.debug("remove_events entered")
    logging.info('New request received:%s',str(request))
    removed_title = request.args.get("alarm_item")
    logging.info('Removed title %s',str(removed_title))
    titles_to_be_removed = []
    for i in range(len(events_list)):
        if events_list[i]['title'] == removed_title:
            titles_to_be_removed.append(i)
    titles_to_be_removed.sort(reverse=True)
    for title in titles_to_be_removed:
        events_list.pop(title)
        if title < len(s.queue)-1: #there has to be -1 because the last item
            s.cancel(s.queue[title]) # ^ in the queue is the new day routine
    for i in range(len(events_list)):
        events_list[i]['title'] = events_list[i]['title'].split(' ')
        events_list[i]['title'][0] = str(i+1)
        events_list[i]['title'] = " ".join(events_list[i]['title'])
    save_events()

@app.route('/index')
def homepage():
    """The landing page creation routine."""
    logging.debug("homepage entered")
    s.run(blocking=False)
    if request.args.get("alarm"):
        new_event = set_up_new_event()
        add_event(new_event)
        if is_today(new_event['time']) == True:
            schedule_an_event(new_event)
    if request.args.get("alarm_item"):
        remove_events()
    if request.args.get("notif"):
        remove_notification()
    if request.args.get("covid"):
        make_covid_notif()
    raw_time = time.localtime()
    parsed_time = str(raw_time[3])+":"
    if raw_time[4] < 10:
        parsed_time+= '0' + str(raw_time[4])
    else:
        parsed_time+= str(raw_time[4])
    return render_template('template.html',
                           notifications = notifications_list,
                           alarms = events_list,
                           title = parsed_time,
                           favicon = 'static/images/'+FAVICON,
                           image = IMAGE)

def load(): # add try {} catch {} segment, add notification loading
    """Fuction loading persistent events and notifications."""
    logging.debug("load entered")
    txt = None
    global events_list
    try:
        with open(PERSISTENT_ALARMS, mode='r') as f:
            txt = f.read()
    except:
        logging.critical("Unable to open PERSISTENT_ALARMS file.")
    try:
        events_list = json.loads(txt)
    except:
        logging.critical("Unable to process json in PERSISTENT_ALARMS file.")
    logging.debug('Alarms_list is: %s',str(events_list))

    global notifications_list
    try:
        with open(PERSISTENT_NOTIFICATIONS, mode='r') as f:
            txt = f.read()
    except:
        logging.critical("Unable to open PERSISTENT_NOTIFICATION file.")
    try:
        notifications_list = json.loads(txt)
    except:
        logging.critical("Unable to process json in PERSISTENT_NOTIFICATIONS file.")
    logging.debug('Notifications_list is: %s',str(notifications_list))

    global routines
    try:
        with open(PERSISTENT_ROUTINES, mode='r') as f:
            txt = f.read()
    except:
        logging.critical("Unable to open PERSISTENT_ROUTINES file.")
    try:
        routines = json.loads(txt)
    except:
        logging.critical("Unable to process json in PERSISTENT_ROUTINES file.")
    logging.debug('Routines is: %s',str(routines))

def load_definitions():
    """Function loading definitions and constants."""
    logging.debug("load_definitions entered")
    txt = ""
    try:
        with open(CONFIG_FILE, 'r') as f:
            txt = f.read()
    except:
        logging.critical("Unable to open CONFIG_FILE.")
        raise Exception("Unable to open CONFIG_FILE.")
    try:
        definitions = json.loads(txt)
    except:
        logging.critical("Unable to process json in CONFIG_FILE")
        raise Exception("Unable to process json in CONFIG_FILE")
    #
    logging.debug('Definition dictionary:\n%s',str(definitions))
    #
    try:
        global PERSISTENT_ALARMS
        PERSISTENT_ALARMS = str(definitions['P_A'])
        #
        global PERSISTENT_NOTIFICATIONS
        PERSISTENT_NOTIFICATIONS = str(definitions['P_N'])
        #
        global ALARMS_ARE_ANNOUNCEMENTS
        ALARMS_ARE_ANNOUNCEMENTS = bool(definitions['A_A_A'])
        #
        global UPDATES_ARE_ANNOUNCEMENTS
        UPDATES_ARE_ANNOUNCEMENTS = bool(definitions['U_A_A'])
        #
        global FILTER_FOR_KEYWORDS
        FILTER_FOR_KEYWORDS = definitions['F_F_K']
        #
        global NEWS_ARTICLES
        NEWS_ARTICLES = int(definitions['N_A'])
        #
        global WEATHER_API_KEY
        WEATHER_API_KEY = str(definitions['W_API_KEY'])
        #
        global CITY_NAME
        CITY_NAME = str(definitions['C_N'])
        #
        global NEWS_API_KEY
        NEWS_API_KEY = str(definitions['N_API_KEY'])
        #
        global COUNTRY
        COUNTRY = str(definitions['C'])
        #
        global PERSISTENT_ROUTINES
        PERSISTENT_ROUTINES = str(definitions['P_R'])
        #
        global FAVICON
        FAVICON = str(definitions['FAV'])
        #
        global IMAGE
        IMAGE = str(definitions['IM'])
    except:
        logging.critical("Config file corrupted.")
        raise Exception("Config file corrupted.")

def first_day():
    """Schedules new day routine and any other routines."""
    logging.debug("first_day entered")
    raw_time = time.localtime()
    time_now = {'year': raw_time[0],
                'month': raw_time[1],
                'day': raw_time[2],
                'hour': raw_time[3],
                'minute': raw_time[4],
                'second': raw_time[5]}
    seconds = sec_s_mn(time_now)
    s.enter(60**3-seconds,1, new_day)

    #new_event['time'] = datetime.strptime(new_event['time'], '%Y-%m-%dT%H:%M')#2020-11-30T21:01
    #new_event['time'] = {'year': string, #
    #                     'month': string, #
    #                     'day': string, # year, month and day must be set to today to show
    #                                    # properly in the scheduled list of events
    #                     'hour': str(new_event['time'].hour),
    #                     'minute': str(new_event['time'].minute),
    #                     'second': 0}
    #new_event['title'] = "ROUTINE"
    #new_event['news'] = None / "news"
    #new_event['weather'] = None / "weather"
    #new_event['covid'] = None / "covid"
    #new_event['content'] = "Routine's description."
    set_up_routines()

def set_up_routines():
    for routine in routines:
        routine['time']['year']=time_now['year']
        routine['time']['month']=time_now['month']
        routine['time']['day']=time_now['day']
        add_event(routine)
        schedule_an_event(routine)
    save_events()

#body
if __name__ == "__main__":
    logging.debug("main entered")
    logging.info("Loading files...")
    load_definitions()
    load()
    first_day()
    logging.info("Starting.")
    app.run()
