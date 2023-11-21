import ast
import base64
import json
import os
import pickle
import random
import re
import ssl
import time
import traceback

import capmonster_python
import cloudscraper
import requests
from bs4 import BeautifulSoup
from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from fake_useragent import UserAgent
from web3.auto import w3

from Rescue_Site_System.ReadyFiles.utils import twitter_tasks
from Rescue_Site_System.ReadyFiles.utils import bcolors

def random_user_agent():
    browser_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_{2}_{3}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{1}.{2}) Gecko/20100101 Firefox/{1}.{2}',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{0}.{1}.{2} Edge/{3}.{4}.{5}'
    ]

    chrome_version = random.randint(70, 108)
    firefox_version = random.randint(70, 108)
    safari_version = random.randint(605, 610)
    edge_version = random.randint(15, 99)

    chrome_build = random.randint(1000, 9999)
    firefox_build = random.randint(1, 100)
    safari_build = random.randint(1, 50)
    edge_build = random.randint(1000, 9999)

    browser_choice = random.choice(browser_list)
    user_agent = browser_choice.format(chrome_version, firefox_version, safari_version, edge_version, chrome_build, firefox_build, safari_build, edge_build)

    return user_agent


class Discord:

    def __init__(self, token, proxy, cap_key):

        self.cap = capmonster_python.HCaptchaTask(cap_key)
        self.token = token
        self.proxy = proxy

        # print(token)
        # print(proxy)
        # print(cap_key)

        self.session = self._make_scraper()
        self.ua = random_user_agent()
        self.session.user_agent = self.ua
        self.super_properties = self.build_xsp(self.ua)

        self.cfruid, self.dcfduid, self.sdcfduid = self.fetch_cookies(self.ua)
        self.fingerprint = self.get_fingerprint()


    def JoinServer(self, invite):

        rer = self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token})

        # print(rer.text, rer.status_code)
        # print(rer.text)
        # print(rer.status_code)

        if "200" not in str(rer):
            site = "a9b5fb07-92ff-493f-86fe-352a2803b3df"
            tt = self.cap.create_task("https://discord.com/api/v9/invites/" + invite, site)
            # print(f"Created Captcha Task {tt}")
            captcha = self.cap.join_task_result(tt)
            captcha = captcha["gRecaptchaResponse"]
            # print(f"[+] Solved Captcha ")
            # print(rer.text)

            self.session.headers = {'Host': 'discord.com', 'Connection': 'keep-alive',
                               'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
                               'X-Super-Properties': self.super_properties,
                               'Accept-Language': 'en-US', 'sec-ch-ua-mobile': '?0',
                               "User-Agent": self.ua,
                               'Content-Type': 'application/json', 'Authorization': 'undefined', 'Accept': '*/*',
                               'Origin': 'https://discord.com', 'Sec-Fetch-Site': 'same-origin',
                               'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty',
                               'Referer': 'https://discord.com/@me', 'X-Debug-Options': 'bugReporterEnabled',
                               'Accept-Encoding': 'gzip, deflate, br',
                               'x-fingerprint': self.fingerprint,
                               'Cookie': f'__dcfduid={self.dcfduid}; __sdcfduid={self.sdcfduid}; __cfruid={self.cfruid}; __cf_bm=DFyh.5fqTsl1JGyPo1ZFMdVTupwgqC18groNZfskp4Y-1672630835-0-Aci0Zz919JihARnJlA6o9q4m5rYoulDy/8BGsdwEUE843qD8gAm4OJsbBD5KKKLTRHhpV0QZybU0MrBBtEx369QIGGjwAEOHg0cLguk2EBkWM0YSTOqE63UXBiP0xqHGmRQ5uJ7hs8TO1Ylj2QlGscA='}
            rej = self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token}, json={
                "captcha_key": captcha,
                "captcha_rqtoken": str(rer.json()["captcha_rqtoken"])
            })
            # print(rej.text())
            # print(rej.status_code)
            if "200" in str(rej):
                return 'Successfully Join 0'
            if "200" not in str(rej):
                return 'Failed Join'

        else:
            with self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token}) as response:
                # print(response.text)
                pass
            return 'Successfully Join 1'


    def _make_scraper(self):
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )

    def build_xsp(self, ua):
        # ua = get_useragent()
        _,fv = self.get_version(ua)
        data = json.dumps({
            "os": "Windows",
            "browser": "Chrome",
            "device": "",
            "system_locale": "en-US",
            "browser_user_agent": ua,
            "browser_version": fv,
            "os_version": "10",
            "referrer": "",
            "referring_domain": "",
            "referrer_current": "",
            "referring_domain_current": "",
            "release_channel": "stable",
            "client_build_number": self.get_buildnumber(),
            "client_event_source": None
        }, separators=(",",":"))
        return base64.b64encode(data.encode()).decode()

    def get_version(self, user_agent):  # Just splits user agent
        chrome_version = user_agent.split("/")[3].split(".")[0]
        full_chrome_version = user_agent.split("/")[3].split(" ")[0]
        return chrome_version, full_chrome_version

    def get_buildnumber(self):  # Todo: make it permanently work
        r = requests.get('https://discord.com/app', headers={'User-Agent': 'Mozilla/5.0'})
        asset = re.findall(r'([a-zA-z0-9]+)\.js', r.text)[-2]
        assetFileRequest = requests.get(f'https://discord.com/assets/{asset}.js',
                                        headers={'User-Agent': 'Mozilla/5.0'}).text
        try:
            build_info_regex = re.compile('buildNumber:"[0-9]+"')
            build_info_strings = build_info_regex.findall(assetFileRequest)[0].replace(' ', '').split(',')
        except:
            # print("[-]: Failed to get build number")
            pass
        dbm = build_info_strings[0].split(':')[-1]
        return int(dbm.replace('"', ""))

    def fetch_cookies(self, ua):
        try:
            url = 'https://discord.com/'
            headers = {'user-agent': ua}
            response = self.session.get(url, headers=headers, proxies=self.proxy)
            cookies = response.cookies.get_dict()
            cfruid = cookies.get("__cfruid")
            dcfduid = cookies.get("__dcfduid")
            sdcfduid = cookies.get("__sdcfduid")
            return cfruid, dcfduid, sdcfduid
        except:
            # print(response.text)
            return 1

    def get_fingerprint(self):
        try:
            fingerprint = self.session.get('https://discord.com/api/v9/experiments', proxies=self.proxy).json()['fingerprint']
            # print(f"[=]: Fetched Fingerprint ({fingerprint[:15]}...)")
            return fingerprint
        except Exception as err:
            # print(err)
            return 1





