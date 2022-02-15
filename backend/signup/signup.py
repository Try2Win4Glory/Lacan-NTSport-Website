from backend.resources.database import DBClient
import hashlib, os
def signup_account(**kwargs):
    dbclient = DBClient()
    collection = dbclient.db.accounts
    try:
        trytofind = dbclient.get_array(collection, {"username": kwargs['username']})
        trytofind['username']
        return False, "This username is already taken!"
    except:
        pass
    kwargs['salt'] = os.urandom(64)
    kwargs.pop('psw-repeat')
    salt = hashlib.pbkdf2_hmac('sha256', kwargs['salt'], os.environ['salt_key'].encode(), 5000).hex().encode()
    kwargs['psw'] = hashlib.pbkdf2_hmac('sha256', kwargs['psw'].encode(), salt, 20000).hex()
    dbclient.create_doc(collection, kwargs)
    return True, ''
def discord_signup(userid):
    dbclient = DBClient()
    collection = dbclient.db.accounts
    account = dbclient.get_array(collection, {'username': str(userid), 'discord_account': True})
    if account:
        return True, ''
    data = {}
    data['username'] = str(userid)
    data['discord_account'] = True
    dbclient.create_doc(collection, data)
    return True, ''