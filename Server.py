import ast
import pickle
import traceback
from datetime import datetime
import json
import threading
import time
import uuid
import tls_client

from flask import Flask, jsonify, request


from eth_account.messages import encode_defunct
from eth_account.signers.local import LocalAccount
from fake_useragent import UserAgent
from web3.auto import w3
from Twitter_model.Main_model import *
from sqlalchemy.orm import sessionmaker
from Creating_DBs import *

import warnings
from sqlalchemy.exc import SAWarning
warnings.filterwarnings('ignore',
 r"^Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively\, "
 "and SQLAlchemy must convert from floating point - rounding errors and other "
 "issues may occur\. Please consider storing Decimal numbers as strings or "
 "integers on this platform for lossless storage\.$",
 SAWarning, r'^sqlalchemy\.sql\.type_api$')


app = Flask(__name__)
my_function_lock = threading.Lock()

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



def database_cleaner():
    while True:

        try:
            Session = sessionmaker(bind=engine)
            session = Session()

            raffles = session.query(AccessedRaffle).all()

            data = []
            for raffle_ in raffles:

                try:
                    raffle = raffle_.raffle[0]
                except:
                    session.query(AccessedRaffle).filter(AccessedRaffle.id == raffle_.id).delete()
                    continue

            session.commit()
            print(datetime.now(), '- данные Cleaner обновлены')

            links = session.query(Raffle.platformLink).all()
            # print(len(raffles), len(set(raffles)))

            used_Link = []
            used = []

            a = session.query(Raffle).filter(Raffle.category != 'one_time').all()
            print(len(a))
            # session.commit()

            print('ready')



            raffles =  session.query(Raffle).all()
            for raffle in raffles:

                if raffle.id not in used:
                    used.append(raffle.id)
                else:
                    session.query(Raffle).filter(Raffle.id == raffle.id).delete()
                    session.commit()

                if raffle.platformLink not in used_Link or raffle.platform == 'Twitter':
                    used_Link.append(raffle.platformLink)
                else:
                    # print(raffle.platformLink)
                    session.query(Raffle).filter(Raffle.id == raffle.id).delete()
                    session.commit()



                deadline = 999999999999
                # if raffle.id == '158c3808-01a8-489c-b0c9-fad4dff07bce':
                # print(raffle.id, raffle.deadline, int(time.time()))


                if raffle.deadline is not None:

                    # if raffle.platform == 'Alphabot' and raffle.category != 'one_time':
                    #     print(raffle.deadline, time.time())

                    if ' ' in raffle.deadline:
                        try:
                            date_obj = datetime.strptime(raffle.deadline, '%Y-%m-%d %H:%M:%S')
                            deadline = int(date_obj.timestamp())
                        except:
                            deadline = 0
                    elif raffle.deadline != None and raffle.deadline != '':
                        try:
                            deadline = int(raffle.deadline)

                            if len(raffle.deadline) == 13:
                                deadline = int(raffle.deadline[:-3])

                        except:
                            deadline = 0

                        if deadline < int(time.time()):
                            ses = session.query(Raffle).filter(Raffle.id == raffle.id).first()
                            ses.category = 'one_time'
                            session.commit()
                            continue

                    # if raffle.platform == 'Superful':
                    #     print(raffle.id, deadline, time.time(), raffle.category)

                    elif int(time.time())-int(raffle.timestamp) > 864000 or int(time.time())>deadline:
                        ses = session.query(Raffle).filter(Raffle.id == raffle.id).first()
                        ses.category = 'one_time'
                        session.commit()

                    elif len(str(raffle.deadline)) == 13 and (int(str(raffle.deadline)[:-3]) if raffle.platform=='Superful' else int(str(raffle.deadline)[:-3]) + 36000) < int(time.time()):


                        ses = session.query(Raffle).filter(Raffle.id == raffle.id).first()
                        ses.category = 'one_time'
                        session.commit()


                    elif int(time.time())-int(raffle.timestamp) > 864000*4 or int(time.time())>deadline+864000*2:
                        session.query(Raffle).filter(Raffle.id == raffle.id).first()
                        session.commit()



                try:
                    if raffle.requirements == []:
                        session.query(Raffle).filter(Raffle.id == raffle.id).delete()
                        session.commit()
                except:
                    pass

                # print(link, category)

                # print(category, name)
                # if category != None:
                #     rr = session.query(Raffle).filter(Raffle.platformLink == link and Raffle.category == category).all()
                #
                #     # try:
                #     #     print(rr[0].platformLink, rr[0].category)
                #     #     print(rr[1].platformLink, rr[1].category)
                #     #     print(rr[2].platformLink, rr[2].category)
                #     #     print(rr[3].platformLink, rr[3].category)
                #     # except:
                #     #     pass
                #
                #     if len(rr) > 1:
                #         for rrr in rr:
                #             if rrr == rr[0]:
                #                 continue
                #             session.query(Raffle).filter(Raffle.id==rrr.id).delete()
                #             session.commit()


            session.close()


            # time.sleep(300)
        except:
            # traceback.print_exc()
            pass

        try:
            session.close()
        except:
            pass




