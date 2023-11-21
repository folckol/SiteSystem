# import database
import json
import time
import traceback
import uuid

from sqlalchemy.orm import sessionmaker

from ReadyFiles.premint import Premint
from ReadyFiles.free_nft import FreeNFT
from ReadyFiles.alphabot import AlphaBot
from ReadyFiles.superfull import Superful
from ReadyFiles.twitterRaffleModel import Account
import concurrent.futures
import threading

from Creating_DBs import *


# def create_database():
#     database.create_db()
#
#     directory = '1k'
#     private_keys = get_list(f'{directory}/private_keys.txt')
#     addresses = utils.get_address(private_keys)
#     proxies = get_list(f'{directory}/proxies.txt')
#     # discord_tokens = get_list(f'{directory}/discord_tokens.txt')
#     tw_auth_tokens = get_list(f'{directory}/tw_auth_tokens.txt')
#     tw_csrfs = get_list(f'{directory}/tw_csrfs.txt')
#
#     # Insert accounts data to database       **Create index out of range exception**
#     for i in range(len(private_keys)):
#         proxy_list = proxies[i].split(':')
#         proxy = f'http://{proxy_list[2]}:{proxy_list[3]}@{proxy_list[0]}:{proxy_list[1]}'
#         data = {'address': addresses[i],
#                 'private_key': private_keys[i],
#                 'auth_token': tw_auth_tokens[i],
#                 'csrf': tw_csrfs[i],
#                 'discord_token': 'discord_tokens[i]',
#                 'proxy': proxy}
#         database.add_account(data)
#     # Export accounts to csv file
#     database.export_accounts()


def split_list(lst, n):
    k, m = divmod(len(lst), n)
    return (lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def UpdateDB(res, discord_id, raffle_data, name, address, data, status, id__ = None):

    Session = sessionmaker(bind=engine)
    session = Session()

    next_ = False
    raffles_ = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == discord_id).all()
    for raffle_ in raffles_:
        try:
            if raffle_.raffle[0].platformLink == raffle_data['raffle_url']:
                next_ = True
                break
        except:
            try:
                if raffle_.raffle[0].id == id__:
                    next_ = True
                    break
            except:
                pass

    if next_ == True:
        RAFFLE = raffle_

    else:
        idd = str(uuid.uuid4())
        RAFFLE = AccessedRaffle(id=idd,
                                discordId=discord_id,
                                result='[]')
        try:
            RAFFLE.raffle = [session.query(Raffle).filter(Raffle.platformLink == raffle_data['raffle_url']).first()]
        except:
            RAFFLE.raffle = [session.query(Raffle).filter(Raffle.id == id__).first()]


        session.add(RAFFLE)
        session.commit()

        RAFFLE = session.query(AccessedRaffle).filter(AccessedRaffle.id == idd).first()

    result = json.loads(RAFFLE.result)

    next__ = False
    for i in result:
        if name == i['name']:
            if res == None:
                i['address'] = address
                i['data'] = data
                i['status'] = status


                next__ = True
                break

            else:
                i['address'] = address
                i['result'] = res

                next__ = True
                break

    if next__ == False:

        result.append({'name': name,
                       'address': address,
                       'data': data,
                       'status': status,
                       'result': res})

    RAFFLE.result = json.dumps(result)

    session.commit()
    session.close()



