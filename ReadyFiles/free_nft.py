import random
import ssl
import time
import traceback

import capmonster_python
import cloudscraper
import requests
import tls_client
from bs4 import BeautifulSoup
from eth_account.messages import encode_defunct
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

class FreeNFT:

    def __init__(self, accs_data, raffle_name, cap_key, id):
        self.accs_data = accs_data

        self.id = id
        self.address = accs_data['address']
        self.private_key = accs_data['private_key'][2:].strip()
        self.tw_auth_token = accs_data['auth_token']
        self.tw_csrf = accs_data['csrf']
        self.proxy = {'http': accs_data['proxy'], 'https': accs_data['proxy']}
        self.cap_key = cap_key[0]
        self.raffle_name = raffle_name
        self.session = None

        self.slug = None
        self.twitter_ids = None
        self.message = None

    def execute_task(self):
        status = False
        start = time.time()
        # progress_bar = tqdm(total=8, desc=f"{self.id} - Processing...")
        print(f"{self.id} - Processing...")

        try:
            while status == False:
                self.session = tls_client.Session(

                    client_identifier="chrome110",
                    random_tls_extension_order=True

                )

                # print(self.proxy)


                self.session.proxies = self.proxy
                self.session.user_agent = random_user_agent()

                # self.session.headers.update({'referer': "https://freenft.com/", 'origin': 'https://freenft.com'})
                response = self.session.get("https://api.freenft.com/intents")

                # print(response.text)


                # progress_bar.update(1)
                all_data = response.json()['intents']
                for data in all_data:
                    # print(data['name'], self.raffle_name)
                    if data['name'] == self.raffle_name:
                        self.slug = data['slug']
                        self.twitter_ids = data['twitterIdsArray']
                        break
                self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
                response = self.session.post("https://api.freenft.com/auth/verify")
                # progress_bar.update(2)
                nonce = self._get_nonce()
                print(nonce)
                if nonce:
                    # progress_bar.update(3)
                    message = encode_defunct(text=nonce)
                    signed_message = w3.eth.account.sign_message(message, private_key=self.private_key)
                    signature = signed_message["signature"].hex()
                    data = {"publicAddress": self.address.lower(), "signature": signature}
                    response = self.session.post("https://api.freenft.com/auth/signin", json=data)

                    print(response.text)

                    # progress_bar.update(4)
                    token_FN = response.json()['token']
                    self.session.headers.update({'authorization': f'Bearer {token_FN}'})
                    response = self.session.get(f'https://api.freenft.com/wl/{self.slug}/status')
                    p = response.json()

                    data = {'slug': self.slug}
                    response = self.session.get("https://api.freenft.com/intentRegistration")
                    print(response.text)
                    for intent in response.json()['registrationIntents']:
                        if intent['intent'] == self.slug and intent['isRegistered'] == True:
                            # progress_bar.update(8)
                            self.message = f'{self.id} - {bcolors.OKGREEN}Account has already been submitted for {self.raffle_name}{bcolors.ENDC}'
                            self.status = f'Account has already been successfully'
                            status = True
                            break

                    # progress_bar.update(5)
                    # Twitter Follow

                    twitter_session = self._make_scraper_2()
                    twitter_session.proxies = self.session.proxies

                    raffle_data = {'user_id': self.twitter_ids, 'tweet_id': ''}
                    twitter_results = twitter_tasks(twitter_session, self.accs_data, raffle_data, self.id)
                    if twitter_results[0]:
                        # progress_bar.update(6)
                        if status == True:
                            break

                        errors = 0

                        while True:
                            self.session.headers.update({'authorization': f'Bearer {token_FN}'})
                            response = self.session.get(f'https://api.freenft.com/wl/{self.slug}/status')
                            p = response.json()
                            # print(p)

                            if errors == 4:
                                break

                            errors+=1
                            print(errors)

                            if p['twitterUsername'] == "":
                                if status == True:
                                    break
                                #  Connecting twitter
                                try:
                                    oauthToken, oauthVerifier = self.connect_twitter()
                                    # progress_bar.update(7)
                                    data = {'slug': self.slug,
                                            'oauthToken': oauthToken,
                                            'oauthVerifier': oauthVerifier}
                                    self.session.headers.update({'Content-Type': 'application/json'})
                                    response = self.session.post("https://api.freenft.com/verify/addTwitter", json=data)
                                    if response.status_code == 200:
                                        data = self.solve_captcha()
                                        self.session.headers['content-type'] = 'application/json'
                                        try:
                                            data_ = {'slug': self.slug}
                                            response = self.session.post(f"https://api.freenft.com/verify/checkTwitterReq", json=data_)

                                            print(data)
                                            print(1010010)
                                            response = self.session.post(f"https://api.freenft.com/wl/{self.slug}/register", json=data)
                                            if 'registration requirements' in response.text:
                                                break
                                            response = self.session.get("https://api.freenft.com/intentRegistration")
                                            for intent in response.json()['registrationIntents']:
                                                if intent['intent'] == self.slug and intent['isRegistered'] == True:
                                                    # progress_bar.update(8)
                                                    self.message = f'{self.id} - {bcolors.OKGREEN}Account has already been submitted for {self.raffle_name}{bcolors.ENDC}'
                                                    self.status = f'Account has already been successfully'
                                                    status = True
                                                    break
                                        except:
                                            break
                                    else:
                                        if response.status_code == 403:
                                            status = True
                                            break
                                        self.message = f'{self.id} - {bcolors.FAIL}Error response code 403{bcolors.ENDC}'
                                except:
                                    self.message = f'{self.id} - {bcolors.FAIL}Twitter connection failed{bcolors.ENDC}'
                                    status = True
                                    break
                            else:
                                if data:
                                    # progress_bar.update(7)
                                    # print(data)

                                    self.session.headers['content-type'] = 'application/json'
                                    try:

                                        data_ = {'slug': self.slug}
                                        response = self.session.post(f"https://api.freenft.com/verify/checkTwitterReq",
                                                                     json=data_)

                                        print(response.text)
                                        print(1010010)

                                        data = self.solve_captcha()
                                        print(data)

                                        response = self.session.post(f"https://api.freenft.com/wl/{self.slug}/register", json=data)

                                        print(response.text)

                                        if response.json()['status'] == "Intent is not active":
                                            self.message = f'{self.id} - {bcolors.FAIL}Intent is not active{bcolors.ENDC}'
                                            break
                                        response = self.session.get("https://api.freenft.com/intentRegistration")
                                        if response.json()['isRegistered'] == True:

                                            # progress_bar.update(8)
                                            self.message = f'{self.id} - {bcolors.OKGREEN}Account successfully submitted for {self.raffle_name}{bcolors.ENDC}'
                                            self.status = f'Account successfully submitted for {self.raffle_name}'
                                            status = True
                                            break
                                    except Exception as e:
                                        # print(f'Error: {e}')
                                        break
                        if errors == 4:
                            self.status = 'Twitter account is connected to another FreeNFT account'
                            break

                    else:
                        self.message = twitter_results[1]
                        break
            else:



                self.message = f'{self.id} - {bcolors.FAIL}First response error{bcolors.ENDC}'
                self.status = 'First response error'
        except:

            traceback.print_exc()

            self.message = f'{self.id} - {bcolors.FAIL}Unknown error{bcolors.ENDC}'
            self.status = 'First response error'

        # progress_bar.set_description(self.message)
        # progress_bar.close()
        total_time = time.time() - start
        print(f'{self.message} | Time: {total_time}')
        return [total_time, self.status]

    def solve_captcha(self):
        try:
            # print('Solving captcha...')
            # print(self.cap_key)
            cap = capmonster_python.HCaptchaTask(self.cap_key)
            cap.set_proxy('http', self.proxy['http'].split('/')[-1].split('@')[1].split(':')[0],self.proxy['http'].split('/')[-1].split('@')[1].split(':')[1],self.proxy['http'].split('/')[-1].split('@')[0].split(':')[0],self.proxy['http'].split('/')[-1].split('@')[0].split(':')[1])
            tt = cap.create_task("https://freenft.com/", 'c21ddfd2-1bfb-4ab3-88d3-40d839b03c66')
            captcha = cap.join_task_result(tt)
            captcha = captcha["gRecaptchaResponse"]
            # print('Captcha solved')
            return {"captchaToken": captcha, "refCode": "", "answers": None}
        except:
            self.message = f'{self.id} - {bcolors.FAIL}Captcha error{bcolors.ENDC}'

    def connect_twitter(self):
        # print('Connecting twitter...')
        payload = {"address": self.address.lower(),
                   "intent": self.slug,
                   "originUri": "https://freenft.com",
                   "provider": "twitter",
                   "redirectUri": f"/whitelist/{self.slug}"}
        try:
            response = self.session.post('https://api.freenft.com/oauth1/twitter', json=payload, allow_redirects=True)
            oauth_token = response.json()['authorizeUrl'].split('oauth_token=')[-1]
            self.session.cookies.update({'auth_token': self.tw_auth_token, 'ct0': self.tw_csrf})
            params = {'oauth_token': oauth_token}
            response = self.session.get(f'https://api.twitter.com/oauth/authorize', params=params, allow_redirects=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            authenticity_token = soup.find('input', attrs={'name': 'authenticity_token'}).get('value')
            payload = {'authenticity_token': authenticity_token,
                       'redirect_after_login': f'https://api.twitter.com/oauth/authorize?oauth_token={oauth_token}',
                       'oauth_token': oauth_token}
            twitter_ssession = response.headers['set-cookie'].split('_twitter_sess=')[-1].split(';')[0]
            self.session.cookies.update({'_twitter_sess': twitter_ssession})
            self.session.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
            response = self.session.post(f'https://api.twitter.com/oauth/authorize', data=payload, allow_redirects=False)
            soup = BeautifulSoup(response.text, 'html.parser')
            link = soup.find('a', class_='maintain-context').get('href')
            oauth_verifier = link.split('oauth_verifier=')[-1]

            response = self.session.get(link, data=payload, allow_redirects=False)
            return oauth_token, oauth_verifier
        except Exception as e:
            # print(f'Twitter connection error: {e}')
            self.message = f'{self.id} - {bcolors.FAIL}Twitter connection failed{bcolors.ENDC}'

    def _make_scraper(self):

        return tls_client.Session(

            client_identifier="chrome110",

            random_tls_extension_order=True

        )

    def _make_scraper_2(self):

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

    def _get_nonce(self):
        try:
            data = {'publicAddress': self.address.lower()}
            self.session.headers.update({'content-type': 'text/plain;charset=UTF-8', 'referer': 'https://freenft.com/'})
            response = self.session.post("https://api.freenft.com/auth/nonce", json=data)

            nonce = response.json()["nonce"]
            return nonce

        except:
            self.message = f'{self.id} - {bcolors.FAIL}Nonce error{bcolors.ENDC}'

