import datetime
import json
import logging
import random
import threading
import time
import traceback
import uuid
import warnings

import pytz
import requests
import wsgiserver
from colorama import init, Fore
from flask import Flask, jsonify, request, Response, send_from_directory
from flask_cors import CORS
from sqlalchemy.orm import sessionmaker
from Creating_DBs import *
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table, Boolean, DateTime, and_, func, cast, \
    Float, or_
from PaymentMachine import *


def split_list(lst, size):

    return [lst[i:i+size] for i in range(0, len(lst), size)]



app = Flask(__name__)
CORS(app)

init(autoreset=True)

formatter = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)


class User1(Base):
    __tablename__ = 'Session'

    id = Column(String, primary_key=True)
    userId = Column(String)
    sessionToken = Column(String)




class Account1(Base):
    __tablename__ = 'Account'

    id = Column(String, primary_key=True)
    providerAccountId = Column(String)

    User = relationship('User2', backref='account')
    userId = Column(String, ForeignKey('User.id'))


class Refr(Base):
    __tablename__ = 'RaffleBotSubscription'

    id = Column(String, primary_key=True)
    rafflesLeft = Column(Integer)
    rafflesPerDay = Column(Integer)
    expires = Column(DateTime)

    User = relationship('User2', backref='raffle_bot_subscription')
    userId = Column(String, ForeignKey('User.id'))


class CommunitySubscription(Base):
    __tablename__ = 'CommunitySubscription'

    id = Column(String, primary_key=True)
    expires = Column(DateTime)

    User = relationship('User2', backref='community_subscription')
    userId = Column(String, ForeignKey('User.id'))


# class RaffleBotSubscription(Base):
#     id = Column(String, primary_key=True)
#     expires = Column(DateTime)
#     rafflesLeft = Column(Integer)
#     rafflesPerDay = Column(Integer)
#     maxNumAccounts = Column(Integer)
#     user           User     @relation(fields: [userId], references: [id], onDelete: Cascade)
#     userId = Column(String)
# }

def RefreshDay():

    engine1 = create_engine(
        '')
    SessionA = sessionmaker(bind=engine1)
    sessionA = SessionA()

    users = sessionA.query(Refr).all()

    for user in users:
        user.rafflesLeft = user.rafflesPerDay

    sessionA.commit()
    sessionA.close()


def CheckUser(userId, sessionToken):
    # print(userId, sessionToken)

    engine1 = create_engine(
        '')
    SessionA = sessionmaker(bind=engine1)
    sessionA = SessionA()

    # print(userId, sessionToken)
    status_ = sessionA.query(User1.sessionToken).filter(User1.userId == str(userId)).all()

    raffleBotStatus = sessionA.query(User2.raffleBotUser).filter(User2.id == str(userId)).first()
    # print(str(raffleBotStatus)[1:-2].lower())

    status = None
    # print(status_)
    for i in status_:

        # print(i[0])

        if sessionToken == i[0]:
            status = True
            break


    if status != None and status == True:

            if str(raffleBotStatus)[1:-2].lower() == 'true':
                sessionA.close()
                return [True, True]
            else:
                sessionA.close()
                return [True, False]
    else:

        sessionA.close()
        return [False, False]


def event_stream(DiscordId):

    while True:

        Session = sessionmaker(bind=engine)
        session = Session()

        event = session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.discordId == DiscordId).first()

        if event == None:
            data = {'status': 'inactive',
                    'accessedAccountsNumber': None,
                    'totalAccountsNumber': None,
                    'currentRaffleName': None,
                    'endTime': None}

            break

        time.sleep(1)

        try:
            data = {'status': event.status,
                    'accessedAccountsNumber': event.accessedAccountsNumber,
                    'totalAccountsNumber': event.totalAccountsNumber,
                    'currentRaffleName': event.currentRaffleName,
                    'endTime': (event.endTime - int(time.time()))//60}

            # print(data)

            if event.status == 'success' or event.status == 'cancelled':
                session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.discordId == DiscordId).delete()
                session.commit()
                break
            try:
                yield f'data: {json.dumps(data)}\n\n'
            except:
                time.sleep(5)
                yield f'data: {json.dumps(data)}\n\n'

        except KeyError:
            pass

        except:

            traceback.print_exc()

            session.close()
            return f'data: Error\n\n'


    yield f'data: {json.dumps(data)}\n\n'


@app.route('/events', methods=['GET'])
def events():

    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')



    userId = request.args.get('userId')
    sessionToken = request.args.get('sessionToken')

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:
            # print(e)
            # time.sleep(random.randint(100, 150) / 100)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    owner_id = request.args.get('discordId')

    return Response(event_stream(owner_id), content_type='text/event-stream')

# @app.route('/deleteEvent', methods=['POST'])
# def create_account():

# добавление ячеек для пользователя, в соответствии с запрошенным количеством
@app.route('/create_db/<string:count>', methods=['POST'])
def create_account(count):
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    discordId = request.json()['discordId']

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id==discordId).first()
    if user == None:

        user = User(id=str(uuid.uuid4()),
                    discord_id=discordId,
                    userId="")
        accounts = []
        for i in range(count):

            acc=Accounts(id=str(uuid.uuid4()),
                         name=i)
            accounts.append(acc)

        user.accounts = accounts

        session.add(user)
        session.commit()
    session.close()


    return jsonify({'message': 'Database created successfully'}), 200

# увеличение количества ячеек в соответствии с запрошенным количеством
@app.route('/db_increase', methods=['POST'])
def db_increase():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    # userId = request.args.get('userId')
    # sessionToken = request.args.get('sessionToken')
    #
    # try:
    #     if CheckUser(userId, sessionToken):
    #         pass
    #     else:
    #         return jsonify({'message': 'Пользователь не найден'}), 500
    # except:
    #     return jsonify({'message': 'Error 0'}), 500

    count = request.get_json()['count']
    user_id = request.get_json()['discord_id']

    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter(User.discord_id == user_id).first()

    max_num = 0
    for account in user.accounts:
        if int(account.name) > max_num:
            max_num = int(account.name)

    for i in range(max_num+1, max_num+1+count):
        acc = Accounts(id=str(uuid.uuid4()),
                       name=i)
        user.accounts.append(acc)

    session.commit()
    session.close()


    return jsonify({'message': 'Database updated successfully'}), 201

