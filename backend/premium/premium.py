from flask import session
from backend.resources.database import DBClient
dbclient = DBClient()
def get_premium_data(user):
  collection = dbclient.db.accounts
  data = dbclient.get_array(collection, {'username': session['username']})
  return data, dbclient
def check_for_premium(user):
  data, dbclient = get_premium_data(user)
  premium = data['premium']
  expiresIn = data['expiresIn']
  return premium, expiresIn
def get_all_accounts(args):
  collection = dbclient.db.accounts
  data = dbclient.get_many(collection, {'premium': True})
  return data