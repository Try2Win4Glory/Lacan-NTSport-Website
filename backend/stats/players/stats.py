from backend.stats.database import DBClient
from nitrotype import Racer
import datetime
dbclient = DBClient()
c = dbclient.db.racers
def create_profile(username):
    racer = Racer(username)
    races = (racer.races)
    wpm = racer.wpm_average
    data = {'username': username, "races": [races], "wpms": [wpm], 'hourly': [[races,wpm, datetime.datetime.today().hour]]}
    c.insert_one(data)
    return data

def get_stats(username):
    data = c.find_one({"username": username})
    if data == None:
        data = create_profile(username)
    return data

def update_stats_all():
    docs = c.find()
    for doc in docs:
        username = doc['username']
        racer = Racer(username)
        doc['races'].append(racer.races)
        doc['wpms'].append(racer.wpm_average)
        dbclient.update_array(c, {'username':username}, doc)

def update_stats_hourly():
    docs = c.find()
    for doc in docs:
        username = doc['username']
        racer = Racer(username)
        doc['hourly'].append([racer.races, racer.wpm_average, datetime.datetime.today().hour])
        dbclient.update_array(c, {'username':username}, doc)