def execute_tasks_twitter(id_, sleeping, id_list, raffle_data, discord_id, id__):



    for data in id_list:

        try:

            time.sleep(sleeping)

            accs_data = {'address': None,
                         'private_key': None,
                         'auth_token': data['TwitterAuthToken'],
                         'csrf': data['TwitterCsrf'],
                         'discord_token': None,

                         'proxy': data['ProxyData']}

            result = Account(accs_data).execute_tasks(raffle_data)

            print(result[-1])

            print(id__)

            try:
                UpdateDB(None, discord_id, raffle_data, data['name'], data['MetaMaskAddress'], result[-1],
                         False if 'fail' in result[-1].lower() or ('success' not in result[-1].lower() and 'submit' not in result[-1].lower()) else True, id__)

                # global_results.append({'name': data['name'],
                #                        'address': data['MetaMaskAddress'],
                #                        'data': result[-1],
                #                        'status': True if 'success' in result[-1].lower() or 'submit' in result[-1].lower() else False})
            except:

                UpdateDB(None, discord_id, raffle_data, data['name'], data['MetaMaskAddress'], result[-1], False, id__)

                # global_results.append({'name': data['name'],
                #                        'address': data['MetaMaskAddress'],
                #                        'data': result[-1],
                #                        'status': False})

            Session = sessionmaker(bind=engine)
            session = Session()


        except:

            traceback.print_exc()

            Session = sessionmaker(bind=engine)
            session = Session()

            UpdateDB(None, discord_id, raffle_data, data['name'], data['MetaMaskAddress'], 'Data entered incorrectly',
                     False, id__)

            # global_results.append({'name': data['name'],
            #                        'address': data['MetaMaskAddress'],
            #                        'data': 'Data entered incorrectly',
            #                        'status': False})

        event = session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.id == id_).first()
        if event.status == 'cancelled':
            session.close()
            break

        event.accessedAccountsNumber = event.accessedAccountsNumber + 1

        if event.accessedAccountsNumber == event.totalAccountsNumber:
            event.status = 'success'

        session.commit()
        session.close()


def execute_tasks(id_ ,sleeping, id_list, raffle_data, cap_key, raffle_type, discord_id):
    time_list = []
    numbers = 0

    for data in id_list:

        try:


            if raffle_data['discord_invite'] != [] and (cap_key == None or cap_key == ''):



                Session = sessionmaker(bind=engine)
                session = Session()

                UpdateDB(None, discord_id, raffle_data, data['name'], data['MetaMaskAddress'], 'Error with Captcha Key', False)
                # global_results.append({'name': data['name'],
                #                        'address': data['MetaMaskAddress'],
                #                        'data': 'Error with Captcha Key',
                #                        'status': False})

                event = session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.id == id_).first()
                if event.status == 'cancelled':
                    session.close()
                    break

                event.accessedAccountsNumber = event.accessedAccountsNumber + 1

                if event.accessedAccountsNumber == event.totalAccountsNumber:
                    event.status = 'success'

                session.commit()
                session.close()

                continue

            time.sleep(sleeping)

            accs_data = {'address': data['MetaMaskAddress'],
                         'private_key': data['MetaMaskPrivateKey'],
                         'auth_token': data['TwitterAuthToken'],
                         'csrf': data['TwitterCsrf'],
                         'discord_token': data['DiscordToken'],

                         'proxy': data['ProxyData']}

            if raffle_type == 'Premint':
                result = Premint(accs_data, raffle_data, cap_key, data['name'], discord_id).execute_task()

                # if result[-1] == 'Premint login failed (5)':
                #     result = PremintTLS(accs_data, raffle_data, cap_key, data['name'], discord_id).execute_task()

            elif raffle_type == 'Alphabot':
                result = AlphaBot(accs_data, raffle_data, cap_key, data['name'], discord_id).execute_tasks()
            elif raffle_type == 'Superful':
                result = Superful(accs_data, raffle_data, cap_key, data['name'], discord_id).execute_tasks()
            elif raffle_type == 'FreeNFT':
                result = FreeNFT(accs_data, raffle_data['raffle_name'], cap_key, data['name']).execute_task()

            print(result[-1])
            try:
                UpdateDB(None, discord_id, raffle_data, data['name'], data['MetaMaskAddress'], result[-1], False if 'fail' in result[-1].lower() or ('success' not in result[-1].lower() and 'submit' not in result[-1].lower()) else True)

                # global_results.append({'name': data['name'],
                #                        'address': data['MetaMaskAddress'],
                #                        'data': result[-1],
                #                        'status': True if 'success' in result[-1].lower() or 'submit' in result[-1].lower() else False})
            except:

                UpdateDB(None, discord_id, raffle_data, data['name'], data['MetaMaskAddress'], result[-1], False)

                # global_results.append({'name': data['name'],
                #                        'address': data['MetaMaskAddress'],
                #                        'data': result[-1],
                #                        'status': False})

            Session = sessionmaker(bind=engine)
            session = Session()


        except:

            Session = sessionmaker(bind=engine)
            session = Session()

            UpdateDB(None, discord_id, raffle_data, data['name'], data['MetaMaskAddress'], 'Data entered incorrectly', False)

            # global_results.append({'name': data['name'],
            #                        'address': data['MetaMaskAddress'],
            #                        'data': 'Data entered incorrectly',
            #                        'status': False})

        event = session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.id == id_).first()
        if event.status == 'cancelled':

            session.close()
            break

        event.accessedAccountsNumber = event.accessedAccountsNumber+1

        if event.accessedAccountsNumber == event.totalAccountsNumber:
            event.status = 'success'

        session.commit()
        session.close()



        # Superfull(accs_data, raffle_data, cap_key, id).execute_tasks()
        # time_list.append(result[0])
        # if result[1]:
        #     numbers += 1

    #
    # print(f'\nNumber of successful registrations: {numbers}')
    # print(f'Average time per acc: {sum(time_list)/len(time_list)}')


