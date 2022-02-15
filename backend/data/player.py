'''
from backend.data.player import get_all_player_comps, find_player_comps_by_username, create_player_comp, update_player_comp, player_leaderboard, racer_data, get_player_comp_data
'''

from backend.resources.database import DBClient
from nitrotype import Racer
import jsonpickle, random
import cloudscraper, json, time, copy
dbclient = DBClient()
def get_player_comp_data(compid):
    #get collection first
    collection = dbclient.db.player_comps # collection in the comps database named test for some reason lol
    #now to get the data
    data = dbclient.get_array(collection, {'compid': compid})
    #now that we got the data let's parse the data and change it into leaderboards
    return data, dbclient
  
def racer_data(racer):
    racer = Racer(racer)
    return racer

def player_leaderboard(compid, category="races"):
    data, dbclient = get_player_comp_data(compid)
    data = update_player_comp(data, dbclient)
    usernames = []
    displays = []
    categorylist = []
    datalist = []
    for user in data['players']:
        user['wpm'] = round(float(user['wpm']),2)
        user['accuracy'] = round(float(user['accuracy']),2)
        user['points'] = round(float(user['points']),2)
        usernames.append(user['username'].lower())
        displays.append(user['display'])
        if category == "races":
            categorylist.append(user['total-races'])
        elif category == "points":
            categorylist.append(user['points'])
        elif category == "speed":
            categorylist.append(user['wpm'])
        elif category == "accuracy":
            categorylist.append(user['accuracy'])
        try:
            user['points'] = user['total-races']*(100+int(user['wpm']))*user['accuracy']/100
        except:
            user['total-races'] = 0
            user['points'] = 0
            user['wpm'] = 0
            user['accuracy'] = 0
        datalist.append((user['total-races'], user['points'], user['wpm'], user['accuracy']))
    sortcategory = sorted(categorylist, reverse=True)
    zipped_lists = zip(categorylist, usernames, displays, datalist)
    sorted_zipped_lists = sorted(zipped_lists, reverse=True)
    cleanresult = []
    for t in sorted_zipped_lists:
        cleanresult.append(tuple([x for x in t if not t.index(x) == 0]))
    return cleanresult
def update_player_comp(data, dbclient):
    old = copy.deepcopy(data)
    collection = dbclient.db.player_comps
    other = data['other']
    players = data['players']
    racer = other['racer']
    if round(time.time()) >= other['endcomptime']:
        return data
    page = racer(racer)
    info = json.loads(page)
    try:
        for user in players:
            for elem in info['results']['members']:
                if user['username'] == elem['username']:
                    try:
                        typed = float(elem['typed'])
                        secs = float(elem['secs'])
                        errs = float(elem
                        ['errs'])
                    except:
                        typed = 0
                        secs = 0
                        errs = 0
                    user['ending-races'] = elem['played']
                    user['total-races'] = user['ending-races'] - user['starting-races']
                    user['display'] = elem['displayName']
                    user['ending-typed'] = typed
                    user['ending-secs'] = float(secs)
                    user['ending-errs'] = errs
                    try:
                        user['wpm'] = (user['ending-typed']-user['starting-typed'])/5/float(user['ending-secs']-user['starting-secs'])*60
                        user['accuracy'] = 100-(((user['ending-errs']-user['starting-errs'])/(user['ending-typed']-user['starting-typed']))*100)
                        user['points'] = user['total-races']*(100+(user['wpm']/2))*user['accuracy']/100
                    except:
                        user['wpm'] = 0
                        user['accuracy'] = 0
                        user['points'] = 0
                    break
            else:
              res = [ sub['username'] for sub in players ]
        for elem in info['results']['members']:
            if elem['username'] in res:
                continue
            else:
                players.append({
                    "username": elem['username'],
                    "starting-races": elem['played'],
                    "ending-races": elem['played'],
                    "total-races": 0,
                    "display": elem['displayName'] or elem['username'],
                    "starting-typed": elem['typed'],
                    "ending-typed": elem['typed'], 
                    "starting-secs": float(elem['secs']), 
                    "ending-secs": float(elem['secs']),
                    "starting-errs": (elem['errs']), "ending-errs": (elem['errs'])
                })
    except Exception as e:
        return
    dbclient.update_array(collection, old, racer_data)
    return racer_data
def create_player_comp(compid, racer, endcomptime, user):
    dbclient = DBClient()
    does_compid_exist = dbclient.get_array(dbclient.db.player_comps, {'compid': str(compid)})
    if does_compid_exist:
        return False, 'Compid already exists!'
    page = player_comp_data(racer)
    info = json.loads(page)
    try:
        info['results']['members']
    except:
        return False, "This team does not exist!"
    results = {
        "results": {
            "compid": str(compid),
            "racer": [],
            "other": {}
        }
    }
    for elem in info['results']['members']:
        if elem['displayName'] != None:
            displayname = elem['displayName']
        else:
            displayname = elem['username']
        try:
            typed = elem['typed']
            secs = elem['secs']
            errs = elem['errs']
        except:
            typed = 0
            secs = 0
            errs = 0
        results['results']['players'].append({
            "username": elem['username'],
            "starting-races": elem['played'],
            "ending-races": elem['played'],
            "total-races": 0,
            "display": displayname,
            "starting-typed": typed,
            "ending-typed": typed, 
            "starting-secs": float(secs), 
            "ending-secs": float(secs),
            "starting-errs": (errs), "ending-errs": (errs), 
            "wpm": 0,
            "accuracy": 0,
            "points": 0
        })
    results['results']['other'] = {
        "player": racer,
        "endcomptime": endcomptime,
        "author": user,
        "ended": False
    }
    dbclient.create_doc(dbclient.db.player_comps, results['results'])
    return True, ""
def find_player_comps_by_username(username):
    dbclient = DBClient()
    comps = dbclient.db.player_comps.find({'other.author': (username)})
    return comps
def delete_player_comp(compid, session):
    data, dbclient = get_player_comp_data(compid)
    data['other']['author'] = str(data['other']['author'])
    if data['other']['author'] == str(session['username']) or data['other']['author'] == str(session['userid']):
        print(dbclient.db.player_comps.delete_one({'compid': str(compid)}).deleted_count)
        return True
    else:
        return False
def get_all_player_comps(filter={}):
    collection = dbclient.db.player_comps
    return collection.find(filter), dbclient

def bkg_task():
    while True:
        comps, dbclient = get_all_player_comps({'other.ended': False})
        for x in comps:
            if round(time.time()) < x['other']['endcomptime']:
                update_player_comp(x, dbclient)
                continue
            else:
                x['other']['ended'] = True
                update_player_comp(x, dbclient)
        print('Updated All Player Comps - '+str(int(time.time())))
        time.sleep(60)