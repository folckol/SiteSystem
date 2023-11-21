import os
import threading
import re

import requests
from flask import Flask, request, jsonify
import discord

app = Flask(__name__)

# Discord bot token
TOKEN = ""

# Discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

users = []


def extract_links(text):
    # удаляем все символы переноса строки
    text = text.replace("\\n", " ")

    # регулярное выражение для поиска ссылок
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    # поиск всех совпадений в тексте
    links = re.findall(pattern, text)

    # возвращаем список всех найденных ссылок
    return links

@client.event
async def on_message(message):

    links = []

    if message.author.bot:  # Проверяем, является ли автор сообщения ботом
        if message.embeds:  # Проверяем, есть ли в сообщении Embeds
            for embed in message.embeds:
                links_ = extract_links(str(embed.to_dict()))  # Выводим Embeds
                for i in links_:
                    links.append(i)
        else:
            links = extract_links(message.content)  # Выводим текст сообщения

    elif message.author.id in users:
        links = extract_links(message.content)

    new_links = []
    for i in links:
        s = i
        if i[-1] == '/':
            s = i[:-1]

        new_links.append(s.split(')')[0])

    print(new_links)

    for i in new_links:

        premints = []
        alphabots = []
        superfulls = []

        if 'https://www.premint.xyz' in i:
            premints.append(i.split(')')[0])
        elif 'https://www.superful.xyz' in i:
            superfulls.append(i.split(')')[0])
        elif 'https://www.alphabot.app' in i:
            if 'https://www.alphabot.app/dashboard' not in i and 'https://www.alphabot.app/calendar' not in i:
                alphabots.append(i.split(')')[0])

        if alphabots != []:
            payload = {'links': alphabots}
            requests.post('http://127.0.0.1:27000/data/alphabot', json=payload)
        elif premints != []:
            payload = {'links': premints}
            requests.post('http://127.0.0.1:27000/data/premint', json=payload)
        elif superfulls != []:
            payload = {'links': superfulls}
            requests.post('http://127.0.0.1:27000/data/superfull', json=payload)





if __name__ == '__main__':
    client.run(TOKEN)

