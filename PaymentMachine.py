import datetime
import hashlib
import os
import random
import threading
import time
import traceback
import uuid
from threading import Timer

import requests
from flask import Flask, request, jsonify, send_file
from eth_keys import keys
from sqlalchemy import Boolean, Float
from sqlalchemy.orm import sessionmaker
from tronpy import Tron
from qrcode import QRCode
import sqlite3
import json
import time
from web3 import Web3
from eth_utils import to_checksum_address
from Creating_DBs import *

ERC20_ABI = json.loads('[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')


app = Flask(__name__)

# Configure Tron
tron = Tron()

# Configure Binance Smart Chain
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

class User2(Base):
    __tablename__ = 'User'

    id = Column(String, primary_key=True)
    name = Column(String)
    raffleBotUser = Column(Boolean)
    communityMember = Column(Boolean)

    referralCode = Column(String)
    referralRedirectPool = Column(Float)
    referralPercentage = Column(Float)

    RaffleBotSubscription = relationship('Refr', backref='user')
    CommunitySubscription = relationship('CommunitySubscription', backref='user')
    Account = relationship('Account1', backref='user')




# Database setup
def create_connection():
    conn = sqlite3.connect('wallets.db', check_same_thread=False)
    return conn

def init_database(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY,
            network TEXT NOT NULL,
            address TEXT NOT NULL,
            private_key TEXT NOT NULL,
            is_busy INTEGER DEFAULT 0,
            discordId INTEGER,
            expiresTime STRING
        )
    """)
    conn.commit()
    conn.close()

def insert_wallet(conn, wallet):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO wallets (network, address, private_key)
        VALUES (?, ?, ?)
    """, (wallet['network'], wallet['address'], wallet['private_key']))
    conn.commit()
    conn.close()