def schedule_function():
    while True:

        # print('1')
        #
        # try:
        #     get_free_nft_raffles()
        # except:
        #
        #     traceback.print_exc()
        #
        #     print('Ошибка с FreeNFT')

        analiseless_data = get_resources()

        print(analiseless_data)

        for data in analiseless_data:

            Session = sessionmaker(bind=engine)
            session = Session()

            # try:
            #     session.query(Raffle).filter(Raffle.category == data['name']).delete()
            #     session.commit()
            # except:
            #     pass

            result_data = execute_query(data['links'])
            # print(data['name'], len(result_data))
            # new_results = []

            # print('go')


            __ = session.query(Raffle).filter(Raffle.platform == 'Premint').all()
            _ = []
            for i in __:
                _.append(i.platformLink)
            names = []
            for i in result_data:
                names.append(i['Link'])
                # if i not in _:
                #     new_results.append(i)

            # print('go2')

            for i in _:
                # print(i)
                if i not in names:
                    try:
                        delete_list = []
                        r = session.query(Raffle).filter(
                            Raffle.platformLink == i and Raffle.category == data['name']).all()
                        # print(r)
                        for ir in r:
                            if ir == r[0]:
                                r.category = 'open'
                                session.commit()
                            else:
                                delete_list.append(Raffle.id)

                        for ir in delete_list:
                            session.query(Raffle).filter(Raffle.id == ir).delete()
                            session.commit()

                    except:
                        pass

            # print('go3')

            for i in result_data:

                # print(i)

                try:
                    a = i['Discord']['Info'][0]
                    continue
                except:
                    pass

                status = 1
                rfls = session.query(Raffle).all()

                for rfl in rfls:
                    if rfl.platformLink == i['Link'] and rfl.category == data['name']:
                        status = None
                        break

                if status is None:
                    # print(i['Link'], data['name'])
                    continue

                raffle = Raffle(id=str(uuid.uuid4()),
                                platform='Premint',
                                category=data['name'],
                                name=i['RaffleName'],
                                platformLink=i['Link'],
                                timestamp=str(int(time.time()))
                                )

                # print(i['RaffleName'])
                if i['Project_Info']['Total_Supply'] != None:
                    raffle.TotalSupply = i['Project_Info']['Total_Supply']
                if i['Project_Info']['Number_of_winners'] != None:
                    raffle.NumberOfWinners = i['Project_Info']['Number_of_winners']
                if i['ProfilePictureLink'] != None:
                    raffle.profilePicture = i['ProfilePictureLink']
                if i['ProfileBannerLink'] != None:
                    raffle.banner = i['ProfileBannerLink']
                if i['Project_Info']['Verified_Twitter'] != None:
                    raffle.subscribers = i['Project_Info']['Verified_Twitter'][1]
                if i['Project_Info']['Registration_Closing'] != None:
                    raffle.deadline = i['Project_Info']['Registration_Closing']
                if i['Min_wallet_balance']:
                    raffle.hold = ''
                    raffle.hold += i['Min_wallet_balance']
                if i['NFT']['Hold'] != []:
                    if raffle.hold != None:
                        raffle.hold += '|'
                        for ii in i['NFT']['Hold']:
                            raffle.hold += ii
                            if ii != i['NFT']['Hold'][-1]:
                                raffle.hold += '|'
                    else:
                        raffle.hold = ''
                        for ii in i['NFT']['Hold']:
                            raffle.hold += ii
                            if ii != i['NFT']['Hold'][-1]:
                                raffle.hold += '|'

                reqs = []


                if i['Need_Discord'] != False:
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Discord',
                                            action='Connect',
                                            clarification=''))


                for twitter_reqs in i['Twitter']['Follow']:
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='Follow',
                                            clarification=twitter_reqs))

                for twitter_reqs in i['Twitter']['LikeRetweet']:
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='LikeRetweet',
                                            clarification=twitter_reqs))

                for discord_reqs in i['Discord']['Join']:
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Discord',
                                            action='Join',
                                            clarification=discord_reqs))

                raffle.requirements = reqs

                # print(raffle.name, raffle.category)

                if len(reqs) > 0:
                    session.add(raffle)
                    session.commit()

            session.close()




        print(datetime.now(), '- данные обновлены')

        time.sleep(3000)  # 600 секунд = 10 минут


def AlphabotGetRaffles():


    while True:

        start_time = time.time()

        try:
            get_alphabot_raffles()
        except Exception as e:
            traceback.print_exc()
            print('Ошибка с Alphabot')
            pass

        end_time = time.time()
        elapsed_time = end_time - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)

        print(f"Обновление данных Alphabot завершено: {int(hours):02d}:{int(minutes):02d}:{seconds:.5f}")

        time.sleep(3000)


def get_alphabot_raffles():

    all_raffles = []
    for i in [0, 1, 2, 3]:
        d = session_alphabot.get(
            f'https://www.alphabot.app/api/projectData/search?sort=starCount&sortDir=-1&pageNum={i}&search=&earliest=1681074000000&pageSize=100&blockchains=ETH')
        for ii in d.json():
            if ii['name'] not in all_raffles:
                all_raffles.append(ii)

    for i in all_raffles:

        time.sleep(2)

        d = session_alphabot.get(f'https://www.alphabot.app/api/projectData/{i["_id"]}/raffles').json()

        for dd in d:

            raffle_url = f'https://www.alphabot.app/{dd["slug"]}'

            Session = sessionmaker(bind=engine)
            session = Session()

            usedRaffles = session.query(Raffle.platformLink).all()
            if raffle_url in usedRaffles:
                session.close()
                continue

            session.close()

            with session_alphabot.get(raffle_url, timeout=15) as response:
                try:
                    data = response.text
                except:
                    continue
                # print(data)

                result = json.loads(data.split(',"project":')[-1].split(',"statusCode"')[0])

                id_ = str(uuid.uuid4())
                raffle = Raffle(id=id_,
                                timestamp=str(int(time.time())))

                try:
                    if result['requirePremium'] == True:
                        continue

                except:
                    pass

                raffle.platform = 'Alphabot'
                raffle.category = 'open'

                # SolanaTest
                if result['blockchain'] == 'SOL':
                    return 'Skip (SOL)'

                raffle.platformLink = raffle_url



                # Подписки в твиттере
                twitter_follows = result['twitterFollows']

                reqs = []
                user_ids = []
                for user in twitter_follows:
                    user_ids.append(user['id'])
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='Follow',
                                            clarification=f"@{user['name']}|{user['id']}"))

                # Ретвиты + лайки в твиттере
                try:
                    retweet_id = result['twitterRetweet'].split('/')[-1]
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='LikeRetweet',
                                            clarification=retweet_id))
                except:
                    retweet_id = []

                try:
                    raffle.banner = result['projectData']['twitterBannerImage']

                except:
                    raffle.banner = ''

                try:

                    raffle.profilePicture = result['projectData']['twitterProfileImage']

                except:
                    raffle.profilePicture = ''

                try:

                    raffle.name = result['name']

                except:
                    raffle.name = ''

                try:

                    raffle.hold = result['requiredEth']

                except:
                    raffle.hold = '0'

                try:
                    raffle.deadline = result['endDate']
                except:
                    raffle.deadline = ''

                try:
                    raffle.captcha = result['connectCaptcha']
                except:
                    raffle.captcha = False

                try:
                    subscribers = Get_user_followers(result['twitterId'])
                    raffle.subscribers = subscribers
                except:
                    raffle.subscribers = ''

                discord_status = result['connectDiscord']
                skipRaffle = False

                if discord_status == True:

                    links = []

                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Discord',
                                            action='Connect',
                                            clarification=''))

                    # try:
                    #     discordInvite = result['discordUrl']
                    #     if discordInvite != '' and discordInvite != None and discordInvite not in links:
                    #         reqs.append(Requirement(id=str(uuid.uuid4()),
                    #                                 platform='Discord',
                    #                                 action='Join',
                    #                                 clarification=discordInvite))
                    #         links.append(discordInvite)
                    # except:
                    #     pass

                    roles = result['discordServerRoles']
                    # print(roles)

                    for i in roles:

                        try:
                            if i['inviteLink'] not in links:

                                reqs.append(Requirement(id=str(uuid.uuid4()),
                                                        platform='Discord',
                                                        action='Join',
                                                        clarification=i['inviteLink']))

                                links.append(i['inviteLink'])

                        except:
                            pass

                        try:
                            if len(i['roles']) > 0:
                                skipRaffle = True
                                break
                        except:
                            pass
                try:
                    email_status = result['connectEmail']
                    if email_status == True:
                        skipRaffle = True
                except:
                    pass

                # print(skipRaffle)
                if skipRaffle == True:
                    continue

                raffle.requirements = reqs

                Session = sessionmaker(bind=engine)
                session = Session()

                raffles = session.query(Raffle.platformLink).all()
                if raffle_url in raffles:
                    id_ = session.query(Raffle.id).filter(Raffle.platformLink == raffle_url).first()
                else:
                    session.add(raffle)
                    session.commit()


                session.commit()
                session.close()