# добавление нового аккаунта
@app.route('/accounts', methods=['POST'])
def create_accounts():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]


    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)

            # print(status)

            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:
            # time.sleep(random.randint(100, 150) / 100)
            print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    data = request.get_json()
    # print(data)

    discord_id = data['discordId']
    type = data['type']
    accounts = data['accounts']

    Session = sessionmaker(bind=engine)
    session = Session()

    # print(discord_id)

    try:
        user = session.query(User).filter(User.discord_id == discord_id).first()
        discord_id = user.discord_id
        if user.userId == '':
            user.userId = userId
            session.commit()

        user = session.query(User).filter(User.discord_id == discord_id and User.userId == userId).first()
    except:
        return jsonify({'message': f'This user does not exist'}), 500

    try:
        count = 0
        if type == 'proxy':
            last_name = ''
            for acc in user.accounts:
                if acc.ProxyData == '' or acc.ProxyData == None:
                    try:
                        last_name = acc.name
                        acc.ProxyStatus = 'ACTIVE'
                        acc.ProxyType = data['proxyType']
                        acc.ProxyData = f"{data['proxyType']}://{accounts[count].rstrip().split(':')[2]}:{accounts[count].rstrip().split(':')[3]}@{accounts[count].rstrip().split(':')[0]}:{accounts[count].rstrip().split(':')[1]}"
                        count+=1
                    except IndexError:
                        session.commit()
                        return jsonify({'message': f'Proxy added: {count} | The number of the last account added: {last_name}'}), 200

        elif type == 'metamask':

            last_name = ''
            for acc in user.accounts:
                if acc.MetaMaskAddress == '' or acc.MetaMaskAddress == None:
                    try:
                        last_name = acc.name

                        mmData = accounts[count].split(':')

                        # acc.MetaMaskStatus = 'ACTIVE'
                        acc.MetaMaskAddress = mmData[0].rstrip()
                        acc.MetaMaskPrivateKey = mmData[1].rstrip()
                        count+=1
                    except IndexError:
                        session.commit()
                        return jsonify({'message': f'Metamask added: {count} | The number of the last account added: {last_name}'}), 200


        elif type == 'discord':

            last_name = ''
            for acc in user.accounts:
                if acc.DiscordStatus == '' or acc.DiscordStatus == None:
                    try:
                        last_name = acc.name
                        acc.DiscordStatus = 'ACTIVE'
                        acc.DiscordToken = accounts[count].rstrip()
                        count+=1
                    except IndexError:
                        session.commit()
                        return jsonify({'message': f'Discord added: {count} | The number of the last account added: {last_name}'}), 200


        elif type == 'twitter':

            last_name = ''
            for acc in user.accounts:
                if acc.TwitterAuthToken == '' or acc.TwitterAuthToken == None:
                    try:

                        last_name = acc.name
                        acc.TwitterStatus = 'ACTIVE'
                        # print(accounts[count])
                        twData = accounts[count].rstrip()

                        acc.TwitterAuthToken = twData.split('auth_token=')[-1].split(';')[0]
                        acc.TwitterCsrf = twData.split('ct0=')[-1].split(';')[0]
                        count += 1
                    except IndexError:
                        session.commit()
                        return jsonify(
                            {'message': f'Twitter added: {count} | The number of the last account added: {last_name}'}), 200

        elif type == 'email':

            last_name = ''
            for acc in user.accounts:
                if acc.Email == '' or acc.Email == None:
                    try:
                        last_name = acc.name
                        acc.Email = accounts[count].rstrip().split(':')[0]
                        count += 1
                    except IndexError:
                        session.commit()
                        return jsonify(
                            {'message': f'Email added: {count} | The number of the last account added: {last_name}'}), 200


        elif type == 'CaptchaKey':

            user.CaptchaKey = accounts

        session.commit()

        return jsonify({'message': 'Аккаунты были успешно добавлены'}), 200

    except KeyError:
        pass

    except:

        traceback.print_exc()

        return jsonify({'message': 'Пользователь не найден'}), 500



@app.route('/replaceBannedAccounts', methods=['POST'])
def replaceBannedAccounts():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)

            # print(status)

            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:
            # time.sleep(random.randint(100, 150) / 100)
            print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    data = request.get_json()
    # print(data)

    discord_id = data['discordId']
    type = data['type']
    accounts = data['accounts']

    Session = sessionmaker(bind=engine)
    session = Session()

    # print(discord_id)

    try:
        user = session.query(User).filter(User.discord_id == discord_id).first()
        discord_id = user.discord_id
        if user.userId == '':
            user.userId = userId
            session.commit()

        user = session.query(User).filter(User.discord_id == discord_id and User.userId == userId).first()
    except:
        return jsonify({'message': f'This user does not exist'}), 500

    try:
        count = 0
        if type == 'proxy':
            last_name = ''
            for acc in user.accounts:
                if acc.ProxyStatus == 'BAN':
                    try:
                        acc.ProxyStatus = 'ACTIVE'
                        acc.ProxyType = data['proxyType']
                        acc.ProxyData = f"{data['proxyType']}://{accounts[count].rstrip().split(':')[2]}:{accounts[count].rstrip().split(':')[3]}@{accounts[count].rstrip().split(':')[0]}:{accounts[count].rstrip().split(':')[1]}"
                        count += 1
                    except IndexError:
                        session.commit()
                        return jsonify({'message': f'success'}), 200

        elif type == 'discord':

            last_name = ''
            for acc in user.accounts:
                if acc.DiscordStatus == 'BAN':
                    try:
                        acc.DiscordStatus = 'ACTIVE'
                        acc.DiscordToken = accounts[count].rstrip()
                        count += 1
                    except IndexError:
                        session.commit()
                        return jsonify({'message': f'success'}), 200


        elif type == 'twitter':

            last_name = ''
            for acc in user.accounts:
                if acc.TwitterStatus == 'BAN':
                    try:
                        acc.TwitterStatus = 'ACTIVE'
                        # print(accounts[count])
                        twData = accounts[count].rstrip()

                        acc.TwitterAuthToken = twData.split('auth_token=')[-1].split(';')[0]
                        acc.TwitterCsrf = twData.split('ct0=')[-1].split(';')[0]
                        count += 1
                    except IndexError:
                        session.commit()
                        return jsonify({'message': f'success'}), 200


        session.commit()

        return jsonify({'message': 'success'}), 200

    except KeyError:
        pass

    except:

        traceback.print_exc()

        return jsonify({'message': 'Пользователь не найден'}), 500


# получение списка аккаунтов для владельца
@app.route('/get_all_accounts', methods=['GET'])
def get_accounts_():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    userId = request.args.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500



        except Exception as e:

            # traceback.print_exc()
            time.sleep(random.randint(100,150)/100)

            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    owner_id = request.args.get('discordId')

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == owner_id and User.userId == userId).first()

    data = []
    try:
        for account in user.accounts:
            # print(account.Email)

            if account.TwitterStatus == None and account.TwitterAuthToken == None and account.TwitterCsrf == None and account.DiscordStatus == None and account.DiscordToken == None and account.MetaMaskAddress == None and account.MetaMaskPrivateKey == None and account.Email == None and account.ProxyStatus == None and account.ProxyType == None and  account.ProxyData == None:
                continue

            data.append({'name': account.name,
                         'TwitterStatus': account.TwitterStatus,
                         'TwitterAuthToken': account.TwitterAuthToken,
                         'TwitterCsrf': account.TwitterCsrf,
                         'DiscordStatus': account.DiscordStatus,
                         'DiscordToken': account.DiscordToken,
                         # 'MetaMaskStatus': account.MetaMaskStatus,
                         'MetaMaskAddress': account.MetaMaskAddress,
                         'MetaMaskPrivateKey': account.MetaMaskPrivateKey,
                         'Email': account.Email,
                         'ProxyStatus': account.ProxyStatus,
                         'ProxyType': account.ProxyType,
                         'ProxyData': account.ProxyData})

        session.close()


        return jsonify(data)

    except:

        session.close()

        return jsonify({'message': 'This user does not exist'}), 500

# @app.route('/get_accessed_raffle', methods=['GET'])
# def get_accessed_raffle():
#     userId = request.args.get('userId')
#     sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]
#
#     er = 0
#     while er < 5:
#         try:
#             status = CheckUser(userId, sessionToken)
#             if status[0] and status[1]:
#                 # print(er)
#                 break
#             elif not status[0]:
#                 return jsonify({'message': 'Пользователь не найден'}), 500
#             elif status[0] and not status[1]:
#                 return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500
#
#         except Exception as e:
#
#             # time.sleep(random.randint(100, 150) / 100)
#
#             # print(e)
#             pass
#         er += 1
#
#     else:
#         return jsonify({'message': 'Error 0'}), 500
#
#     owner_id = request.args.get('discordId')
#
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     accessedRaffles = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == owner_id).all()
#     raffle_ = accessedRaffles[-1]
#
#     data = []
#
#     raffle = raffle_.raffle[0]
#
#     # print(raffle.id)
#
#     reqs = []
#     for req in raffle.requirements:
#         reqs.append({'platform': req.platform,
#                      'action': req.action,
#                      'clarification': req.clarification})
#
#     data.append({'id': raffle.id,
#                  'platform': raffle.platform,
#                  'category': raffle.category,
#                  'profilePicture': raffle.profilePicture,
#                  'banner': raffle.banner,
#                  'name': raffle.name,
#                  'TotalSupply': raffle.TotalSupply,
#                  'NumberOfWinners': raffle.NumberOfWinners,
#                  'hold': float(raffle.hold) if raffle.hold != None else 0,
#                  'subscribers': int(raffle.subscribers.replace(',', '')),
#                  'deadline': raffle.deadline,
#                  'platformLink': raffle.platformLink,
#                  'captcha': raffle.captcha,
#                  'requirements': reqs,
#
#                  'result': raffle_.result,
#
#                  })
#
#     session.close()
#
#     return jsonify(data)



