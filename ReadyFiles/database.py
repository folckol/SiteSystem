import csv
import sqlite3 as sql


def create_db():
    con = sql.connect('database.db')
    with con:
        try:
            con.execute("""
                CREATE TABLE accounts (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    address TEXT,
                    private_key TEXT,
                    auth_token TEXT,
                    csrf TEXT,
                    discord_token TEXT,
                    proxy TEXT
                );
            """)

            con.execute("""
                CREATE TABLE my_raffles (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    accs_count INTEGER,
                    hold_sum INTEGER,
                    results TEXT
                    raffle_id INTEGER
                );
            """)
        except:
            pass


def create_raffle_table(name):
    con = sql.connect('database.db')
    with con:
        con.execute(f"""
            CREATE TABLE {name} (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                premint_login INTEGER,
                twitter_connect INTEGER,
                discord_connect INTEGER,
                twitter_follow INTEGER,
                twitter_like_retweet INTEGER,
                premint_registered INTEGER
            );
        """)
        sql = 'INSERT INTO USER (id, name, age) values(?, ?, ?)'
        data = [
            (1, 'Alice', 21),
            (2, 'Bob', 22),
            (3, 'Chris', 23)
        ]
        con.executemany(sql, data)

def add_account(data):
    con = sql.connect('database.db')
    with con:
        con.execute(f"""
            INSERT INTO accounts (address, private_key, auth_token, csrf, discord_token, proxy)
            VALUES ('{data['address']}', '{data['private_key']}', '{data['auth_token']}', '{data['csrf']}', '{data['discord_token']}', '{data['proxy']}')
            """)


def add_raffle(data):
    con = sql.connect('database.db')
    with con:
        con.execute(f"""
            INSERT INTO accounts (name, accs_count, hold_sum, results)
            VALUES ({data['name']}, {data['accs_count']}, {data['hold_sum']}, {data['results']})
            """)


def get_account(id):
    con = sql.connect('database.db')
    with con:
        data = con.execute(f"SELECT * FROM accounts WHERE id={id}")
        for row in data:
            result = {'address': row[1],
                    'private_key': row[2],
                    'auth_token': row[3],
                    'csrf': row[4],
                    'discord_token': row[5],
                    'proxy': row[6]}
    return result


def export_accounts():
    conn = sql.connect('database.db')
    cursor = conn.cursor()
    data = cursor.execute('SELECT * FROM accounts')
    with open('1k/accounts.csv', 'w+') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'address', 'private_key', 'auth_token', 'csrf', 'discord_token', 'proxy'])
            writer.writerows(data)