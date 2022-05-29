#DO NOT RUN THE PROGRAM!
#pip install cloudscraper==1.2.58
import os

#os.system("pip install cloudscraper==1.2.58")

'''os.system("pip install zipp==3.4.1")
os.system("pip install zipp==3.8.0")

os.system("pip install click==8.0.1")
os.system("pip install click==8.1.3")

os.system("pip install h2==4.1.0")

os.system("pip install importlib-metadata==3.10.1")
os.system("pip install importlib-metadata==4.11.3")'''



from flask import Flask, render_template, request, redirect, session, send_file
from backend.data.comp import leaderboards, create_comp, find_comps_by_username, find_comps_by_invite, find_comps_by_multiplayer, find_comps_by_scheduled, get_comp_data, delete_comp, update_comp, get_all_comps, bkg_task, invite_user, timestamp, convert_secs, get_all_cars
from backend.settings.password import change_password

from backend.data.player import get_all_player_comps, create_player_comp, update_player_comp, player_leaderboards, get_player_comp_data, delete_player_comp, find_player_comps_by_username, add_player, remove_player_from_comp, player_bkg_task

from backend.maintenance.maintenance import maintenance_function

'''
from backend.data.player import create_player_comp
from backend.data.player import update_player_comp 
from backend.data.player import player_leaderboard 
from backend.data.player import get_player_comp_data
'''

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
app.config["DISCORD_REDIRECT_URI"] = "https://ntsport.xyz/oauth/callback"

discord = DiscordOAuth2Session(app)
  
@app.route('/coming-soon/')
def coming_soon():
  return render_template('1_home/comingsoon.html', **session)
  
@app.route('/')
def home():
    return render_template('/1_home/home.html', **session)

@app.route("/user/<name>")
def user_route(name):
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return

@app.route('/discordlogin')
def discordlogin():
    return discord.create_session(scope=['identify'], **session)
    
@app.route('/oauth/discordsignup')
def discordsignup():
    session['discord_signup'] = True
    return discord.create_session(scope=['identify'], **session)  


@app.route("/callback/")
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
def comp_body_html(compid):
    data = get_comp_data(compid)[0]
    if data == None:
        return redirect('/invalid-comp')
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
    return render_template("3_competitions/team_data/comp_body.html", players=lb)
@app.route('/veryencryptedapiendpoint/team-comp/<compid>')
def comp_data(compid):
    return comp_body_html(compid)
def comp_html(compid):
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    data = get_comp_data(compid)[0]
    if data == None:
        return redirect('/invalid-comp')
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
    return render_template('/3_competitions/team_data/comp_page.html', players=lb, link=f'https://ntsport.xyz/team-comp/{compid}', hours=hours, minutes=minutes, seconds=seconds, team=data['other']['team'], compdesc=compdesc, get_money=get_money, compid=compid, isauthor=isauthor, allowed=data['allowed'], **session)

def player_comp_html(compid):
    args = request.args
    try:
        should_update = session['update_'+compid]
    except:
        should_update = True
    session['update_'+compid] = True
    try:
        sortby = args['sortby']
        if sortby == 'races':
            lb = player_leaderboards(compid, 'races', should_update)
        if sortby == 'wpm':
            lb = player_leaderboards(compid, 'speed', should_update)
        if sortby == 'acc':
            lb = player_leaderboards(compid, 'accuracy', should_update)
        if sortby == 'points':
            lb = player_leaderboards(compid, 'points', should_update)
    except:
        lb = player_leaderboards(compid, 'races', should_update)
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
    return render_template('3_competitions/player_data/player_comp.html', players=lb, link=f'https://ntsport.xyz/player-comp/{compid}', hours=hours, minutes=minutes, seconds=seconds, racer=data['other']['player'], get_money=get_money, isauthor=isauthor, allowed=data['allowed'], compid=compid, **session)


