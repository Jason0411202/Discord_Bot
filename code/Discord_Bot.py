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
schedule_List=list() #記事資料庫

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

def System_Commend(message,commend):
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
    elif re.search(r'dl ',commend): # 下載youtube mp3功能
        videoID=commend[20:]
        return '點擊下方連結便可以下載mp3囉~記得感謝バニラ跟主人喔 ~喵喵\n'+'https://www.backupmp3.com/zh/?v='+videoID
    elif re.search(r'rem ',commend): # 記事功能
        return Schedule_Edit(message,commend)
    elif commend=='help': #列出指令集
        return '喵喵~你可以使用 System call+指令 就可以命令我喔~但是除了主人以外不可以瑟瑟~喵\n指令列表:\nchat :開啟聊天功能\n/chat :關閉聊天功能\nbus :查看公車時刻資訊\ntrain :查看火車時刻資訊\ndl YT影片連結 :下載youtube mp3\nrem add 年 月 日 時 分 備註(一定要寫) :新增記事\nrem ls :查看自己的記事\nrem del 編號 :刪除指定編號的記事\nhelp:查看指令集'
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

def Codeforce_Time_Check(): #負責在每天指定時間發有關Codeforce的訊息
    return_Message=''
    try:
        today=datetime.date.today() # 取得今日時間
        codeforce_Data=Codeforce_Check() # 取得最近一場Codeforce比賽的時間(只有秒數)
        local_time = datetime.datetime.fromtimestamp(codeforce_Data['startTimeSeconds']) # 轉成日期形式
        return_Message=return_Message+'主人~~還請您看這裡~喵\nバニラ每天都會很努力的為主人找找Codeforce的比賽資訊呦~\n'
        if today.month==local_time.month and today.day==local_time.day:
            return_Message=return_Message+'啊~**今天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，主人要不要來呢?...嗯..バニラ也會陪在您身邊一起幫忙想的，一起努力吧 ~喵喵\n'
        elif today.month==local_time.month and today.day+1==local_time.day:
            return_Message=return_Message+'嗯~**明天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，主人做好準備了嗎?我相信主人一定可以的 ~喵喵\n'
        elif today.month==local_time.month and today.day+2==local_time.day:
            return_Message=return_Message+'咦~我發現**後天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，主人如果累了的話，就先休息一下，明天再準備吧 ~喵喵\n'
        else:
            return_Message=return_Message+'咦~我發現**好多天後的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶，時間還很久，主人可以先陪我玩嗎? ~喵喵\n'
        
        return_Message=return_Message+'詳細資訊還請上Codeforce官網查看喔~\nhttps://codeforces.com/contests'
    except:
        return_Message=return_Message+'嗚...人家突然找不到Codeforce的資料惹..主人對不起...'
    
    return return_Message

def Is_Past_Time(input_Time):
    now = datetime.datetime.now() #取得現在時間
    if input_Time['year'] < now.year:
        return True
    elif input_Time['year'] > now.year:
        return False
    elif input_Time['month'] < now.month:
        return True
    elif input_Time['month'] > now.month:
        return False
    elif input_Time['date'] < now.day:
        return True
    elif input_Time['date'] > now.day:
        return False
    elif input_Time['hour'] < now.hour:
        return True
    elif input_Time['hour'] > now.hour:
        return False
    elif input_Time['minute'] <= now.minute:
        return True
    elif input_Time['minute'] > now.minute:
        return False

def IsValidDate(year, month, day):
    try:
        datetime.date(year, month, day)
        return True
    except:
        return False

