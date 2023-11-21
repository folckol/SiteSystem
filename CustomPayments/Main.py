import os
import random
import threading
import time
from threading import Timer

import requests
from flask import Flask, request, jsonify
from eth_keys import keys
from tronapi import Tron
from qrcode import QRCode
import sqlite3
import json
import time
from web3 import Web3
from eth_utils import to_checksum_address

ERC20_ABI = json.loads('[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')
TRONGRID_API = 'https://api.trongrid.io/v1'
USDT_CONTRACT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'  # USDT контракт на сети Tron
CHECK_INTERVAL = 60  # Время между проверками в секундах (60 секунд)
TIMEOUT = 10 * 60  # Время ожидания в секундах (10 минут)

app = Flask(__name__)

# Configure Tron
tron = Tron()

# Configure Binance Smart Chain
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

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
            is_busy INTEGER DEFAULT 0
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

def mark_wallet_busy(conn, wallet, busy=True):
    cur = conn.cursor()
    cur.execute("""
        UPDATE wallets
        SET is_busy = ?
        WHERE address = ?
    """, (int(busy), wallet))
    conn.commit()
    conn.close()

def get_wallet(conn, network):
    cur = conn.cursor()
    cur.execute("""SELECT address FROM wallets WHERE is_busy=0 AND network=:network""", {'network': network})
    wallets = cur.fetchall()

    if network == 'BSC':
        wallet = random.choice(wallets)[0]
        cur.execute(f"""SELECT private_key FROM wallets WHERE address=?""",[wallet])
        private = cur.fetchone()[0]
        conn.close()
        return wallet, private
    else:
        wallet = random.choice(wallets)[0]
        cur.execute(f"""
                SELECT private_key FROM wallets WHERE address = ?""", [wallet])
        private = cur.fetchone()[0]
        conn.close()
        return wallet, private





def generate_wallets(network, count=100):
    wallets = []
    if network == 'BSC':
        for _ in range(count):
            acct = w3.eth.account.create()
            wallets.append({
                'network': network,
                'address': acct.address,
                'private_key': acct.privateKey.hex()
            })
    elif network == 'TRON':

        data = []
        with open('walletsTron.txt', 'r') as file:
            for i in file:
                data.append(i.strip('\n'))

        for _ in range(count):
            acct = data[_]
            wallets.append({
                'network': network,
                'address': acct.split('	')[0],
                'private_key': acct.split('	')[1]
            })

    return wallets

def all_DB():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(f"""SELECT * FROM wallets""")
    for i in cur.fetchall():
        print(i)

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
    return qr.make_image(fill_color="black", back_color="white")

def wait_for_balances_BSC(
    rpc_url: str,
    wallet_address: str,
    user_id: str,
    token_addresses: dict,
    expected_amounts: dict,
    decimals: int = 18,
    timeout: int = 600,

):
    w3 = Web3(Web3.HTTPProvider(rpc_url))
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
        all_balances_reached = True

        for symbol, contract in token_contracts.items():

            balance = contract.functions.balanceOf(wallet_address).call()
            # print(symbol, balance, target_amounts[symbol])

            if balance < target_amounts[symbol]:

                all_balances_reached = False
                break

        if all_balances_reached:
            # print("Успех! Балансы кошелька достигли целей.")
            requests.post('')
            mark_wallet_busy(create_connection(), wallet_address, busy=False)
            return

    # print("Таймаут истек. Балансы кошелька не достигли целей.")
    mark_wallet_busy(create_connection(), wallet_address, busy=False)
    requests.post('')

def get_token_balance(address, contract_address):

    url = f'{TRONGRID_API}/accounts/{address}/assets'
    response = requests.get(url)
    data = response.json()

    for token in data.get('data', []):
        if token['key'] == contract_address:
            return int(token['value']) / 10 ** 6  # Количество USDT может быть с 6 десятичными знаками

    return 0

def wait_for_balances_TRON(wallet, private, user_id, amount, timeout=600):
    start_time = time.time()
    start_balance = get_token_balance(wallet, USDT_CONTRACT)

    while time.time() - start_time < TIMEOUT:
        balance = get_token_balance(wallet, USDT_CONTRACT)
        # print(f'Текущий баланс USDT: {balance:.6f}')
        if balance-start_balance > amount:
            # print(f'Кошелек пополнен на {balance:.6f} USDT!')

            mark_wallet_busy(create_connection(), wallet, busy=False)
            requests.post('')

            return

        time.sleep(CHECK_INTERVAL)

    mark_wallet_busy(create_connection(), wallet, busy=False)
    requests.post('')


@app.route('/replenish_balance', methods=['POST'])
def replenish_balance():
    if request.method == 'POST':
        user_id = request.json['user_id']
        amount = request.json['amount']
        coin = request.json['coin']
        network = request.json['network']

        wallet, private = get_wallet(create_connection(), network)
        print(wallet, private)
        mark_wallet_busy(create_connection(), wallet)
        qr_code_filename = generate_qr_code(wallet)

        if network == 'BSC' and coin == 'USDT':
            t = threading.Thread(target=wait_for_balances_BSC,
                                 args=("https://bsc-dataseed.binance.org/", wallet, user_id, {"USDT": "0x55d398326f99059ff775485246999027b3197955"},{'USDT': amount}))
            t.start()
        elif network == 'BSC' and coin == 'BUSD':
            t = threading.Thread(target=wait_for_balances_BSC,
                                 args=("https://bsc-dataseed.binance.org/", wallet, user_id, {"BUSD": "0xe9e7cea3dedca5984780bafc599bd69add087d56"},{'BUSD': amount}))
            t.start()
        elif network == 'TRON' and coin == 'USDT':
            t = threading.Thread(target=wait_for_balances_TRON,
                                 args=(wallet, private, user_id, amount))
            t.start()


        response = {
            "wallet": wallet,
            "qr_code": '1'
        }
        return jsonify(response)

if __name__ == '__main__':

    # firstTime()
    all_DB()
    # print('Кошельки созданы')

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5390)), debug=False)