def SuperfulGetRaffles():

    while True:

        start_time = time.time()

        try:
            get_superful_raffles()
        except Exception as e:
            # traceback.print_exc()
            # print('Ошибка с Superful')
            pass

        end_time = time.time()
        elapsed_time = end_time - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)

        print(f"Обновление данных Superful завершено: {int(hours):02d}:{int(minutes):02d}:{seconds:.5f}")

        time.sleep(3000)


def get_superful_raffles():

    payload = {
        "filter_category": [],
        "filter_requirements": [],
        "page": 1,
        "page_size": 500
    }

    with session_superful.post('https://www.superful.xyz/superful-api/v1/project/events',json = payload, timeout=15) as response:
        # print(response.text)

        data_ = response.json()
        # print(data)

        for slug in data_['results']:

            slug_ = slug['slug']
            link = f'https://www.superful.xyz/superful-api/v1/project?event_slug={slug_}'
            with session_superful.get(link, timeout=15) as response:

                data = response.json()
                # print(data)

                for event in data['events']['results']:
                    if event['slug'] == slug_:

                        id_ = str(uuid.uuid4())
                        raffle = Raffle(id=id_,
                                        timestamp=str(int(time.time())))

                        name = event['name']
                        raffle.name = name

                        raffle.category = 'open'


                        profilePicture = event['collab']['logo_url'] if data['project']['logo_url'] == 'https://superful-assets-prod.s3.amazonaws.com/images/1e22c7ce-9035-4958-9dcf-468cf33b13bb.jpg' else data['project']['logo_url']
                        raffle.profilePicture = profilePicture


                        banner = event['collab']['banner_url'] if data['project']['banner_url'] == 'https://superful-assets-prod.s3.amazonaws.com/images/9ab6a301-a37a-4232-93a3-6f2669286d71.jpg' else data['project']['banner_url']
                        raffle.banner = banner

                        try:
                            hold = event['wallet_balance_required']
                            raffle.hold = hold
                        except:
                            raffle.hold = None

                        def convert_to_timestamp(date_str):
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            return int(date_obj.timestamp())

                        try:
                            if 'superful' not in data['project']['twitter_username']:
                                subscribers = Get_user_followers(Get_user_id(data['project']['twitter_username']))
                            else:
                                subscribers = Get_user_followers(Get_user_id(event['collab']['twitter_handler']))
                        except:
                            try:
                                subscribers = Get_user_followers(Get_user_id(event['collab']['twitter_handler']))
                            except:
                                subscribers = Get_user_followers(Get_user_id(event['twitter_requirements'][0]))

                        raffle.subscribers = subscribers

                        deadline = event['end_date']+' '+event['end_time']
                        raffle.deadline = int(convert_to_timestamp(deadline))-36000


                        try:
                            if data['project']['total_supply'] == 1337:
                                raffle.TotalSupply = data['project']['total_supply']
                            else:
                                raffle.TotalSupply = event['collab']['total_supply']
                        except:
                            pass

                        try:
                            raffle.NumberOfWinners = event['spots']
                        except:
                            pass

                        platformLink = f'https://www.superful.xyz/{event["slug"]}'
                        raffle.platformLink = platformLink

                        used_ds= []

                        raffle.platform = 'Superful'

                        captcha = event['recaptcha_required']
                        raffle.captcha = captcha


                        reqs = []

                        if event['tweet_id_verify'] != '':
                            reqs.append(Requirement(id=str(uuid.uuid4()),
                                                    platform='Twitter',
                                                    action='LikeRetweet',
                                                    clarification=event['tweet_id_verify']))

                        for twitter_req in event['twitter_requirements']:
                            twitter_id = Get_user_id(twitter_req)
                            reqs.append(Requirement(id=str(uuid.uuid4()),
                                                    platform='Twitter',
                                                    action='Follow',
                                                    clarification=f'@{twitter_req}|{twitter_id}'))


                        if event['discord_requirements']['required'] == True:
                            reqs.append(Requirement(id=str(uuid.uuid4()),
                                                    platform='Discord',
                                                    action='Connect',
                                                    clarification=''))

                            if event['collab']['discord_invite_code'] != '' and event['collab']['discord_invite_code'] not in used_ds:
                                reqs.append(Requirement(id=str(uuid.uuid4()),
                                                        platform='Discord',
                                                        action='Join',
                                                        clarification=f"https://discord.gg/{event['collab']['discord_invite_code']}"))
                                used_ds.append(event['collab']['discord_invite_code'])

                        pa = 0
                        for discord_req in event['discord_requirements']['requirements']:

                            if discord_req['role_required'] == True:
                                pa = 1
                                break

                            if discord_req['server_invite_code'] != None and discord_req['server_invite_code'] != '' and discord_req['server_invite_code'] not in used_ds:
                                reqs.append(Requirement(id=str(uuid.uuid4()),
                                                        platform='Discord',
                                                        action='Join',
                                                        clarification=f"https://discord.gg/{discord_req['server_invite_code']}"))
                                used_ds.append(discord_req['server_invite_code'])

                        if pa == 1:
                            continue

                        raffle.requirements = reqs

                        timestamp = int(datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S').timestamp())

                        if timestamp <= int(time.time()):
                            continue

                        Session = sessionmaker(bind=engine)
                        session = Session()


                        raffles = session.query(Raffle.platformLink).all()
                        if platformLink in raffles:
                            id_ = session.query(Raffle.id).filter(Raffle.platformLink == platformLink).first()
                        else:
                            session.add(raffle)
                            session.commit()

                        session.close()
                        # print(name)
                        break



def get_resources():
    with my_function_lock:
        links = []
        premints = ['https://www.premint.xyz/collectors/explore/top/',
                    'https://www.premint.xyz/collectors/explore/new/',
                    'https://www.premint.xyz/collectors/explore/']

        for premint_link in premints:

            with session.get(premint_link, timeout=15) as response:
                # print(response.text)

                if premint_link == premints[0]:
                    local = {'name': 'top_this_week',
                             'links': []}
                elif premint_link == premints[1]:
                    local = {'name': 'new',
                             'links': []}
                elif premint_link == premints[2]:
                    local = {'name': 'today',
                             'links': []}

                soup = BeautifulSoup(response.content, "lxml")

                elements = soup.find_all('div', class_='d-flex strong border-left border-right border-bottom p-3')

                for element in elements:
                    link = element.find('a', class_="text-lightdark heading heading-5")
                    link = link.get('href')

                    full_link = f'https://www.premint.xyz{link}'

                    local['links'].append(full_link)

                links.append(local)

        return links

def execute_query(links):

    results = []

    for link in links:
        try:
            response = session.get(link)
            # print(link)
            # print(response.text)

            result = {  'Link': link,

                        'RaffleName': None,

                        'ProfilePictureLink': None,
                        'ProfileBannerLink': None,

                        'Twitter': {
                                    'Follow': [],
                                    'LikeRetweet': []
                                   },
                        'Need_Discord': False,
                        'Discord': {'Join': [],
                                    'Info': []
                                    },
                        'NFT': {'Hold': []
                                },
                        'Code': None,
                        'Additional_info': None,
                        'Min_wallet_balance': None,
                        'Project_Info': {'Name': None,
                                         'Registration_Closing': None,
                                         'Mint_Date': None,
                                         'Mint_Price': None,
                                         'Total_Supply': None,
                                         'Number_of_winners': None,
                                         'Raffle_Time': None,
                                         'Official_Link': None,
                                         'Verified_Twitter': None,
                                         'Verified_Discord': None,
                                         'Alert': None}
                        }

            soup = BeautifulSoup(response.text, "html.parser")

            bb = soup.findAll('div', class_='heading heading-5 mb-0')
            for i in bb:
                if 'Discord' in i.text:
                    result['Need_Discord'] = True

            boxes = soup.findAll('div', class_='col-12')
            # print(box)
            for box in boxes:

                conditions = box.find_all('div')
                for condition in conditions:
                    text = condition.text.replace('   ', '').replace('\n', '').replace('  ', ' ').replace('  ', ' ')

                    if 'Enter your email' in text:
                        result['Additional_info'] = 'Email'

                    elif 'Hold' in text:
                        links = condition.findAll('a')
                        for link in links:
                            result['NFT']['Hold'].append(link.get('href'))

                    elif 'Follow' in text:
                        links = condition.findAll('a')
                        for link in links:

                            username = str(link.get('href')).split('/')[-1]
                            id_ = Get_user_id(username)

                            result['Twitter']['Follow'].append(f'@{username}|{id_}')

                    elif 'Must Like' in text or 'Must Retweet' in text:
                        links = condition.findAll('a')
                        for link in links:
                            result['Twitter']['LikeRetweet'].append(str(link.get('href')).split('/')[-1])

                    elif 'Have at least' in text:
                        count = text.split('Have at least ')[-1].split(' ')[0]
                        result['Min_wallet_balance'] = count

                    elif 'Join' in text:

                        result['Need_Discord'] = True

                        links = condition.findAll('a')
                        for link in links:
                            result['Discord']['Join'].append(link.get('href'))

                        if 'role' in text:
                            result['Discord']['Info'].append(text)

                headings = box.find_all('div.heading')
                for heading in headings:
                    if 'Discord' in heading.text:
                        result['Need_Discord'] = True


            try:
                name = soup.find('h1', class_='heading heading-1')
                result['RaffleName'] = name.text.replace('\n                            ', '').replace('  ', '').replace('\n', '')
            except:
                pass

            try:
                picture = soup.find('div', class_='has-bg-cover')
                result['ProfileBannerLink'] = picture.get('style').split("url('")[1].split("')")[0]
            except:
                pass

            try:
                picture = soup.find('div', class_='profile-picture')
                result['ProfilePictureLink'] = picture.find('img').get('src')
            except:
                pass

            try:
                alert = soup.find('div', class_='alert-warning').text
                result['Project_Info']['Alert'] = alert
            except:
                pass

            try:
                main_name = soup.find('h1', class_='heading').text
                result['Project_Info']['Name'] = main_name.replace('\n                            ', '').replace('  ', '').replace('\n', '')
            except:
                pass

            info_boxes = soup.findAll('div', class_='col-6')

            for info_box in info_boxes:
                name = info_box.find('div', class_='text-uppercase').text
                info = info_box.find('span').text

                if 'Registration Closes' in name:
                    result['Project_Info']['Registration_Closing'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                elif 'Mint Date' in name:
                    result['Project_Info']['Mint_Date'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                elif 'Mint Price' in name:
                    result['Project_Info']['Mint_Price'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                elif 'Total Supply' in name:
                    result['Project_Info']['Total_Supply'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                    if result['Project_Info']['Total_Supply'] == 'NoneNFTs':
                        result['Project_Info']['Total_Supply'] = None
                    elif 'NFTs' in result['Project_Info']['Total_Supply'] and ' ' not in result['Project_Info']['Total_Supply']:
                        result['Project_Info']['Total_Supply'] = result['Project_Info']['Total_Supply'].replace('NFTs', ' NFTs')
                elif 'Number of Winners' in name:
                    result['Project_Info']['Number_of_winners'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                    if 'Spots' in result['Project_Info']['Number_of_winners'] and ' ' not in result['Project_Info']['Number_of_winners']:
                        result['Project_Info']['Number_of_winners'] = result['Project_Info']['Number_of_winners'].replace("Spots", ' Spots')
                elif 'Raffle Time' in name:
                    result['Project_Info']['Raffle_Time'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                elif 'Official Link' in name:
                    result['Project_Info']['Official_Link'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                elif 'Verified Twitter' in name:
                    # result['Project_Info']['Verified_Twitter'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                    try:
                        result['Project_Info']['Verified_Twitter'] = [info.split('\n                            ')[0].replace('  ', '').replace('\n', ''), info.split('\n                            ')[1].replace('  ', '').replace('\n', '')]
                    except:
                        result['Project_Info']['Verified_Twitter'] = [
                            info.split('\n                            ')[0].replace('  ', '').replace('\n', '')]

                elif 'Verified Discord' in name:
                    # result['Project_Info']['Verified_Twitter'] = info.replace('\n                            ', '').replace('  ', '').replace('\n', '')
                    try:
                        result['Project_Info']['Verified_Discord'] = [info.split('\n                            ')[0].replace('  ', '').replace('\n', ''), info.split('\n                            ')[1].replace('  ', '').replace('\n', '')]
                    except:
                        pass

            results.append(result)

        except:

            continue


    return results

def get_raffle_data_alphabot(raffle_url, category):
    with session_alphabot.get(raffle_url, timeout=15) as response:
        data = response.text
        # print(data)

        result = json.loads(data.split(',"project":')[-1].split(',"statusCode"')[0])

        id_ = str(uuid.uuid4())
        raffle = Raffle(id=id_,
                        timestamp=str(int(time.time())))

        try:
            if result['requirePremium'] == True:
                return 'Skip'

        except:
            pass

        raffle.platform = 'Alphabot'
        raffle.category = category

        if result['blockchain'] == 'SOL':
            return 'Skip (SOL)'

        raffle.platformLink = raffle_url

        # Подписки в твиттере
        twitter_follows = result['twitterFollows']

        reqs = []
        user_ids = []
        for user in twitter_follows:
            user_ids.append(user['id'])
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Twitter',
                                    action='Follow',
                                    clarification=f"@{user['name']}|{user['id']}"))

        # Ретвиты + лайки в твиттере
        try:
            retweet_id = result['twitterRetweet'].split('/')[-1]
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Twitter',
                                    action='LikeRetweet',
                                    clarification=retweet_id))
        except:
            retweet_id = []

        try:
            raffle.banner = result['projectData']['twitterBannerImage']

        except:
            raffle.banner = ''

        try:

            raffle.profilePicture = result['projectData']['twitterProfileImage']

        except:
            raffle.profilePicture = ''

        try:

            raffle.name = result['name']

        except:
            raffle.name = ''

        try:

            raffle.hold = result['requiredEth']

        except:
            raffle.hold = '0'

        try:
            raffle.deadline = result['endDate']
        except:
            raffle.deadline = ''

        try:
            raffle.captcha = result['connectCaptcha']
        except:
            raffle.captcha = False

        try:
            subscribers = Get_user_followers(result['twitterId'])
            raffle.subscribers = subscribers
        except:
            raffle.subscribers = ''

        discord_status = result['connectDiscord']
        skipRaffle = False

        if discord_status == True:

            links = []

            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Discord',
                                    action='Connect',
                                    clarification=''))

            # try:
            #     discordInvite = result['discordUrl']
            #     if discordInvite != '' and discordInvite != None and discordInvite not in links:
            #         reqs.append(Requirement(id=str(uuid.uuid4()),
            #                                 platform='Discord',
            #                                 action='Join',
            #                                 clarification=discordInvite))
            #         links.append(discordInvite)
            # except:
            #     pass

            roles = result['discordServerRoles']

            for i in roles:

                try:
                    if i['inviteLink'] not in links:
                        reqs.append(Requirement(id=str(uuid.uuid4()),
                                                platform='Discord',
                                                action='Join',
                                                clarification=i['inviteLink']))
                    links.append(i['inviteLink'])

                except:
                    pass

                try:
                    if len(i['roles']) > 0:
                        skipRaffle = True
                        break
                except:
                    pass

        email_status = result['connectEmail']
        if email_status == True:
            skipRaffle = True

        # print(skipRaffle)
        if skipRaffle == True:
            return 'Skip'

        raffle.requirements = reqs

        Session = sessionmaker(bind=engine)
        session = Session()

        raffles = session.query(Raffle.platformLink).all()
        if raffle_url in raffles:
            id_ = session.query(Raffle.id).filter(Raffle.platformLink == raffle_url).first()
        else:
            session.add(raffle)
            session.commit()

        return id_

def get_raffle_data_superful(slug, category):
    slug_ = slug.split('/')[-1]
    link = f'https://www.superful.xyz/superful-api/v1/project?event_slug={slug_}'
    with session_superful.get(link, timeout=15) as response:

        data = response.json()
        # print(data)

        for event in data['events']['results']:
            if event['slug'] == slug_:

                id_ = str(uuid.uuid4())
                raffle = Raffle(id=id_,
                                timestamp=str(int(time.time())))

                name = event['name']
                raffle.name = name

                raffle.category = category

                profilePicture = event['collab']['logo_url']
                raffle.profilePicture = profilePicture

                banner = event['collab']['banner_url']
                raffle.banner = banner

                hold = event['wallet_balance_required']
                raffle.hold = hold

                subscribers = Get_user_followers(Get_user_id(event['twitter_requirements'][0]))
                raffle.subscribers = subscribers

                def convert_to_timestamp(date_str):
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    return int(date_obj.timestamp())

                deadline = event['end_date']+' '+event['end_time']
                raffle.deadline = convert_to_timestamp(deadline)

                platformLink = f'https://www.superful.xyz/{slug_}'
                raffle.platformLink = platformLink

                raffle.platform = 'Superful'

                captcha = event['recaptcha_required']
                raffle.captcha = captcha

                used_ds = []

                reqs = []

                if event['tweet_id_verify'] != '':
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='LikeRetweet',
                                            clarification=event['tweet_id_verify']))

                for twitter_req in event['twitter_requirements']:
                    twitter_id = Get_user_id(twitter_req)
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='Follow',
                                            clarification=f'@{twitter_req}|{twitter_id}'))


                if event['discord_requirements']['required'] == True:
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Discord',
                                            action='Connect',
                                            clarification=''))

                    if event['collab']['discord_invite_code'] != '' and event['collab']['discord_invite_code'] not in used_ds:
                        reqs.append(Requirement(id=str(uuid.uuid4()),
                                                platform='Discord',
                                                action='Join',
                                                clarification=f"https://discord.gg/{event['collab']['discord_invite_code']}"))
                        used_ds.append(event['collab']['discord_invite_code'])

                for discord_req in event['discord_requirements']['requirements']:

                    if discord_req['role_required'] == True:
                        return 'Role Required'

                    if discord_req['server_invite_code'] != None and discord_req['server_invite_code'] != '' and discord_req['server_invite_code'] not in used_ds:
                        reqs.append(Requirement(id=str(uuid.uuid4()),
                                                platform='Discord',
                                                action='Join',
                                                clarification=f"https://discord.gg/{discord_req['server_invite_code']}"))
                        used_ds.append(discord_req['server_invite_code'])

                raffle.requirements = reqs

                timestamp = int(datetime.strptime(deadline, '%Y-%m-%d %H:%M:%S').timestamp())

                if timestamp <= int(time.time()):
                    return 'Raffle is over'

                Session = sessionmaker(bind=engine)
                session = Session()


                raffles = session.query(Raffle.platformLink).all()
                if platformLink in raffles:
                    id_ = session.query(Raffle.id).filter(Raffle.platformLink == platformLink).first()
                else:
                    session.add(raffle)
                    session.commit()

                session.close()

                return id_




