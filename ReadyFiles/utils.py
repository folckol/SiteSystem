import capmonster_python
from web3 import Web3
import json
import time
import random
import ssl
import cloudscraper
import requests
from fake_useragent import UserAgent


class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def twitter_tasks_TLS(session_, accs_data, raffle_data, id):
    authorization_token = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
    csrf = accs_data['csrf']
    auth_token = accs_data['auth_token']
    cookie = f'auth_token={auth_token}; ct0={csrf}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {authorization_token}',
        'x-csrf-token': csrf,
        'cookie': cookie
    }

    print(raffle_data)

    session = _make_scraper()
    session.proxies = session_.proxies

    if len(raffle_data['tweet_id']) > 0:
        for tweet_id in raffle_data['tweet_id']:
            payload = {"variables": {"tweet_id": tweet_id}, "queryId": "lI07N6Otwv1PhnEgXILM7A"}
            try:
                with session.post("https://api.twitter.com/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet",  headers=headers, json=payload, timeout=30) as response:
                    if 'suspended' in response.text or 'You are unable to follow more people at this time' in response.text:
                        message = f'{id} - {bcolors.FAIL}Twitter banned{bcolors.ENDC}'
                        return [False, message]
            except:
                message = f'{id} - {bcolors.FAIL}Like failed{bcolors.ENDC}'
                return [False, message]
            time.sleep(random.choice([n/10 for n in range(5, 30)]))
            try:
                with session.post("https://api.twitter.com/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet", headers=headers, json=payload, timeout=30) as response:
                    if 'suspended' in response.text or 'You are unable to follow more people at this time' in response.text:
                        message = f'{id} - {bcolors.FAIL}Twitter banned{bcolors.ENDC}'
                        return [False, message]
            except:
                message = f'{id} - {bcolors.FAIL}Retweet failed{bcolors.ENDC}'
                return [False, message]
            time.sleep(random.choice([n/10 for n in range(5, 30)]))

    # Follow
    headers['Content-Type'] = 'application/json'
    for user_id in raffle_data['user_id']:
        try:
            with session.post(f"https://api.twitter.com/1.1/friendships/create.json?user_id={user_id}&follow=true", headers=headers, timeout=30) as response:
                if 'suspended' in response.text or 'You are unable to follow more people at this time' in response.text:
                    message = f'{id} - {bcolors.FAIL}Twitter banned{bcolors.ENDC}'
                    return [False, message]
        except:
            message = f'{id} - {bcolors.FAIL}Follow failed{bcolors.ENDC}'
            return [False, message]
        time.sleep(random.choice([n/10 for n in range(5, 30)]))

    return [True]


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

def twitter_tasks(session, accs_data, raffle_data, id):
    authorization_token = 'AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA'
    csrf = accs_data['csrf']
    auth_token = accs_data['auth_token']
    cookie = f'auth_token={auth_token}; ct0={csrf}'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {authorization_token}',
        'x-csrf-token': csrf,
        'cookie': cookie
    }

    message = ''

    print(raffle_data)

    if len(raffle_data['tweet_id']) > 0:
        for tweet_id in raffle_data['tweet_id']:
            payload = {"variables": {"tweet_id": tweet_id}, "queryId": "lI07N6Otwv1PhnEgXILM7A"}
            try:
                with session.post("https://api.twitter.com/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet",  headers=headers, json=payload, timeout=30) as response:
                    if 'suspended' in response.text or 'You are unable to follow more people at this time' in response.text:
                        message = f'{id} - {bcolors.FAIL}Twitter banned{bcolors.ENDC}'
                        return [False, message]
            except:
                message = f'{id} - {bcolors.FAIL}Like failed{bcolors.ENDC}'
                return [False, message]
            time.sleep(random.choice([n/10 for n in range(5, 30)]))
            try:
                with session.post("https://api.twitter.com/graphql/ojPdsZsimiJrUGLR1sjUtA/CreateRetweet", headers=headers, json=payload, timeout=30) as response:
                    if 'suspended' in response.text or 'You are unable to follow more people at this time' in response.text:
                        message = f'{id} - {bcolors.FAIL}Twitter banned{bcolors.ENDC}'
                        return [False, message]
            except:
                message = f'{id} - {bcolors.FAIL}Retweet failed{bcolors.ENDC}'
                return [False, message]
            time.sleep(random.choice([n/10 for n in range(5, 30)]))

    # Follow
    headers['Content-Type'] = 'application/json'
    for user_id in raffle_data['user_id']:
        try:
            with session.post(f"https://api.twitter.com/1.1/friendships/create.json?user_id={user_id}&follow=true", headers=headers, timeout=30) as response:
                if 'suspended' in response.text or 'You are unable to follow more people at this time' in response.text:
                    message = f'{id} - {bcolors.FAIL}Twitter banned{bcolors.ENDC}'
                    return [False, message]
        except:
            message = f'{id} - {bcolors.FAIL}Follow failed{bcolors.ENDC}'
            return [False, message]
        time.sleep(random.choice([n/10 for n in range(5, 30)]))

    return [True]


def get_list(file_name):
    list = []
    with open(file_name) as file:
        while (line := file.readline().rstrip()):
            list.append(line)
    return list


def get_private_key():
    web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
    list = []
    mnemonics = get_list('test_files/mnemonics.txt')
    for mnemonic in mnemonics:
        web3.eth.account.enable_unaudited_hdwallet_features()
        account = web3.eth.account.from_mnemonic(mnemonic)
        private_key = account.key.hex()
        list.append(private_key)
    return list


def get_address(private_keys):
    web3 = Web3(Web3.HTTPProvider('https://rpc.ankr.com/eth'))
    list = []
    for key in private_keys:
        account = web3.eth.account.from_key(key)
        address = account.address
        list.append(address)
    return list


def get_tokens(cookie):
    json_data = json.loads(cookie)
    result = {'auth_token': '', 'csrf': ''}

    for object in json_data:
        if object['domain'] == '.twitter.com' and object['name'] == 'auth_token':
            result['auth_token'] = object['value']
        elif object['domain'] == '.twitter.com' and object['name'] == 'ct0':
            result['csrf'] = object['value']

    return result

def check_cap_balance(cap_key):
    cap = capmonster_python.HCaptchaTask(cap_key)
    bal = cap.get_balance()
    if str(bal) == "0" or str(bal) == "0.0":
        print("More Funds Then 0 Needed")
