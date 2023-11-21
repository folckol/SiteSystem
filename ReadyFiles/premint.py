import pickle
import traceback

import tls_client
from bs4 import BeautifulSoup
from eth_account.messages import encode_defunct
from web3.auto import w3

from Rescue_Site_System.ReadyFiles.utils import twitter_tasks
from Rescue_Site_System.ReadyFiles.utils import bcolors


import base64
import json
import random
import re
import ssl

import cloudscraper
import requests, capmonster_python, os, time

class Discord:

    def __init__(self, token, proxy, cap_key):

        print(cap_key)

        self.cap = capmonster_python.HCaptchaTask(cap_key)
        self.token = token
        self.proxy = proxy

        # print(token)
        # print(proxy)
        # print(cap_key)

        self.session = self._make_scraper()
        self.ua = random_user_agent()
        self.session.user_agent = self.ua
        # self.session.proxies = self.proxy
        self.super_properties = self.build_xsp(self.ua)


        self.cfruid, self.dcfduid, self.sdcfduid = self.fetch_cookies(self.ua)
        self.fingerprint = self.get_fingerprint()


    def JoinServer(self, invite):
        print({"authorization": self.token})
        rer = self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token})

        print(rer.text, rer.status_code)
        # print(rer.text)
        # print(rer.status_code)

        # print(self.cap)

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
            print(rej.text)
            # print(rej.status_code)
            if "200" in str(rej):
                return 'Successfully Join 0', self.super_properties
            if "200" not in str(rej):
                return 'Failed Join', self.super_properties

        else:
            with self.session.post("https://discord.com/api/v9/invites/" + invite, headers={"authorization": self.token}) as response:
                # print(response.text)
                pass
            return 'Successfully Join 1', self.super_properties


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

