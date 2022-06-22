'''

def send_cash(self, username, amount):
        if self.logged_in == False:
            self.login()
        sendto_id = self.get_user_id(username)
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = self.session.sesh.cookies
        uhash = cookies['ntuserrem']
        data = f"amount={amount}&password={urllib.parse.quote(self.password)}&playersCash={str(self.data['data']['money'])}&recipient={sendto_id}&feePercent=0&uhash={uhash}"
        self.session.post(
            f'https://www.nitrotype.com/api/friends/{sendto_id}/sendcash',
            data=data, headers=headers).text

    def check_cash_received(self):
        if self.logged_in == False:
            self.login()
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        cookies = self.session.sesh.cookies
        uhash = cookies['ntuserrem']
        received = self.session.post('https://www.nitrotype.com/api/items/cash-gifts', data=f'uhash={uhash}', headers=headers)
        return received
    def check_friend_requests(self):
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
        if self.logged_in == False:
            self.login()
        received = self.session.get('https://www.nitrotype.com/api/friend-requests', headers=headers)
        return received

def __init__(self):
        self.session = requests.RequestsSession()
        self.password = os.environ['password']
        self.username = '<whatever account we decide to use>'
        self.logged_in = False
    def login(self):
        req = self.session.post('https://www.nitrotype.com/api/login', data={'username': '<whatever username>', 'password': self.password})
        self.data = req
        self.logged_in = True
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