# получение списка розыгрышей для владельца
# @app.route('/userraffles', methods=['GET'])
# def get_user_raffles():
#     userId = request.args.get('userId')
#     sessionToken = request.headers.get('sessionToken').split('Bearer
#[-1
#     er = 0
#     while er < 5:
#         try:
#             status = CheckUser(userId, sessionToken)
#             if status[0] and status[1]:
#                 # print(er)
#                 break
#             elif not status[0]:
#                 return jsonify({'message': 'Пользователь не найден'}), 500
#             elif status[0] and not status[1]:
#                 return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500
#
#         except Exception as e:
#
#             # time.sleep(random.randint(100, 150) / 100)
#
#             # print(e)
#             pass
#         er += 1
#
#     else:
#         return jsonify({'message': 'Error 0'}), 500
#
#     owner_id = request.args.get('discordId')
#
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     user = session.query(User).filter(User.discord_id == owner_id and User.userId == userId).first()
#
#
#     try:
#
#         data = []
#         for raffle in user.my_raffles:
#
#             reqs = []
#             for req in raffle.requirements:
#                 reqs.append({'platform': req.platform,
#                              'action': req.action,
#                              'clarification': req.clarification})
#
#             data.append({'platform': raffle.platform,
#                          'category': raffle.category,
#                          'profilePicture': raffle.profilePicture,
#                          'banner': raffle.banner,
#                          'name': raffle.name,
#                          'hold': float(raffle.hold) if raffle.hold != None else 0,
#                          'TotalSupply': raffle.TotalSupply,
#                          'NumberOfWinners': raffle.NumberOfWinners,
#                          'subscribers': int(raffle.subscribers.replace(',', '')),
#                          'deadline': raffle.deadline,
#                          'platformLink': raffle.platformLink,
#                          'captcha': raffle.captcha,
#                          'requirements': reqs
#                          })
#
#         session.close()
#
#         return jsonify(data)
#
#     except:
#
#         return jsonify({'message': 'This user does not exist'}), 500

def Sorting(sort, session, text, page, platform):

    if text:
        try:
            if 'subscribers' in sort and 'noHold' in sort:
                raffles = session.query(Raffle)\
                    .filter(and_(func.lower(Raffle.name).like(f'%{text}%')),
                           and_(Raffle.platform == platform),
                           and_(Raffle.category != 'one_time'),
                           and_(or_(Raffle.hold == 0, Raffle.hold == None)))\
                    .order_by(cast(Raffle.subscribers, Integer).desc()).offset(page * 18).limit(18).all()
            elif 'subscribers' in sort:
                raffles = session.query(Raffle) \
                    .filter(and_(func.lower(Raffle.name).like(f'%{text}%')),
                            and_(Raffle.platform == platform),
                            and_(Raffle.category != 'one_time')) \
                    .order_by(cast(Raffle.subscribers, Integer).desc()).offset(page * 18).limit(18).all()
            elif 'noHold' in sort:
                raffles = session.query(Raffle) \
                    .filter(and_(func.lower(Raffle.name).like(f'%{text}%')),
                            and_(Raffle.platform == platform),
                            and_(Raffle.category != 'one_time'),
                           and_(or_(Raffle.hold == 0, Raffle.hold == None))) \
                    .offset(page * 18).limit(18).all()

            else:
                raffles = session.query(Raffle).filter(and_(func.lower(Raffle.name).like(f'%{text}%')),
                                                       and_(Raffle.platform == platform),
                                                       and_(Raffle.category != 'one_time')).offset(page * 18).limit(
                    18).all()


        except:

            raffles = session.query(Raffle).filter(and_(func.lower(Raffle.name).like(f'%{text}%')), and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).offset(page*18).limit(18).all()

    else:
        try:
            if 'subscribers' in sort and 'noHold' in sort:
                raffles = session.query(Raffle)\
                    .filter(and_(Raffle.platform == platform),
                           and_(Raffle.category != 'one_time'),
                           and_(or_(Raffle.hold == 0, Raffle.hold == None)))\
                    .order_by(cast(Raffle.subscribers, Integer).desc()).offset(page * 18).limit(18).all()
            elif 'subscribers' in sort:
                raffles = session.query(Raffle) \
                    .filter(and_(Raffle.platform == platform),
                            and_(Raffle.category != 'one_time')) \
                    .order_by(cast(Raffle.subscribers, Integer).desc()).offset(page * 18).limit(18).all()
            elif 'noHold' in sort:
                raffles = session.query(Raffle) \
                    .filter(and_(Raffle.platform == platform),
                            and_(Raffle.category != 'one_time'),
                           and_(or_(Raffle.hold == 0, Raffle.hold == None))) \
                    .offset(page * 18).limit(18).all()

            else:
                raffles = session.query(Raffle).filter(and_(Raffle.platform == platform)).offset(page * 18).limit(
                    18).all()


        except:
            print(platform, page)
            raffles = session.query(Raffle).filter(and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).offset(page * 18).limit(18).all()

    return raffles



