from backend.resources.database import DBClient
import hashlib, os
def login_account(username, password):
    dbclient = DBClient()
    collection = dbclient.db.accounts
    account = dbclient.get_array(collection, {'username': username})
    salt = hashlib.pbkdf2_hmac('sha256', account['salt'], os.environ['salt_key'].encode(), 5000).hex().encode()
    check_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 20000).hex()
    return check_password == account['psw']
def discord_login(userid):
    dbclient = DBClient()
    collection = dbclient.db.accounts
    account = dbclient.get_array(collection, {'username': str(userid), 'discord_account': True})
    return True if account else False