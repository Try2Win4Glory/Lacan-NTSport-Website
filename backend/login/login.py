import copy
from backend.resources.database import DBClient
import hashlib, os
def login_account(username, password):
    dbclient = DBClient()
    collection = dbclient.db.accounts
    account = dbclient.get_array(collection, {'username': username})
    salt = hashlib.pbkdf2_hmac('sha256', account['salt'], os.environ['salt_key'].encode(), 5000).hex().encode()
    check_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 20000).hex()
  
    '''# Auto Add these fields into the account section upon logging in:
    old = copy.deepcopy(account)
    account["premium"] = False
    account["expiresIn"] = 0
    dbclient.update_array(collection, old, account)'''
  
    return check_password == account['psw']

'''
# Quickly add new inserts to all accounts:
def add_to_everyone():
  dbclient = DBClient()
  collection = dbclient.db.accounts
  for account in collection.find():
    old = copy.deepcopy(account)
    account['premium'] = False
    account['expiresIn'] = 0
    dbclient.update_array(collection, old, account)
  return "success"'''


def discord_login(userid):
    dbclient = DBClient()
    collection = dbclient.db.accounts
    account = dbclient.get_array(collection, {'username': str(userid), 'discord_account': True})
    return True if account else False