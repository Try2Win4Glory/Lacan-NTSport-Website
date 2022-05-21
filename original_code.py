'''
from flask import Flask, render_template, request, redirect, session
from backend.data.comp import leaderboards, create_comp, find_comps_by_username, get_comp_data, delete_comp, update_comp, get_all_comps, bkg_task, invite_user, timestamp

from backend.data.player import get_all_player_comps
from backend.data.player import create_player_comp
from backend.data.player import update_player_comp 
from backend.data.player import player_leaderboard 
from backend.data.player import get_player_comp_data

from backend.signup.signup import signup_account, discord_signup
import os
from backend.login.login import login_account, discord_login
import time
import random, string
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import math
import datetime
import threading
import json

def log(x, base=None):
    try:
        return math.log(x, base)
    except:
        return 0
def get_money(a, w, r):
    value = (a*log(w*w, 2)*(1+(a/10))+(1250*(5-(100-a))))*r
    return value if value > 0 else 0
  
app = Flask(__name__)
app.secret_key = os.environ['app_key']
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"    # !! Only in development environment.

app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("DISCORD_BOT_TOKEN")
app.config["DISCORD_REDIRECT_URI"] = "https://Official-LNS-Website.a1sauces.repl.co/oauth/callback"

discord = DiscordOAuth2Session(app)
@app.route('/')
def home():
    return render_template('/1_home/home.html', **session)

@app.route('/discordlogin')
def discordlogin():
    return discord.create_session(scope=['identify'], **session)
    
@app.route('/discordsignup')
def discordsignup():
    session['discord_signup'] = True
    return discord.create_session(scope=['identify'], **session)  


@app.route("/oauth/callback/")
def callback():
    discord.callback()
    signup = False
    try:
        if session['discord_signup']:
            signup = True
    except:
        pass
    user = discord.fetch_user()
    userid = (user.id)
    session['logged_in'] = False
    if signup:
        discord_signup(userid)
        session['logged_in'] = True
        session['username'] = str(user)
        session['userid'] = userid
        return redirect('/dashboard')
    else:
        success = discord_login(userid)
        if not success:
            session['login_error_message'] = "No account found with this discord account!"
        else:
            session['logged_in'] = True
            session['username'] = str(user)
            session['userid'] = userid
        return redirect('/dashboard/')
  
def comp_html(compid):
    data = get_comp_data(compid)[0]
    #print(data['allowed'])
    if str(data['other']['public']) == "False":
      try:
        allowed = str(session['username']) in data['allowed']
      except:
        allowed = False
          
      try:
        if str(session['username']) == str(data['other']['author']):
          allowed = True
        else:
          if str(session['username']) in data['allowed']:
            allowed = True
          else:
            allowed = False
      except:
        allowed = False
            
      if allowed == False:
        return redirect('/invalid-comp')
      else:
        pass
        
    args = request.args
    try:
        sortby = args['sortby']
        if sortby == 'races':
            lb = leaderboards(compid, 'races')
        if sortby == 'wpm':
            lb = leaderboards(compid, 'speed')
        if sortby == 'acc':
            lb = leaderboards(compid, 'accuracy')
        if sortby == 'points':
            lb = leaderboards(compid, 'points')
    except:
        lb = leaderboards(compid, 'races')

    endcomptime = data['other']['endcomptime']
    if time.time() > endcomptime:
        hours = 0
        minutes = 0
        seconds = 0
    else:
        timeleft = endcomptime - round(time.time())
        timeleft = str(datetime.timedelta(seconds=timeleft)).split(':')
        hours = timeleft[0]
        minutes = timeleft[1]
        seconds = timeleft[2]
    compdesc = None
    try:
      if data['other']['compdesc'] != None:
        compdesc = data['other']['compdesc']
      else:
        compdesc = "No Description has been provided."
    except:
      compdesc = "No Description has been provided."
    try:
      loggedinas = str(session['username'])
      author = str(data['other']['author'])
      if loggedinas == author:
        isauthor = True
      else:
        isauthor = False
    except:
      isauthor = False
    try:
        data['allowed']
    except:
        data['allowed'] = []
    return render_template('/3_competitions/team_data/comp_page.html', players=lb, link=f'https://Official-LNS-Website.a1sauces.repl.co/team-comp/{compid}', hours=hours, minutes=minutes, seconds=seconds, team=data['other']['team'], compdesc=compdesc, get_money=get_money, compid=compid, isauthor=isauthor, allowed=data['allowed'], **session)

def player_comp_html(compid):
    args = request.args
    try:
        sortby = args['sortby']
        if sortby == 'races':
            lb = player_leaderboard(compid, 'races')
        if sortby == 'wpm':
            lb = player_leaderboard(compid, 'speed')
        if sortby == 'acc':
            lb = player_leaderboard(compid, 'accuracy')
        if sortby == 'points':
            lb = player_leaderboard(compid, 'points')
    except:
        lb = player_leaderboard(compid, 'races')
    data = get_player_comp_data(compid)[0]
    endcomptime = data['other']['endcomptime']
    if time.time() > endcomptime:
        hours = 0
        minutes = 0
        seconds = 0
    else:
        timeleft = endcomptime - round(time.time())
        timeleft = str(datetime.timedelta(seconds=timeleft)).split(':')
        hours = timeleft[0]
        minutes = timeleft[1]
        seconds = timeleft[2]
    return render_template('3_competititons/player_data/player_comp.html', players=lb, link=f'https://Official-LNS-Website.a1sauces.repl.co/player-comp/{compid}', hours=hours, minutes=minutes, seconds=seconds, racer=data['other']['racer'], get_money=get_money, **session)

@app.route('/statistics/player/')
def stats_player():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    try:
        session['userid']
        comps = find_comps_by_username(int(session['userid']))
    except:
        comps = find_comps_by_username(session['username'])
    return render_template('4_stats/stats_page.html', session=session, comps=comps, **session)
  
@app.route('/dashboard/')
def dashboard():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    try:
        session['userid']
        comps = find_comps_by_username(int(session['userid']))
    except:
        comps = find_comps_by_username(session['username'])

    return render_template('/1_home/dashboard.html', session=session, comps=comps, time=time, datetime=datetime, timestamp=timestamp, **session)


@app.route('/lnschat/')
def lnschat():
  return render_template('6_other/lnschat.html', **session)

@app.route('/racer-stats/')
def stats():
  return render_template('4_stats/stats.html', **session)

@app.route('/user_search/')
def user_search():
  return render_template('4_stats/user_search.html', **session)

@app.route('/customcomp/<id>')
def custom_comp(id):
    if int(id) == 1:
        return comp_html("06926861")

@app.route('/head/')
def head():
  return render_template('general/head.html', **session)

@app.route('/commands/')
def commands():
  return render_template('2_bot/commands.html', **session)

@app.route('/privacy/')
def privacy():
  return render_template('2_bot/privacy.html', **session)

@app.route('/view-comps/')
def view_comps():
  return render_template('in_work/cards.html', **session)

@app.route('/vote/')
def vote():
  return render_template('6_other/vote.html', **session)

@app.route('/invite/')
def invite():
  return render_template('2_bot/invite.html', **session)

@app.route('/support/')
def support():
  return render_template('2_bot/support.html', **session)

@app.route('/team/')
def team():
  return render_template('2_bot/team.html', **session)

@app.route('/veryencryptedapiendpoint/logout')
def logout_api():
    session.clear()
    return redirect('/')
    
@app.route('/signup/')
def signup():
    message = ""
    try:
        message = session['signup_error_message'].copy()
        session.pop('signup_error_message')
    except:
        pass
    return render_template('8_user/signup.html', message=message, **session)

@app.route('/team-comp/<compid>')
def comp(compid):
    return comp_html(compid)

@app.route('/invalid-comp/')
def invalid_comp():
  return render_template('/3_competitions/invalid/comp_invalid.html', **session)


@app.route('/player-comp/<compid>')
def player_comp(compid):
    return player_comp_html(compid)

@app.route('/updates/')
def updates():
  return render_template('7_news/updates.html', **session)
  
@app.route('/veryencryptedapiendpoint/signup', methods=['POST'])
def signup_api():
    form = request.form
    success, message = signup_account(**dict(form))
    if success:
        return redirect('/')
    else:
        session['signup_error_message'] = message
        return redirect('/signup')
        
@app.route('/login')
def login():
    message = ""
    try:
        message = session['login_error_message']
        session.pop('login_error_message')
    except:
        pass
    try:
        if session['logged_in']:
            return redirect('/dashboard')
    except:
        pass
    return render_template('8_user/login.html', message=message, **session)

@app.route('/veryencryptedapiendpoint/login', methods=['POST'])
def login_api():
    form = request.form
    username = form['username']
    password = form['password']
    try:
        login_success = login_account(username, password)
    except:
        login_success = False
    if login_success:
        session['logged_in'] = True
        session['username'] = username
        return redirect('/dashboard')
    else:
        session['login_error_message'] = "No account found with these credentials!"
        return redirect('/login')
    return

@app.route('/team-comp/create')
def comp_create():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    message = None
    try:
        message = session['create_error_message']
    except:
        pass
    return render_template('/3_competitions/team_data/make_comp.html', message=message, **session)

@app.route('/lnsgames/hangman/')
def lns_hangman():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    message = None
    try:
        message = session['create_error_message']
    except:
        pass
    return render_template('/5_games/hangman.html', message=message, **session)

@app.route('/lnsgames/typerace/')
def lns_typerace():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    message = None
    try:
        message = session['create_error_message']
    except:
        pass
    return render_template('/5_games/typerace.html', message=message, **session)

@app.route('/player-comp/create')
def player_comp_create():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    message = None
    try:
        message = session['create_error_message']
    except:
        pass
    return render_template('3_competitions/player_data/make_player_comp.html', message=message, **session)

@app.route('/account/settings')
def account_settings():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    message = None
    try:
        message = session['create_error_message']
    except:
        pass
    return render_template('in_work/settings.html', message=message, **session)
  
@app.route('/veryencryptedapiendpoint/team-comp/create', methods=['POST'])
def create_api():
    try:
      print(request.form['public-or-private'])
      public = "True"
    except:
      public = "False"
    timetype = request.form['timetype']
    thetime = int(request.form['timeamount'])
    endcomptime = round(time.time())
    if timetype == 'months':
        endcomptime += 2592000*int(thetime)
    if timetype == 'days':
        endcomptime += 86400*int(thetime)
    if timetype == 'hours':
        endcomptime += 3600*int(thetime)
    if timetype == 'minutes':
        endcomptime += 60*int(thetime)
    while True:
        compid = ''.join(random.choices(list(string.ascii_letters+string.digits), k=8))
        team = request.form['team']
        try:
            try:
                session['userid']
                success, message = create_comp(compid, team, endcomptime, user=session['userid'])
            except:
                success, message = create_comp(compid, team, endcomptime, user=session['username'])
            if success:
                return redirect(f'/team-comp/{compid}')
            if not success and message == 'Compid already exists!':
                continue
            else:
                session['create_error_message'] = message
                return redirect('/create')
        except Exception as e:
            raise e


@app.route('/veryencryptedapiendpoint/player-comp/create', methods=['POST'])
def player_create_api():
    timetype = request.form['timetype']
    thetime = int(request.form['timeamount'])
    endcomptime = round(time.time())
    if timetype == 'months':
        endcomptime += 2592000*int(thetime)
    if timetype == 'days':
        endcomptime += 86400*int(thetime)
    if timetype == 'hours':
        endcomptime += 3600*int(thetime)
    if timetype == 'minutes':
        endcomptime += 60*int(thetime)
    while True:
        compid = ''.join(random.choices(list(string.ascii_letters+string.digits), k=8))
        racer = request.form['racer']
        try:
            try:
                session['userid']
                success, message = create_player_comp(compid, racer, endcomptime, user=session['userid'])
            except:
                success, message = create_player_comp(compid, racer, endcomptime, user=session['username'])
            if success:
                return redirect(f'/player-comp/{compid}')
            if not success and message == 'Compid already exists!':
                continue
            else:
                session['create_error_message'] = message
                return redirect('/player_create')
        except Exception as e:
            raise e


@app.route('/veryencryptedapiendpoint/team-comp/invite', methods=['POST'])
def create_invite_api():
    data = json.loads(request.data.decode())
    username = data['username']
    compid = data['compid']
    try:
        invite_user(compid, username)
        return(f'{data["username"]} has been invited to view this competition.')
    except Exception as e:
        return str(e)


@app.route('/team-comp/invite/{compid}')
def comp_invite():
    try:
        if not session['logged_in']:
            return redirect('/login')
    except:
        return redirect('/login')
    message = None
    try:
        message = session['create_error_message']
    except:
        pass
    return render_template('/3_competitions/team_data/comp_page.html', message=message, invite_user=invite_user, **session)
  
          
@app.route('/veryencryptedapiendpoint/delete', methods=['POST'])
def delete_api():
    compid = request.form['compid']
    print(delete_comp(compid, session))
    return 'ok'


def delete_player_comp_api():
    compid = request.form['compid']
    print(delete_comp(compid, session))
    return 'ok'

def bkg_player_task():
    while True:
        player_comps, dbclient = get_all_player_comps({'other.ended': False})
        for x in player_comps:
            if round(time.time()) < x['other']['endcomptime']:
                update_comp(x, dbclient)
                continue
            else:
                x['other']['ended'] = True
                update_player_comp(x, dbclient)
        print('Updated All Comps - '+str(int(time.time())))
        time.sleep(60)
      
def bkg_task():
    while True:
        comps, dbclient = get_all_comps({'other.ended': False})
        for x in comps:
            if round(time.time()) < x['other']['endcomptime']:
                update_comp(x, dbclient)
                continue
            else:
                x['other']['ended'] = True
                update_comp(x, dbclient)
        print('[+] Updated All Comps - '+str(int(time.time())))
        time.sleep(60)
thread = threading.Thread(target=bkg_task)
thread.start()
app.run(host='0.0.0.0')
'''