class AlphaBot:

    def __init__(self, accs_data, raffle_data, cap_key, id, discord_id):
        self.id = id
        self.cap_key = cap_key[0]
        print(self.cap_key)
        self.address = accs_data['address']
        self.private_key = accs_data['private_key'][2:].strip()
        self.tw_auth_token = accs_data['auth_token']
        self.tw_csrf = accs_data['csrf']
        self.discord_token = accs_data['discord_token']
        self.proxy = {'http': accs_data['proxy'], 'https': accs_data['proxy']}
        self.raffle_url = raffle_data['raffle_url']
        self.discord_invite = raffle_data['discord_invite']
        self.discord_id_ = discord_id

        self.session = None
        self.nonce = None
        self.payload = None
        self.slug = None
        self.data = None
        self.twitter_id = None
        self.discord_id = None
        self.message = None
        self.result = False

    def session_status(self):

        with self.session.get('https://www.alphabot.app/api/auth/session', timeout=10) as response:
            # print(response.text)

            try:
                if response.json()['signed'] == True:
                    return True
                else:
                    return False
            except:
                return False

    def execute_tasks(self):


        self.session = self._make_scraper()
        self.session.proxies = self.proxy
        self.session.user_agent = random_user_agent()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        start = time.time()
        print(f"{self.id} - Processing...")

        if self.login():

            if self.get_ids():
                self.submit_entry()
            else:
                if self.twitter_connect():
                    if self.discord_connect():
                        self.login()
                        self.get_ids()
                        self.submit_entry()




        total_time = time.time() - start
        print(f'{self.message} | Time: {total_time}')
        return [total_time, self.result]

    def CheckWinners(self):

        # print(f"{self.id} - Checking...")

        self.session = self._make_scraper()
        self.session.proxies = self.proxy
        self.session.user_agent = random_user_agent()
        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        start = time.time()
        print(f"{self.id} - Processing...")

        if self.login():
            self.Checker()

        total_time = time.time() - start
        print(f'{self.message} | Time: {total_time}')
        return [total_time, self.result]

    def Checker(self):

        self.slug = self.raffle_url.split('/')[-1]

        with self.session.get(f"https://www.alphabot.app/{self.slug}", timeout=15,
                               allow_redirects=False) as response:
            print(response.text)
            result = json.loads(response.text.split('<script id="__NEXT_DATA__" type="application/json">')[-1].split('</script><script src=')[0])

            result = result['props']['pageProps']['project']

            if result['isFinalized'] == True:
                if result['isWinner'] == True:
                    self.result = 'Won'
                else:
                    self.result = 'Lost'

            else:
                self.result = 'Raffle is not finished yet'


    def login(self):
        try:
            self.session.headers.update({'referer': 'https://www.alphabot.app/', "content-type": "application/x-www-form-urlencoded"})
            with self.session.get('https://www.alphabot.app/', timeout=15) as response:
                if response.ok:
                    self.nonce = self._get_nonce()
                    if self.nonce:
                        message = encode_defunct(text=self._get_message_to_sign())
                        signed_message = w3.eth.account.sign_message(message, private_key=self.private_key)
                        signature = signed_message["signature"].hex()
                        data = f"web3provider=metamask&address={self.address.lower()}&signature={signature}"
                        with self.session.get("https://www.alphabot.app/api/auth/csrf", data=data, timeout=15) as response:
                            csrfToken = response.json()['csrfToken']
                            payload = {'redirect': 'false',
                                       'address': f'{self.address.lower()}',
                                       'signature': f'{signature}',
                                       'csrfToken': f'{csrfToken}',
                                       'callbackUrl': 'https://www.alphabot.app/',
                                       'json': 'true'}
                            with self.session.post('https://www.alphabot.app/api/auth/callback/credentials?', data=payload, timeout=15) as response:
                                with self.session.get('https://www.alphabot.app/api/session', timeout=15) as response:
                                    self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})
                                    with self.session.get('https://www.alphabot.app/#profile') as response:
                                        with self.session.get('https://www.alphabot.app/api/session', timeout=15) as response:
                                            pass
                                        with self.session.get('https://www.alphabot.app/api/auth/providers', timeout=15) as response:
                                            pass
                                        with self.session.get('https://www.alphabot.app/api/auth/csrf', timeout=15) as response:
                                            pass

                                        self.data = {'csrfToken': csrfToken,
                                                     'callbackUrl': 'https://www.alphabot.app/#profile',
                                                     'json': 'true'}

                                        return True
        except:
            # print('Failed to log in')
            self.message = f'{self.id} - {bcolors.FAIL}Failed to log in{bcolors.ENDC}'
            self.result = 'Failed to log in'
            return False

    def get_ids(self):
        try:
            with self.session.get('https://www.alphabot.app/api/auth/session', timeout=15, allow_redirects=False) as response:
                self.twitter_id = response.json()['twitterId']
                self.discord_id = response.json()['discordId']
                # print(self.twitter_id, self.discord_id)
                if self.twitter_id != None and self.discord_id != None:
                    # print('Ids get successfully')
                    return True
        except:
            # print('Failed to get ids')
            return False

    def submit_entry(self):
        user_ids, retweet_id, self.slug, discord_invite = self.get_raffle_data()
        accs_data = {'csrf': self.tw_csrf,
                     'auth_token': self.tw_auth_token}
        raffle_data = {'user_id': user_ids,
                       'tweet_id': [retweet_id]}
        twitter_results = twitter_tasks(self.session, accs_data, raffle_data, self.id)

        if twitter_results[0] == True:

            status = False
            if self.discord_invite != []:
                if self.discord_join():
                    status = True
            else:
                status = True

            if status:

                captcha = self.solve_captcha()
                data = {'answers': [],
                        'applicationCode': '',
                        'captcha': captcha,
                        'discordId': self.discord_id,
                        'mintAddress': self.address,
                        'pw': '',
                        'slug': self.slug,
                        'twitterId': self.twitter_id}
                self.session.headers.update({'content-type': 'text/plain;charset=UTF-8', 'referer': self.raffle_url})
                try:
                    with self.session.post("https://www.alphabot.app/api/register", json=data, timeout=15, allow_redirects=False) as response:
                        if response.json()['success']:
                            # print('Registration successful')
                            self.message = f'{self.id} - {bcolors.OKGREEN}Account successfully submitted{bcolors.ENDC}'
                            self.result = 'Account successfully submitted'
                        elif response.json()['reason'] == 'you_already_entered':
                            self.message = f'{self.id} - {bcolors.OKGREEN}Account has already been submitted{bcolors.ENDC}'
                            self.result = 'Account has already been submitted'
                        else:

                            print(response.json())

                            # print('Registration failed')
                            self.message = f'{self.id} - {bcolors.FAIL}Registration failed{bcolors.ENDC}'
                            self.result = 'Registration failed 0'
                except:
                    # print('Registration failed')
                    self.message = f'{self.id} - {bcolors.FAIL}Registration failed{bcolors.ENDC}'
                    self.result = 'Registration failed 1'
        else:
            self.message = twitter_results[1]
            self.result = 'Registration failed 2'

    def discord_connect(self):
        try:
            with self.session.post("https://www.alphabot.app/api/auth/signin/discord?", data=self.data, timeout=15, allow_redirects=False) as response:
                url = json.loads(response.text)['url']
                redirect_uri = url.split('redirect_uri=')[-1].split('&')[0]
                client_id = url.split('client_id=')[-1].split('&')[0]
                discord_headers = {
                    'authority': 'discord.com',
                    'authorization': self.discord_token,
                    'content-type': 'application/json',
                    'referer': f'https://discord.com/oauth2/authorize?redirect_uri={redirect_uri}&scope=identify%20guilds%20email%20applications.commands.permissions.update&response_type=code&prompt=none&client_id={client_id}&state=null',
                    'x-super-properties': 'eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJydS1SVSIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMDkuMC4wLjAgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwOS4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMC4xNS43IiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE3NDA1MSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ==',
                }
                json_data = {
                    'permissions': '0',
                    'authorize': True,
                }
                with self.session.post(url, headers=discord_headers, json=json_data, timeout=15, allow_redirects=False) as response:
                    if response.ok:
                        with self.session.get(response.json()['location'], timeout=15, allow_redirects=False) as response:
                            if response.ok:
                                return True
                            else:
                                # print('Discord connection failed | Error type: 3')
                                self.message = f'{self.id} - {bcolors.FAIL}Discord connection failed{bcolors.ENDC}'
                                return False
                    else:
                        # print('Discord connection failed | Error type: 2')
                        self.message = f'{self.id} - {bcolors.FAIL}Discord connection failed{bcolors.ENDC}'
                        return False
        except:
            # print('Discord connection failed | Error type: 1')
            self.message = f'{self.id} - {bcolors.FAIL}Discord connection failed{bcolors.ENDC}'
            return False

    def twitter_connect(self):
            try:
                with self.session.post("https://www.alphabot.app/api/auth/signin/twitter?", data=self.data, timeout=15, allow_redirects=False) as response:
                    print(response.text)
                    url = json.loads(response.text)['url']
                    oauth_token = url.split('oauth_token=')[-1].split('&')[0]
                    self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                    with self.session.get(url, timeout=15, allow_redirects=False) as response:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')
                        payload = {'authenticity_token': authenticity_token,
                                   'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
                                   'oauth_token': oauth_token}
                        with self.session.post(f"https://api.twitter.com/oauth/authorize", data=payload, timeout=15) as response:
                            soup = BeautifulSoup(response.text, 'html.parser')
                            link = soup.find('a', class_='maintain-context').get('href')
                            # user_url = response.text.split('<a href="')[1].split('"')[0]
                            with self.session.get(link, data=payload, timeout=30, allow_redirects=False) as response:
                                return True
            except Exception as e:
                # print(f'Twitter connection failed')
                traceback.print_exc()

                self.message = f'{self.id} - {bcolors.FAIL}Twitter connection failed{bcolors.ENDC}'
                self.result = 'Twitter connection failed'
                return False

    def discord_join(self):

        result = []

        for discord_invite in self.discord_invite:

            try:
                res = Discord(token=self.discord_token, proxy=self.proxy, cap_key=self.cap_key).JoinServer(discord_invite)
                if 'Successfully Join' in res:
                    self.result = 'Discord join success'
                    result.append(True)
                else:
                    self.result = 'Discord join failed 0'
                    result.append(False)
            except:

                traceback.print_exc()

                self.result = 'Discord join failed 1'
                return False

            time.sleep(3)

        for i in result:
            if i == False:
                return False

        return True

    def get_raffle_data(self):
        with self.session.get(self.raffle_url, timeout=15) as response:
            data = response.text
            twitter_follows = data.split('"twitterFollows":')[-1].split(',"twitterId"')[0]
            twitter_follows = ast.literal_eval(twitter_follows)
            user_ids = []
            for user in twitter_follows:
                user_ids.append(user['id'])
            try:
                retweet_id = \
                data.split('"twitterRetweet":"')[-1].split('","twitterRetweetType"')[0].split('/')[5].split('"')[0]
            except:
                retweet_id = []

            try:
                discord_invite = data.split('"inviteLink":"')[1].split('"')[0].split('/')[-1]
            except:
                discord_invite = False

            slug = self.raffle_url.split('/')[-1]
            return user_ids, retweet_id, slug, discord_invite

    def solve_captcha(self):
        try:
            # print(f'Solving captcha...')
            cap = capmonster_python.HCaptchaTask(self.cap_key)
            tt = cap.create_task("https://www.alphabot.app/", '65a6959a-b216-4c41-92a3-15bf96f418fc')
            captcha = cap.join_task_result(tt)
            captcha = captcha["gRecaptchaResponse"]
            # print(f'Captcha solved')
            return captcha
        except:
            self.message = f'{self.id} - {bcolors.FAIL}Captcha error{bcolors.ENDC}'
            self.result = 'Captcha error'

    def _make_scraper(self):
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers(
            "ECDH-RSA-NULL-SHA:ECDH-RSA-RC4-SHA:ECDH-RSA-DES-CBC3-SHA:ECDH-RSA-AES128-SHA:ECDH-RSA-AES256-SHA:"
            "ECDH-ECDSA-NULL-SHA:ECDH-ECDSA-RC4-SHA:ECDH-ECDSA-DES-CBC3-SHA:ECDH-ECDSA-AES128-SHA:"
            "ECDH-ECDSA-AES256-SHA:ECDHE-RSA-NULL-SHA:ECDHE-RSA-RC4-SHA:ECDHE-RSA-DES-CBC3-SHA:ECDHE-RSA-AES128-SHA:"
            "ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-NULL-SHA:ECDHE-ECDSA-RC4-SHA:ECDHE-ECDSA-DES-CBC3-SHA:"
            "ECDHE-ECDSA-AES128-SHA:ECDHE-ECDSA-AES256-SHA:AECDH-NULL-SHA:AECDH-RC4-SHA:AECDH-DES-CBC3-SHA:"
            "AECDH-AES128-SHA:AECDH-AES256-SHA"
        )
        ssl_context.set_ecdh_curve("prime256v1")
        ssl_context.options |= (ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_3 | ssl.OP_NO_TLSv1)
        ssl_context.check_hostname = False

        return cloudscraper.create_scraper(
            debug=False,
            ssl_context=ssl_context
        )

    def _get_message_to_sign(self) -> str:
        return f"Sign this message to either enter a raffle that requires holding a specific NFT, edit your profile, or to gain access to premium functionality with Alphabot. ({self.nonce})"

    def _get_nonce(self):
        try:
            with self.session.get(f"https://www.alphabot.app/api/auth/nonce?address={self.address.lower()}", timeout=15) as response:
                if response.ok:
                    nonce = response.json()['nonce']
                    return nonce
                else:
                    # print(f"Unknown status code while getting nonce [{response.status_code}]")
                    self.message = f'{self.id} - {bcolors.FAIL}Unknown status code while getting noncer{bcolors.ENDC}'
                    self.result = 'Unknown status code while getting nonce'
        except Exception as err:
            # print('error')
            self.message = f'{self.id} - {bcolors.FAIL}Nonce error{bcolors.ENDC}'
            self.result = 'Nonce error'