def main_Twitter(id__, discord_id, sleeping, acc_list, thread_count, raffle_data, need_time=1200):
    Session = sessionmaker(bind=engine)
    session = Session()

    event = session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.discordId == discord_id).first()
    # print(event.status)

    if event == None:

        id_ = str(uuid.uuid4())

        event = StartRaffleEventResponse(id = id_,
                                         status = 'running',
                                         discordId = discord_id,
                                         accessedAccountsNumber = 0,
                                         totalAccountsNumber = len(acc_list),
                                         currentRaffleName = 'Twitter Raffle',
                                         endTime = need_time+int(time.time()))

        session.add(event)

    else:

        if event.status == 'success':

            id_ = event.id
            event.status = 'running'
            event.accessedAccountsNumber = 0
            event.totalAccountsNumber = len(acc_list)
            event.currentRaffleName = 'Twitter Raffle'
            event.endTime = need_time+int(time.time())



    session.commit()
    session.close()


    spl_list = split_list(acc_list, thread_count)

    threads = []
    for list in spl_list:
        thread = threading.Thread(target=execute_tasks_twitter, args=(id_, sleeping,list, raffle_data, discord_id, id__))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()




def main(discord_id, sleeping, acc_list, thread_count, raffle_data, raffle_type, cap_key=None, need_time=1200):
    Session = sessionmaker(bind=engine)
    session = Session()

    event = session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.discordId == discord_id).first()
    # print(event.status)

    if event == None:

        id_ = str(uuid.uuid4())

        event = StartRaffleEventResponse(id = id_,
                                         status = 'running',
                                         discordId = discord_id,
                                         accessedAccountsNumber = 0,
                                         totalAccountsNumber = len(acc_list),
                                         currentRaffleName = raffle_data['raffle_name'],
                                         endTime = need_time+int(time.time()))

        session.add(event)

    else:

        if event.status == 'success':

            id_ = event.id
            event.status = 'running'
            event.accessedAccountsNumber = 0
            event.totalAccountsNumber = len(acc_list)
            event.currentRaffleName = raffle_data['raffle_name']
            event.endTime = need_time+int(time.time())



    session.commit()
    session.close()


    spl_list = split_list(acc_list, thread_count)

    threads = []
    for list in spl_list:
        thread = threading.Thread(target=execute_tasks, args=(id_, sleeping,list, raffle_data, cap_key, raffle_type, discord_id))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    Session = sessionmaker(bind=engine)
    session = Session()

    next_ = False
    raffles_ = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == discord_id).all()
    for raffle_ in raffles_:
        try:
            if raffle_.raffle[0].platformLink == raffle_data['raffle_url']:
                break
        except:
            pass

    global_results = json.loads(raffle_.result)

    user = session.query(User).filter(User.discord_id == discord_id).first()
    accounts = user.accounts

    for i in global_results:
        for ii in accounts:
            if ii.name == str(i['name']):

                try:

                    if 'twitter' in i['data'].lower():
                        ii.TwitterStatus = 'BAN'
                        session.commit()

                    elif 'discord' in i['data'].lower():
                        ii.DiscordStatus = 'BAN'
                        session.commit()

                    elif 'Premint login' in i['data'].lower():
                        ii.ProxyStatus = 'BAN'
                        session.commit()

                except:

                    pass
    session.close()

