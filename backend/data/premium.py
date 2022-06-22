import nitrotype, urllib
from bs4 import BeautifulSoup
import json
import re
from backend.resources.database import DBClient
import os
import time
class BankAccount:
    def __init__(self):
        self.session = nitrotype.Racer('travis').requests
        self.password = os.getenv('password')
        self.username = 'almightyone1'
        self.logged_in = False
    def login(self):
        req = self.session.post('https://test.nitromath.com/api/v2/auth/login/username', data={'username': self.username, 'password': self.password})
        self.data = req.json()
        self.token = self.data['results']['token']
        self.logged_in = True
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded', "Authorization": "Bearer "+self.token}
    def get_user_id(self, racer):

        newdata = {}
        response = requests.get(
            f'https://www.nitrotype.com/racer/{racer}').content
        soup = BeautifulSoup(response, 'html5lib')
        for script in soup.find('head'):
            if 'RACER_INFO' in str(script):
                newdata = json.loads(re.findall('{".+}', str(script))[0])
                newdata = json.loads(re.findall('{".+}', str(script))[0])
        if newdata == {}:
            self.success = False
            return
        return newdata['userID']

    def check_cash_received(self):
        if self.logged_in == False:
            self.login()
        received = self.session.post('https://test.nitromath.com/api/v2/players/receive-cash', headers=self.headers).json()
        return received
    def check_friend_requests(self):
        if self.logged_in == False:
            self.login()
        received = self.session.get('https://test.nitromath.com/api/v2/friend-requests', headers=self.headers)
        return received

    def send_cash(self, username, amount):
        if self.logged_in == False:
            self.login()
        sendto_id = self.get_user_id(username)
        data = f"amount={amount}&password={urllib.parse.quote(self.password)}&playersCash={str(self.data['data']['money'])}&recipient={sendto_id}&feePercent=0"
        self.session.post(
            f'https://test.nitromath.com/api/v2/friends/{sendto_id}/send-cash',
            data=data, headers=self.headers).text

    def cash_received(self, username, amount):
        data = {'username': username, 'amount': amount, 'claimed': False}
        dbclient = DBClient()
        dbclient.create_doc(dbclient.db.cash, data)

    def check_cash(self, username, ntuser):
        dbclient = DBClient()
        docs = list(dbclient.db.cash.find({"claimed": False, "username": ntuser}))
        total = 0
        for doc in docs:
            total += int(doc["amount"])
        if total >= 100000:
            dbclient.db.cash.update_many({"username":ntuser, "claimed":False}, {"$set": {"claimed":True}})
            dbclient.db.accounts.update_one({"username": username}, {"$set": {"premium":True, "expiresIn":time.time()+2592000}})
            return True
        else:
            return False