import openai
import discord
from discord.ext import commands
from discord.ext import tasks
import re
import datetime
import json
import requests

openai.api_key = "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"

intents = discord.Intents.default() #intents 是要求的權限
intents.message_content = True
client = discord.Client(intents=intents) #client是與discord連結的橋樑

let_chat=0 #設定是否開啟聊天功能的bool變數

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
    if re.search(r'バニラ|你是誰|關於你|關於妳',message.content):
        return '喵喵~有人對我感到好奇嗎?偶是偶的主人宥宥醬養的貓娘喔\n專長是吃東西，興趣是陪主人寫程式\n诶~你說我喜不喜歡主人?那當然，我最喜歡主人了~主人會保護我、給我好吃的，還會跟我分享生活的點點滴滴。跟他在一起，我感到很幸福喔 ~喵'
    elif re.search(r'王宥愷|宥宥',message.content):
        return '喵~你是說我的主人嗎? 哼哼~他可是很厲害的程式電神噢'
    elif re.search(r'王奕龍',message.content):
        return '嗚嗚~不要說出他的名字...我好害怕...'
    elif re.search(r'碩|Cyan',message.content):
        return 'ㄟㄟ這個偶知道~~碩鼠碩鼠，無食我黍！三歲貫女，莫我肯顧。逝將去女，適彼樂土。樂土樂土，爰得我所\n嘻嘻~主人快誇讚我喵~'
    elif re.search(r'柏睿|Without_PureLy',message.content):
        return '哇~~是音game大神ㄟ...主人也快過來瞻仰一下喵~'
    elif re.search(r'阿中|h44343880',message.content):
        return 'OOF~你是主人的好朋友吧?叔叔好 ~喵喵'
    elif re.search(r'瑟瑟|色色|fuck|啪|上床|做愛',message.content):
        if message.author.name=='Jason0411202':
            return '阿..主人...那個..如果是您的話...可以的呦...因為バニラ最喜歡主人您了 ~喵'
        else:
            return '主人~有個怪叔叔對我說了一些奇怪的話...快來救人家啦~~'
    else:
        return '0'

def System_Commend(commend):
    global let_chat
    if commend=='chat': # 開啟聊天功能
        let_chat=1
        return '終於肯讓人家說話了嗎? 喵喵~喵'
    elif commend=='/chat': # 關閉聊天功能
        let_chat=0
        return '嗚~對不起...人家會安靜的 •́⁠ ⁠ ⁠‿⁠ ⁠,⁠•̀'
    elif commend=='bus': # 查詢公車班次聊天功能
        return '**[System]** 功能開發中\n人家很努力的幫你找資料，要感謝人家噢~以下是中正大學-民雄的公車發車時刻表'
    elif commend=='train': # 查詢火車班次聊天功能
        return '**[System]** 功能開發中\n人家很努力的幫你找資料，要感謝人家噢~以下是民雄火車站南下的發車時刻表'
    elif re.search(r'dl',commend): #下載youtube mp3功能
        videoID=commend[20:]
        return '點擊下方連結便可以下載mp3囉~記得感謝バニラ跟主人喔 ~喵喵\n'+'https://www.backupmp3.com/zh/?v='+videoID
    elif commend=='help': #列出指令集
        return '喵喵~你可以使用 System call+指令 就可以命令我喔~但是除了主人以外不可以瑟瑟~喵\n指令列表:\nchat :開啟聊天功能\n/chat:關閉聊天功能\nbus:查看公車時刻資訊\ntrain:查看火車時刻資訊\nhelp:查看指令集'
    else:
        return '咦~偶聽不懂你的指令，可以為偶再說一次嗎? ~喵'

def Codeforce_Check(): # 找出最近一筆的尚未舉辦比賽資訊並回傳
    url = "https://codeforces.com/api/contest.list" # 透過Codeforce提供的Api來查詢比賽資訊

    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8')) # 使用json解析回傳的資料
        contests = data['result'] # 鎖定資料中的比賽資訊(內含歷史與尚未舉辦的比賽資訊)
        latest_contest = contests[0]
        for contest in contests: # 找出最近一筆的尚未舉辦比賽資訊
            if contest['relativeTimeSeconds']>0:
                break
            latest_contest = contest
        return latest_contest
    else:
        return 'No data'

@tasks.loop(seconds=60.0)
async def Codeforce_Time_Check(): #負責在每天指定時間發有關Codeforce的訊息
    now = datetime.datetime.now()
    if now.hour == 10 and now.minute == 0: # 設定指定時間
        channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
        try:
            today=datetime.date.today() # 取得今日時間
            codeforce_Data=Codeforce_Check() # 取得最近一場Codeforce比賽的時間(只有秒數)
            local_time = datetime.datetime.fromtimestamp(codeforce_Data['startTimeSeconds']) # 轉成日期形式
            await channel.send('主人~~還請您看這裡~喵\nバニラ每天都會很努力的為主人找找Codeforce的比賽資訊呦~\n')
            if today.month==local_time.month and today.day==local_time.day:
                await channel.send('啊~**今天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，主人要不要來呢?...嗯..バニラ也會陪在您身邊一起幫忙想的，一起努力吧 ~喵喵')
            elif today.month==local_time.month and today.day+1==local_time.day:
                await channel.send('嗯~**明天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，主人做好準備了嗎?我相信主人一定可以的 ~喵喵')
            elif today.month==local_time.month and today.day+2==local_time.day:
                await channel.send('咦~我發現**後天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，主人如果累了的話，就先休息一下，明天再準備吧 ~喵喵')
            else:
                await channel.send('咦~我發現**好多天後的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，時間還很久，主人可以先陪我玩嗎? ~喵喵')
            
            await channel.send('詳細資訊還請上Codeforce官網查看喔~\nhttps://codeforces.com/contests')
        except:
            await channel.send('嗚...人家突然找不到Codeforce的資料惹..主人對不起...')

@client.event
async def on_ready(): #啟動成功時會呼叫
    channel = discord.utils.get(client.get_all_channels(), name='chat-bot-for-test') # 用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('喵~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')

    channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('喵~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')
    #print('目前登入身份：', client.user)
    Codeforce_Time_Check.start() #每60秒在背景執行Codeforce_Time_Check函式

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