class Premint:

    def __init__(self, accs_data, raffle_data, cap_key, id, discord_id):
        self.accs_data = accs_data
        self.raffle_data = raffle_data

        self.discord_id = discord_id

        self.id = id
        self.cap_key = cap_key[0]
        self.address = accs_data['address']
        self.private_key = accs_data['private_key'][2:].strip()
        self.tw_auth_token = accs_data['auth_token']
        self.tw_csrf = accs_data['csrf']
        self.discord_token = accs_data['discord_token']
        self.proxy = {'http': accs_data['proxy'], 'https': accs_data['proxy']}
        self.raffle_url = raffle_data['raffle_url']
        self.discord_status = raffle_data['discord_status']
        self.discord_invite = raffle_data['discord_invite']

        self.sup = 'eyJvcyI6Ik1hYyBPUyBYIiwiYnJvd3NlciI6IkNocm9tZSIsImRldmljZSI6IiIsInN5c3RlbV9sb2NhbGUiOiJydS1SVSIsImJyb3dzZXJfdXNlcl9hZ2VudCI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xMDkuMC4wLjAgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjEwOS4wLjAuMCIsIm9zX3ZlcnNpb24iOiIxMC4xNS43IiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6IiIsInJlbGVhc2VfY2hhbm5lbCI6InN0YWJsZSIsImNsaWVudF9idWlsZF9udW1iZXIiOjE3NDA1MSwiY2xpZW50X2V2ZW50X3NvdXJjZSI6bnVsbCwiZGVzaWduX2lkIjowfQ=='

        # print(self.discord_invite)

        self.csrf = None
        self.session = None
        self.nonce = None
        self.captcha_required = None
        self.registered = None
        self.message = None
        self.result = 'There are not enough funds on your account '

    def execute_task(self):

        # print(self.cap_key)

        start = time.time()
        print(f"{self.id} - Processing...")
        # try:

        folder_path = f'{os.getcwd()}/USERs_data/{self.discord_id}'
        folder2_path = f'{folder_path}/premint'
        file_name = f'{folder2_path}/{self.id}.pkl'
        self.nonce_folder = f'{folder2_path}/{self.id}.txt'

        status = False

        if not os.path.exists(folder_path):
            # Если папка не существует, то создаем ее
            os.makedirs(folder_path)
            os.makedirs(folder2_path)

            self.session = self._make_scraper()
            self.session.proxies = self.proxy
            self.session.user_agent = random_user_agent()
            adapter = requests.adapters.HTTPAdapter(max_retries=5)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)

            if self.discord_invite != []:
                if self.discord_join():
                    time.sleep(5)
                else:
                    pass
            if self.premint_login():

                with open(file_name, "wb") as f:
                    pickle.dump(self.session, f)

                if self.twitter_connect():
                    # print('1')
                    if self.discord_status:
                        if self.discord_connect():
                            pass
                        else:
                            return [self.result]
                    twitter_tasks(self.session, self.accs_data, self.raffle_data, self.id)
                    # print('1')
                    if self.check_registration():
                        # print('1')
                        self.enter_raffle()

                        if self.result == 'Submitting entry failed 3':

                            try:
                                status = self.disconnect_discord_()
                            except:

                                traceback.print_exc()

                                self.result = 'Problems with Discord Token 1'
                                status = False
            # except:
            #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
            #     self.result = False

        else:

            if not os.path.exists(folder2_path):
                os.makedirs(folder2_path)

                self.session = self._make_scraper()
                self.session.proxies = self.proxy
                self.session.user_agent = random_user_agent()
                adapter = requests.adapters.HTTPAdapter(max_retries=5)
                self.session.mount('http://', adapter)
                self.session.mount('https://', adapter)

                if self.discord_invite != []:
                    if self.discord_join():
                        time.sleep(5)
                    else:
                        pass
                if self.premint_login():
                    with open(file_name, "wb") as f:
                        pickle.dump(self.session, f)
                    # print('1')
                    if self.twitter_connect():
                        # print('1')
                        if self.discord_status:
                            if self.discord_connect():
                                pass
                            else:
                                return [self.result]
                        twitter_tasks(self.session, self.accs_data, self.raffle_data, self.id)
                        # print('1')
                        if self.check_registration():
                            # print('1')
                            self.enter_raffle()

                            if self.result == 'Submitting entry failed 3':

                                try:
                                    status = self.disconnect_discord_()
                                except:
                                    traceback.print_exc()
                                    self.result = 'Problems with Discord Token 1'
                                    status = False
                # except:
                #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
                #     self.result = False


            else:

                try:
                    with open(file_name, "rb") as f:
                        self.session = pickle.load(f)

                    with open(self.nonce_folder, "r") as f:
                        self.nonce = f.read().rstrip()

                    if self.session_status():
                        if self.discord_invite != []:
                            if self.discord_join():
                                # print('asdad')
                                time.sleep(5)
                            else:
                                pass

                        print('1')
                        if self.twitter_connect():
                            print('1')
                            print(self.raffle_data)
                            if self.discord_status:
                                print('asdad 1')
                                if self.discord_connect():
                                    print('asdad 2')
                                    pass
                                else:
                                    print('asdad 2 ==')
                                    return [self.result]
                            twitter_tasks(self.session, self.accs_data, self.raffle_data, self.id)
                            print('asdad 3 ')
                            if self.check_registration():
                                print('1')

                                self.enter_raffle()

                                if self.result == 'Submitting entry failed 3':

                                    try:
                                        status = self.disconnect_discord_()
                                    except:
                                        traceback.print_exc()
                                        self.result = 'Problems with Discord Token 1'
                                        status = False

                    else:

                        self.session = self._make_scraper()
                        self.session.proxies = self.proxy
                        self.session.user_agent = random_user_agent()
                        adapter = requests.adapters.HTTPAdapter(max_retries=5)
                        self.session.mount('http://', adapter)
                        self.session.mount('https://', adapter)

                        if self.discord_invite != []:
                            if self.discord_join():
                                time.sleep(5)
                            else:
                                pass
                        if self.premint_login():
                            with open(file_name, "wb") as f:
                                pickle.dump(self.session, f)
                            if self.twitter_connect():
                                # print('1')
                                if self.discord_status:
                                    if self.discord_connect():
                                        pass
                                    else:
                                        return [self.result]
                                twitter_tasks(self.session, self.accs_data, self.raffle_data, self.id)
                                # print('1')
                                if self.check_registration():
                                    # print('1')
                                    self.enter_raffle()

                                    if self.result == 'Submitting entry failed 3':

                                        try:
                                            status = self.disconnect_discord_()
                                        except:
                                            traceback.print_exc()
                                            self.result = 'Problems with Discord Token 1'
                                            status = False

                        # except:
                        #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
                        #     self.result = False



                except:

                    # print(11111)
                    # print(self.proxy)

                    self.session = self._make_scraper()
                    self.session.proxies = self.proxy
                    self.session.user_agent = random_user_agent()
                    adapter = requests.adapters.HTTPAdapter(max_retries=5)
                    self.session.mount('http://', adapter)
                    self.session.mount('https://', adapter)

                    if self.discord_invite != []:
                        if self.discord_join():
                            time.sleep(5)
                        else:
                            pass
                    if self.premint_login():
                        with open(file_name, "wb") as f:
                            pickle.dump(self.session, f)
                        # print('1')
                        if self.twitter_connect():
                            # print('1')
                            if self.discord_status:
                                if self.discord_connect():
                                    pass
                                else:
                                    return [self.result]
                            twitter_tasks(self.session, self.accs_data, self.raffle_data, self.id)
                            # print('1')
                            if self.check_registration():
                                # print('1')
                                self.enter_raffle()

                                if self.result == 'Submitting entry failed 3':

                                    try:
                                        status = self.disconnect_discord_()
                                    except:
                                        traceback.print_exc()
                                        self.result = 'Problems with Discord Token 1'
                                        status = False

                        # except:
                        #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
                        #     self.result = False


        if status == False:
            total_time = time.time() - start
            print(f'{self.result} | Time: {total_time}')
            return [total_time, self.result]

        else:
            return Premint(self.accs_data, self.raffle_data, [self.cap_key], self.id, self.discord_id).execute_task()


    def execute_task_check_result(self):

        # print(self.cap_key)

        start = time.time()
        print(f"{self.id} - Processing...")
        # try:

        folder_path = f'{os.getcwd()}/USERs_data/{self.discord_id}'
        folder2_path = f'{folder_path}/premint'
        file_name = f'{folder2_path}/{self.id}.pkl'
        self.nonce_folder = f'{folder2_path}/{self.id}.txt'

        status = False

        if not os.path.exists(folder_path):
            # Если папка не существует, то создаем ее
            os.makedirs(folder_path)
            os.makedirs(folder2_path)

            self.session = self._make_scraper()
            self.session.proxies = self.proxy
            self.session.user_agent = random_user_agent()
            adapter = requests.adapters.HTTPAdapter(max_retries=5)
            self.session.mount('http://', adapter)
            self.session.mount('https://', adapter)


            if self.premint_login():

                with open(file_name, "wb") as f:
                    pickle.dump(self.session, f)

                self.check_winners()
            # except:
            #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
            #     self.result = False

        else:

            if not os.path.exists(folder2_path):
                os.makedirs(folder2_path)

                self.session = self._make_scraper()
                self.session.proxies = self.proxy
                self.session.user_agent = random_user_agent()
                adapter = requests.adapters.HTTPAdapter(max_retries=5)
                self.session.mount('http://', adapter)
                self.session.mount('https://', adapter)


                if self.premint_login():
                    with open(file_name, "wb") as f:
                        pickle.dump(self.session, f)
                    self.check_winners()
                # except:
                #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
                #     self.result = False


            else:

                try:
                    with open(file_name, "rb") as f:
                        self.session = pickle.load(f)

                    with open(self.nonce_folder, "r") as f:
                        self.nonce = f.read().rstrip()

                    if self.session_status():
                        self.check_winners()

                    else:

                        self.session = self._make_scraper()
                        self.session.proxies = self.proxy
                        self.session.user_agent = random_user_agent()
                        adapter = requests.adapters.HTTPAdapter(max_retries=5)
                        self.session.mount('http://', adapter)
                        self.session.mount('https://', adapter)


                        if self.premint_login():
                            with open(file_name, "wb") as f:
                                pickle.dump(self.session, f)
                            self.check_winners()
                        # except:
                        #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
                        #     self.result = False



                except:

                    # print(11111)
                    # print(self.proxy)

                    self.session = self._make_scraper()
                    self.session.proxies = self.proxy
                    self.session.user_agent = random_user_agent()
                    adapter = requests.adapters.HTTPAdapter(max_retries=5)
                    self.session.mount('http://', adapter)
                    self.session.mount('https://', adapter)


                    if self.premint_login():
                        with open(file_name, "wb") as f:
                            pickle.dump(self.session, f)
                        self.check_winners()

                        # except:
                        #     self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
                        #     self.result = False

        total_time = time.time() - start
        print(f'{self.result} | Time: {total_time}')
        return [total_time, self.result]




    def disconnect_discord_(self):

        with self.session.get('https://www.premint.xyz/accounts/social/connections/', timeout=10) as response:
            soup = BeautifulSoup(response.content, "lxml")

            accs = soup.find('fieldset').findAll('label')

            for acc in accs:
                print(acc.text)
                if 'discord' in acc.text.lower():
                    account_id = acc.find('input').get('value')
                    break

            self.session.headers.update({
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "x-csrftoken": self.csrf
            })

            data = f"csrfmiddlewaretoken={self.csrf}&account={account_id}"

            with self.session.post('https://www.premint.xyz/accounts/social/connections/', data=data, timeout=10) as response:
                if response.ok:
                    return True
                else:
                    self.result = 'Problems with Discord Token'
                    return False




    def session_status(self):

        with self.session.get('https://www.premint.xyz/profile/', timeout=10) as response:
            # print(response.text)

            soup = BeautifulSoup(response.content, "lxml")

            wallets = soup.findAll('span', class_="text-monospace")
            for i in wallets:

                if self.address[:4].lower() in i.text.lower():
                    # print(i.text)
                    return True

            return False


    def premint_login(self):
        self.session.headers.update({
                "referer": "https://www.premint.xyz/v1/login_api/",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
            })
        try:
            with self.session.get("https://www.premint.xyz/login/", timeout=15) as response:
                # print(response.text)
                if response.ok:
                    self.csrf = response.cookies["csrftoken"]
                    self.session.headers.update({"x-csrftoken": self.csrf})
                    self.nonce = self._get_nonce()

                    with open(self.nonce_folder, 'w') as file:
                        file.write(self.nonce)

                    data = f"username={self.address.lower()}"
                    if self.nonce:
                        with self.session.post("https://www.premint.xyz/v1/signup_api/", data=data, timeout=15) as response:
                            if response.ok:
                                message = encode_defunct(text=self._get_message_to_sign())
                                signed_message = w3.eth.account.sign_message(message, private_key=self.private_key)
                                signature = signed_message["signature"].hex()
                                data = f"web3provider=metamask&address={self.address.lower()}&signature={signature}"
                                with self.session.post("https://www.premint.xyz/v1/login_api/", data=data, timeout=15) as response:
                                    self.session.cookies.update({'SessionState': response.cookies['SessionState']})
                                    if response.ok:
                                        if response.json()["success"]:
                                            return True
                                        else:
                                            self.message = f'{self.id} - {bcolors.FAIL}Premint login failed{bcolors.ENDC}'
                                            self.result = 'Premint login failed (0)'
                                            return False
                                    else:
                                        self.message = f'{self.id} - {bcolors.FAIL}Premint login failed{bcolors.ENDC}'
                                        self.result = 'Premint login failed (1)'
                                        return False
                            else:
                                self.message = f'{self.id} - {bcolors.FAIL}Premint login failed{bcolors.ENDC}'
                                self.result = 'Premint login failed (2)'
                                return False
                    else:
                        self.message = f'{self.id} - {bcolors.FAIL}Premint login failed{bcolors.ENDC}'
                        self.result = 'Premint login failed (3)'
                        return False
                else:
                    self.message = f'{self.id} - {bcolors.FAIL}Premint login failed{bcolors.ENDC}'
                    self.result = 'Premint login failed (4)'
                    return False
        except Exception as e:
            traceback.print_exc()
            self.message = f'{self.id} - {bcolors.FAIL}Premint login failed{bcolors.ENDC}'
            self.result = 'Premint login failed (5)'
            return False

    def twitter_connect(self):
        try:
            with self.session.get('https://www.premint.xyz/accounts/twitter/login/?process=connect&next=%2Fprofile%2F', timeout=15) as response:
                soup = BeautifulSoup(response.text, 'html.parser')
                oauth_token = soup.find('input', attrs={'name': 'redirect_after_login'}).get('value')
                oauth_token = oauth_token.split('oauth_token=')[-1]
                self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                with self.session.get(f'https://api.twitter.com/oauth/authenticate?oauth_token={oauth_token}&oauth_callback=https%3A%2F%2Fwww.premint.xyz%2Faccounts%2Ftwitter%2Flogin%2Fcallback%2F', timeout=15) as response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')
                    payload = {'authenticity_token': authenticity_token,
                               'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
                               'oauth_token': oauth_token}
                    self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                    with self.session.post(f'https://api.twitter.com/oauth/authorize', data=payload, timeout=15, allow_redirects=False) as response:
                        self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                        soup = BeautifulSoup(response.text, 'html.parser')
                        link = soup.find('a', class_='maintain-context').get('href')
                        with self.session.get(link, timeout=15) as response:
                            if response.ok:
                                return True
                            else:
                                self.message = f'{self.id} - {bcolors.FAIL}Twitter connection failed{bcolors.ENDC}'
                                self.result = 'Twitter connection failed'
                                return False
        except:
            self.message = f'{self.id} - {bcolors.FAIL}Twitter connection failed{bcolors.ENDC}'
            self.result = 'Twitter connection failed'
            return False

    def check_winners(self):
        try:
            with self.session.get(self.raffle_url, timeout=15) as response:
                if response.ok:
                    soup = BeautifulSoup(response.content, "lxml")
                    # print(soup)

                    try:
                        element = soup.find('div', class_='heading heading-3 mb-3')

                        # print(element.text, f'- {self.address}')
                        self.result = element.text
                    except:
                        # print(f'{self.id} - Этот аккаунт не был зарегистрирован')
                        self.result = 'Unknown result'
        except:
            pass

    def discord_connect(self):
        try:
            with self.session.get(
                    'https://www.premint.xyz/accounts/discord/login/?process=connect&scope=guilds.members.read&next=%2Fprofile%2F',
                    timeout=15, allow_redirects=False) as response:
                link = response.headers['Location']
                redirect_uri = link.split('redirect_uri=')[-1].split('&')[0]
                client_id = link.split('client_id=')[-1].split('&')[0]
                state = link.split('state=')[-1]
                return self.discord_authorize(redirect_uri, client_id, state, link)
        except:
            self.message = f'{self.id} - {bcolors.FAIL}Discord connection failed{bcolors.ENDC}'
            self.result = 'Discord connection failed'
            return False

    def discord_join(self):

        # print('============')

        result = []

        for invite in self.discord_invite:
            try:
                res, self.sup = Discord(token=self.discord_token, proxy=self.proxy, cap_key=self.cap_key).JoinServer(invite)
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



    def enter_raffle(self):
        try:
            self.error = ''
            with self.session.get(self.raffle_url, timeout=15) as response:
                self.error = response.text
                if response.ok:
                    soup = BeautifulSoup(response.content, "lxml")
                    self.csrf = soup.find_all("input", {"name": "csrfmiddlewaretoken"})[0]["value"]

                    payload = f"csrfmiddlewaretoken={self.csrf}" \
                           "&params_field={}" \
                           f"&nonce={self.nonce}" \
                           f"&minting_wallet={self.address.lower()}" \
                           "&registration-form-submit=1"
                    print(payload)
                    with self.session.post(self.raffle_url, data=payload, timeout=15) as response:

                        time.sleep(4)

                        if response.ok:
                            with self.session.get(self.raffle_url, timeout=15) as response:
                                if response.ok:
                                    soup = BeautifulSoup(response.content, "lxml")
                                    # print(soup)
                                    try:
                                        element = soup.find('div', class_='heading heading-3 mb-2 d-block')
                                        # print(element)
                                        if 'Registered' in element.text:
                                            self.message = f'{self.id} - {bcolors.OKGREEN}Entry submitting succesfully{bcolors.ENDC}'
                                            self.result = 'Entry submitted successfully'
                                            return True
                                        else:
                                            print('Trabl', element.text)
                                            self.result = 'Submitting entry failed 4'
                                            return False
                                    except:
                                        self.message = f'{self.id} - {bcolors.OKGREEN}Submitting entry failed 0{bcolors.ENDC}'
                                        self.result = 'Submitting entry failed 0'
                                        return False
                        else:
                            self.message = f'{self.id} - {bcolors.FAIL}Submitting entry failed 1{bcolors.ENDC}'
                            self.result = 'Submitting entry failed 1'
                            return False
                else:
                    self.message = f'{self.id} - {bcolors.FAIL}Submitting entry failed 2{bcolors.ENDC}'
                    self.result = 'Submitting entry failed 2'
                    return False
        except Exception as e:
            if 'This social account is connected to another one of your wallets.' in self.error:
                self.disconnect_twitter()
                self.disconnect_discord()
                self.premint_login()
            else:

                print(self.error)

                self.message = f'{self.id} - {bcolors.FAIL}Submitting entry failed 3{bcolors.ENDC}'
                self.result = 'Submitting entry failed 3'
                return False

    def disconnect_twitter(self):
        try:
            with self.session.get('https://www.premint.xyz/accounts/twitter/login/?next=%2Fdisconnect%2Ftwitter%2F', timeout=10) as response:
                soup = BeautifulSoup(response.text, 'html.parser')
                oauth_token = soup.find('input', attrs={'name': 'referer'}).get('value')
                oauth_token = oauth_token.split('oauth_token=')[-1]
                authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')
                with self.session.get(f'https://api.twitter.com/oauth/authenticate?oauth_token={oauth_token}&oauth_callback=https%3A%2F%2Fwww.premint.xyz%2Faccounts%2Ftwitter%2Flogin%2Fcallback%2F', timeout=10) as response:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    link = soup.find('a', class_='maintain-context').get('href')
                    oauth_verifier = link.split('oauth_verifier=')[-1]
                    with self.session.get(link, timeout=10) as response:
                        pass
        except:
            self.message = f'{self.id} - {bcolors.FAIL}Disconnecting twitter failed{bcolors.ENDC}'

    def disconnect_discord(self):
        try:
            with self.session.get('https://www.premint.xyz/accounts/discord/login/?next=%2Fdisconnect%2Fdiscord%2F',
                                  timeout=10, allow_redirects=False) as response:
                link = response.headers['Location']
                redirect_uri = link.split('redirect_uri=')[-1].split('&')[0]
                client_id = link.split('client_id=')[-1].split('&')[0]
                state = link.split('state=')[-1]

                self.discord_authorize(redirect_uri, client_id, state, link)

                with self.session.get('https://www.premint.xyz/disconnect/discord/', timeout=10,
                                      allow_redirects=True) as response:
                    with self.session.get('https://www.premint.xyz/logout?next=/disconnect/discord/', timeout=10,
                                          allow_redirects=True) as response:
                        with self.session.get('https://www.premint.xyz/logout/?next=/disconnect/discord/', timeout=10,
                                              allow_redirects=True) as response:
                            pass
        except:
            self.message = f'{self.id} - {bcolors.FAIL}Disconnecting discord failed{bcolors.ENDC}'
            self.result = 'Disconnecting discord failed'

    def discord_authorize(self, redirect_uri, client_id, state, link):
        try:
            with self.session.get(link, timeout=15, allow_redirects=False) as response:
                if response.ok:
                    text = response.text
                    link = text.split('<a href="')[-1].split('">')[0]
                    with self.session.get(link, timeout=15, allow_redirects=False) as response:
                        if response.ok:

                            discord_headers = {
                                'authority': 'discord.com',
                                'authorization': self.discord_token,
                                'content-type': 'application/json',
                                'referer': f'https://discord.com/oauth2/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=guilds.members.read+identify+guilds&response_type=code&state={state}',
                                'x-super-properties': self.sup,
                            }

                            json_data = {
                                'permissions': '0',
                                'authorize': True,
                            }

                            with self.session.post(
                                    f'https://discord.com/api/v9/oauth2/authorize?client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope=guilds.members.read%20identify%20guilds&state={state}',
                                    json=json_data, headers=discord_headers, timeout=10,
                                    allow_redirects=False) as response:
                                time.sleep(1)
                                # link = response.json()['location']
                                link_ = response.json()['location']

                                # print(link)
                                # print(link_)

                                with self.session.get(link_, timeout=10, allow_redirects=True) as response:
                                    return True
                        else:
                            self.message = f'{self.id} - {bcolors.FAIL}Discord authorization failed{bcolors.ENDC}'
                            self.result = 'Discord authorization failed 0'
                            return False

                else:
                    self.message = f'{self.id} - {bcolors.FAIL}Discord authorization failed{bcolors.ENDC}'
                    self.result = 'Discord authorization failed 1'
                    return False
        except:

            self.message = f'{self.id} - {bcolors.FAIL}Discord authorization failed{bcolors.ENDC}'
            self.result = 'Discord authorization failed 2'
            return False

    def check_registration(self):
        try:
            with self.session.get(self.raffle_url, timeout=15) as response:
                if response.ok:
                    soup = BeautifulSoup(response.content, "lxml")
                    # print(soup)
                    try:
                        element = soup.find('div', class_='heading heading-3 mb-2 d-block')
                        print(element.text)
                        if 'Registered' in element.text:
                            self.message = f'{self.id} - {bcolors.OKGREEN}Entry has already been submitted{bcolors.ENDC}'
                            self.result = 'Entry has already been submitted'
                            return False
                        else:
                            return True
                    except Exception as e:

                        # print(e)

                        element = soup.find('span', class_='text-danger')
                        if element.text == 'is closed':
                            self.message = f'{self.id} - {bcolors.FAIL}Raffle is closed{bcolors.ENDC}'
                            self.result = 'Raffle is closed'
                            return False

        except Exception as e:
            # print(e)
            return True

    def check_results(self):
        return True

    def _get_message_to_sign(self) -> str:
        return "Welcome to PREMINT!\n\n" \
               "Signing is the only way we can truly know \n" \
               "that you are the owner of the wallet you \n" \
               "are connecting. Signing is a safe, gas-less \n" \
               "transaction that does not in any way give \n" \
               "PREMINT permission to perform any \n" \
               "transactions with your wallet.\n\n" \
               f"Wallet address:\n{self.address.lower()}\n\n" \
               f"Nonce: {self.nonce}"

    def _get_nonce(self):
        try:
            with self.session.get("https://www.premint.xyz/v1/login_api/", timeout=15) as response:
                if response.ok:
                    nonce = response.json()["data"]
                    return nonce
                else:
                    pass
        except:
            pass

    @staticmethod
    def _make_scraper():
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