@app.route('/raffles', methods=['GET'])
def get_raffle_text_():


    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    try:
        text = request.args.get('search')

        if text == '':
            text = None

    except:
        text = None

    try:
        sort = request.args.get('sort').split(',')

        if sort == '':
            sort = None

    except:
        sort = None

    platform = request.args.get('platform')
    category = request.args.get('category')


    if category == 'selection':
        page = (request.args.get('page'))

        if page == 'null':
            page = 0
        else:
            page = int(page)

    else:
        page = 0

    if category == 'selection':

        Session = sessionmaker(bind=engine)
        session = Session()

        raffles = Sorting(sort, session, text, page, platform)

        print(len(raffles))

        # aa = split_list(raffles, 18)
        # try:
        #     raffles = aa[page]
        # except:
        #     session.close()
        #
        #     return jsonify({'raffles': [],
        #                     'nextPage': None})


        data = []
        used = []

        # raffles = set(raffles)

        for raffle in raffles:

            # if raffle.category == 'one_time':
            #     continue
            #
            # if raffle.name in used:
            #     continue

            used.append(raffle.name)

            reqs = []
            for req in raffle.requirements:
                reqs.append({'platform': req.platform})

            deadline = raffle.deadline
            if deadline != None and '.' not in deadline and ' ' not in deadline and deadline != '':
                # print(deadline)

                try:
                    if raffle.platform == 'Alphabot':
                        dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]) + 36000)

                    elif raffle.platform == 'Superful':

                        dt_object = datetime.datetime.fromtimestamp(int(deadline))


                    else:
                        dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]))

                    deadline = dt_object.strftime("%d.%m.%Y %H:%M")

                except:
                    pass
            try:
                if raffle.subscribers.replace(',', '') == '':
                    raffle.subscribers = '0'
            except:
                pass

            data.append({'id': raffle.id,
                         'platform': raffle.platform,
                         'profilePicture': raffle.profilePicture,
                         'banner': raffle.banner,
                         'name': raffle.name,
                         'NumberOfWinners': raffle.NumberOfWinners,
                         'hold': float(raffle.hold) if raffle.hold != None else 0,
                         'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                         'deadline': deadline,
                         'requirements': reqs
                         })

        session.close()
        # print(len(data))
        # llst = split_list(data, 18)
        # data = llst[page]
        try:
            raffles = Sorting(sort, session, text, page+1, platform)

            if len(raffles) > 0:
                page = page+1
            else:
                page= None

        except:
            page = None

        return jsonify({'raffles': data,
                        'nextPage': page})

    elif category == 'topToday':

        Session = sessionmaker(bind=engine)
        session = Session()

        if text:
            raffles = session.query(Raffle).filter(and_(func.lower(Raffle.name).like(f'%{text}%')), and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).all()
        else:
            raffles = session.query(Raffle).filter(and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).all()

        data = []

        for raffle in raffles:

            if raffle.category != 'today':
                continue

            reqs = []
            for req in raffle.requirements:
                reqs.append({'platform': req.platform,
                             'action': req.action,
                             'clarification': req.clarification})

            data.append({'id': raffle.id,
                         'platform': raffle.platform,
                         'category': raffle.category,
                         'profilePicture': raffle.profilePicture,
                         'banner': raffle.banner,
                         'name': raffle.name,
                         'TotalSupply': raffle.TotalSupply,
                         'NumberOfWinners': raffle.NumberOfWinners,
                         'hold': float(raffle.hold) if raffle.hold != None else 0,
                         'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                         'deadline': raffle.deadline,
                         'platformLink': raffle.platformLink,
                         'captcha': raffle.captcha,
                         'requirements': reqs
                         })

        session.close()

        # llst = split_list(data, 18)
        # data = llst[page]

        return jsonify({'raffles': data,
                        'nextPage': None})

    elif category == 'topWeek':

        Session = sessionmaker(bind=engine)
        session = Session()

        if text:
            raffles = session.query(Raffle).filter(and_(func.lower(Raffle.name).like(f'%{text}%')), and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).all()
        else:
            raffles = session.query(Raffle).filter(and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).all()

        data = []

        for raffle in raffles:

            if raffle.category != 'top_this_week':
                continue

            reqs = []
            for req in raffle.requirements:
                reqs.append({'platform': req.platform,
                             'action': req.action,
                             'clarification': req.clarification})

            data.append({'id': raffle.id,
                         'platform': raffle.platform,
                         'category': raffle.category,
                         'profilePicture': raffle.profilePicture,
                         'banner': raffle.banner,
                         'name': raffle.name,
                         'TotalSupply': raffle.TotalSupply,
                         'NumberOfWinners': raffle.NumberOfWinners,
                         'hold': float(raffle.hold) if raffle.hold != None else 0,
                         'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                         'deadline': raffle.deadline,
                         'platformLink': raffle.platformLink,
                         'captcha': raffle.captcha,
                         'requirements': reqs
                         })

        session.close()

        # llst = split_list(data, 18)
        # data = llst[page]

        return jsonify({'raffles': data,
                        'nextPage': None})

    elif category == 'new':

        Session = sessionmaker(bind=engine)
        session = Session()

        if text:
            raffles = session.query(Raffle).filter(and_(func.lower(Raffle.name).like(f'%{text}%')), and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).all()
        else:
            raffles = session.query(Raffle).filter(and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).all()

        data = []

        for raffle in raffles:

            if raffle.category != 'new':
                continue

            reqs = []
            for req in raffle.requirements:
                reqs.append({'platform': req.platform,
                             'action': req.action,
                             'clarification': req.clarification})

            data.append({'id': raffle.id,
                         'platform': raffle.platform,
                         'category': raffle.category,
                         'profilePicture': raffle.profilePicture,
                         'banner': raffle.banner,
                         'name': raffle.name,
                         'TotalSupply': raffle.TotalSupply,
                         'NumberOfWinners': raffle.NumberOfWinners,
                         'hold': float(raffle.hold) if raffle.hold != None else 0,
                         'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                         'deadline': raffle.deadline,
                         'platformLink': raffle.platformLink,
                         'captcha': raffle.captcha,
                         'requirements': reqs
                         })

        session.close()

        # llst = split_list(data, 18)
        # data = llst[page]

        return jsonify({'raffles': data,
                        'nextPage': None})


@app.route('/myRaffles', methods=['GET'])
def get_raffles_my():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')


    # platform = request.args.get('platform')
    owner_id = request.args.get('discordId')
    userId = request.args.get('userId')

    try:
        page = request.args.get('page')

        if page == 'null':
            page = 0
        else:
            page = int(page)

    except:
        page = 0

    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:

            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    Session = sessionmaker(bind=engine)
    session = Session()

    raffles = session.query(AccessedRaffle).filter(and_(AccessedRaffle.discordId == owner_id)).offset(page * 18).limit(18).all()

    data = []
    for raffle_ in raffles:

        try:
            raffle = raffle_.raffle[0]
        except:
            # traceback.print_exc()
            continue

        # print(raffle.id)

        reqs = []
        for req in raffle.requirements:
            reqs.append({'platform': req.platform})

        deadline = raffle.deadline
        if deadline != None and '.' not in deadline and ' ' not in deadline and deadline != '':
            # print(deadline)

            try:
                if raffle.platform == 'Alphabot':
                    dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]) + 36000)

                elif raffle.platform == 'Superful':

                    dt_object = datetime.datetime.fromtimestamp(int(deadline))


                else:
                    dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]))

                deadline = dt_object.strftime("%d.%m.%Y %H:%M")

            except:
                pass

        data.append({'id': raffle.id,
                     'platform': raffle.platform,
                     'category': raffle.category,
                     'profilePicture': raffle.profilePicture,
                     'banner': raffle.banner,
                     'name': raffle.name,
                     'TotalSupply': raffle.TotalSupply,
                     'NumberOfWinners': raffle.NumberOfWinners,
                     'hold': float(raffle.hold) if raffle.hold != None else 0,
                     'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                     'deadline': deadline,
                     'platformLink': raffle.platformLink,
                     'captcha': raffle.captcha,
                     'requirements': reqs,


                     })

    try:
        raffles = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == owner_id).offset((page+1) * 18).limit(18).all()[::-1]

        if len(raffles) > 0:
            page = page + 1
        else:
            page = None

    except:
        page = None

    session.close()

    return jsonify({'raffles': data,
                    'nextPage': page})


@app.route('/myRaffle/<string:id>', methods=['GET'])
def get_raffle_my(id):
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    # platform = request.args.get('platform')
    owner_id = request.args.get('discordId')
    userId = request.args.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:

            # time.sleep(random.randint(100, 150) / 100)

            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    Session = sessionmaker(bind=engine)
    session = Session()

    raffles = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == owner_id).all()

    for raffle_ in raffles:

        try:
            raffle = raffle_.raffle[0]
        except:
            continue

        if raffle.id != id:
            continue

        # print(raffle.id)

        reqs = []
        for req in raffle.requirements:
            reqs.append({'platform': req.platform,
                         'action': req.action,
                         'clarification': req.clarification})

        deadline = raffle.deadline
        if deadline != None and '.' not in deadline and ' ' not in deadline and deadline != '':
            # print(deadline)

            try:
                if raffle.platform == 'Alphabot':
                    dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]) + 36000)

                elif raffle.platform == 'Superful':

                    dt_object = datetime.datetime.fromtimestamp(int(deadline))


                else:
                    dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]))

                deadline = dt_object.strftime("%d.%m.%Y %H:%M")

            except:
                pass

        old_data = json.loads(raffle_.result)
        new_data = []
        for i in old_data:
            ii = i
            ii['name'] = int(i['name'])
            new_data.append(ii)

        data={'id': raffle.id,
                     'platform': raffle.platform,
                     'category': raffle.category,
                     'profilePicture': raffle.profilePicture,
                     'banner': raffle.banner,
                     'name': raffle.name,
                     'TotalSupply': raffle.TotalSupply,
                     'NumberOfWinners': raffle.NumberOfWinners,
                     'hold': float(raffle.hold) if raffle.hold != None else 0,
                     'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                     'deadline': deadline,
                     'platformLink': raffle.platformLink,
                     'captcha': raffle.captcha,
                     'requirements': reqs,

                     'result': new_data,

                     }

        session.close()

        return jsonify(data), 200

    return jsonify({'message': 'Раффл не найден',
                    'error': True}), 404



