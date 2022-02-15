from flask import Flask, render_template, request, redirect, session
from backend.data.comp import leaderboards, create_comp, find_comps_by_username, get_comp_data, delete_comp, update_comp, get_all_comps, bkg_task, invite_user

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
    return render_template('home.html', **session)


@app.route('/discordlogin')
def discordlogin():
    return discord.create_session(scope=['identify'])
    
@app.route('/discordsignup')
def discordsignup():
    session['discord_signup'] = True
    return discord.create_session(scope=['identify'])  


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
        return redirect('/dashboard')
def comp_html(compid):
    data = get_comp_data(compid)[0]
    try:
        if str(data['other']['public']) != "True":
          if session['logged_in'] and str(session['username']) != str(data['other']['author']):
            return redirect('/invalid-comp')
          else:
            pass
        else:
          pass
    except:
        return redirect('/invalid-comp')
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
    return render_template('comp_page.html', players=lb, link=f'https://Official-LNS-Website.a1sauces.repl.co/team-comp/{compid}', hours=hours, minutes=minutes, seconds=seconds, team=data['other']['team'], get_money=get_money)

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
    return render_template('player_comp.html', players=lb, link=f'https://Official-LNS-Website.a1sauces.repl.co/player-comp/{compid}', hours=hours, minutes=minutes, seconds=seconds, racer=data['other']['racer'], get_money=get_money)

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
    return render_template('stats_page.html', session=session, comps=comps)

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
    return render_template('dashboard.html', session=session, comps=comps, time=time)

@app.route('/stocks',methods = ['POST', 'GET'])
def stocks():
  if request.method == 'POST':
    result = request.form
  return render_template("stocks.html",result = result)

@app.route('/lnschat/')
def lnschat():
  return render_template('lnschat.html')

@app.route('/racer-stats/')
def stats():
  return render_template('stats.html')

@app.route('/customcomp/<id>')
def custom_comp(id):
    if int(id) == 1:
        return comp_html("06926861")

@app.route('/commands/')
def commands():
  return render_template('/commands.html')

@app.route('/privacy/')
def privacy():
  return render_template('/privacy.html')

@app.route('/invite/')
def invite():
  return render_template('/invite.html')

@app.route('/support/')
def support():
  return render_template('/support.html')

@app.route('/team/')
def team():
  return render_template('/team.html')

@app.route('/veryencryptedapiendpoint/logout')
def logout_api():
    session.clear()
    return redirect('/')
    
@app.route('/signup')
def signup():
    message = ""
    try:
        message = session['signup_error_message'].copy()
        session.pop('signup_error_message')
    except:
        pass
    return render_template('signup.html', message=message)

@app.route('/team-comp/<compid>')
def comp(compid):
    return comp_html(compid)

@app.route('/invalid-comp/')
def invalid_comp():
    return render_template('/comp_invalid.html')


@app.route('/player-comp/<compid>')
def player_comp(compid):
    return player_comp_html(compid)

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
    return render_template('login.html', message=message)

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
    return render_template('make_comp.html', message=message)

@app.route('/lnsgames/hangman')
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
    return render_template('/games/hangman.html', message=message)

@app.route('/lnsgames/typerace')
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
    return render_template('/games/typerace.html', message=message)

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
    return render_template('player_data/make_player_comp.html', message=message)

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
    return render_template('settings.html', message=message)
  
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
    username = request.form['username']
    while True:
        compid = ''.join(random.choices(list(string.ascii_letters+string.digits), k=8))
        username = request.form['username']
        try:
            try:
                session['userid']
                success, message = create_invite_link(compid, username, user=session['userid'])
            except:
                success, message = create_invite_link(compid, username, user=session['username'])
            if success:
                return redirect(f'/team-comp/invite/{compid}-{{session.username}}')
            if not success and message == 'Invite ID already exists!':
                continue
            else:
                session['create_error_message'] = message
                return redirect('/')
        except Exception as e:
            raise e

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
    return render_template('comp_page.html', message=message, invite_user=invite_user)
  

@app.route('/nitrotype/calculator')
def calculate():
  return render_template('/resources/nt_calculator.html')
          
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