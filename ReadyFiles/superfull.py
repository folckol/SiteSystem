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
from fake_useragent import UserAgent
from web3.auto import w3

import Rescue_Site_System.ReadyFiles.utils
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
        self.cap.set_proxy('http', proxy['http'].split('/')[-1].split('@')[-1].split(':')[0],proxy['http'].split('/')[-1].split('@')[-1].split(':')[1],proxy['http'].split('/')[-1].split('@')[0].split(':')[0],proxy['http'].split('/')[-1].split('@')[0].split(':')[1])
        print('http', proxy['http'].split('/')[-1].split('@')[-1].split(':')[0],proxy['http'].split('/')[-1].split('@')[-1].split(':')[1],proxy['http'].split('/')[-1].split('@')[0].split(':')[0],proxy['http'].split('/')[-1].split('@')[0].split(':')[1])

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









class Superful:

    def __init__(self, accs_data, raffle_data, cap_key, id, discord_id):
        self.discord_id = discord_id
        self.accs_data = accs_data
        self.raffle_data = raffle_data
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
        self.captcha_required = raffle_data['captcha_required']
        self.session = None
        self.message = None
        self.result = False

    def session_status(self):

        with self.session.get('https://www.superful.xyz/superful-api/v1/account/me', timeout=10) as response:
            # print(response.text)

            try:
                if response.json()['addresses']['eth'][0]['verified'] == True:
                    return True
                else:
                    return False
            except:
                return False

    def discord_join(self):


        result = []
        print(self.discord_invite)

        for invite in self.discord_invite:

            try:
                # print(invite)

                res = Discord(token=self.discord_token, proxy=self.proxy, cap_key=self.cap_key).JoinServer(invite)
                # print(res)
                if 'Successfully Join' in res:
                    self.result = 'Discord join success'
                    result.append(True)
                else:
                    self.result = 'Discord join failed 0'
                    return False
            except:
                traceback.print_exc()
                self.result = 'Discord join failed 1'
                result.append(False)

            time.sleep(3)

        for i in result:
            if i == False:
                return False

        return True

    def execute_tasks(self):
        start = time.time()
        print(f"{self.id} - Processing...")

        try:
            if self.login_superful():

                if self.connect_twitter():
                    if self.connect_discord():

                        tt = False
                        if self.raffle_data['discord_status'] == True:
                            if self.discord_invite != []:
                                if self.discord_join():
                                    tt = True
                        else:
                            tt = True

                        if tt == True:
                            twitter_tasks(self.session, self.accs_data, self.raffle_data, self.id)
                            self.enter_raffle()

        except:

            traceback.print_exc()

            self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
            self.result = False


        total_time = time.time() - start
        print(f'{self.message} | Time: {total_time}')
        return [total_time, self.message]

    def execute_tasks_check_winners(self):
        start = time.time()
        print(f"{self.id} - Processing...")

        try:
            if self.login_superful():

                self.checkWinners()

        except:

            traceback.print_exc()

            self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
            self.result = False


        total_time = time.time() - start
        print(f'{self.message} | Time: {total_time}')
        return [total_time, self.message]

    def login_superful(self):
        try:
            self.session = self._make_scraper()
            self.session.proxies = self.proxy
            self.session.user_agent = UserAgent().random
            adapter = requests.adapters.HTTPAdapter(max_retries=5)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)

            self.session.headers.update({"referer": "https://www.superful.xyz/get-started",
                                         "content-type": "application/json",
                                         'origin': 'https://www.superful.xyz'})

            with self.session.get('https://www.superful.xyz/dashboard', timeout=15) as resopnse:pass

            with self.session.post("https://www.superful.xyz/superful-api/v1/account/login", json={"address": self.address, "signature": None}, timeout=15) as response:
                print(response.text)

                try:
                    if response.json()['statusCode'] == 500:
                        self.message = f'Superful login failed 2'
                        return False
                except:
                    pass

                if response.ok:
                    nonce = response.json()['sign_message']
                    if nonce:
                        message = encode_defunct(text=nonce)
                        signed_message = w3.eth.account.sign_message(message, private_key=self.private_key)
                        signature = signed_message["signature"].hex()
                        with self.session.post("https://www.superful.xyz/superful-api/v1/account/login", json={"address": self.address.lower(), "signature": signature}, timeout=15) as response:
                            try:
                                if response.json()['statusCode'] == 500:
                                    self.message = f'Superful login failed 2'
                                    return False
                            except:
                                pass
                            print(response.text)
                            token = response.json()['token']
                            self.session.headers.update({'authorization': token})
                            with self.session.get('https://www.superful.xyz/settings', timeout=15, allow_redirects=False) as response:
                                return True
        except Exception as e:

            traceback.print_exc()

            self.message = f'Superful login failed 1'
            self.result = False
            return False

    def checkWinners(self):

        for i in range(1, 100):
            try:
                with self.session.get('https://www.superful.xyz/superful-api/v1/project/event/submissions?page=1&page_size=10&status=joined') as response:
                    for i in response.json()['results']:
                        if i['event_slug'] == self.raffle_url.split('/')[-1]:
                            self.message = i['status']
                            break
            except:
                self.message = 'Unknown result'
                break
            time.sleep(0.5)


    def connect_twitter(self):
        try:
            with self.session.get('https://www.superful.xyz/superful-api/v1/account/connect/twitter/v1?next=https://www.superful.xyz/settings', timeout=15, allow_redirects=False) as response:
                url = response.json()['url']
                oauth_token = url.split('oauth_token=')[-1]
                self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                with self.session.get(url, timeout=15, allow_redirects=False) as response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')
                    payload = {'authenticity_token': authenticity_token,
                               'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
                               'oauth_token': oauth_token}
                    self.session.headers.update({'content-type': 'application/x-www-form-urlencoded'})
                    with self.session.post(f'https://api.twitter.com/oauth/authorize', data=payload, timeout=15, allow_redirects=False) as response:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        link = soup.find('a', class_='maintain-context').get('href')
                        with self.session.get(link, timeout=15) as response:
                            return True
        except:
            self.message = f'{self.id} - Twitter connection failed'
            self.result = False
            return False

    def connect_discord(self):
        try:
            with self.session.get("https://www.superful.xyz/superful-api/v1/account/connect/discord?next=https://www.superful.xyz/settings", timeout=15, allow_redirects=False) as response:
                url = json.loads(response.text)['url']
                redirect_uri = url.split('redirect_uri=')[-1].split('&')[0]
                client_id = url.split('client_id=')[-1].split('&')[0]
                state = url.split('state=')[-1]
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
                url = f'https://discord.com/api/v9/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=identify%20guilds%20email%20applications.commands.permissions.update&state={state}'
                with self.session.post(url, headers=discord_headers, json=json_data, timeout=15, allow_redirects=False) as response:
                    if response.ok:
                        with self.session.get(response.json()['location'], timeout=15, allow_redirects=False) as response:
                            if response.ok:
                                return True
        except:
            self.message = f'{self.id} - Discord connection failed'
            self.result = False
            return False

    def enter_raffle(self):
        try:
            with self.session.get(self.raffle_url, timeout=15) as response:
                raffle_id = response.text.split('"prefetchEvent":{"id":"')[1].split('"')[0]
                captcha = ''
                if self.captcha_required:
                    captcha = self.solve_captcha()
                payload = {'captcha': captcha,
                           'custom_fields': [],
                           'id': raffle_id,
                           'mint_address': self.address.lower()}
                self.session.headers.update({"content-type": "application/json"})
                with self.session.post('https://www.superful.xyz/superful-api/v1/project/event/register', json=payload, timeout=15) as response:
                    try:
                        if response.json()['success']:
                            self.message = f'{self.id} - Entry submitted successfully'
                            self.result = True
                    except:
                        if response.json()['message'] == 'You already registered this event.':
                            self.message = f'{self.id} - Entry has already been submitted'
                            self.result = True
                        else:
                            self.message = f'{self.id} - Submitting entry failed: {response.json()["message"]}'
                            self.result = False
        except:
            self.message = f'{self.id} - Submitting entry failed'
            self.result = False

    def solve_captcha(self):
        try:
            cap = capmonster_python.RecaptchaV2Task(self.cap_key)
            tt = cap.create_task(self.raffle_url, '6Lf9ZCYgAAAAANbod3nwYtteIUlNGmrmoKnwu5uW')
            captcha = cap.join_task_result(tt)
            captcha = captcha["gRecaptchaResponse"]
            return captcha
        except:
            self.message = f'{self.id} - Captcha error'
            self.result = False

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