@app.route('/deleteMyRaffle', methods=['POST'])
def delete_my_raffles():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    # platform = request.args.get('platform')
    owner_id = request.json.get('discordId')
    raffleId = request.json.get('raffleId')
    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:

            # time.sleep(random.randint(100, 150) / 100)

            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    Session = sessionmaker(bind=engine)
    session = Session()

    raffles = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == owner_id).all()

    data = []
    for raffle_ in raffles:
        try:
            raffle = raffle_.raffle[0]
        except:
            continue

        if raffle.id == raffleId:

            raffle_.raffle.pop(0)
            session.query(AccessedRaffle).filter(AccessedRaffle.id == raffle_.id).delete()
            session.commit()
            break

    session.close()

    return jsonify({'message': 'Succesfully'})

@app.route('/deleteRaffle', methods=['POST'])
def delete_raffle():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    # platform = request.args.get('platform')
    raffleId = request.json.get('raffleId')
    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:

            # time.sleep(random.randint(100, 150) / 100)

            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(Raffle).filter(Raffle.id == raffleId).delete()
    session.commit()

    session.close()

    return jsonify({'message': 'Successfully deleted'})


@app.route('/hideRaffle', methods=['POST'])
def hide_raffle():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    # platform = request.args.get('platform')
    raffleId = request.json.get('raffleId')

    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:

            # time.sleep(random.randint(100, 150) / 100)

            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    Session = sessionmaker(bind=engine)
    session = Session()

    raffle = session.query(Raffle).filter(Raffle.id == raffleId).first()
    raffle.category = 'one_time'
    session.commit()
    session.close()

    return jsonify({'message': 'Successfully hide'})



@app.route('/getCaptchaKey', methods=['GET'])
def get_captcha_key():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    # platform = request.args.get('platform')
    owner_id = request.args.get('discordId')
    userId = request.args.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:

            # time.sleep(random.randint(100, 150) / 100)

            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    try:
        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.discord_id == owner_id).first()

        data = {'status': 'success',
                'message': None,
                'captchaKey': user.CaptchaKey}

        session.close()

        return jsonify(data)

    except:

        data = {'status': 'Error',
                'message': 'Данный пользователь еще не вводил ключ от Capmonster',
                'captchaKey': ''}

        return jsonify(data)



@app.route('/favouriteRaffles', methods=['GET'])
def get_raffles_fav():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    platform = request.args.get('platform')
    owner_id = request.args.get('discordId')
    userId = request.args.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:

            # time.sleep(random.randint(100, 150) / 100)

            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500

    Session = sessionmaker(bind=engine)
    session = Session()

    raffles = session.query(Raffle).filter(Raffle.platform == platform).all()
    user_favourite_raffles = session.query(User).filter(User.discord_id == owner_id).first()

    data = []
    used = []
    for raffle in raffles:

        if raffle.name in used:
            continue

        try:
            if raffle not in user_favourite_raffles.favourite_raffles:
                continue
        except:
            return jsonify({'message': 'У вас нет любимых раффлов'}), 500


        used.append(raffle.name)

        reqs = []
        for req in raffle.requirements:
            reqs.append({'platform': req.platform,
                         'action': req.action,
                         'clarification': req.clarification})

        data.append({'id': raffle.id,
                     'platform': raffle.platform,
                     'category': raffle.category,
                     'profilePicture': raffle.profilePicture,
                     'banner': raffle.banner,
                     'name': raffle.name,
                     'TotalSupply': raffle.TotalSupply,
                     'NumberOfWinners': raffle.NumberOfWinners,
                     'hold': float(raffle.hold) if raffle.hold != None else 0,
                     'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                     'deadline': raffle.deadline,
                     'platformLink': raffle.platformLink,
                     'captcha': raffle.captcha,
                     'requirements': reqs
                     })

    session.close()

    return jsonify(data)





# получение списка розыгрышей по категории
# @app.route('/raffles', methods=['GET'])
# def get_raffles_by_category():
#     platform = request.args.get('platform')
#     category = request.args.get('category')
#
#     if category == 'selection':
#         page = int(request.args.get('page'))
#     else:
#         page = 0
#
#
#
#     # sessionToken = request.args.get('sessionToken')
#     #
#     # er = 0
#     # while er < 5:
#     #     try:
#     #         if CheckUser(userId, sessionToken):
#     #             # print(er)
#     #             break
#     #         else:
#     #             return jsonify({'message': 'Пользователь не найден'}), 500
#     #     except Exception as e:
#     #         # print(e)
#     #         pass
#     #     er+=1
#     #
#     # else:
#     #     return jsonify({'message': 'Error 0'}), 500
#
#     # print(category)
#
#     if category == 'selection':
#
#         Session = sessionmaker(bind=engine)
#         session = Session()
#
#         raffles = session.query(Raffle).filter(and_(Raffle.platform == platform), and_(Raffle.category != 'one_time')).all()
#         print(len(raffles))
#
#         aa = split_list(raffles, 18)
#         raffles = aa[page]
#
#         data = []
#         used = []
#
#         # raffles = set(raffles)
#
#         for raffle in raffles:
#
#             # if raffle.category == 'one_time':
#             #     continue
#             #
#             # if raffle.name in used:
#             #     continue
#
#             used.append(raffle.name)
#
#             reqs = []
#             for req in raffle.requirements:
#                 reqs.append({'platform': req.platform,
#                              'action': req.action,
#                              'clarification': req.clarification})
#
#             deadline = raffle.deadline
#             if  deadline != None and '.' not in deadline and ' ' not in deadline and deadline!='':
#                 # print(deadline)
#
#                 try:
#                     if raffle.platform == 'Alphabot':
#                         dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3])+36000)
#
#                     elif raffle.platform == 'Superful':
#
#                         dt_object = datetime.datetime.fromtimestamp(int(deadline))
#
#
#                     else:
#                         dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]))
#
#                     deadline = dt_object.strftime("%d.%m.%Y %H:%M")
#
#                 except:
#                     pass
#
#
#             data.append({'id': raffle.id,
#                          'platform': raffle.platform,
#                          'category': raffle.category,
#                          'profilePicture': raffle.profilePicture,
#                          'banner': raffle.banner,
#                          'name': raffle.name,
#                          'TotalSupply': raffle.TotalSupply,
#                          'NumberOfWinners': raffle.NumberOfWinners,
#                          'hold': float(raffle.hold) if raffle.hold != None else 0,
#                          'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers.replace(',', '')!='' else 0,
#                          'deadline': deadline,
#                          'platformLink': raffle.platformLink,
#                          'captcha': raffle.captcha,
#                          'requirements': reqs
#                          })
#
#         session.close()
#         # print(len(data))
#         # llst = split_list(data, 18)
#         # data = llst[page]
#         try:
#             a = aa[page+1]
#             page += 1
#         except:
#             page = None
#
#
#         return jsonify({'raffles': data,
#                         'nextPage': page})
#
#     elif category == 'topToday':
#
#         Session = sessionmaker(bind=engine)
#         session = Session()
#
#         raffles = session.query(Raffle).filter(Raffle.platform == platform).all()
#
#         data = []
#
#         for raffle in raffles:
#
#             if raffle.category != 'today':
#                 continue
#
#             reqs = []
#             for req in raffle.requirements:
#                 reqs.append({'platform': req.platform,
#                              'action': req.action,
#                              'clarification': req.clarification})
#
#             data.append({'id': raffle.id,
#                          'platform': raffle.platform,
#                          'category': raffle.category,
#                          'profilePicture': raffle.profilePicture,
#                          'banner': raffle.banner,
#                          'name': raffle.name,
#                          'TotalSupply': raffle.TotalSupply,
#                          'NumberOfWinners': raffle.NumberOfWinners,
#                          'hold': float(raffle.hold) if raffle.hold != None else 0,
#                          'subscribers': int(raffle.subscribers.replace(',', '')),
#                          'deadline': raffle.deadline,
#                          'platformLink': raffle.platformLink,
#                          'captcha': raffle.captcha,
#                          'requirements': reqs
#                          })
#
#         session.close()
#
#         # llst = split_list(data, 18)
#         # data = llst[page]
#
#         return jsonify({'raffles': data,
#                         'nextPage': None})
#
#     elif category == 'topWeek':
#
#         Session = sessionmaker(bind=engine)
#         session = Session()
#
#         raffles = session.query(Raffle).filter(Raffle.platform == platform).all()
#
#         data = []
#
#         for raffle in raffles:
#
#             if raffle.category != 'top_this_week':
#                 continue
#
#             reqs = []
#             for req in raffle.requirements:
#                 reqs.append({'platform': req.platform,
#                              'action': req.action,
#                              'clarification': req.clarification})
#
#             data.append({'id': raffle.id,
#                          'platform': raffle.platform,
#                          'category': raffle.category,
#                          'profilePicture': raffle.profilePicture,
#                          'banner': raffle.banner,
#                          'name': raffle.name,
#                          'TotalSupply': raffle.TotalSupply,
#                          'NumberOfWinners': raffle.NumberOfWinners,
#                          'hold': float(raffle.hold) if raffle.hold != None else 0,
#                          'subscribers': int(raffle.subscribers.replace(',', '')),
#                          'deadline': raffle.deadline,
#                          'platformLink': raffle.platformLink,
#                          'captcha': raffle.captcha,
#                          'requirements': reqs
#                          })
#
#         session.close()
#
#         # llst = split_list(data, 18)
#         # data = llst[page]
#
#         return jsonify({'raffles': data,
#                         'nextPage': None})
#
#     elif category == 'new':
#
#         Session = sessionmaker(bind=engine)
#         session = Session()
#
#         raffles = session.query(Raffle).filter(Raffle.platform == platform).all()
#
#         data = []
#
#         for raffle in raffles:
#
#             if raffle.category != 'new':
#                 continue
#
#             reqs = []
#             for req in raffle.requirements:
#                 reqs.append({'platform': req.platform,
#                              'action': req.action,
#                              'clarification': req.clarification})
#
#             data.append({'id': raffle.id,
#                          'platform': raffle.platform,
#                          'category': raffle.category,
#                          'profilePicture': raffle.profilePicture,
#                          'banner': raffle.banner,
#                          'name': raffle.name,
#                          'TotalSupply': raffle.TotalSupply,
#                          'NumberOfWinners': raffle.NumberOfWinners,
#                          'hold': float(raffle.hold) if raffle.hold != None else 0,
#                          'subscribers': int(raffle.subscribers.replace(',', '')),
#                          'deadline': raffle.deadline,
#                          'platformLink': raffle.platformLink,
#                          'captcha': raffle.captcha,
#                          'requirements': reqs
#                          })
#
#         session.close()
#
#         # llst = split_list(data, 18)
#         # data = llst[page]
#
#         return jsonify({'raffles': data,
#                         'nextPage': None})



