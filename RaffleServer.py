import sqlite3
import threading
import time
import traceback
import uuid

from flask import Flask, jsonify, request
from sqlalchemy.orm import sessionmaker
from waitress import serve

from Creating_DBs import *
from Rescue_Site_System.main import main, main_Twitter, main_checker

app = Flask(__name__)

def start_raffle(user_id, id, first_account, last_account, exceptions, need_time):

    if type(id) == str:


        Session = sessionmaker(bind=engine)
        session = Session()

        raffle = session.query(Raffle).filter(Raffle.id == id).first()

        platform = raffle.platform
        captcha_status = raffle.captcha

        user = session.query(User).filter(User.discord_id == user_id).first()

        discord_id = user.discord_id

        raffle_data = {'raffle_url': raffle.platformLink,
                       'raffle_name': raffle.name,
                       'tweet_id': [],
                       'user_id': [],
                       'discord_status': False,
                       'discord_invite': []}

        for requirement in raffle.requirements:

            # print(requirement.platform, requirement.action)

            if requirement.platform == 'Twitter':
                if requirement.action == 'Follow':
                    raffle_data['user_id'].append(requirement.clarification.split('|')[-1])
                elif requirement.action == 'LikeRetweet':
                    raffle_data['tweet_id'].append(requirement.clarification)
            elif requirement.platform == 'Discord':
                if requirement.action == 'Connect':
                    raffle_data['discord_status'] = True
                elif requirement.action == 'Join':
                    raffle_data['discord_invite'].append(requirement.clarification.split('/')[-1])

        ready_accounts = []
        for account in user.accounts:
            if int(account.name) < int(first_account) or int(account.name) > int(last_account) or account.name in exceptions:
                continue
            else:
                ready_accounts.append({'name': account.name,
                                       'TwitterStatus': account.TwitterStatus,
                                       'TwitterAuthToken': account.TwitterAuthToken,
                                       'TwitterCsrf': account.TwitterCsrf,
                                       'DiscordStatus': account.DiscordStatus,
                                       'DiscordToken': account.DiscordToken,
                                       'MetaMaskAddress': account.MetaMaskAddress,
                                       'MetaMaskPrivateKey': account.MetaMaskPrivateKey,
                                       'Email': account.Email,
                                       'ProxyType': account.ProxyType,
                                       'ProxyData': account.ProxyData
                                       })

        CaptchaKey = session.query(User.CaptchaKey).filter(User.discord_id == discord_id).first()

        # if CaptchaKey == None or CaptchaKey == '':
        #     return 'Вы не ввели api ключ от capmonster'
        # for i in ready_accounts:
        #     if '0x' not in i['MetaMaskPrivateKey'] or len(i['MetaMaskPrivateKey']) != 66:
        #         return 'В одном из ваших аккаунтов неверно введен приватный ключ от кошелька'

        session.close()

        # need_time = 600
        if platform == 'Premint':

            if raffle_data['discord_invite'] == []:
                timing = 30
            else:
                timing = 50


            threading_calculator = (len(ready_accounts)//(need_time//timing))+1
            sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

            main(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'Premint', CaptchaKey, need_time)

        elif platform == 'Alphabot':

            if raffle_data['discord_invite'] == []:
                timing = 40
            else:
                timing = 110
            threading_calculator = (len(ready_accounts) // (need_time // timing)) + 1
            sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

            main(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'Alphabot', CaptchaKey, need_time)

        elif platform == 'Superful':

            if captcha_status != None and captcha_status != 'False':
                raffle_data['captcha_required'] = True
                if raffle_data['discord_invite'] == []:
                    timing = 23
                else:
                    timing = 50
                threading_calculator = (len(ready_accounts) // (need_time // timing)) + 1
                sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

                main(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'Superful', CaptchaKey, need_time)
            else:
                raffle_data['captcha_required'] = False
                if raffle_data['discord_invite'] == []:
                    timing = 50
                else:
                    timing = 120
                threading_calculator = (len(ready_accounts) // (need_time // timing)) + 1
                sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

                main(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'Superful', CaptchaKey, need_time)

        elif platform == 'FreeNFT':

            timing = 20
            threading_calculator = (len(ready_accounts) // (need_time // timing)) + 1
            sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

            main(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'FreeNFT', CaptchaKey, need_time)
    else:



        RaffleInfo = id

        id__ = str(uuid.uuid4())
        try:
            raffle = Raffle(id = id__,
                            platform = 'Twitter',
                            category = 'one_time',
                            platformLink = RaffleInfo['Link'],
                            timestamp = str(int(time.time())),
                            name = f'Twitter Raffle ({RaffleInfo["Link"].split("/")[3]})'
                            )
        except:
            raffle = Raffle(id=id__,
                            platform='Twitter',
                            category='one_time',
                            platformLink=RaffleInfo['Link'],
                            timestamp=str(int(time.time())),
                            name=f'Twitter Raffle'
                            )

        reqs = []
        if RaffleInfo['LikeStatus']:
            reqs.append(Requirement(id = str(uuid.uuid4()),
                                    platform = 'Twitter',
                                    action = 'Like',
                                    clarification = 'True',
                            ))

        if RaffleInfo['RetweetStatus']:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Twitter',
                                    action='Retweet',
                                    clarification='True',
                                    ))

        for i in RaffleInfo['FollowIds']:
            reqs.append(Requirement(id=str(uuid.uuid4()),
                                    platform='Twitter',
                                    action='Follow',
                                    clarification=i,
                                    ))

        if RaffleInfo['CommentStatus']:

            tweetText = ''
            CommentData = RaffleInfo['CommentData']

            if CommentData['Sentences'] == None:
                CommentData['Sentences'] = []

            if len(CommentData['Sentences']) != 0:
                reqs.append(Requirement(id=str(uuid.uuid4()),
                                        platform='Twitter',
                                        action='Sentences',
                                        clarification='True',
                                        ))

            if CommentData['MaxTags'] != 0:
                maxTags = CommentData['MaxTags']
                minTags = CommentData['MinTags']

                if minTags == maxTags:
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='Tags',
                                            clarification=f'{minTags}',
                                            ))
                else:
                    reqs.append(Requirement(id=str(uuid.uuid4()),
                                            platform='Twitter',
                                            action='Tags',
                                            clarification=f'{minTags}-{maxTags}',
                                            ))
        raffle.requirements = reqs


        Session = sessionmaker(bind=engine)
        session = Session()

        session.add(raffle)

        user = session.query(User).filter(User.discord_id == user_id).first()

        ready_accounts = []
        for account in user.accounts:
            if int(account.name) < int(first_account) or int(account.name) > int(
                    last_account) or account.name in exceptions:
                continue
            else:
                ready_accounts.append({'name': account.name,
                                       'TwitterStatus': account.TwitterStatus,
                                       'TwitterAuthToken': account.TwitterAuthToken,
                                       'TwitterCsrf': account.TwitterCsrf,
                                       'DiscordStatus': account.DiscordStatus,
                                       'DiscordToken': account.DiscordToken,
                                       'MetaMaskAddress': account.MetaMaskAddress,
                                       'MetaMaskPrivateKey': account.MetaMaskPrivateKey,
                                       'Email': account.Email,
                                       'ProxyType': account.ProxyType,
                                       'ProxyData': account.ProxyData
                                       })

        timing = 20
        threading_calculator = (len(ready_accounts) // (need_time // timing)) + 1
        sleeping = need_time / (len(ready_accounts) // threading_calculator + 1) - timing

        discord_id = user.discord_id

        session.commit()
        session.close()

        main_Twitter(id__, discord_id, sleeping, ready_accounts, threading_calculator, RaffleInfo, need_time)

def check_raffle(user_id, id, first_account, last_account, exceptions, need_time):

    Session = sessionmaker(bind=engine)
    session = Session()

    raffle = session.query(Raffle).filter(Raffle.id == id).first()

    platform = raffle.platform
    # captcha_status = raffle.captcha

    user = session.query(User).filter(User.discord_id == user_id).first()

    discord_id = user.discord_id

    raffle_data = {'raffle_url': raffle.platformLink,
                   'raffle_name': raffle.name,
                   'tweet_id': [],
                   'user_id': [],
                   'discord_status': False,
                   'discord_invite': []}


    ready_accounts = []
    for account in user.accounts:
        if int(account.name) < int(first_account) or int(account.name) > int(last_account) or account.name in exceptions:
            continue
        else:
            ready_accounts.append({'name': account.name,
                                   'TwitterStatus': account.TwitterStatus,
                                   'TwitterAuthToken': account.TwitterAuthToken,
                                   'TwitterCsrf': account.TwitterCsrf,
                                   'DiscordStatus': account.DiscordStatus,
                                   'DiscordToken': account.DiscordToken,
                                   'MetaMaskAddress': account.MetaMaskAddress,
                                   'MetaMaskPrivateKey': account.MetaMaskPrivateKey,
                                   'Email': account.Email,
                                   'ProxyType': account.ProxyType,
                                   'ProxyData': account.ProxyData
                                   })

    session.close()

    # need_time = 600
    if platform == 'Premint':


        timing = 30

        threading_calculator = (len(ready_accounts)//(need_time//timing))+1
        sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

        main_checker(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'Premint', None)

    elif platform == 'Alphabot':

        timing = 15
        threading_calculator = (len(ready_accounts) // (need_time // timing)) + 1
        sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

        print(f'Check {discord_id} results')
        print(sleeping)
        main_checker(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'Alphabot', None)

    elif platform == 'Superful':


        raffle_data['captcha_required'] = True

        timing = 23

        threading_calculator = (len(ready_accounts) // (need_time // timing)) + 1
        sleeping = need_time/(len(ready_accounts)//threading_calculator+1)-timing

        main_checker(discord_id, sleeping, ready_accounts, threading_calculator, raffle_data, 'Superful', None)



@app.route('/RaffleChecker', methods=['POST'])
def RaffleChecker():
    try:
        data = request.get_json()

        user_id = data['discordId']
        id = data['raffleId']
        first_account = data['firstAcc']
        last_account = data['lastAcc']
        exceptions = data['exceptions']
        need_time = data['time']

        # Session = sessionmaker(bind=engine)
        # session = Session()
        #
        # raffle = session.query(Raffle).filter(Raffle.id == id).first()
        #
        # raffle_data = {'raffle_url': raffle.platformLink,
        #                'raffle_name': raffle.name}
        #
        # session.close()


        t = threading.Thread(target=check_raffle, args=(user_id, id, first_account, last_account, exceptions, need_time))
        t.start()

        return jsonify({'status': True})


    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'status': False})


@app.route('/start', methods=['POST'])
def get_raffle_by_link():
    try:
        data = request.get_json()

        user_id = data['discordId']
        id = data['raffleId']
        first_account = data['firstAcc']
        last_account = data['lastAcc']
        exceptions = data['exceptions']
        need_time = data['time']

        RaffleInfo = None
        try:
            RaffleInfo = data['RaffleInfo']
        except:
            pass

        if RaffleInfo:

            t = threading.Thread(target=start_raffle,
                                 args=(user_id, RaffleInfo, first_account, last_account, exceptions, need_time))
            t.start()

            return jsonify({'status': True})

        else:

            Session = sessionmaker(bind=engine)
            session = Session()

            raffle = session.query(Raffle).filter(Raffle.id == id).first()

            raffle_data = {'raffle_url': raffle.platformLink,
                           'raffle_name': raffle.name,
                           'tweet_id': [],
                           'user_id': [],
                           'discord_status': False,
                           'discord_invite': []}
            for requirement in raffle.requirements:
                if requirement.action == 'Join':
                    raffle_data['discord_invite'].append(requirement.clarification.split('/')[-1])



            session.close()

            if raffle_data['discord_invite'] == []:

                t = threading.Thread(target=start_raffle, args=(user_id, id, first_account, last_account, exceptions, need_time))
                t.start()

                return jsonify({'status': True})

            else:
                user = session.query(User).filter(User.discord_id == user_id).first()
                if user.CaptchaKey == None or user.CaptchaKey == '':
                    return jsonify({'status': False})
                else:
                    t = threading.Thread(target=start_raffle,
                                         args=(user_id, id, first_account, last_account, exceptions, need_time))
                    t.start()

                    return jsonify({'status': True})


    except Exception as e:
        print(e)
        traceback.print_exc()
        return jsonify({'status': False})




if __name__ == '__main__':
    # conn = sqlite3.connect('raffles.db')
    # c = conn.cursor()
    #
    # # добавляем новый столбец с именем 'новый_столбец' и типом данных 'INTEGER'
    # c.execute('ALTER TABLE StartRaffleEventResponse ADD COLUMN endTime INTEGER')
    #
    # # сохраняем изменения и закрываем соединение
    # conn.commit()
    # conn.close()


    serve(app, port=27500)