def Schedule_Edit(message,commend):
    return_Message=''
    input_Info=list(commend.split())

    if len(input_Info)<2: #輸入不包含指令
        return_Message=return_Message+'喵喵~您是不是忘記輸入指令了呢...偶看不懂QQ'
    elif input_Info[1]!='add' and input_Info[1]!='ls' and input_Info[1]!='del': # 輸入的指令錯誤
        return_Message=return_Message+'喵喵~您輸入的指令為 **'+input_Info[1]+'** ，記得只能透過**add**,**ls**,**del**其中一個指令來存取記事資料庫喔~'
    else: # 通過初步格式檢測
        if input_Info[1]=='ls': # 輸入指令為ls
            if len(input_Info)>2:
                return_Message=return_Message+'**ls**的指令後面不用再加東西了喔~不過好險我還是知道您的意思 ~喵\n'

            counter=1
            for i in schedule_List: #列出所有已加入的記事
                if i['author']==message.author.name:
                    return_Message=return_Message+str(counter)+'. **'+str(i['year'])+'年'+str(i['month'])+'月'+str(i['date'])+'日 '+str(i['hour'])+'點'+str(i['minute'])+'分** **'+i['author']+'** 要我記得提醒他 **'+i['remark']+'**\n'
                    counter+=1
            if counter>1:
                return_Message=return_Message+'\n登登~之前請偶幫忙記的時間就是以上這些了~厲害吧 ~喵，主人快誇讚我'
            else:
                return_Message=return_Message+'目前的記事資料庫中沒有任何事情喔~好開心...這樣主人就有更多時間可以陪陪バニラ了 ~喵~喵喵'
        elif input_Info[1]=='add': # 輸入指令為add
            if len(input_Info)<8: # 少輸入某些資訊
                return_Message=return_Message+'喵喵~您是不是少輸入了某些資訊呢...偶看不懂QQ\n記得每一項資訊都要正確輸入喔~'
            elif len(input_Info)>8: # 多輸入某些資訊
                return_Message=return_Message+'喵喵~您是不是多輸入了某些資訊呢...偶看不懂QQ\n欸對了喵~備註文字的敘述不可以有空格喔~'
            elif not input_Info[2].isdigit(): # 輸入年分非數字
                return_Message=return_Message+'喵喵~您輸入的年分為 **'+input_Info[2]+'** ，看起來不是數字呦~'
            elif not input_Info[3].isdigit(): # 輸入月份非數字
                return_Message=return_Message+'喵喵~您輸入的月分為 **'+input_Info[3]+'** ，看起來不是數字呦~'
            elif not input_Info[4].isdigit(): # 輸入日期非數字
                return_Message=return_Message+'喵喵~您輸入的日期為 **'+input_Info[4]+'** ，看起來不是數字呦~'
            elif not input_Info[5].isdigit(): # 輸入時間(時)非數字
                return_Message=return_Message+'喵喵~您輸入的時間(時)為 **'+input_Info[5]+'** ，看起來不是數字呦~'
            elif not input_Info[6].isdigit(): # 輸入時間(分)非數字
                return_Message=return_Message+'喵喵~您輸入的時間(分)為 **'+input_Info[6]+'** ，看起來不是數字呦~'
            elif not IsValidDate(int(input_Info[2]),int(input_Info[3]),int(input_Info[4])): # 輸入年月日不存在
                return_Message=return_Message+'喵喵~您輸入的年分與日期為 **'+input_Info[2]+'年'+input_Info[3]+'月'+input_Info[4]+'日'+'** ，看起來不存在耶~'
            elif int(input_Info[5]) < 0 or int(input_Info[5]) > 24: # 輸入時間(時)不存在
                return_Message=return_Message+'喵喵~您輸入的時間(時)為 **'+input_Info[5]+'** ，看起來不存在耶~'
            elif int(input_Info[6]) < 0 or int(input_Info[6]) > 60: # 輸入時間(分)不存在
                return_Message=return_Message+'喵喵~您輸入的時間(分)為 **'+input_Info[6]+'** ，看起來不存在耶~'
            else: # 通過格式檢測
                new_Schedule={}
                new_Schedule['year']=int(input_Info[2])
                new_Schedule['month']=int(input_Info[3])
                new_Schedule['date']=int(input_Info[4])
                new_Schedule['hour']=int(input_Info[5])
                new_Schedule['minute']=int(input_Info[6])
                new_Schedule['remark']=input_Info[7]
                new_Schedule['author']=message.author.name #寫入創建此記事的使用者名稱
                if Is_Past_Time(new_Schedule): # 輸入的是過去的時間
                    return_Message=return_Message+'喵喵~您累了嗎?這個時間已經過了呦~辛苦了，要不要休息一下呢 ~喵'
                else:
                    schedule_List.append(new_Schedule.copy())
                    return_Message=return_Message+'バニラ記住了~\n**'+str(new_Schedule['year'])+'年'+str(new_Schedule['month'])+'月'+str(new_Schedule['date'])+'日 '+str(new_Schedule['hour'])+'點'+str(new_Schedule['minute'])+'分** 偶會記得提醒 **'+new_Schedule['author']+' '+new_Schedule['remark']+'** 的~'
        elif input_Info[1]=='del': # 輸入指令為del
            if len(input_Info)==2: # 未指定刪除編號
                return_Message=return_Message+'喵~您要記得指定欲刪除記事的編號，這樣偶才知道要刪除哪一筆喔'
            elif not input_Info[2].isdigit(): # 指定的刪除編號非數字
                return_Message=return_Message+'喵~您指定的刪除編號為 **'+input_Info[2]+'** ，好像不是數字耶，要不要再想想~\n'
            else:
                if len(input_Info)>3:
                    return_Message=return_Message+'指定刪除的編號後面不用再加東西了喔~不過好險我還是知道您的意思 ~喵\n'
                
                counter=1
                delete_Success=0
                for i in schedule_List:
                    if i['author']==message.author.name:
                        if counter==int(input_Info[2]):
                            schedule_List.remove(i)
                            delete_Success+=1  
                            break
                        counter+=1
                if delete_Success==1:
                    return_Message=return_Message+'喵喵~記事已經刪除成功了喔\n**'+str(i['year'])+'年'+str(i['month'])+'月'+str(i['date'])+'日 '+str(i['hour'])+'點'+str(i['minute'])+'分** **'+i['author']+'** 不需要再 **'+i['remark']+'** 了~'
                else:
                    return_Message=return_Message+'嗚...偶找不到你說的那筆記事...喔對了，想查看編號的話使用**ls**指令就可以囉'

    return return_Message

