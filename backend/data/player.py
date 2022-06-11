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
    collection = dbclient.db.player_comps
    #now to get the data
    data = dbclient.get_array(collection, {'compid': compid})
    #now that we got the data let's parse the data and change it into leaderboards
    return data, dbclient
  
def update_player_comp(data, dbclient):
    newdata = []
    #print(len(data['players']))
    for x in data['players']:
        try:
            racer = (Racer(x['username']))
            tag = racer.tag[1:-2].upper()
            requests = racer.requests
            team_data = requests.get('https://www.nitrotype.com/api/v2/teams/'+tag).json()['results']
        except:
            newdata.append(x)
        lst = (team_data['season'])
        def build_dict(seq, key):
            return dict((d[key], dict(d)) for (index, d) in enumerate(seq))
        
        people_by_name = build_dict(lst, key="username")
        szn_data = people_by_name.get(x['username'])
        #print(szn_data)
        x['ending-races'] = szn_data['played']
        x["ending-typed"] = szn_data['typed']
        x['ending-secs'] = szn_data['secs']
        x['ending-errs'] = szn_data['errs']
        x['ending-points'] = szn_data['points']
        x['display'] = szn_data['displayName']
        try:
            x['wpm'] = (x['ending-typed']-x['starting-typed'])/5/float(x['ending-secs']-x['starting-secs'])*60
        except:
            x['wpm'] = 0
        try:
            x['accuracy'] = 100-(((x['ending-errs']-x['starting-errs'])/(x['ending-typed']-x['starting-typed']))*100)
        except:
            x['accuracy'] = 0
        x['points'] = x['ending-points'] - x['starting-points']
        x['total-races'] = x['ending-races'] - x['starting-races']
        newdata.append(x)
        #team_cached[tag] = [team_data['season'], time.time()]
    data['players'] = newdata
    dbclient.update_array(dbclient.db.player_comps, {"compid": data['compid']}, data)
    return (data)
def add_player(username, compid):
    data, dbclient = get_player_comp_data(compid)
    for x in data['players']:
        if x['username'].lower() == username.lower():
            return "User already added"
    racer = (Racer(username))
    tag = racer.tag[1:-2].upper()
    requests = racer.requests
    try:
        team_data = requests.get('https://www.nitrotype.com/api/v2/teams/'+tag).json()['results']
    except:
        raise TypeError("Must join team")
    lst = (team_data['season'])
    def build_dict(seq, key):
        return dict((d[key], dict(d)) for (index, d) in enumerate(seq))
    
    people_by_name = build_dict(lst, key="username")
    szn_data = people_by_name.get(username)
    #print(szn_data)
    x = {"username": username}
    x['starting-races'] = szn_data['played']
    x["starting-typed"] = szn_data['typed']
    x['starting-secs'] = szn_data['secs']
    x['starting-errs'] = szn_data['errs']
    x['starting-points'] = szn_data['points']
    
    x['ending-races'] = szn_data['played']
    x["ending-typed"] = szn_data['typed']
    x['ending-secs'] = szn_data['secs']
    x['ending-errs'] = szn_data['errs']
    x['ending-points'] = szn_data['points']

    x['display'] = szn_data['displayName']
    
    x['wpm'] = 0
    x['accuracy'] = 0
    x['points'] = 0
    x['total-races'] = 0
    data['players'].append(x)
    dbclient.update_array(dbclient.db.player_comps, {"compid": compid}, data)
    return data
def player_leaderboards(compid, category="races", update=True):
    data, dbclient = get_player_comp_data(compid)
    if update:
        data = update_player_comp(data, dbclient)
    usernames = []
    displays = []
    categorylist = []
    datalist = []
    
    for user in data['players']:
        user['wpm'] = round(float(user['wpm']),2)
        user['accuracy'] = round(float(user['accuracy']),2)
        user['points'] = round(user['points'])
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
        '''try:
            user['points'] = user['total-races']*(100+int(user['wpm']))*user['accuracy']/100
            userpoints = user['points']
            user['points'] = round(float(userpoints))
            #user['points'] = "{:,}".format(user['points'])
        except:
            user['total-races'] = 0
            user['points'] = 0
            user['wpm'] = 0
            user['accuracy'] = 0'''
        datalist.append((user['total-races'], user['points'], user['wpm'], user['accuracy']))
    sortcategory = sorted(categorylist, reverse=True)
    zipped_lists = zip(categorylist, usernames, displays, datalist)
    sorted_zipped_lists = sorted(zipped_lists, reverse=True)
    cleanresult = []
    for t in sorted_zipped_lists:
        cleanresult.append(tuple([x for x in t if not t.index(x) == 0]))
    return cleanresult
def create_player_comp(compid, racer, endcomptime, user):
    dbclient = DBClient()
    does_compid_exist = dbclient.get_array(dbclient.db.player_comps, {'compid': str(compid)})
    if does_compid_exist:
        return False, 'Compid already exists!'
    results = {
        "results": {
            "compid": str(compid),
            "racer": [],
            "other": {}
        }
    }
    results['results']['players'] = []
    results['results']['other'] = {
        "player": racer,
        "endcomptime": endcomptime,
        "author": user,
        "ended": False
    }
    dbclient.create_doc(dbclient.db.player_comps, results['results'])
    add_player(racer, compid)
    return True, ""

def find_player_comps_by_username(username):
    dbclient = DBClient()
    player_comps = dbclient.db.player_comps.find({'other.author': (username)})
    return player_comps

def delete_player_comp(compid, session):
    data, dbclient = get_comp_data(compid)
    creator = str(data['other']['author'])
    if creator == str(session['username']) or data['other']['author'] == str(session['userid']):
        print(dbclient.db.player_comp.delete_one({'compid': str(compid)}).deleted_count)
        return True
    else:
        return False
def get_all_comps(filter={}):
    collection = dbclient.db.player_comp
    return collection.find(filter), dbclient

''''
def find_player_comps_by_username(username):
    dbclient = DBClient()
    player_comps = dbclient.db.player_comps.find({'other.author': (username)})
    playercomplist = list(player_comps)
    #print(playercomplist)
    #sernames = playercomplist['other']['player']
    #print(usernames)
    dontletthisbeempty = player_comps["dontletthisbeempty"]
    return player_comps, dontletthisbeempty, usernames
# Very interesting that the same structure of code which works fine for multiplayer comps doesn't work at all for player comps hmmm....__import__
# 
  
def find_player_comps_by_username(username):
  dbclient = DBClient()
  player_comps = dbclient.db.player_comps.find({'other.author':(username)})
  usernames = player_comps['username']#Hmmm, I'll set it back to the original code and see what happens ok
  return player_comps, usernames
'''

def remove_player_from_comp(players, session):
    data, dbclient = get_comp_data(players)
    creator = str(data['other']['author'])
    if creator == str(session['username']) or data['other']['author'] == str(session['userid']):
        print(dbclient.db.test.delete_one({'players': str(players)}).deleted_count)
        return True
    else:
        return False

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

def player_bkg_task():
    while True:
        comps, dbclient = get_all_player_comps({'other.ended': False})
        for x in comps:
            if round(time.time()) < x['other']['endcomptime']:
                update_player_comp(x, dbclient)
                continue
            else:
                x['other']['ended'] = True
                update_player_comp(x, dbclient)
        print('[-] Updated All Player Comps - '+str(int(time.time())))
        time.sleep(600)