def get_free_nft_raffles():

    data = session_freenft.get("https://api.freenft.com/intents").json()
    # print(data)
    all_data = data['intents']

    # print(all_data)

    Session = sessionmaker(bind=engine)
    session = Session()

    # try:
    #     session.query(Raffle).filter(Raffle.platform == 'FreeNFT').delete()
    #     session.commit()
    # except:
    #     pass

    # session.close()
    all_names = []
    for data in all_data:

        all_names.append(data['name'])

        id_ = str(uuid.uuid4())
        raffle = Raffle(id=id_,
                        timestamp=str(int(time.time())))

        _ = session.query(Raffle).filter(Raffle.name == data['name']).first()
        if _: continue

        profilePicture = data['imageUrl']
        raffle.profilePicture = profilePicture

        raffle.category = 'FreeNFT'
        raffle.platform = 'FreeNFT'

        try:
            banner = data['banner']['backgroundImage']
            raffle.banner = banner
        except:
            raffle.banner = ''

        name = data['name']
        raffle.name = name

        subscribers = Get_user_followers(data['twitterIdsArray'][0])
        raffle.subscribers = subscribers


        deadline = datetime.fromtimestamp(int(data['endTime']))
        raffle.deadline = deadline

        platformLink = f"https://freenft.com/whitelist/{data['slug']}"
        raffle.platformLink = platformLink

        captcha = 'hcaptcha'
        raffle.captcha = captcha

        reqs = []

        j = 0
        for twitter_req in data['twitterIdsArray']:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Twitter',
                                    action='Follow',
                                    clarification=f'@{data["twitterHandlesArray"][j]}|{twitter_req}'))
            j+=1

        raffle.requirements = reqs



        # Session = sessionmaker(bind=engine)
        # session = Session()

        session.add(raffle)
        session.commit()
        session.close()

    Session = sessionmaker(bind=engine)
    session = Session()

    FN_raffles = session.query(Raffle.name).filter(Raffle.category == 'FreeNFT').all()
    for i in FN_raffles:
        if i in all_names:
            session.query(Raffle).filter(Raffle.name == i).delete()
            session.commit()

    session.close()


