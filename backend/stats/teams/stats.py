from backend.stats.database import DBClient
from nitrotype import Team
import datetime
dbclient = DBClient()
c = dbclient.db.teams
def create_profile(tag):
    team = Team(tag)
    races = (team.alltime_races)
    data = {'tag': tag, "races": [races],'hourly': [[races, datetime.datetime.today().hour]]}
    c.insert_one(data)
    return data

def get_team_stats(tag):
    data = c.find_one({"tag": tag})
    if data == None:
        data = create_profile(tag)
    return data

def update_team_stats_all():
    docs = c.find()
    for doc in docs:
        tag = doc['tag']
        team = Team(tag)
        doc['races'].append(team.alltime_races)
        dbclient.update_array(c, {'tag':tag}, doc)

def update_team_stats_hourly():
    docs = c.find()
    for doc in docs:
        tag = doc['tag']
        team = Team(tag)
        doc['hourly'].append([team.alltime_races, datetime.datetime.today().hour])
        dbclient.update_array(c, {'tag':tag}, doc)