def Schedule_Time_Check():
    return_Message=''
    now = datetime.datetime.now() #取得現在時間

    for i in schedule_List: #刪除過期的記事
        if Is_Past_Time(i):
            schedule_List.remove(i)

    send=0
    for i in schedule_List:
        if i['year']==now.year and i['month']==now.month and i['date']==now.day+1 and now.hour==6 and now.minute==0: #前一天的早上6點提醒
            return_Message=return_Message+'**'+i['author']+'** 早呀~有睡飽嗎?\n**明天** 的 **'+str(i['hour'])+'點'+str(i['minute'])+'分** 要記得 **'+i['remark']+'** 哦 ~喵喵\n'
            send+=1
        elif i['year']==now.year and i['month']==now.month and i['date']==now.day and now.hour==6 and now.minute==0: #當天的早上6點提醒
            return_Message=return_Message+'**'+i['author']+'** 早呀~有睡飽嗎?\n**今天** 的 **'+str(i['hour'])+'點'+str(i['minute'])+'分** 要記得 **'+i['remark']+'** 哦 ~喵喵\n'
            send+=1
        elif i['year']==now.year and i['month']==now.month and i['date']==now.day and i['hour']==now.hour+1 and i['minute']==now.minute: #當天的前一個小時提醒
            return_Message=return_Message+'**'+i['author']+'** 哈囉~今天過的如何呀?\n**等一下** 的 **'+str(i['hour'])+'點'+str(i['minute'])+'分** 要記得 **'+i['remark']+'** 哦，祝您可以順利的完成這件事 ~喵喵\n'
            send+=1

    if send==0:
        return 'no event'
    else:
        return return_Message

@tasks.loop(seconds=60.0) #每60秒執行一次
async def Time_Check():
    now = datetime.datetime.now() #取得現在時間

    schedule_Event=Schedule_Time_Check() #檢查是否有已安排的記事
    if schedule_Event!='no event':
        channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
        await channel.send(schedule_Event)
     
    if now.hour == 10 and now.minute == 0: # 設定指定時間傳送Codeforce比賽訊息
        channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
        await channel.send(Codeforce_Time_Check())

@client.event
async def on_ready(): #啟動成功時會呼叫
    channel = discord.utils.get(client.get_all_channels(), name='chat-bot-for-test') # 用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('喵~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')

    channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('喵~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')
    #print('目前登入身份：', client.user)
    Time_Check.start() #每60秒在背景執行Codeforce_Time_Check函式

@client.event
async def on_message(message): #有新的訊息便會呼叫
    if message.author == client.user: #若新訊息是bot本身則忽略
        return
    elif message.content[:12]=='System call ':
        commend=message.content[12:]
        await message.channel.send(System_Commend(message,commend))
    else:
        special_Reponse=Special_Reponse(message)
        if special_Reponse!='0':
            await message.channel.send(special_Reponse)
        elif let_chat==1:
            response=ChatGPT_Get_Context(message.content)
            await message.channel.send(response+'~喵')

client.run('MTA3MDQwMzQ0NzQ2NTE4OTM5Ng.GWMPbq.ibq0tZQGGjTojvXZUqIa7fDpFC3g5mdbp8tNng')