#
#
# Эндпоинты

@app.route('/data/premint', methods=['POST'])
def premint():

    data = request.get_json()['links']

    try:
        result_data = execute_query(data)

        for i in result_data:

            Session = sessionmaker(bind=engine)
            session = Session()

            # print(i)

            try:
                a = i['Discord']['Info'][0]
                continue
            except:
                pass

            id = str(uuid.uuid4())
            raffle = Raffle(id=id,
                            platform='Premint',
                            category='one_time',
                            name=i['RaffleName'],
                            platformLink=i['Link'],
                            timestamp=str(int(time.time()))
                            )
            if i['Project_Info']['Total_Supply'] != None:
                raffle.TotalSupply = i['Project_Info']['Total_Supply']
            if i['Project_Info']['Number_of_winners'] != None:
                raffle.NumberOfWinners = i['Project_Info']['Number_of_winners']
            if i['ProfilePictureLink'] != None:
                raffle.profilePicture = i['ProfilePictureLink']
            if i['ProfileBannerLink'] != None:
                raffle.banner = i['ProfileBannerLink']
            if i['Project_Info']['Verified_Twitter'] != None:
                raffle.subscribers = i['Project_Info']['Verified_Twitter'][1]
            if i['Project_Info']['Registration_Closing'] != None:
                raffle.deadline = i['Project_Info']['Registration_Closing']


            reqs = []

            if i['Additional_info']  is not None:
                reqs.append(Requirement(id=str(uuid.uuid4()),
                                        platform='Email',
                                        action='Input',
                                        clarification=''))

            if i['Need_Discord'] != False:
                reqs.append(Requirement(id=str(uuid.uuid4()),
                                        platform='Discord',
                                        action='Connect',
                                        clarification=''))

            for twitter_reqs in i['Twitter']['Follow']:
                reqs.append(Requirement(id=str(uuid.uuid4()),
                                        platform='Twitter',
                                        action='Follow',
                                        clarification=twitter_reqs))

            for twitter_reqs in i['Twitter']['LikeRetweet']:
                reqs.append(Requirement(id=str(uuid.uuid4()),
                                        platform='Twitter',
                                        action='LikeRetweet',
                                        clarification=twitter_reqs))

            for discord_reqs in i['Discord']['Join']:
                reqs.append(Requirement(id=str(uuid.uuid4()),
                                        platform='Discord',
                                        action='Join',
                                        clarification=discord_reqs))

            raffle.requirements = reqs



            session.add(raffle)
            session.commit()
            session.close()

        return jsonify(result_data)
    except Exception as e:
        # print(e)
        return jsonify({"error": "No query provided"}), 400