@app.route('/statistics/player/')
def stats_player():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
    try:
        session['userid']
        scomps = find_comps_by_scheduled(int(session['userid']))
    except:
        scomps = find_comps_by_scheduled(session['username'])
    try:
      try:
        mcomps = find_comps_by_invite(int(session['userid']))
      except:
        mcomps = find_comps_by_invite(session['username'])
      try:
        player_comps = find_player_comps_by_username(int(session['userid']))
      except:
        player_comps = find_player_comps_by_username(session['username'])
    except Exception as e:
      print(e)
    return render_template('/1_home/dashboard.html', session=session, comps=comps, mcomps=mcomps, player_comps = player_comps, time=time, datetime=datetime, timestamp=timestamp, convert_secs=convert_secs, scomps=scomps, **session)


@app.route('/lnschat/')
def lnschat():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('6_other/lnschat.html', **session)

@app.route('/nt-spoilers/')
def lns_spoiler():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('6_other/spoiler.html', **session)

@app.route('/racer-stats/')
def stats():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('4_stats/stats.html', **session)

@app.route('/user_search/')
def user_search():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('4_stats/user_search.html', **session)

@app.route('/customcomp/<id>')
def custom_comp(id):
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    if int(id) == 1:
        return comp_html("06926861")

@app.route('/head/')
def head():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('general/head.html', **session)

@app.route('/commands/')
def commands():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('2_bot/commands.html', **session)

@app.route('/blitz/')
def blitz():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('nt_resources/seasons/sect-blitz.html', **session)


@app.route('/newsletter-subscribe/')
def newsletter():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('2_bot/newsletter.html', **session)


@app.route('/privacy/')
def privacy():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('2_bot/privacy.html', **session)

@app.route('/view-comps/')
def view_comps():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('in_work/cards.html', **session)

@app.route('/lnsgames/slotmachine')
def wheel():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('in_work/slot.html', **session)

@app.route('/lnsgames/spin-the-wheel')
def slot():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('in_work/wheel.html', **session)

@app.route('/lnsgames/memory')
def memory():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('in_work/memory.html', **session)

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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('2_bot/team.html', **session)
  
@app.route('/calculator/')
def ntcalculator():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('nt_resources/calculator.html', **session)

@app.route('/season/0.5/')
def season05():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('nt_resources/seasons/season0.5.html', **session)

@app.route('/season/1/')
def season1():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('nt_resources/seasons/season1.html', **session)

@app.route('/veryencryptedapiendpoint/logout')
def logout_api():
    session.clear()
    return redirect('/')
    
@app.route('/signup/')
def signup():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    try:
      print('This User Tried to Signup: '+session['username'])
      return redirect('/dashboard')
    except:
      pass
    message = ""
    try:
        message = session['signup_error_message'].copy()
        session.pop('signup_error_message')
    except:
        pass
    return render_template('8_user/signup.html', message=message, **session)

@app.route('/team-comp/<compid>')
def comp(compid):
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return comp_html(compid)

@app.route('/invalid-comp/')
def invalid_comp():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('/3_competitions/invalid/comp_invalid.html', **session)

@app.route('/lnsgames/shop/')
def lns_shop():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
    return render_template('/5_games/shop.html', message=message, **session)

@app.route('/player-comp/<compid>')
def player_comp(compid):
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return player_comp_html(compid)

@app.route('/news/')
def news():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    return render_template('7_news/news.html', **session)

@app.route('/updates/')
def updates():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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

@app.route('/veryencryptedapiendpoint/settings/password', methods=['POST'])
def settings_password():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    try:
        logged_in = session['logged_in']
    except:
        return 'You are not logged in!'
    if not logged_in:
        return 'You are not logged in!'
    form = request.form
    if form['current_password'] == form['new_password']:
        session['password_change_success'] = False
        session['password_change_message'] = "Your current and new password are the same thing!"
        return redirect('/settings')
    if form['new_password'] != form['confirm_password']:
        session['password_change_success'] = False
        session['password_change_message'] = "The new password and the confirm password are different!"
        return redirect('/stocks')
    else:
        success, message = change_password(session['username'], form['new_password'])
        session['username_change_success'] = success
        session['username_change_message'] = message
    return redirect('/dashboard')