# получение информации о конкретном розыгрыше
@app.route('/raffles/<string:id>', methods=['GET'])
def get_raffle_by_id(id):
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')


    try:

        # userId = request.args.get('userId')
        # sessionToken = request.args.get('sessionToken')
        #
        # er = 0
        # while er < 5:
        #     try:
        #         if CheckUser(userId, sessionToken):
        #             # print(er)
        #             break
        #         else:
        #             return jsonify({'message': 'Пользователь не найден'}), 500
        #     except Exception as e:
        #         # print(e)
        #         pass
        #     er += 1
        #
        # else:
        #     return jsonify({'message': 'Error 0'}), 500

        Session = sessionmaker(bind=engine)
        session = Session()

        # print(id)
        raffle = session.query(Raffle).filter(Raffle.id == id).first()

        # print(raffle.name)

        reqs = []

        if raffle.requirements == None:
            return jsonify({'message': "Incorrect Raffle Requirements"}), 500

        for req in raffle.requirements:
            reqs.append({'platform': req.platform,
                         'action': req.action,
                         'clarification': req.clarification})

        deadline = raffle.deadline
        if deadline != None and '.' not in deadline and ' ' not in deadline and deadline != '':
            # print(deadline)
            if raffle.platform == 'Alphabot':
                dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]) + 36000)
                deadline = dt_object.strftime("%d.%m.%Y %H:%M")

            elif raffle.platform == 'Superful':
                dt_object = datetime.datetime.fromtimestamp(int(deadline))
                deadline = dt_object.strftime("%d.%m.%Y %H:%M")

            else:
                try:
                    dt_object = datetime.datetime.fromtimestamp(int(deadline[:-3]))
                    deadline = dt_object.strftime("%d.%m.%Y %H:%M")
                except:
                    deadline = deadline

        data =  {'id': raffle.id,
                 'platform': raffle.platform,
                 'category': raffle.category,
                 'profilePicture': raffle.profilePicture,
                 'banner': raffle.banner,
                 'name': raffle.name,
                 'TotalSupply': raffle.TotalSupply,
                 'NumberOfWinners': raffle.NumberOfWinners,
                 'hold': float(raffle.hold) if raffle.hold != None else 0,
                 'subscribers': int(raffle.subscribers.replace(',', '')) if raffle.subscribers != None else None,
                 'deadline': deadline,
                 'platformLink': raffle.platformLink,
                 'captcha': raffle.captcha,
                 'requirements': reqs
                 }

        session.close()

        return jsonify(data)
    except KeyError:
        pass
    except:

        traceback.print_exc()

        return jsonify({'message': "I can't find this raffle in the system"}), 500

# получение информации о розыгрыше по ссылке
@app.route('/rafflelink', methods=['GET'])
def get_raffle_by_link():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')


    # userId = request.args.get('userId')
    # sessionToken = request.args.get('sessionToken')
    #
    # er = 0
    # while er < 5:
    #     try:
    #         if CheckUser(userId, sessionToken):
    #             # print(er)
    #             break
    #         else:
    #             return jsonify({'message': 'Пользователь не найден'}), 500
    #     except Exception as e:
    #         # print(e)
    #         pass
    #     er += 1
    #
    # else:
    #     return jsonify({'message': 'Error 0'}), 500

    raffle_link = request.args.get('raffleLink')

    if 'https://www.alphabot.app/' in raffle_link:
        platform = 'Alphabot'
    elif 'https://www.superful.xyz/' in raffle_link:
        platform = 'Superful'
    elif 'https://www.premint.xyz/' in raffle_link:
        platform = 'Premint'
    else:
        return jsonify({'message': 'Invalid link'}), 500

    result_ = requests.get(f'http://localhost:27000/data/raffle?raffleLink={raffle_link}&platform={platform}')
    result = result_.json()

    try:
        er = result['message']

        result = {'message': er,
                  'error': True,
                  'raffle': None}
    except:
        result = {'message': None,
                  'error': False,
                  'raffle':result_.json()}

    # print(result)

    return jsonify(result)

