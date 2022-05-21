from backend.resources.database import DBClient
import hashlib, copy
import asyncio
async def change_password(username, new_password):
    dbclient = DBClient()
    collection = dbclient.db.users
    data = await dbclient.get_array(collection, {'username': username})
    for x in data:
        old = copy.deepcopy(x)
        new_password = hashlib.pbkdf2_hmac('sha256', new_password.encode(), x['salt'], 20000).hex()
        if new_password == x['password']:
            return False, "You didn't change your password!"
        x['password'] = new_password
        await dbclient.update_array(collection, old, x)
        return True, ""
def change_password(username, password):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return asyncio.run(_change_password(username, password))