@app.route('/data/alphabot', methods=['POST'])
def alphabot():

    data = request.get_json()['links']

    ids = []
    for i in data:
        try:
            id_ = get_raffle_data_alphabot(i, 'open')
            return jsonify({'raffle_id': id_})

        except:
            return jsonify({"error": "No query provided"}), 400


@app.route('/data/superful', methods=['POST'])
def superful():

    data = request.get_json()['links']

    ids = []
    for i in data:
        try:
            id_ = get_raffle_data_superful(i, 'open')
            return jsonify({'raffle_id': id_})


        except:
            return jsonify({"error": "No query provided"}), 400


@app.route('/data/raffle', methods=['GET'])
def get_raffle_personal():
    raffle_link = request.args.get('raffleLink')
    platform = request.args.get('platform')

    data = 'Nothing'
    if platform == 'Premint':
        data = execute_query([raffle_link])

        i = data[0]

        try:
            a = i['Discord']['Info'][0]
            return jsonify({'msg': 'Skip Raffle'}), 500
        except:
            pass

        id_ = str(uuid.uuid4())
        raffle = Raffle(id=id_,
                        platform='Premint',
                        category='one_time',
                        name=i['RaffleName'],
                        platformLink=i['Link'],
                        timestamp = str(int(time.time()))
                        )

        # print(i['RaffleName'])
        if i['Project_Info']['Total_Supply'] != None:
            raffle.TotalSupply = i['Project_Info']['Total_Supply']
        if i['Project_Info']['Number_of_winners'] != None:
            raffle.NumberOfWinners = i['Project_Info']['Number_of_winners']
        if i['ProfilePictureLink'] != None:
            raffle.profilePicture = i['ProfilePictureLink']
        if i['ProfileBannerLink'] != None:
            raffle.banner = i['ProfileBannerLink']
        if i['Project_Info']['Verified_Twitter'] != None:
            raffle.subscribers = i['Project_Info']['Verified_Twitter'][1]
        if i['Project_Info']['Registration_Closing'] != None:
            raffle.deadline = i['Project_Info']['Registration_Closing']

        reqs = []

        if i['Additional_info'] is not None:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Email',
                                    action='Input',
                                    clarification=''))

        if i['Need_Discord'] != False:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Discord',
                                    action='Connect',
                                    clarification=''))

        for twitter_reqs in i['Twitter']['Follow']:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Twitter',
                                    action='Follow',
                                    clarification=twitter_reqs))

        for twitter_reqs in i['Twitter']['LikeRetweet']:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Twitter',
                                    action='LikeRetweet',
                                    clarification=twitter_reqs))

        for discord_reqs in i['Discord']['Join']:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Discord',
                                    action='Join',
                                    clarification=discord_reqs))

        raffle.requirements = reqs

        Session = sessionmaker(bind=engine)
        session = Session()

        session.add(raffle)

        session.commit()

        raffle = session.query(Raffle).filter(Raffle.id == id_).first()

        if raffle == None:
            return jsonify({'message': 'Invalid Raffle'}), 500

        reqs = []
        for req in raffle.requirements:
            reqs.append({'platform': req.platform,
                         'action': req.action,
                         'clarification': req.clarification})

        data = {'id': raffle.id,
                'platform': raffle.platform,
                'category': raffle.category,
                'profilePicture': raffle.profilePicture,
                'banner': raffle.banner,
                'name': raffle.name,
                'hold': raffle.hold,
                'subscribers': raffle.subscribers,
                'deadline': raffle.deadline,
                'platformLink': raffle.platformLink,
                'captcha': raffle.captcha,
                'requirements': reqs
                }

        session.close()


    elif platform == 'Alphabot':
        # print(raffle_link)
        id = get_raffle_data_alphabot(raffle_link, 'one_time')

        Session = sessionmaker(bind=engine)
        session = Session()

        raffle = session.query(Raffle).filter(Raffle.id == id).first()

        if raffle == None:
            return jsonify({'message': 'Invalid Raffle'}), 500

        reqs = []
        for req in raffle.requirements:
            reqs.append({'platform': req.platform,
                         'action': req.action,
                         'clarification': req.clarification})

        data = {'id': raffle.id,
                'platform': raffle.platform,
                'category': raffle.category,
                'profilePicture': raffle.profilePicture,
                'banner': raffle.banner,
                'name': raffle.name,
                'hold': raffle.hold,
                'subscribers': raffle.subscribers,
                'deadline': raffle.deadline,
                'platformLink': raffle.platformLink,
                'captcha': raffle.captcha,
                'requirements': reqs
                }

        session.close()

    elif platform == 'Superful':
        # print(raffle_link)
        id = get_raffle_data_superful(raffle_link, 'one_time')
        # print(id)

        Session = sessionmaker(bind=engine)
        session = Session()

        raffle = session.query(Raffle).filter(Raffle.id == id).first()

        if raffle == None:
            return jsonify({'message': 'На данный момент заход в этот раффл невозможен'}), 500

        reqs = []
        for req in raffle.requirements:
            reqs.append({'platform': req.platform,
                         'action': req.action,
                         'clarification': req.clarification})

        data = {'id': raffle.id,
                'platform': raffle.platform,
                'category': raffle.category,
                'profilePicture': raffle.profilePicture,
                'banner': raffle.banner,
                'name': raffle.name,
                'hold': raffle.hold,
                'subscribers': raffle.subscribers,
                'deadline': raffle.deadline,
                'platformLink': raffle.platformLink,
                'captcha': raffle.captcha,
                'requirements': reqs
                }

        session.close()

    return jsonify(data)