# @app.route('/add_favourites', methods=['POST'])
# def add_favourites():
#     userId = request.json.get('userId')
#     sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]
#
#     er = 0
#     while er < 5:
#         try:
#             status = CheckUser(userId, sessionToken)
#             if status[0] and status[1]:
#                 # print(er)
#                 break
#             elif not status[0]:
#                 return jsonify({'message': 'Пользователь не найден'}), 500
#             elif status[0] and not status[1]:
#                 return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500
#
#         except Exception as e:
#
#             time.sleep(random.randint(100,150)/100)
#             # print(e)
#             pass
#         er += 1
#
#     else:
#         return jsonify({'message': 'Error 0'}), 500
#
#     discord_id = request.get_json()['discordId']
#     raffle_id = request.get_json()['raffle_id']
#
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     user = session.query(User).filter(User.discord_id == discord_id and User.userId == userId).first()
#
#     try:
#         raffle = session.query(Raffle).filter(Raffle.id == raffle_id).first()
#
#         user.favourite_raffles.append(raffle)
#
#         session.commit()
#         session.close()
#
#         return jsonify({'status': 'Success'}), 200
#     except:
#         # traceback.print_exc()
#         return jsonify({'message': "Authorization Error"}), 500
#
# @app.route('/remove_favourites', methods=['POST'])
# def remove_favourites():
#     userId = request.json.get('userId')
#     sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]
#
#     er = 0
#     while er < 5:
#         try:
#             status = CheckUser(userId, sessionToken)
#             if status[0] and status[1]:
#                 # print(er)
#                 break
#             elif not status[0]:
#                 return jsonify({'message': 'Пользователь не найден'}), 500
#             elif status[0] and not status[1]:
#                 return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500
#
#         except Exception as e:
#             # time.sleep(random.randint(100, 150) / 100)
#             # print(e)
#             pass
#         er += 1
#
#     else:
#         return jsonify({'message': 'Error 0'}), 500
#
#     discord_id = request.get_json()['discordId']
#     raffle_id = request.get_json()['raffle_id']
#
#     Session = sessionmaker(bind=engine)
#     session = Session()
#
#     user = session.query(User).filter(User.discord_id == discord_id and User.userId == userId).first()
#     raffle = session.query(Raffle).filter(Raffle.id == raffle_id).first()
#
#     try:
#         for favourite_raffle in user.favourite_raffles:
#             if favourite_raffle.id  == raffle.id:
#                 break
#
#
#         user.favourite_raffles.remove(raffle)
#
#         session.commit()
#         session.close()
#
#         return jsonify({'status': 'Success'}), 200
#
#     except:
#
#         session.close()
#
#         return jsonify({'status': 'Error'}), 500

@app.route('/delete_user', methods=['POST'])
def delete_user():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    try:

        discord_id = request.get_json()['discordId']
        specialCodeForDeleting = request.get_json()['SpecialKKJon']
        if specialCodeForDeleting != 'blop(ik30cm92jnf90nd23d':
            return jsonify({'message': 'Error'}), 500

        Session = sessionmaker(bind=engine)
        session = Session()

        user = session.query(User).filter(User.discord_id == discord_id).first()

        session.delete(user)

        session.commit()
        session.close()

        return jsonify({'status': 'Success'}), 200

    except:

        # session.close()

        return jsonify({'status': 'Error'}), 500

@app.route('/stopraffle', methods=['POST'])
def stop_raffle():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')


    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]
    # print(11)

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:
            # time.sleep(random.randint(100, 150) / 100)
            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500


    # print(10)

    data = request.get_json()

    # print(data)

    user_id = data['discordId']


    # print(payload)

    Session = sessionmaker(bind=engine)
    session = Session()
    event = session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.discordId == user_id).first()

    if event.status == 'running':
        event.status = 'cancelled'
        session.commit()
        session.close()

        return jsonify({'status': 'success'})
    else:
        session.close()
        return jsonify({'status': 'error'})


@app.route('/startraffle', methods=['POST'])
def startraffle():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')


    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]
    need_time = request.json.get('time')

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:
            # time.sleep(random.randint(100, 150) / 100)
            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500


    # print(10)

    data = request.get_json()

    # print(data)


    user_id = data['discordId']

    try:
        id = data['raffleId']
    except:
        id = None

    first_account = data['firstAcc']
    last_account = data['lastAcc']

    try:
        exceptions = data['exceptions']
    except:
        exceptions = []

    payload = {'discordId': user_id,
               'raffleId': id,
               'firstAcc': first_account,
               'lastAcc': last_account,
               'exceptions': exceptions,
               'time': need_time
               }
    try:
        payload['RaffleInfo'] = data['TwitterRaffle']
    except:
        pass

    # print(payload)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter(User.discord_id == user_id and User.userId == userId).first()

        raffle = session.query(Raffle).filter(Raffle.id == id).first()

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

        CaptchaKey = session.query(User.CaptchaKey).filter(User.discord_id == user_id).first()

        if raffle_data['discord_invite'] != [] and (CaptchaKey == None or CaptchaKey == ''):
            session.close()
            return jsonify({'message': "Вы не внесли API ключ от Capmonster"}), 500

        try:

            session.close()
            a = user.discord_id

            status = requests.post('http://127.0.0.1:27500/start', json=payload)

            return jsonify({'status': status.json()['status']})

        except:

            session.close()

            return jsonify({'message': "Authorization Error"}), 500

    except AttributeError:

        try:
            session.close()
            a = user.discord_id

            status = requests.post('http://127.0.0.1:27500/start', json=payload)

            return jsonify({'status': status.json()['status']})

        except:
            traceback.print_exc()

            session.close()
            return jsonify({'message': "Error"}), 500

    except KeyError:
        pass
    except:

        traceback.print_exc()

        session.close()
        return jsonify({'message': "Error"}), 500


@app.route('/startRaffleAgain', methods=['POST'])
def startraffleagain():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')


    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]
    need_time = request.json.get('time')

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:
            # time.sleep(random.randint(100, 150) / 100)
            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500


    # print(10)

    data = request.get_json()

    # print(data)

    user_id = data['discordId']
    id = data['raffleId']

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == user_id and User.userId == userId).first()


    # print(payload)



    raffles = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == user_id).all()

    for raffle_ in raffles:

        try:
            raffle = raffle_.raffle[0]
        except:
            continue

        if raffle.id != id:
            continue

        old_data = json.loads(raffle_.result)
        new_data = []
        for i in old_data:
            ii = i
            ii['name'] = int(i['name'])
            new_data.append(ii)

        break
    # print(new_data)
    payload = {'discordId': user_id,
               'raffleId': id,
               'firstAcc': str(new_data[0]['name']),
               'lastAcc': str(new_data[-1]['name']),
               'exceptions': [],
               'time': need_time
               }
    max = 0
    for d in new_data:
        if d['status'] == False or d['status'] == None:
            pass
        else:
            payload['exceptions'].append(str(d['name']))

        if int(d['name']) > max:
            max = int(d['name'])

    payload['lastAcc'] = str(max)

    print(payload)

    try:
        a = user.discord_id

        status = requests.post('http://127.0.0.1:27500/start', json=payload)

        return jsonify({'status': status.json()['status']})

    except:

        return jsonify({'message': "Authorization Error"}), 500

@app.route('/ResultChecker', methods=['POST'])
def ResultChecker():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    userId = request.json.get('userId')
    sessionToken = request.headers.get('Authorization').split('Bearer ')[-1]

    er = 0
    while er < 5:
        try:
            status = CheckUser(userId, sessionToken)
            if status[0] and status[1]:
                # print(er)
                break
            elif not status[0]:
                return jsonify({'message': 'Пользователь не найден'}), 500
            elif status[0] and not status[1]:
                return jsonify({'message': 'У данного пользователя нет доступа к Raffle-боту'}), 500

        except Exception as e:
            # time.sleep(random.randint(100, 150) / 100)
            # print(e)
            pass
        er += 1

    else:
        return jsonify({'message': 'Error 0'}), 500
    # print(10)

    data = request.get_json()

    # print(data)

    user_id = data['discordId']
    id = data['raffleId']

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == user_id and User.userId == userId).first()

    raffles = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == user_id).all()

    for raffle_ in raffles:

        try:
            raffle = raffle_.raffle[0]
        except:
            continue

        if raffle.id != id:
            continue

        old_data = json.loads(raffle_.result)
        new_data = []
        for i in old_data:
            ii = i
            ii['name'] = int(i['name'])
            new_data.append(ii)

        break
    # print(new_data)
    payload = {'discordId': user_id,
               'raffleId': id,
               'firstAcc': str(new_data[0]['name']),
               'lastAcc': str(new_data[-1]['name']),
               'exceptions': [],
               'time': 1200
               }
    max = 0
    for d in new_data:

        if int(d['name']) > max:
            max = int(d['name'])

    payload['lastAcc'] = str(max)

    print(payload)

    try:
        a = user.discord_id

        status = requests.post('http://127.0.0.1:27500/RaffleChecker', json=payload)

        return jsonify({'status': status.json()['status']})

    except:

        return jsonify({'message': "Authorization Error"}), 500

