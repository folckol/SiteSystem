import sqlite3
import time
import traceback
import uuid
from datetime import datetime

import requests
from sqlalchemy import func, and_, cast, Float, or_, Boolean, DateTime
from sqlalchemy.orm import sessionmaker

from Creating_DBs import *
from Rescue_Site_System.ServerGlobal import User2


def CleanEvents():
    Session = sessionmaker(bind=engine)
    session = Session()

    events = session.query(StartRaffleEventResponse).all()
    # print(events)

    for event in events:
        session.query(StartRaffleEventResponse).filter(StartRaffleEventResponse.id == event.id).delete()
        session.commit()

    session.close()


def ChangeRaffleData():

    Session = sessionmaker(bind=engine)
    session = Session()

    raffle = session.query(Raffle).filter(Raffle.id == '65d611ca-6273-453c-a444-60193107f531').first()
    raffle.category = 'one_time'

    session.commit()

    session.close()

def CleanMyRaffles():
    Session = sessionmaker(bind=engine)
    session = Session()

    AccessedRaffles = session.query(AccessedRaffle).all()
    for i in AccessedRaffles:

        session.query(AccessedRaffle).filter(AccessedRaffle.id == i.id).delete()
        session.commit()

    session.close()

def DeleteTwitters():

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == '975081341492293695').first()
    accounts = user.accounts

    for account in accounts:
        account.TwitterStatus = None
        account.TwitterAuthToken = None
        account.TwitterCsrf = None

    session.commit()

    session.close()
def DeleteRaffles():

    Session = sessionmaker(bind=engine)
    session = Session()

    session.query(Raffle).delete()


    session.commit()
    session.close()

def RafflesLen():

    Session = sessionmaker(bind=engine)
    session = Session()

    aa = session.query(Raffle).all()
    print(len(aa))


    # session.commit()
    session.close()

def Cleaner():
    Session = sessionmaker(bind=engine)
    session = Session()

    links = session.query(Raffle.platformLink).all()
    # print(len(raffles), len(set(raffles)))

    used_Link = []
    used = []

    raffles = session.query(Raffle).all()
    for raffle in raffles:

        if raffle.id not in used:
            used.append(raffle.id)
        else:
            session.query(Raffle).filter(Raffle.id == raffle.id).delete()
            session.commit()

        if raffle.platformLink not in used_Link:
            used_Link.append(raffle.platformLink)

        else:
            print(raffle.platformLink)
            session.query(Raffle).filter(Raffle.id == raffle.id).delete()
            session.commit()

        deadline = 999999999999
        # if raffle.id == '158c3808-01a8-489c-b0c9-fad4dff07bce':
        # print(raffle.id, raffle.deadline, int(time.time()))

        if raffle.deadline is not None:



            if ' ' in raffle.deadline:
                try:
                    date_obj = datetime.strptime(raffle.deadline, '%Y-%m-%d %H:%M:%S')
                    deadline = int(date_obj.timestamp())
                except:
                    deadline = 999999999999
            elif raffle.deadline != None and raffle.deadline != '':
                try:
                    deadline = int(raffle.deadline)

                    if len(raffle.deadline) == 13:
                        deadline = int(raffle.deadline[:-3])

                except:
                    deadline = 999999999999

                if raffle.id == 'be849b1f-caae-4685-ab7d-e8c52c129480':
                    print(raffle.id, deadline)

                if deadline < int(time.time()):
                    ses = session.query(Raffle).filter(Raffle.id == raffle.id).first()
                    ses.category = 'one_time'
                    session.commit()

            # if raffle.platform == 'Superful':
            #     print(raffle.id, deadline, time.time(), raffle.category)

            elif int(time.time()) - int(raffle.timestamp) > 864000 or int(time.time()) > deadline:
                ses = session.query(Raffle).filter(Raffle.id == raffle.id).first()
                ses.category = 'one_time'
                session.commit()

            elif len(str(raffle.deadline)) == 13 and (
            int(str(raffle.deadline)[:-3]) if raffle.platform == 'Superful' else int(
                    str(raffle.deadline)[:-3]) + 36000) < int(time.time()):

                ses = session.query(Raffle).filter(Raffle.id == raffle.id).first()
                ses.category = 'one_time'
                session.commit()


            elif int(time.time()) - int(raffle.timestamp) > 864000 * 4 or int(time.time()) > deadline + 864000 * 2:
                session.query(Raffle).filter(Raffle.id == raffle.id).first()
                session.commit()

        # if raffle.requirements == []:
        #     session.query(Raffle).filter(Raffle.id == raffle.id).delete()
        #     session.commit()

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
    print(used_Link)
    session.close()

def FindRaffle():
    Session = sessionmaker(bind=engine)
    session = Session()

    aa = session.query(Raffle).filter(Raffle.id == 'be849b1f-caae-4685-ab7d-e8c52c129480').first()
    print(aa.deadline, int(time.time()))

    # session.commit()
    session.close()