def mark_wallet_busy(conn, wallet, discordId, busy=True):

    if busy == True:
        cur = conn.cursor()
        cur.execute("""
            UPDATE wallets
            SET is_busy = ?,
            discordId = ?,
            expiresTime = ?
            WHERE address = ?
        """, (int(busy), discordId, str((datetime.datetime.utcnow() + datetime.timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")), wallet))
        conn.commit()
        conn.close()
    else:
        cur = conn.cursor()
        cur.execute("""
                    UPDATE wallets
                    SET is_busy = ?,
                    discordId = ?
                    WHERE address = ?
                """, (int(busy), '', wallet))
        conn.commit()
        conn.close()

def mark_wallet_busy_2(conn, discordId, busy=False):

    cur = conn.cursor()
    cur.execute("""
                UPDATE wallets
                SET is_busy = ?,
                discordId = ?,
                expiresTime = ?
                WHERE discordId = ?
            """, (int(busy), None, None, discordId))
    conn.commit()
    conn.close()

def CheckStatus(conn, wallet):
    cur = conn.cursor()
    cur.execute("""
        SELECT is_busy FROM wallets
        WHERE address = ?
    """, (wallet,))
    status = cur.fetchone()
    conn.close()

    return status

def CheckStatus_(conn, discordId):
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM wallets
        WHERE discordId = ?
    """, (discordId,))
    status = cur.fetchone()
    conn.close()

    return status

def get_wallet(conn, network):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT address FROM wallets WHERE is_busy = 0 AND network = '{network}'
    """)
    wallets = cur.fetchall()

    if network == 'BSC':
        wallet = random.choice(wallets)
        print(wallet)
        cur.execute(f"""
                        SELECT private_key FROM wallets WHERE is_busy = 0 AND address = '{wallet[0]}'
                    """)
        private = cur.fetchone()[0]
        conn.close()
        return wallet[0], private
    else:
        wallet = random.choice(wallets)
        cur.execute(f"""
                SELECT private_key FROM wallets WHERE is_busy = 0 AND address = '{wallet[0]}'
            """)
        private = cur.fetchone()[0]
        conn.close()
        return wallet[0], private





def generate_wallets(network, count=200):
    wallets = []
    if network == 'BSC':
        for _ in range(count):
            acct = w3.eth.account.create()
            wallets.append({
                'network': network,
                'address': acct.address,
                'private_key': acct._private_key.hex()
            })
    elif network == 'TRON':
        for _ in range(count):
            wallet = tron.generate_address()
            # print("Wallet address:  %s" % wallet['base58check_address'])
            # print("Private Key:  %s" % wallet['private_key'])

            wallets.append({
                'network': network,
                'address': str(wallet['base58check_address']),
                'private_key': str(wallet['private_key'])
            })
    print(wallets)
    return wallets

def firstTime():

    init_database(create_connection())

    wallets_bsc = generate_wallets('BSC')
    wallets_tron = generate_wallets('TRON')
    for wallet in wallets_bsc + wallets_tron:
        insert_wallet(create_connection(), wallet)

def generate_qr_code(address):
    qr = QRCode()
    qr.add_data(address)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(f'FILEs/{address}.jpg')
    return f'FILEs/{address}.jpg'

def wait_for_balances_BSC(
    rpc_url: str,
    wallet_address: str,
    discordId: int,
    accountsQuantity: int,
    expiresDate: str,
    subscriptionType: str,
    token_addresses: dict,
    expected_amounts: dict,
    referral_data = None,
    decimals: int = 18,
    timeout: int = 600,

):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    address_ = wallet_address
    wallet_address = to_checksum_address(wallet_address)
    token_contracts = {
        symbol: w3.eth.contract(address=to_checksum_address(address), abi=ERC20_ABI)
        for symbol, address in token_addresses.items()
    }

    start_amounts = {
        symbol: contract.functions.balanceOf(wallet_address).call() for symbol, contract in token_contracts.items()
    }

    target_amounts = {
        symbol: int(amount * (10 ** decimals))+start_amounts[symbol] for symbol, amount in expected_amounts.items()
    }

    start_time = time.time()
    while time.time() - start_time < timeout:

        time.sleep(1)

        if CheckStatus(create_connection(), address_)[0] == 0:
            break

        all_balances_reached = True

        for symbol, contract in token_contracts.items():

            balance = contract.functions.balanceOf(wallet_address).call()
            # print(symbol, balance, target_amounts[symbol])

            if balance < target_amounts[symbol]:

                all_balances_reached = False
                break

        if all_balances_reached:
            print(f"Успех! Баланс кошелька достиг целей. ({wallet_address})")

            if referral_data:
                try:
                    engine1 = create_engine(
                        '')
                    SessionA = sessionmaker(bind=engine1)
                    sessionA = SessionA()

                    user = sessionA.query(User2).filter_by(referralCode=referral_data[0]).first()

                    try:
                        amount = user.referralPercentage * expected_amounts['USDT']
                    except:
                        try:
                            amount = user.referralPercentage * expected_amounts['BUSD']
                        except:
                            pass

                    user.referralRedirectPool += amount

                    sessionA.commit()
                    sessionA.close()
                except:

                    traceback.print_exc()

                    with open('LOG.txt', 'a+') as file:
                        file.write(
                            f"{datetime.datetime.utcnow()} - Error with give referral money to user with code {referral_data[0]}\n")

            if subscriptionType == 'Rafflebot':
                requests.post('https://alpharescue.vercel.app/api/payments/createRafflebotSubscription',
                              json={'data':{'user':
                                         {'social_account':
                                              {'id': str(discordId),
                                               'expiresDate': str(expiresDate),
                                               'accountsQuantity': accountsQuantity}
                                          }
                                     }})

                requests.post('http://127.0.0.1:1290/add-role', json={'discordId': discordId,
                                                                      'role': 'Rescue Raffle Bot'})

                time.sleep(5)

                requests.post('http://127.0.0.1:1290/add-role', json={'discordId': discordId,
                                                                      'role': 'Rescue Community Pass'})

                Session = sessionmaker(bind=engine)
                session = Session()

                user = session.query(User).filter(User.discord_id == str(discordId)).first()
                if user == None:

                    user = User(id=str(uuid.uuid4()),
                                discord_id=str(discordId),
                                userId="")
                    accounts = []
                    for i in range(accountsQuantity):
                        acc = Accounts(id=str(uuid.uuid4()),
                                       name=i)
                        accounts.append(acc)

                    user.accounts = accounts

                    session.add(user)
                    session.commit()
                session.close()

            else:

                if referral_data:
                    requests.post('https://alpharescue.vercel.app/api/payments/createCommunityWithReferral',
                                  json={'data': {'user':
                                                     {'social_account':
                                                          {'id': str(discordId),
                                                           'communityExpiresDate': str(expiresDate),
                                                           'rafflebotExpiresDate': str((datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
                                                           'accountsQuantity': 50}
                                                      }
                                                 }})
                    time.sleep(2)


                requests.post('https://alpharescue.vercel.app/api/payments/createCommunitySubscription',
                              json={'data':{'user':
                                         {'social_account':
                                              {'id': str(discordId),
                                               'expiresDate': str(expiresDate),
                                               'accountsQuantity': accountsQuantity}
                                          }
                                     }})

            requests.post('http://127.0.0.1:1290/add-role', json={'discordId': discordId,
                                                                  'role': 'Rescue Community Pass'})

            mark_wallet_busy(create_connection(), wallet_address, discordId, busy=0)

            return

    print(f"Таймаут истек. Баланс кошелька не достиг целей. ({wallet_address})")
    mark_wallet_busy(create_connection(), wallet_address, discordId, busy=0)


def wait_for_balances_TRON(wallet, private, discordId, accountsQuantity, expiresDate, subscriptionType, amount, referral_data, timeout=600):
    url = f"https://apilist.tronscan.org/api/account?address={wallet}&includeToken=true"

    token_balances = requests.get(url).json()['tokens']
    initial_balance = 0
    for tb in token_balances:
        if tb['tokenAbbr'] == 'USDT':
            initial_balance = int(tb['balance']) / 1000000
            break

    start_time = time.time()
    print('Ожидаю кэш')
    while time.time() - start_time < timeout:

        time.sleep(1)

        if CheckStatus(create_connection(), wallet)[0] == 0:
            break

        token_balances = requests.get(url).json()['tokens']
        current_balance = 0
        for tb in token_balances:
            if tb['tokenAbbr'] == 'USDT':
                current_balance = int(tb['balance']) / 1000000
                break

        if (current_balance-initial_balance) >= amount:
            deposit_amount = (current_balance - initial_balance)
            mark_wallet_busy(create_connection(), wallet, discordId, busy=0)
            print('Бабки получены')

            if referral_data:
                try:
                    engine1 = create_engine(
                        '')
                    SessionA = sessionmaker(bind=engine1)
                    sessionA = SessionA()

                    user = sessionA.query(User2).filter_by(referralCode=referral_data[0]).first()

                    amount = user.referralPercentage * amount

                    user.referralRedirectPool += amount

                    sessionA.commit()
                    sessionA.close()

                except:
                    with open('LOG.txt', 'a+') as file:
                        file.write(f"{datetime.datetime.utcnow()} - Error with give referral money to user with code {referral_data[0]}\n")

            if subscriptionType == 'Rafflebot':
                requests.post('https://alpharescue.vercel.app/api/payments/createRafflebotSubscription',
                              json={'data':{'user':
                                         {'social_account':
                                              {'id': str(discordId),
                                               'expiresDate': str(expiresDate),
                                               'accountsQuantity': accountsQuantity}
                                          }
                                     }})

                Session = sessionmaker(bind=engine)
                session = Session()

                user = session.query(User).filter(User.discord_id == str(discordId)).first()
                if user == None:

                    user = User(id=str(uuid.uuid4()),
                                discord_id=str(discordId),
                                userId="")
                    accounts = []
                    for i in range(accountsQuantity):
                        acc = Accounts(id=str(uuid.uuid4()),
                                       name=i)
                        accounts.append(acc)

                    user.accounts = accounts

                    session.add(user)
                    session.commit()
                session.close()

                requests.post('http://127.0.0.1:1290/add-role', json={'discordId': discordId,
                                                                      'role': 'Rescue Raffle Bot'})
                time.sleep(5)

                requests.post('http://127.0.0.1:1290/add-role', json={'discordId': discordId,
                                                                      'role': 'Rescue Community Pass'})

            else:

                if referral_data:
                    requests.post('https://alpharescue.vercel.app/api/payments/createCommunityWithReferral',
                                  json={'data': {'user':
                                                     {'social_account':
                                                          {'id': str(discordId),
                                                           'communityExpiresDate': str(expiresDate),
                                                           'rafflebotExpiresDate': str((datetime.datetime.utcnow() + datetime.timedelta(weeks=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")),
                                                           'accountsQuantity': 50}
                                                      }
                                                 }})
                    time.sleep(2)

                requests.post('https://alpharescue.vercel.app/api/payments/createCommunitySubscription',
                              json={'data':{'user':
                                         {'social_account':
                                              {'id': str(discordId),
                                               'expiresDate': str(expiresDate)}
                                          }
                                     }})

                requests.post('http://127.0.0.1:1290/add-role', json={'discordId': discordId,
                                                                      'role': 'Rescue Community Pass'})

            return


    print('Бабки не были получены за 10 минут')
    mark_wallet_busy(create_connection(), wallet, discordId, busy=0)


def text_to_sha256(text):
    sha256_hash = hashlib.sha256(text.encode()).hexdigest()
    return str(sha256_hash)

if __name__ == '__main__':
    print(text_to_sha256(f""))