@app.route('/team-comp/create')
def comp_create():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    try:
      (request.form['public-or-private'])
      public = "True"
    except:
      public = "False"

    no_data = False
    if request.form['start-timestamp'] == "":
        start_timestamp = time.time()
        no_data = True
    else:
        start_timestamp = int(request.form['start-timestamp'])/1000
    timetype = request.form['timetype']
    thetime = int(request.form['timeamount'])
    endcomptime = int(start_timestamp)
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
                success, message = create_comp(compid, team, start_timestamp, endcomptime, user=session['userid'], no_data=no_data)
            except:
                success, message = create_comp(compid, team, start_timestamp, endcomptime, user=session['username'], no_data=no_data)
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
                return redirect('/player_create/')
        except Exception as e:
            raise e


@app.route('/veryencryptedapiendpoint/team-comp/invite', methods=['POST'])
def create_invite_api():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    data = json.loads(request.data.decode())
    username = data['username']
    compid = data['compid']
    try:
        invite_user(compid, username)
        return(f'{data["username"]} has been invited to view this competition.')
    except Exception as e:
        return str(e)

@app.route('/veryencryptedapiendpoint/player-comp/add', methods=['POST'])
def add_player_api():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    data = json.loads(request.data.decode())
    #print(data)
    username = data['username']
    compid = data['compid']
    try:
        add_player(username, compid)
        session['update_'+compid] = False
        return(f'{data["username"]} has been added to this competition.')
    except Exception as e:
        return str(e)

@app.route('/veryencryptedapiendpoint/player-comp/remove', methods=['POST'])
def remove_player_api():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    data = json.loads(request.data.decode())
    #print(data)
    players = data['players']
    compid = data['compid']
    try:
        remove_player(username, compid)
        session['update_'+compid] = False
        return(f'{data["players"]} has been added to this competition.')
    except Exception as e:
        return str(e)

      
@app.route('/team-comp/invite/{compid}')
def comp_invite():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
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
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    compid = request.form['compid']
    print(delete_comp(compid, session))
    return 'ok'

@app.route('/veryencryptedapiendpoint/deleteplayercomp', methods=['POST'])
def deleteplayer_comp_api():
  if maintenance_function('maintenance', 'permission')[0] == True and maintenance_function('maintenance','permission')[1] != True:
    return redirect('/coming-soon')
  else:
    compid = request.form['compid']
    print(delete_player_comp(compid, session))
    return 'ok'

def delete_player_comp_api():
    compid = request.form['compid']
    print(delete_comp(compid, session))
    return 'ok'

@app.route('/cars/<file>')
def return_car_and_cache(file):
    import nitrotype
    from os.path import exists
    file_exists = exists('cars/'+file)
    if file_exists:
        return send_file('cars/'+file)
    requests = nitrotype.Racer('tranq_').requests
    bytes = requests.get('https://www.nitrotype.com/cars/'+file).content
    with open('cars/'+file, 'wb') as f:
        f.write(bytes)
    return send_file('cars/'+file)

@app.route('/cars/painted/<file>')
def return_car_painted_and_cache(file):
    import nitrotype
    from os.path import exists
    file_exists = exists('cars/painted/'+file)
    if file_exists:
        return send_file('cars/painted/'+file)
    requests = nitrotype.Racer('tranq_').requests
    bytes = requests.get('https://www.nitrotype.com/cars/painted/'+file).content
    with open('cars/painted/'+file, 'wb') as f:
        f.write(bytes)
    return send_file('cars/painted/'+file)
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
        comps, dbclient = get_all_comps(
            {
                'other.ended': False, "$and": [ {"other.startcomptime": {"$lt":time.time()}}, {"other.endcomptime": {"$gt": time.time()}}]
            })
        for x in comps:
            #print(x["compid"])
            if round(time.time()) < x['other']['endcomptime']:
                update_comp(x, dbclient)
                continue
            else:
                x['other']['ended'] = True
                update_comp(x, dbclient)
        print('[+] Updated All Team Comps - '+str(int(time.time())))
        time.sleep(60)
thread = threading.Thread(target=bkg_task)
thread.start()
thread1 = threading.Thread(target=player_bkg_task)
thread1.start()
app.run(host='0.0.0.0')