def Users():
    Session = sessionmaker(bind=engine)
    session = Session()

    aa = session.query(User).all()
    for i in aa:
        print(i.discord_id)

    # session.commit()
    session.close()

def CreateDB():

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == '453456267365580810').first()
    if user == None:

        user = User(id=str(uuid.uuid4()),
                    discord_id='453456267365580810',
                    userId="")
        accounts = []
        for i in range(50):
            acc = Accounts(id=str(uuid.uuid4()),
                           name=i)
            accounts.append(acc)

        user.accounts = accounts

        session.add(user)
        session.commit()


    # session.commit()
    session.close()

def UserData():

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == '923129125261176842').first()
    print(user.CaptchaKey)
    for i in user.accounts:
        print(i.name,
            i.ProxyData,
            i.MetaMaskAddress,
            i.MetaMaskPrivateKey,
            i.TwitterAuthToken,
            i.TwitterCsrf,
            i.DiscordToken)

    # raffles_ = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == '933532486628171776').all()
    # for raffle_ in raffles_:
    #     try:
    #         if raffle_.raffle[0].platformLink == raffles_['dasd']:
    #             next_ = True
    #             break
    #     except:
    #         print(raffle_.result)
    #         try:
    #             if raffle_.raffle[0].id == '8a5cae0b-03bd-4775-98b9-4115e10b03ef':
    #                 print('12')
    #                 break
    #         except:
    #             pass

    # raffle = session.query(Raffle).filter(Raffle.id == 'f5cc5229-b6b2-446a-83e1-38175d952f3c').delete()
    # print(raffle.platform)


    # session.commit()
    session.close()

def UserDataChange():

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == '406467907120267274').first()

    # raffles_ = session.query(AccessedRaffle).filter(AccessedRaffle.discordId == '460719167738347520').all()
    # for raffle_ in raffles_:
    #     try:
    #         if raffle_.raffle[0].platform == 'Twitter':
    #             session.query(Raffle).filter(Raffle.id == raffle_.raffle[0].id).delete()
    #             session.query(AccessedRaffle).filter(AccessedRaffle.id == raffle_.id).delete()
    #             break
    #     except:
    #         pass
    # user.CaptchaKey = 'uuuu'

    for i in user.accounts:


        # pass
        # if i.name in ['30', '31', '32']:
        # i.TwitterStatus = None
        # i.TwitterAuthToken = None
        # i.TwitterCsrf = None
        # i.DiscordStatus = None
        # i.DiscordToken = None
        i.MetaMaskAddress = None
        i.MetaMaskPrivateKey = None
        # i.Email = None
        # i.ProxyStatus = None
        # i.ProxyType = None
        # i.ProxyData = None


    # for i in user.accounts:
    #     if i.TwitterAuthToken == 'nework':
    #         i.TwitterAuthToken = '07fd0d29cc5357b5f2700802a10b6999c29b96bc'
    #         i.TwitterCsrf = '5fdf7842bd53f2a4593f6bee919b82675a71e7a5ae54fde189883f59c820c933d6dacebb1b17253d404e7914efb7c3fcda9cd1052e491d9b34428e19a6b0b8fc6da86c45efac5cbca9995a227f045d8e'
    #         i.Email = 'healthdesfugarde6052@mail.ru'
    #         i.MetaMaskAddress = '0x332868d9a0edf4a51cd7cca094af7a42b5d14035'
    #         i.MetaMaskPrivateKey = '0xb3fdf8c013db849dc58815f0f9a0673b41b615ec3927d0e5e9c2e2aca169ffe4'
    #         i.ProxyData = 'http://edrjqcda:y5fv7eeid3px@104.233.16.104:6368'




    session.commit()
    session.close()

def CheckRaffles():
    Session = sessionmaker(bind=engine)
    session = Session()

    raffles = session.query(Raffle) \
        .filter(and_(Raffle.platform == 'Premint'),
                and_(Raffle.category != 'one_time'),
                and_(or_(Raffle.hold == 0, Raffle.hold == None))) \
        .order_by(cast(Raffle.subscribers, Integer).desc()).offset(1 * 18).limit(18).all()

    print(len(raffles))

    session.commit()
    session.close()

def reqsToDsServer():

    a = requests.post('http://127.0.0.1:1290/remove-role', json={'discordId': '460719167738347520'})
    print(a.text)

def EditRaffles():
    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == '460719167738347520').first()


    for acc in user.accounts:
        if acc.name in ['0']:
            acc.ProxyStatus = 'BAN'


    session.commit()
    session.close()

def create_connection():
    conn = sqlite3.connect('wallets.db', check_same_thread=False)

    cur = conn.cursor()
    cur.execute("""SELECT * FROM wallets""")
    for i in cur.fetchall():
        print(i[4])

    cur.close()

def DeleteAll():
    Session = sessionmaker(bind=engine)
    session = Session()

    users = session.query(User).all()

    for i in users:

        session.delete(i)

    session.commit()
    session.close()

