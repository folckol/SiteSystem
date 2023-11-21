import requests

payload = {'user_id': '2393',
           'amount': 2,
           'coin': 'USDT',
           'network': 'TRON'
           }

r = requests.post('http://127.0.0.1:5390/replenish_balance', json=payload)
print(r.text)
