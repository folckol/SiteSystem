import datetime
import os
import threading

import requests
from discord.ext import tasks
from flask import Flask, request, jsonify
import discord

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table, Boolean, DateTime, and_, func, cast, \
    Float, or_
from Creating_DBs import *

app = Flask(__name__)

class User2(Base):
    __tablename__ = 'User'

    id = Column(String, primary_key=True)
    raffleBotUser = Column(Boolean)
    communityMember = Column(Boolean)

    CommunitySubscription = relationship('CommunitySubscription', back_populates='user', uselist=False)
    RaffleBotSubscription = relationship('RaffleBotSubscription', back_populates='user', uselist=False)

    Account = relationship('Account', back_populates='user', uselist=False)

class Account2(Base):
    __tablename__ = 'Account'

    id = Column(String, primary_key=True)
    providerAccountId = Column(String)

    User = relationship('User', back_populates='account')

class CommunitySubscription(Base):
    __tablename__ = 'CommunitySubscription'

    id = Column(String, primary_key=True, unique=True)

    expires = Column(DateTime)
    user = relationship('User', back_populates='CommunitySubscription')
    Bonuses = Column(String)

class RaffleBotSubscription(Base):
    __tablename__ = 'RaffleBotSubscription'

    id = Column(String, primary_key=True, unique=True)

    expires = Column(DateTime)
    rafflesLeft = Column(Integer)
    rafflesPerDay = Column(Integer)
    maxNumAccounts = Column(Integer)

    user = relationship('User', back_populates='RaffleBotSubscription')

# Discord bot token
TOKEN = ""

# Discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

def add_role_to_user(guild_id, user_id, role_name):
    guild = client.get_guild(guild_id)
    if guild is None:
        print(f"Сервер с ID {guild_id} не найден.")
        return

    target_user = guild.get_member(int(user_id))
    if target_user is None:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        print(f"Роль с названием '{role_name}' не найдена.")
        return

    if role in target_user.roles:
        print(f"У пользователя {target_user.name} уже есть роль '{role_name}'.")
    else:
        client.loop.create_task(target_user.add_roles(role))
        print(f"Роль '{role_name}' успешно выдана пользователю {target_user.name}.")

def remove_role_from_user(guild_id, user_id, role_name):

    guild_id = int(guild_id)
    user_id = int(user_id)


    guild = client.get_guild(guild_id)
    if guild is None:
        print(f"Сервер с ID {guild_id} не найден.")
        return

    target_user = guild.get_member(user_id)
    if target_user is None:
        print(f"Пользователь с ID {user_id} не найден.")
        return

    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        print(f"Роль с названием '{role_name}' не найдена.")
        return

    if role in target_user.roles:
        client.loop.create_task(target_user.remove_roles(role))
        print(f"Роль '{role_name}' успешно удалена у пользователя {target_user.name}.")
    else:
        print(f"У пользователя {target_user.name} нет роли '{role_name}'.")


# Flask webhook endpoint
@app.route('/add-role', methods=['POST'])
def add_role():

    try:
        data = request.get_json()
        add_role_to_user(1042832144386494474, data['discordId'], data['role'])

        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'error'})


@app.route('/remove-role', methods=['POST'])
def remove_role():

    try:
        data = request.get_json()
        remove_role_from_user(1042832144386494474, data['discordId'], data['role'])

        return jsonify({'status': 'success'})
    except:
        return jsonify({'status': 'error'})

@app.route('/check-role', methods=['POST'])
def check_role():
    data = request.get_json()
    user_id = data['user_id']
    role_name = data['role_name']
    guild_id = data['guild_id']

    guild = discord.utils.get(client.guilds, id=guild_id)
    member = guild.get_member(user_id)

    for i in role_name:
        role = discord.utils.get(guild.roles, name=i)
        if role in member.roles:
            print("User has role")
            return jsonify({'status': True})

    print("User does not have role")
    return jsonify({'status': False})


# Discord bot thread
class DiscordThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        client.run(TOKEN)


@tasks.loop(hours=1)  # Запуск задачи каждый час
async def check_roles():

    engine1 = create_engine(
        '')
    SessionA = sessionmaker(bind=engine1)
    sessionA = SessionA()

    users = sessionA.query(User2).all()


    for user in users:
        try:
            if user.RaffleBotSubscription.expires <= datetime.datetime.utcnow():

                requests.post('https://alpharescue.vercel.app/api/payments/invalidRafflebotSubscription',
                              json={
                                  'user': {
                                      'social_account':{
                                          'id': str(user.id)
                                      }
                                  }
                              })



                remove_role_from_user(1042832144386494474, user.Account.providerAccountId, 'Rescue Raffle Bot')
                break
        except:
            try:
                if user.CommunitySubscription.expires <= datetime.datetime.utcnow():

                    requests.post('https://alpharescue.vercel.app/api/payments/invalidCommunitySubscription',
                                  json={
                                      'user': {
                                          'social_account': {
                                              'id': str(user.id)
                                          }
                                      }
                                  })

                    remove_role_from_user(1042832144386494474, user.Account.providerAccountId, 'Rescue Community Pass')
                    break

            except:
                pass

    # sessionA.commit()
    sessionA.close()


@check_roles.before_loop
async def before_check_roles():
    await client.wait_until_ready()


# Start Flask server
if __name__ == '__main__':
    discord_thread = DiscordThread()
    discord_thread.start()
    # app.run(port=os.environ.get('PORT', 1290))
    from waitress import serve

    serve(app, port=1290)