if __name__ == '__main__':

    def premint_session():

        address = ''
        private_key = ''

        account: LocalAccount = address

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


        def _get_message_to_sign(nonce) -> str:

            return "Welcome to PREMINT!\n\n" \
                   "Signing is the only way we can truly know \n" \
                   "that you are the owner of the wallet you \n" \
                   "are connecting. Signing is a safe, gas-less \n" \
                   "transaction that does not in any way give \n" \
                   "PREMINT permission to perform any \n" \
                   "transactions with your wallet.\n\n" \
                   f"Wallet address:\n{account.lower()}\n\n" \
                   f"Nonce: {nonce}"


        def _get_nonce():
            try:
                with session.get("https://www.premint.xyz/v1/login_api/", timeout=15) as response:
                    if response.ok:
                        nonce = response.json()["data"]
                        return nonce
                    else:
                        # print(f"Unknown status code while getting nonce [{response.status_code}]")
                        # print(response.text)
                        pass
            except Exception as err:
                print('error')
                pass


        session = _make_scraper()
        session.proxies = {'http': 'http://',
                                    'https': 'http://'}
        session.user_agent = random_user_agent()

        adapter = requests.adapters.HTTPAdapter(max_retries=1)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.headers.update(
            {
                "referer": "https://www.premint.xyz/v1/login_api/",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
        )

        with session.get("https://www.premint.xyz/login", timeout=15) as response:

            # print(response.text)
            # print(response.cookies)
            # print(response.headers)
            if response.ok:
                session.headers.update({"x-csrftoken": response.cookies["csrftoken"]})
                # print(response.cookies["csrftoken"])
                # print('ok')
                nonce = _get_nonce()
                print(nonce)
                if nonce:
                    message = encode_defunct(text=_get_message_to_sign(nonce))
                    signed_message = w3.eth.account.sign_message(message, private_key=private_key)
                    print(signed_message)
                    signature = signed_message["signature"].hex()
                    data = f"web3provider=metamask&address={account.lower()}&signature={signature}"

                    with session.post("https://www.premint.xyz/v1/login_api/", data=data,
                                      timeout=15) as response:
                        if response.ok:
                            if response.json()["success"]:
                                print(f"Successfully logged in account!")
                            else:
                                print('error')
                        else:
                            print('error')

        return session


    def alphabot_session():
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

        address = ''
        private_key = ''

        session = _make_scraper()
        session.proxies = {'http': 'http://',
                           'https': 'http://'}
        session.user_agent = UserAgent().chrome

        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        try:
            session.headers.update(
                {'referer': 'https://www.alphabot.app/', "content-type": "application/x-www-form-urlencoded"})
            with session.get('https://www.alphabot.app/', timeout=15) as response:
                if response.ok:
                    nonce = _get_nonce_alphabot(session, address)
                    if nonce:
                        message = encode_defunct(text=_get_message_to_sign_alphabot(nonce))
                        signed_message = w3.eth.account.sign_message(message, private_key=private_key)
                        signature = signed_message["signature"].hex()
                        data = f"web3provider=metamask&address={address.lower()}&signature={signature}"
                        with session.get("https://www.alphabot.app/api/auth/csrf", data=data, timeout=15) as response:
                            csrfToken = response.json()['csrfToken']
                            payload = {'redirect': 'false',
                                       'address': f'{address.lower()}',
                                       'signature': f'{signature}',
                                       'csrfToken': f'{csrfToken}',
                                       'callbackUrl': 'https://www.alphabot.app/',
                                       'json': 'true'}
                            with session.post('https://www.alphabot.app/api/auth/callback/credentials?', data=payload,
                                              timeout=15) as response:
                                with session.get('https://www.alphabot.app/api/session', timeout=15) as response:
                                    session.headers.update({'content-type': 'application/x-www-form-urlencoded'})
                                    with session.get('https://www.alphabot.app/#profile') as response:
                                        with session.get('https://www.alphabot.app/api/session',
                                                         timeout=15) as response:
                                            pass
                                        with session.get('https://www.alphabot.app/api/auth/providers',
                                                         timeout=15) as response:
                                            pass
                                        with session.get('https://www.alphabot.app/api/auth/csrf',
                                                         timeout=15) as response:
                                            pass

                                        data = {'csrfToken': csrfToken,
                                                'callbackUrl': 'https://www.alphabot.app/#profile',
                                                'json': 'true'}

                                        return session
        except Exception as e:
            print(e)

            return False

        return session


    def _get_message_to_sign_alphabot(nonce) -> str:
        return f"Sign this message to either enter a raffle that requires holding a specific NFT, edit your profile, or to gain access to premium functionality with Alphabot. ({nonce})"


    def _get_nonce_alphabot(session, address):
        try:
            with session.get(f"https://www.alphabot.app/api/auth/nonce?address={address.lower()}",
                             timeout=15) as response:
                print(response.text)
                if response.ok:
                    nonce = response.json()['nonce']
                    return nonce
                else:
                    # print(f"Unknown status code while getting nonce [{response.status_code}]")
                    pass
        except Exception as err:
            print('error')
            pass


    def superful_session():

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


        session = _make_scraper()
        session.proxies = {'http': 'http://',
                           'https': 'http://'}
        session.user_agent = UserAgent().chrome

        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        return session

    def freenft_session():

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


        session = _make_scraper()
        session.proxies = {'http': 'http://',
                           'https': 'http://'}
        session.user_agent = random_user_agent()

        adapter = requests.adapters.HTTPAdapter(max_retries=3)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        session.headers.update(
            {
                "referer": "https://www.freenft.xyz/",
                'origin': 'https://www.freenft.xyz'
            }
        )

        return session




    session_alphabot = alphabot_session()
    # get_raffle_data('https://www.alphabot.app/secret-dotlist-2iedgu')

    session_superful = superful_session()
    # get_raffle_data_superful('https://www.superful.xyz/retro-hunters-public-raffle')

    session_freenft = tls_client.Session(

            client_identifier="chrome110",

            random_tls_extension_order=True

        )

    # adapter = requests.adapters.HTTPAdapter(max_retries=3)
    # session_freenft.mount('http://', adapter)
    # session_freenft.mount('https://', adapter)

    session_freenft.proxies ={'http': 'http://',
                           'https': 'http://'}

    try:
        with open("Premint.pkl", "rb") as f:
            session = pickle.load(f)
    except:
        session = premint_session()
        with open('Premint.pkl', 'wb') as file:
            pickle.dump(session, file)

    scheduler = threading.Thread(target=schedule_function)
    scheduler.start()

    Superful_scheduler = threading.Thread(target=SuperfulGetRaffles)
    Superful_scheduler.start()

    Alphabot_scheduler = threading.Thread(target=AlphabotGetRaffles)
    Alphabot_scheduler.start()

    cleaner = threading.Thread(target=database_cleaner)
    cleaner.start()

    from waitress import serve
    serve(app,  port=27000)


