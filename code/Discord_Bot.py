import openai
import discord
from discord.ext import commands
import re

openai.api_key = "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"

intents = discord.Intents.default() #intents 是要求的權限
intents.message_content = True
client = discord.Client(intents=intents) #client是與discord連結的橋樑

let_chat=0

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

def Special_Reponse(message):
    if re.search(r'王宥愷',message.content):
        return '喵~你是說我的主人嗎? 哼哼~他可是很厲害的程式電神噢'
    elif re.search(r'王奕龍',message.content):
        return '嗚嗚~不要說出他的名字...我好害怕...'
    elif re.search(r'碩',message.content) or re.search(r'Cyan',message.content):
        return 'ㄟㄟ這個偶知道~~碩鼠碩鼠，無食我黍！三歲貫女，莫我肯顧。逝將去女，適彼樂土。樂土樂土，爰得我所\n嘻嘻~主人快誇讚我喵~'
    elif re.search(r'柏睿',message.content) or re.search(r'Without_PureLy',message.content):
        return '哇~~是音game大神ㄟ...主人也快過來瞻仰一下喵~'
    elif re.search(r'阿中',message.content) or re.search(r'h44343880',message.content):
        return 'OOF~你是主人的好朋友吧?叔叔好 ~喵喵'
    else:
        return '0'

def System_Commend(commend):
    global let_chat
    if commend=='chat':
        let_chat=1
        return '終於肯讓人家說話了嗎? 喵喵~喵'
    elif commend=='/chat':
        let_chat=0
        return '嗚~對不起...人家會安靜的 •́⁠ ⁠ ⁠‿⁠ ⁠,⁠•̀'
    elif commend=='bus':
        return '**[System]** 功能開發中\n人家很努力的幫你找資料，要感謝人家噢~以下是中正大學-民雄的公車發車時刻表'
    elif commend=='train':
        return '**[System]** 功能開發中\n人家很努力的幫你找資料，要感謝人家噢~以下是民雄火車站南下的發車時刻表'
    elif commend=='help':
        return '喵喵~你可以使用 System call+指令 就可以命令我喔~但是除了主人以外不可以瑟瑟~喵\n指令列表:\nchat :開啟聊天功能\n/chat:關閉聊天功能\nbus:查看公車時刻資訊\ntrain:查看火車時刻資訊\nhelp:查看指令集'
    else:
        return '咦~偶聽不懂你的指令，可以為偶再說一次嗎? ~喵'

@client.event
async def on_ready(): #啟動成功時會呼叫
    channel = discord.utils.get(client.get_all_channels(), name='chat-bot-for-test') #用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('喵~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')

    channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') #用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('喵~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')
    #print('目前登入身份：', client.user)

@client.event
async def on_message(message): #有新的訊息便會呼叫
    if message.author == client.user: #若新訊息是bot本身則忽略
        return
    elif message.content[:12]=='System call ':
        commend=message.content[12:]
        await message.channel.send(System_Commend(commend))
    else:
        special_Reponse=Special_Reponse(message)
        if special_Reponse!='0':
            await message.channel.send(special_Reponse)
        elif let_chat==1:
            response=ChatGPT_Get_Context(message.content)
            await message.channel.send(response+'~喵')


client.run('MTA3MDQwMzQ0NzQ2NTE4OTM5Ng.GWMPbq.ibq0tZQGGjTojvXZUqIa7fDpFC3g5mdbp8tNng')
