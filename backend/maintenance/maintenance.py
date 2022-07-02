from backend.resources.database import DBClient
from flask import session


def maintenance_function(maintenance, permission):
    dbclient = DBClient()
    maintenance_collection = dbclient.db.maintenance
    maintenance_data = dbclient.get_array(maintenance_collection,{"success": True})
    maintenance = maintenance_data["maintenance"]
    if maintenance_data['maintenance'] == True:
        permission_collection = dbclient.db.maintenance_permission
        permission_data = dbclient.get_array(permission_collection,{"success": True})
        #print(permission_data['permission'])
        try:
            if session['username'] in permission_data['permission']:
                permission = True
            else:
                permission = False
        except:
            permission = None
    else:
        permission = None
    return maintenance, permission
