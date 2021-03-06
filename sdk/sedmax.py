import json
import requests
import pandas as pd


class Sedmax:

    def __init__(self, host='http://127.0.0.1'):
        self.host = host
        self.token = None
        self.username = None
        self.password = None

    def login(self, username, password):
        r = requests.post(
            self.host + '/sedmax/auth/login',
            data=json.dumps({'Login': username, 'Password': password})
        )

        if r.status_code == 200:
            self.token = r.cookies.get_dict()["jwt"]
            self.username = username
            self.password = password
        else:
            raise Exception(f'Status code: {r.status_code}. {r.json()["message"]}')

    def update_token(self):
        if self.username is not None and self.password is not None:
            r = requests.post(
                self.host + '/sedmax/auth/login',
                data=json.dumps({'Login': self.username, 'Password': self.password})
            )
            if r.status_code == 200:
                self.token = r.cookies.get_dict()["jwt"]
            else:
                raise Exception(f'Status code: {r.status_code}, message: {r.json()["message"]}')
        else:
            raise Exception(f'Need to login first. Use login("username", "password") method.')

    def get_token(self):
        return self.token

    def get_url(self):
        return self.host

    def get_data(self, url, request):
        r = requests.post(
            url,
            json=request,
            cookies={'jwt': self.token}
        )

        if r.status_code == 200:
            return r.json()
        elif r.status_code == 401 or r.status_code == 403:
            self.update_token()
            new_r = requests.post(
                url,
                json=request,
                cookies={'jwt': self.token}
            )
            if new_r.status_code == 200:
                return new_r.json()
            else:
                raise Exception(f'Status code: {r.status_code}, message: {r.json()["message"]}')
        else:
            raise Exception(f'Status code: {r.status_code}, message: {r.json()["message"]}')

    def categories(self):
        url = self.host + '/sedmax/web/archive/categories'
        request = {}
        r = self.get_data(url, request)
        return r['categories']

    def devices_tree(self):
        url = self.host + '/sedmax/web/archive/devices_tree'
        df = pd.DataFrame()
        for category in ['electro', 'energy', 'emission']:
            data = self.get_data(url, {'category': category})
            data = pd.DataFrame(data['treeObject'])
            data['category'] = category
            df = pd.concat([df, data]).reset_index(drop=True)

        return df

    def devices_list(self, nodes):
        if type(nodes) is not list:
            raise Exception(f'Nodes expected to be a "list" type, got {type(nodes)} instead')

        url = self.host + '/sedmax/devices_configurator/devices/list'
        request = {
            'limit': 0,
            'nodes': nodes,
            'offset': 0
        }
        r = self.get_data(url, request)

        return pd.DataFrame(r['devices'])

    def ti_list(self, nodes):
        if type(nodes) is not list:
            raise Exception(f'Nodes expected to be a "list" type, got {type(nodes)} instead')

        url = self.host + '/sedmax/devices_configurator/ti/list'
        request = {
            'nodes': nodes,
        }
        r = self.get_data(url, request)

        return pd.DataFrame(r['ti'])

#s.electro.get_electro_data([{'device': 101, 'channel': "ea_imp"}],period="30min",begin='2021-01-24',end='2021-01-26')
 #s.electro.get_data(["dev-101_ea_imp"],period=["30min"],begin='2021-01-24',end='2021-01-26')


