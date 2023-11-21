import json

import gspread
import requests
from web3 import Web3
import time

ERC20_ABI = json.loads('[{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"constant":true,"inputs":[],"name":"_decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"_symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"burn","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"renounceOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]')


# Подключение к провайдеру BSC (нужно указать свой провайдер)
w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))

# Адреса кошельков для проверки (можно добавить/удалить адреса)


# Адрес монеты, баланс которой нужно проверить (нужно указать свой адрес)
token_address_USDT = '0x55d398326f99059ff775485246999027b3197955'
token_address_BUSD = '0xe9e7cea3dedca5984780bafc599bd69add087d56'

# Функция для проверки баланса в монете
def check_balance_BSC(wallet_address):
    balance = w3.eth.get_balance(wallet_address)
    # print(f'Баланс кошелька {wallet_address}: {balance} wei')

    # Если интересует конкретная монета, можно использовать функцию contract.call()

    q = 0
    for i in [token_address_USDT, token_address_BUSD]:
        contract = w3.eth.contract(address=w3.to_checksum_address(i), abi=ERC20_ABI)
        token_balance = contract.functions.balanceOf(wallet_address).call()

        q+=token_balance/(10 ** 18)

        # print(f'Баланс монеты в кошельке {wallet_address}: {token_balance/(10 ** 18)}')

    return q


def CheckBalanceTRON(wallet):
    url = f"https://apilist.tronscan.org/api/account?address={wallet}&includeToken=true"

    token_balances = requests.get(url).json()['tokens']
    initial_balance = 0
    for tb in token_balances:
        if tb['tokenAbbr'] == 'USDT':
            initial_balance = int(tb['balance']) / 1000000
            break

    return initial_balance

# Бесконечный цикл проверки каждую минуту
wallet_addresses_BSC = []
wallet_addresses_TRON = []

def google_sheets():


    gs = gspread.service_account(filename='')
    ah = gs.open_by_key('')

    worksheet = ah.worksheet('Кошельки платежки')

    data = worksheet.get_all_values()
    # for i in data[1:]:
    #     print(i)

    return data[1:]

def updateGT(name, balance):
    gs = gspread.service_account(filename='')
    ah = gs.open_by_key('')

    worksheet = ah.worksheet('Кошельки платежки')

    row = worksheet.find(name, in_column=1).row

    worksheet.update_cell(row, 5, balance)

while True:
    data = google_sheets()

    for i in data:

        try:
            if i[1] == 'BSC':
                balance = check_balance_BSC(i[2])
            else:
                balance = CheckBalanceTRON(i[2])

            print(balance)

            updateGT(i[0], int(balance))

            time.sleep(1.5)
        except:
            print('Error')
            pass

    time.sleep(2)