def main_checker(discord_id, sleeping, acc_list, thread_count, raffle_data, raffle_type, cap_key=None):


    spl_list = split_list(acc_list, thread_count)

    threads = []
    for list in spl_list:
        thread = threading.Thread(target=execute_tasks_checker, args=(sleeping, list, raffle_data, cap_key, raffle_type, discord_id))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    Session = sessionmaker(bind=engine)
    session = Session()

    next_ = False
    raffles_ = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == discord_id).all()
    for raffle_ in raffles_:
        try:
            if raffle_.raffle[0].platformLink == raffle_data['raffle_url']:
                break
        except:
            pass

    global_results = json.loads(raffle_.result)

    user = session.query(User).filter(User.discord_id == discord_id).first()
    accounts = user.accounts

    for i in global_results:
        for ii in accounts:
            if ii.name == str(i['name']):

                try:

                    if 'twitter' in i['data'].lower():
                        ii.TwitterStatus = 'BAN'
                        session.commit()

                    elif 'discord' in i['data'].lower():
                        ii.DiscordStatus = 'BAN'
                        session.commit()

                    elif 'Premint login' in i['data'].lower():
                        ii.ProxyStatus = 'BAN'
                        session.commit()

                except:

                    pass
    session.close()

def execute_tasks_checker(sleeping, id_list, raffle_data, cap_key, raffle_type, discord_id):

    for data in id_list:

        try:

            time.sleep(sleeping)

            accs_data = {'address': data['MetaMaskAddress'],
                         'private_key': data['MetaMaskPrivateKey'],
                         'auth_token': data['TwitterAuthToken'],
                         'csrf': data['TwitterCsrf'],
                         'discord_token': data['DiscordToken'],

                         'proxy': data['ProxyData']}

            if raffle_type == 'Premint':
                result = Premint(accs_data, raffle_data, [cap_key], data['name'], discord_id).execute_task_check_result()

                # if result[-1] == 'Premint login failed (5)':
                #     result = PremintTLS(accs_data, raffle_data, cap_key, data['name'], discord_id).execute_task()

            elif raffle_type == 'Alphabot':
                print(accs_data)
                result = AlphaBot(accs_data, raffle_data, [cap_key], data['name'], discord_id).CheckWinners()
            elif raffle_type == 'Superful':
                result = Superful(accs_data, raffle_data, [cap_key], data['name'], discord_id).execute_tasks_check_winners()


            print(result[-1])

            try:
                UpdateDB(result[-1], discord_id, raffle_data, data['name'], data['MetaMaskAddress'], result[-1],
                         False if 'fail' in result[-1].lower() or ('success' not in result[-1].lower() and 'submit' not in result[-1].lower()) else True)

                # global_results.append({'name': data['name'],
                #                        'address': data['MetaMaskAddress'],
                #                        'data': result[-1],
                #                        'status': True if 'success' in result[-1].lower() or 'submit' in result[-1].lower() else False})
            except:

                UpdateDB(result[-1], discord_id, raffle_data, data['name'], data['MetaMaskAddress'], result[-1], False)


        except:
            traceback.print_exc()