def AddRaffleBotUser():

    a = '1032328199293636639'
    count = 50

    Session = sessionmaker(bind=engine)
    session = Session()

    user = session.query(User).filter(User.discord_id == a).first()
    if user == None:

        user = User(id=str(uuid.uuid4()),
                    discord_id=a,
                    userId="")
        accounts = []
        for i in range(count):
            acc = Accounts(id=str(uuid.uuid4()),
                           name=i)
            accounts.append(acc)

        user.accounts = accounts

        session.add(user)
        session.commit()

    else:
        if len(user.accounts) < count:
            for i in range(len(user.accounts), len(user.accounts)+(count-len(user.accounts))):
                acc = Accounts(id=str(uuid.uuid4()),
                               name=i)
                user.accounts.append(acc)

            session.commit()


        session.close()

    requests.post('https://alpharescue.vercel.app/api/payments/createRafflebotSubscription',
                  json={'data': {'user':
                                     {'social_account':
                                          {'id': a,
                                           'expiresDate': '2023-08-11T19:36:21.137Z',
                                           'accountsQuantity': 50}
                                      }
                                 }})

    requests.post('http://127.0.0.1:1290/add-role', json={'discordId': a,
                                                          'role': 'Rescue Raffle Bot'})
    time.sleep(5)
    requests.post('http://127.0.0.1:1290/add-role', json={'discordId': a,
                                                          'role': 'Rescue Community Pass'})

def AddCommunityPassUser():

    a = '1021536387301916743'


    requests.post('https://alpharescue.vercel.app/api/payments/createCommunitySubscription',
                  json={'data': {'user':
                                     {'social_account':
                                          {'id': a,
                                           'expiresDate': '2023-09-06T19:36:21.137Z'}
                                      }
                                 }})

    # requests.post('http://127.0.0.1:1290/add-role', json={'discordId': a,
    #                                                       'role': 'Rescue Raffle Bot'})
    # time.sleep(5)
    requests.post('http://127.0.0.1:1290/add-role', json={'discordId': a,
                                                          'role': 'Rescue Community Pass'})



def DeleteUserWhoExpires():
    class User1(Base):
        __tablename__ = 'Session'

        id = Column(String, primary_key=True)
        userId = Column(String)
        sessionToken = Column(String)



    class User2(Base):
        __tablename__ = 'User'

        id = Column(String, primary_key=True)
        raffleBotUser = Column(Boolean)
        communityMember = Column(Boolean)

        RaffleBotSubscription = relationship('Refr', backref='user')
        CommunitySubscription = relationship('CommunitySubscription', backref='user')
        Account = relationship('Account1', backref='user')

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

    engine1 = create_engine(
        '')
    SessionA = sessionmaker(bind=engine1)
    sessionA = SessionA()

    # print(userId, sessionToken)
    users = sessionA.query(User2).all()
    for user in users:
        try:
            # print(user.Account[0].providerAccountId, user.raffleBotUser, user.communityMember)

            if user.raffleBotUser and user.RaffleBotSubscription[0].expires<datetime.utcnow():
                requests.post('http://127.0.0.1:1290/remove-role', json={'discordId': user.Account[0].providerAccountId,
                                                                      'role': 'Rescue Raffle Bot'})

            if user.communityMember and user.CommunitySubscription[0].expires<datetime.utcnow():
                requests.post('http://127.0.0.1:1290/remove-role', json={'discordId': user.Account[0].providerAccountId,
                                                                      'role': 'Rescue Community Pass'})

            # print(user.RaffleBotSubscription[0].expires, datetime.utcnow(), user.RaffleBotSubscription[0].expires>datetime.utcnow())
        except:
            pass
        # print('------------------------------------------------------------')

    sessionA.close()

def CheckUsersDB():
    engine1 = create_engine(
        '')
    SessionA = sessionmaker(bind=engine1)
    sessionA = SessionA()

    users = sessionA.query(User2).all()
    for user in users:
        try:
            if user.raffleBotUser:
                print(user.name, user.Account[0].providerAccountId, user.CommunitySubscription[0].expires)

        except:


            print(user.name, user.Account[0].providerAccountId, user.RaffleBotSubscription[0].expires)
            pass

    sessionA.close()
    # time.sleep(10)

def CheckRefBalance():
    from PaymentMachine import User2

    engine1 = create_engine(
        '')
    SessionA = sessionmaker(bind=engine1)
    sessionA = SessionA()

    user = sessionA.query(User2).filter_by(referralCode='byxir2023').first()

    print(user.referralRedirectPool)

    # sessionA.commit()
    sessionA.close()

# CheckRefBalance()
# ChangeRaffleData()
# CleanEvents()
# CleanMyRaffles()
# DeleteTwitters()
# DeleteRaffles()
# RafflesLen()
# Cleaner()
# FindRaffle()
# Users()
# CreateDB()
# UserData()
# UserDataChange()
# CheckRaffles()
# reqsToDsServer()
# EditRaffles()
# create_connection()
# DeleteAll()
# AddRaffleBotUser()
AddCommunityPassUser()
# DeleteUserWhoExpires()
# CheckUsersDB()
