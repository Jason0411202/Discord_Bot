import openai
import discord
from discord.ext import commands
import re

openai.api_key = "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"

intents = discord.Intents.default() #intents 是要求的權限
intents.message_content = True
client = discord.Client(intents=intents) #client是與discord連結的橋樑

def ChatGPT_Get_Context(question):
    response = openai.Completion.create(
    model="text-davinci-003",
    prompt="\nHuman: "+question+"\nAI:",
    temperature=0.9,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0.0,
    presence_penalty=0.6,
    stop=[" Human:", " AI:"]
    )

    return response["choices"][0]["text"]

@client.event
async def on_ready(): #啟動成功時會呼叫
    print('目前登入身份：', client.user)

@client.event
async def on_message(message): #有新的訊息便會呼叫
    if message.author == client.user: #若新訊息是bot本身則忽略
        return
    elif message.content[0]!='!': #新訊息前面沒有!則忽略
        return
    elif re.search(r'王奕龍',message.content):
        await message.channel.send('拜託~我不想聽到它的名字')
    elif re.search(r'王宥愷',message.content):
        await message.channel.send('在我的心中，他是程式電神')
    else:
        response=ChatGPT_Get_Context(message.content)
        await message.channel.send(response)
        print(message.content[1:])

client.run('MTA3MDQwMzQ0NzQ2NTE4OTM5Ng.GWMPbq.ibq0tZQGGjTojvXZUqIa7fDpFC3g5mdbp8tNng')