@app.route('/checkrole', methods=['POST'])
def get_user_role_status():
    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')

    data = request.get_json()
    print(data)

    try:
        user_id = data['discordId']
    except:
        return jsonify({'message': 'Discord Id not found'}) , 500

    role = data['role']

    e = requests.post('http://127.0.0.1:1290/check-role', json={'user_id': int(user_id),
                                                                'role_name': role,
                                                                'guild_id': })

    return jsonify(e.json())

# Payments System


@app.route('/CheckReplenishment', methods=['GET'])
def CheckReplenishment():

    print(Fore.RED + f'[{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] [{request.method}] [{request.remote_addr}] - {request.url}')


    discordId = request.args.get('discordId')
    discordId = int(discordId)

    status = CheckStatus_(create_connection(), discordId)
    if status:
        print(status)
        response = {
            "address": status[2],
            "image": f"https://alpharescue.online:3500/QR/{status[2]}.jpg",
            "expiresTime": status[6]
        }

        return jsonify(response), 200
    else:
        return jsonify({'status': 'Error'}), 500

@app.route('/QR/<string:id>', methods=['GET'])
def CheckReplenishmentQR(id):
    try:
        return send_from_directory(os.path.join(app.root_path, 'FILEs'), f'{id}')
    except:
        return jsonify({'status': 'QR is not exists'}), 500

@app.route('/image/<string:id>', methods=['GET'])
def Images(id):
    try:
        return send_from_directory(os.path.join(app.root_path, 'IMAGEs'), f'{id}')
    except:
        return jsonify({'status': 'Image is not exists'}), 500

@app.route('/StopReplenishment', methods=['POST'])
def StopReplenishment():

    discordId = request.json['discordId']

    mark_wallet_busy_2(create_connection(), discordId)

    return jsonify({'status': 'success'})

@app.route('/CreateReplenishment', methods=['POST'])
def replenish_balance():

    try:

        print(request.json)

        discordId = request.json['discordId']

        try:
            amount = request.json['amount']
        except:
            amount = None

        coin = request.json['coin']
        network = request.json['network']

        try:
            accountsQuantity = request.json['accountsQuantity']
        except:
            accountsQuantity = None

        expiresDate = request.json['expiresDate']
        requestHash = request.json['hash']
        subscriptionType = request.json['subscriptionType']

        try:
            referralCode = request.json['referralCode']

            referral_data = [referralCode]

        except:
            referral_data = None


        if subscriptionType == 'Rafflebot':
            print(f"SpecialCode:{discordId}:{expiresDate}:{accountsQuantity}")
            Hash = text_to_sha256(f"SpecialCode:{discordId}:{expiresDate}:{accountsQuantity}")
        else:
            Hash = text_to_sha256(f"SpecialCode:{discordId}:{expiresDate}")

        print(requestHash, Hash)
        # print(f"SpecialCode:{discordId}:{expiresDate}:{amount}", )

        if Hash == requestHash:
            pass
        else:
            return jsonify({'status': 'Data error'}), 500


        try:
            mark_wallet_busy_2(create_connection(), discordId)
        except:
            pass

        # print(request.json)
        # print(Hash)
        # input()


        wallet, private = get_wallet(create_connection(), 'TRON' if network == 'TRC20' else 'BSC')
        print(wallet, private)
        mark_wallet_busy(create_connection(), wallet, discordId)
        qr_code_filename = generate_qr_code(wallet)

        if network == 'BEP20' and coin == 'USDT':
            t = threading.Thread(target=wait_for_balances_BSC,
                                 args=("https://bsc-dataseed.binance.org/", wallet, discordId, accountsQuantity, expiresDate, subscriptionType, {"USDT": "0x55d398326f99059ff775485246999027b3197955"},{'USDT': amount}, referral_data))
            t.start()
        elif network == 'BEP20' and coin == 'BUSD':
            t = threading.Thread(target=wait_for_balances_BSC,
                                 args=("https://bsc-dataseed.binance.org/", wallet, discordId, accountsQuantity, expiresDate, subscriptionType, {"BUSD": "0xe9e7cea3dedca5984780bafc599bd69add087d56"},{'BUSD': amount}, referral_data))
            t.start()
        elif network == 'TRC20' and coin == 'USDT':
            t = threading.Thread(target=wait_for_balances_TRON,
                                 args=(wallet, private, discordId, accountsQuantity, expiresDate, subscriptionType, amount, referral_data))
            t.start()


        return jsonify({'address': wallet}), 200

    except KeyError:
        traceback.print_exc()
        return jsonify({'status': 'Data error'}), 500

    except Exception as e:

        traceback.print_exc()

        return jsonify({'status': 'Data error'}), 500



def O():
    while True:
        # print(1)

        now = datetime.datetime.now(timezone)

        if now.hour == 1 and now.minute == 10:
            # Печатаем текущее время
            RefreshDay()
            time.sleep(600)

def UserSubscriptionChecker():
    while True:
        engine1 = create_engine(
            '')
        SessionA = sessionmaker(bind=engine1)
        sessionA = SessionA()

        users = sessionA.query(User2).all()
        for user in users:
            try:

                try:
                    if user.CommunitySubscription[0].expires < datetime.datetime.utcnow():
                        requests.post('http://127.0.0.1:1290/remove-role',
                                      json={'discordId': user.Account[0].providerAccountId,
                                            'role': 'Rescue Community Pass'})
                        user.communityMember = False
                        sessionA.query(CommunitySubscription).filter_by(user=user).delete()

                        sessionA.commit()
                except:
                    # traceback.print_exc()
                    pass

                if user.RaffleBotSubscription[0].expires < datetime.datetime.utcnow():
                    requests.post('http://127.0.0.1:1290/remove-role',
                                  json={'discordId': user.Account[0].providerAccountId,
                                        'role': 'Rescue Raffle Bot'})
                    user.raffleBotUser = False
                    user.CommunitySubscription = None
                    user.RaffleBotSubscription = None
                    sessionA.query(CommunitySubscription).filter_by(user=user).delete()
                    sessionA.query(Refr).filter_by(user=user).delete()

                    sessionA.commit()


            except:
                pass

        sessionA.close()
        time.sleep(10)

@app.route('/.well-known/acme-challenge/<string:id>', methods=['GET'])
def getFiles(file):
    if file == 'ESAI8kEGh06FXorxUffZdJGzIubCIikO-kqTQAy3Wxg':
        return 'ESAI8kEGh06FXorxUffZdJGzIubCIikO-kqTQAy3Wxg.BpgCLj2EFgBVs-cLflVp3WqK6p1pnIfdJ2e7L5NrN5M'

if __name__ == '__main__':
    ssl_cert = (r"C:\Certbot\live\www.alpharescue.online\fullchain.pem", r"C:\Certbot\live\www.alpharescue.online\privkey.pem")
    # ssl_cert = (r"C:\Program Files\OpenSSL-Win64\bin\cert.pem", r"C:\Program Files\OpenSSL-Win64\bin\key.pem")
    timezone = pytz.timezone('Europe/Moscow')

    warnings.filterwarnings('ignore', category=DeprecationWarning, module='sqlalchemy')

    # firstTime()
    # print('Кошельки созданы')

    _scheduler = threading.Thread(target=O)
    _scheduler.start()

    # _scheduler1 = threading.Thread(target=UserSubscriptionChecker)
    # _scheduler1.start()

    from cheroot.wsgi import Server as WSGIServer
    from cheroot.ssl.builtin import BuiltinSSLAdapter


    server = WSGIServer(('0.0.0.0', 3500), app)
    server.ssl_adapter = BuiltinSSLAdapter(ssl_cert[0], ssl_cert[1])
    server.start()

    # app.run(host='0.0.0.0', port=3500)



