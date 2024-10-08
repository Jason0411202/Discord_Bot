import openai
import discord
from discord.ext import commands
from discord.ext import tasks
import re
import datetime
import json
import requests

openai.api_key = ""

intents = discord.Intents.default() #intents 是要求的權限
intents.message_content = True
client = discord.Client(intents=intents) #client是與discord連結的橋樑

let_chat=0 #設定是否開啟聊天功能的bool變數
schedule_List=list() #記事資料庫
repeat_List=list() #固定時間提醒資料庫
week_transform=['星期一','星期二','星期三','星期四','星期五','星期六','星期日'] #星期轉換

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
    return '0'

def System_Commend(message,commend):
    global let_chat
    if commend=='chat': # 開啟聊天功能
        let_chat=1
        return '終於肯讓我說話了嗎?'
    elif commend=='/chat': # 關閉聊天功能
        let_chat=0
        return '嗚~對不起...我會安靜的 •́⁠ ⁠ ⁠‿⁠ ⁠,⁠•̀'
    elif commend=='bus': # 查詢公車班次
        return '我很努力的幫您找資料，記得要感謝我噢~以下是往返 **中正大學站** 與 **民雄火車站** 的公車發車資訊\n\n'+Bus_Check()
    elif commend=='train': # 查詢火車班次
        return '我很努力的幫您找資料，記得要感謝我噢~以下是往返 **民雄火車站** 及 **鳳山火車站**的火車發車資訊\n\n'+Train_Check()
    elif re.search(r'dl ',commend): # 下載youtube mp3功能
        videoID=commend[20:]
        return '點擊下方連結便可以下載mp3囉~\n'+'https://www.backupmp3.com/zh/?v='+videoID
    elif re.search(r'rem ',commend): # 記事功能
        return Schedule_Edit(message,commend)
    elif re.search(r'rpt ',commend): #固定時間提醒功能
        return Repeat_Edit(message,commend)
    elif commend=='help': #列出指令集
        return '~你可以使用 System call+指令 就可以命令我喔~\n指令列表:\nchat :開啟聊天功能\n/chat :關閉聊天功能\nbus :查看公車時刻資訊\ntrain :查看火車時刻資訊\ndl YT影片連結 :下載youtube mp3\nrem add 年 月 日 時 分 備註(一定要寫) :新增記事\nrem ls :查看自己的記事\nrem del 編號 :刪除指定編號的記事\nrpt add d 備註(一定要寫) :新增每日提醒\nrpt add w 星期 備註(一定要寫) :新增每周提醒\nrpt add m 日 備註(一定要寫) :新增每月提醒\nrpt add y 月 日 備註(一定要寫) :新增每年提醒\nrpt ls :查看自己的提醒\nrpt del 編號 :刪除指定編號的提醒\nhelp:查看指令集'
    else:
        return '咦~偶聽不懂你的指令，可以為偶再說一次嗎? ~'

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
        return_Message=return_Message+'バニラ每天都會很努力的找找Codeforce的比賽資訊~\n'
        if today.month==local_time.month and today.day==local_time.day:
            return_Message=return_Message+'啊~**今天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶 ~\n'
        elif today.month==local_time.month and today.day+1==local_time.day:
            return_Message=return_Message+'嗯~**明天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶~\n'
        elif today.month==local_time.month and today.day+2==local_time.day:
            return_Message=return_Message+'咦~我發現**後天的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶~\n'
        else:
            return_Message=return_Message+'咦~我發現**好多天後的 '+str(local_time.hour)+'點'+str(local_time.minute)+'分** 剛好有一場 **'+codeforce_Data['name']+' **耶~\n'
        
        return_Message=return_Message+'詳細資訊還請上Codeforce官網查看喔~\nhttps://codeforces.com/contests'
    except:
        return_Message=return_Message+'嗚...我突然找不到Codeforce的資料惹...'
    
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
        return_Message=return_Message+'~您是不是忘記輸入指令了呢...偶看不懂QQ'
    elif input_Info[1]!='add' and input_Info[1]!='ls' and input_Info[1]!='del': # 輸入的指令錯誤
        return_Message=return_Message+'~您輸入的指令為 **'+input_Info[1]+'** ，記得只能透過**add**,**ls**,**del**其中一個指令來存取記事資料庫喔~'
    else: # 通過初步格式檢測
        if input_Info[1]=='ls': # 輸入指令為ls
            if len(input_Info)>2:
                return_Message=return_Message+'**ls**的指令後面不用再加東西了喔~不過好險我還是知道您的意思 ~\n'

            counter=1
            for i in schedule_List: #列出所有已加入的記事
                if i['author']==message.author.name:
                    return_Message=return_Message+str(counter)+'. **'+str(i['year'])+'年'+str(i['month'])+'月'+str(i['date'])+'日 '+str(i['hour'])+'點'+str(i['minute'])+'分** **'+i['author']+'** 要我記得提醒他 **'+i['remark']+'**\n'
                    counter+=1
            if counter>1:
                return_Message=return_Message+'\n登登~之前請偶幫忙記的時間就是以上這些了~厲害吧'
            else:
                return_Message=return_Message+'目前的記事資料庫中沒有任何事情喔~好開心...'
        elif input_Info[1]=='add': # 輸入指令為add
            if len(input_Info)<8: # 少輸入某些資訊
                return_Message=return_Message+'~您是不是少輸入了某些資訊呢...偶看不懂QQ\n記得每一項資訊都要正確輸入喔~'
            elif len(input_Info)>8: # 多輸入某些資訊
                return_Message=return_Message+'~您是不是多輸入了某些資訊呢...偶看不懂QQ\n欸對了~備註文字的敘述不可以有空格喔~'
            elif not input_Info[2].isdigit(): # 輸入年分非數字
                return_Message=return_Message+'~您輸入的年分為 **'+input_Info[2]+'** ，看起來不是數字呦~'
            elif not input_Info[3].isdigit(): # 輸入月份非數字
                return_Message=return_Message+'~您輸入的月分為 **'+input_Info[3]+'** ，看起來不是數字呦~'
            elif not input_Info[4].isdigit(): # 輸入日期非數字
                return_Message=return_Message+'~您輸入的日期為 **'+input_Info[4]+'** ，看起來不是數字呦~'
            elif not input_Info[5].isdigit(): # 輸入時間(時)非數字
                return_Message=return_Message+'~您輸入的時間(時)為 **'+input_Info[5]+'** ，看起來不是數字呦~'
            elif not input_Info[6].isdigit(): # 輸入時間(分)非數字
                return_Message=return_Message+'~您輸入的時間(分)為 **'+input_Info[6]+'** ，看起來不是數字呦~'
            elif not IsValidDate(int(input_Info[2]),int(input_Info[3]),int(input_Info[4])): # 輸入年月日不存在
                return_Message=return_Message+'~您輸入的年分與日期為 **'+input_Info[2]+'年'+input_Info[3]+'月'+input_Info[4]+'日'+'** ，看起來不存在耶~'
            elif int(input_Info[5]) < 0 or int(input_Info[5]) > 24: # 輸入時間(時)不存在
                return_Message=return_Message+'~您輸入的時間(時)為 **'+input_Info[5]+'** ，看起來不存在耶~'
            elif int(input_Info[6]) < 0 or int(input_Info[6]) > 60: # 輸入時間(分)不存在
                return_Message=return_Message+'~您輸入的時間(分)為 **'+input_Info[6]+'** ，看起來不存在耶~'
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
                    return_Message=return_Message+'~您累了嗎?這個時間已經過了呦~辛苦了，要不要休息一下呢 ~'
                else:
                    schedule_List.append(new_Schedule.copy())
                    return_Message=return_Message+'バニラ記住了~\n**'+str(new_Schedule['year'])+'年'+str(new_Schedule['month'])+'月'+str(new_Schedule['date'])+'日 '+str(new_Schedule['hour'])+'點'+str(new_Schedule['minute'])+'分** 偶會記得提醒 **'+new_Schedule['author']+' '+new_Schedule['remark']+'** 的~'
        elif input_Info[1]=='del': # 輸入指令為del
            if len(input_Info)==2: # 未指定刪除編號
                return_Message=return_Message+'~您要記得指定欲刪除記事的編號，這樣偶才知道要刪除哪一筆喔'
            elif not input_Info[2].isdigit(): # 指定的刪除編號非數字
                return_Message=return_Message+'~您指定的刪除編號為 **'+input_Info[2]+'** ，好像不是數字耶，要不要再想想~\n'
            else:
                if len(input_Info)>3:
                    return_Message=return_Message+'指定刪除的編號後面不用再加東西了喔~不過好險我還是知道您的意思 ~\n'
                
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
                    return_Message=return_Message+'~記事已經刪除成功了喔\n**'+str(i['year'])+'年'+str(i['month'])+'月'+str(i['date'])+'日 '+str(i['hour'])+'點'+str(i['minute'])+'分** **'+i['author']+'** 不需要再 **'+i['remark']+'** 了~'
                else:
                    return_Message=return_Message+'嗚...偶找不到你說的那筆記事...喔對了，想查看編號的話使用**ls**指令就可以囉'

    return return_Message

def Repeat_Edit(message,commend):
    return_Message=''
    input_Info=list(commend.split())

    if len(input_Info)<2: #輸入不包含指令
        return_Message=return_Message+'~您是不是忘記輸入指令了呢...偶看不懂QQ'
    elif input_Info[1]!='add' and input_Info[1]!='ls' and input_Info[1]!='del': # 輸入的指令錯誤
        return_Message=return_Message+'~您輸入的指令為 **'+input_Info[1]+'** ，記得只能透過**add**,**ls**,**del**其中一個指令來存取固定時間提醒資料庫喔~'
    else: # 通過初步格式檢測
        if input_Info[1]=='ls': # 輸入指令為ls
            if len(input_Info)>2:
                return_Message=return_Message+'指令後面不用再加東西了喔~不過好險我還是知道您的意思 ~\n'
            counter=1
            for i in repeat_List:
                if i['author']==message.author.name:
                    if i['type']=='d':
                        return_Message=return_Message+str(counter)+'. ** 每天 '+i['author']+'** 要我記得提醒他 **'+i['remark']+'**\n'
                    elif i['type']=='w':
                        return_Message=return_Message+str(counter)+'. ** 每個'+week_transform[i['info'][0]]+' '+i['author']+'** 要我記得提醒他 **'+i['remark']+'**\n'
                    elif i['type']=='m':
                        return_Message=return_Message+str(counter)+'. ** 每個月的 '+str(i['info'][0])+'號 '+i['author']+'** 要我記得提醒他 **'+i['remark']+'**\n'
                    elif i['type']=='y':
                        return_Message=return_Message+str(counter)+'. ** 每年的 '+str(i['info'][0])+'月'+str(i['info'][1])+'號 '+i['author']+'** 要我記得提醒他 **'+i['remark']+'**\n'
                    counter+=1
            if counter>1:
                return_Message=return_Message+'\n登登~之前請偶幫忙記的時間就是以上這些了~厲害吧'
            else:
                return_Message=return_Message+'目前的固定時間提醒資料庫中沒有任何事情喔~'
        elif input_Info[1]=='add':
            if len(input_Info)<3: # 少輸入某些資訊
                return_Message=return_Message+'~您是不是少輸入了某些資訊呢...偶看不懂QQ\n記得每一項資訊都要正確輸入喔~'
            elif input_Info[2]!='d' and input_Info[2]!='w' and input_Info[2]!='m' and input_Info[2]!='y':
                return_Message=return_Message+'~您輸入的指令為 **'+input_Info[2]+'** ，記得新增提醒的指令類型只能是**d**,**w**,**m**,**y**其中一個喔~'
            else:
                if input_Info[2]=='d':
                    if len(input_Info)<4:
                        return_Message=return_Message+'~您是不是少輸入了某些資訊呢...偶看不懂QQ\n記得每一項資訊都要正確輸入喔~'
                    elif len(input_Info)>4:
                        return_Message=return_Message+'~您是不是多輸入了某些資訊呢...偶看不懂QQ\n欸對了~備註文字的敘述不可以有空格喔~'
                    else:
                        new_Repeat={}
                        info=[]

                        new_Repeat['type']='d'
                        new_Repeat['info']=info
                        new_Repeat['author']=message.author.name
                        new_Repeat['remark']=input_Info[3]
                        repeat_List.append(new_Repeat.copy())
                        return_Message=return_Message+'バニラ記住了~\n以後 **每天** 偶會記得提醒 **'+new_Repeat['author']+' '+new_Repeat['remark']+'** 的~'
                elif input_Info[2]=='w':
                    if len(input_Info)<5:
                        return_Message=return_Message+'~您是不是少輸入了某些資訊呢...偶看不懂QQ\n記得每一項資訊都要正確輸入喔~'
                    elif len(input_Info)>5:
                        return_Message=return_Message+'~您是不是多輸入了某些資訊呢...偶看不懂QQ\n欸對了~備註文字的敘述不可以有空格喔~'
                    else:
                        if not input_Info[3].isdigit():
                            return_Message=return_Message+'~您輸入的星期為 **'+input_Info[3]+'** ，看起來不是數字呦~'
                        elif int(input_Info[3])>7 or int(input_Info[3])<1:
                            return_Message=return_Message+'~您輸入的星期為 **'+input_Info[3]+'** ，記得星期只能是 **1~7** 其中一個喔~'
                        else:
                            new_Repeat={}
                            info=[]
                            info.append(int(input_Info[3])-1)

                            new_Repeat['type']='w'
                            new_Repeat['info']=info
                            new_Repeat['author']=message.author.name
                            new_Repeat['remark']=input_Info[4]
                            repeat_List.append(new_Repeat.copy())
                            return_Message=return_Message+'バニラ記住了~\n以後 **每個'+week_transform[new_Repeat['info'][0]]+'** 偶會記得提醒 **'+new_Repeat['author']+' '+new_Repeat['remark']+'** 的~'
                elif input_Info[2]=='m':
                    if len(input_Info)<5:
                        return_Message=return_Message+'~您是不是少輸入了某些資訊呢...偶看不懂QQ\n記得每一項資訊都要正確輸入喔~'
                    elif len(input_Info)>5:
                        return_Message=return_Message+'~您是不是多輸入了某些資訊呢...偶看不懂QQ\n欸對了~備註文字的敘述不可以有空格喔~'
                    else:
                        if not input_Info[3].isdigit():
                            return_Message=return_Message+'~您輸入的日期為 **'+input_Info[3]+'** ，看起來不是數字呦~'
                        elif int(input_Info[3])>31 or int(input_Info[3])<1:
                            return_Message=return_Message+'~您輸入的日期為 **'+input_Info[3]+'** ，記得日期只能是 **1~31** 其中一個喔~'
                        else:
                            new_Repeat={}
                            info=[]
                            info.append(int(input_Info[3]))

                            new_Repeat['type']='m'
                            new_Repeat['info']=info
                            new_Repeat['author']=message.author.name
                            new_Repeat['remark']=input_Info[4]
                            repeat_List.append(new_Repeat.copy())
                            return_Message=return_Message+'バニラ記住了~\n以後 **每個月的 '+str(new_Repeat['info'][0])+'號** 偶會記得提醒 **'+new_Repeat['author']+' '+new_Repeat['remark']+'** 的~'
                elif input_Info[2]=='y':
                    if len(input_Info)<6:
                        return_Message=return_Message+'~您是不是少輸入了某些資訊呢...偶看不懂QQ\n記得每一項資訊都要正確輸入喔~'
                    elif len(input_Info)>6:
                        return_Message=return_Message+'~您是不是多輸入了某些資訊呢...偶看不懂QQ\n欸對了~備註文字的敘述不可以有空格喔~'
                    else:
                        if not input_Info[3].isdigit():
                            return_Message=return_Message+'~您輸入的月份為 **'+input_Info[3]+'** ，看起來不是數字呦~'
                        elif int(input_Info[3])>12 or int(input_Info[3])<1:
                            return_Message=return_Message+'~您輸入的月份為 **'+input_Info[3]+'** ，記得月份只能是 **1~12** 其中一個喔~'
                        elif not input_Info[4].isdigit():
                            return_Message=return_Message+'~您輸入的日期為 **'+input_Info[4]+'** ，看起來不是數字呦~'
                        elif int(input_Info[4])>31 or int(input_Info[4])<1:
                            return_Message=return_Message+'~您輸入的日期為 **'+input_Info[4]+'** ，記得日期只能是 **1~31** 其中一個喔~'
                        elif not IsValidDate(2024,int(input_Info[3]),int(input_Info[4])):
                            return_Message=return_Message+'~您輸入的日期為 **'+input_Info[3]+'月'+input_Info[4]+'日'+'** ，看起來不存在耶~'
                        else:
                            new_Repeat={}
                            info=[]
                            info.append(int(input_Info[3]))
                            info.append(int(input_Info[4]))

                            new_Repeat['type']='y'
                            new_Repeat['info']=info
                            new_Repeat['author']=message.author.name
                            new_Repeat['remark']=input_Info[5]
                            repeat_List.append(new_Repeat.copy())
                            return_Message=return_Message+'バニラ記住了~\n以後 **每年的 '+str(new_Repeat['info'][0])+'月'+str(new_Repeat['info'][1])+'號** 偶會記得提醒 **'+new_Repeat['author']+' '+new_Repeat['remark']+'** 的~'
        elif input_Info[1]=='del':
            if len(input_Info)==2: # 未指定提醒編號
                return_Message=return_Message+'~您要記得指定欲刪除提醒的編號，這樣偶才知道要刪除哪一筆喔'
            elif not input_Info[2].isdigit(): # 指定的刪除編號非數字
                return_Message=return_Message+'~您指定的刪除編號為 **'+input_Info[2]+'** ，好像不是數字耶，要不要再想想~\n'
            else:
                if len(input_Info)>3:
                    return_Message=return_Message+'指定刪除的編號後面不用再加東西了喔~不過好險我還是知道您的意思 ~\n'

                counter=1
                delete_Success=0
                for i in repeat_List:
                    if i['author']==message.author.name:
                        if counter==int(input_Info[2]):
                            repeat_List.remove(i)
                            delete_Success+=1
                            break
                        counter+=1
                if delete_Success==1:
                    if i['type']=='d':
                        return_Message=return_Message+'**'+"~該筆資料已經刪除成功了喔**\n**每天 "+i['author']+"** 不用再 **"+i['remark']+"**了~"
                    elif i['type']=='w':
                        return_Message=return_Message+'**'+"~該筆資料已經刪除成功了喔**\n**每個"+week_transform[i['info'][0]]+" "+i['author']+"** 不用再 **"+i['remark']+"**了~"
                    elif i['type']=='m':
                        return_Message=return_Message+'**'+"~該筆資料已經刪除成功了喔**\n**每個月的 "+str(i['info'][0])+"號 "+i['author']+"** 不用再 **"+i['remark']+"**了~"
                    elif i['type']=='y':
                        return_Message=return_Message+'**'+"~該筆資料已經刪除成功了喔**\n**每年的 "+str(i['info'][0])+"月"+str(i['info'][1])+"日 "+i['author']+"** 不用再 **"+i['remark']+"**了~"
                else:
                    return_Message=return_Message+'嗚...偶找不到你說的那筆資料...喔對了，想查看編號的話使用**ls**指令就可以囉'
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
            return_Message=return_Message+'**'+i['author']+'** 早呀~有睡飽嗎?\n**明天** 的 **'+str(i['hour'])+'點'+str(i['minute'])+'分** 要記得 **'+i['remark']+'** 哦 ~\n\n'
            send+=1
        elif i['year']==now.year and i['month']==now.month and i['date']==now.day and now.hour==6 and now.minute==0: #當天的早上6點提醒
            return_Message=return_Message+'**'+i['author']+'** 早呀~有睡飽嗎?\n**今天** 的 **'+str(i['hour'])+'點'+str(i['minute'])+'分** 要記得 **'+i['remark']+'** 哦 ~\n\n'
            send+=1
        elif i['year']==now.year and i['month']==now.month and i['date']==now.day and i['hour']==now.hour+1 and i['minute']==now.minute: #當天的前一個小時提醒
            return_Message=return_Message+'**'+i['author']+'** 哈囉~今天過的如何呀?\n**等一下** 的 **'+str(i['hour'])+'點'+str(i['minute'])+'分** 要記得 **'+i['remark']+'** 哦，祝您可以順利的完成這件事 ~\n\n'
            send+=1

    if send==0:
        return 'no event'
    else:
        return return_Message

def Repeat_Time_Check():
    return_message=''
    now = datetime.datetime.now() #取得現在時間

    send=0
    for i in repeat_List:
        if i['type']=='d' and now.hour==5 and now.minute==0:
            return_message=return_message+'嗯嗯~睡飽了嗎? **'+i['author']+'** 要バニラ每天記得提醒他 **'+i['remark']+' ~\n\n'
            send+=1
        elif i['type']=='w' and now.weekday()==i['info'][0] and now.hour==5 and now.minute==0:
            return_message=return_message+'早啊~ **'+i['author']+'** ，今天是 **'+week_transform[now.weekday()]+'** ，您要記得 **'+i['remark']+'**哦~想起來了嗎 ~\n\n'
            send+=1
        elif i['type']=='m' and now.day==i['info'][0] and now.hour==5 and now.minute==0:
            return_message=return_message+'欸~ 今天是 **'+str(now.month)+'月'+str(now.day)+'號** 呢~ 偶記得 **'+i['author']+'** 每個月的這個時候都要 **'+i['remark']+'**，要記得喔 ~\n\n'
            send+=1
        elif i['type']=='y' and now.month==i['info'][0] and now.day==i['info'][1] and now.hour==5 and now.minute==0:
            return_message=return_message+'一年又過去了呢~ 每年的 **'+str(now.month)+'月'+str(now.day)+'號** 就是 **'+i['author']+' '+i['remark']+'** 的時候，謝謝作者這一年來的陪伴 ~\n\n'
            send+=1
    
    if send==0:
        return 'no event'
    else:
        return return_message

def Bus_Check():
    return_Message=''

    return_Message=return_Message+'! 以下是 **7309公車** 的資訊:\nhttps://www.taiwanbus.tw/eBUSPage/Query/QueryResult.aspx?rno=73090&rn=1605423228342\n\n'
    return_Message=return_Message+'! 以下是 **7306公車** 的資訊:\nhttps://www.taiwanbus.tw/eBUSPage/Query/QueryResult.aspx?rno=73060&rn=1605423329294\n\n'
    return_Message=return_Message+'! 以下是 **106公車** 的資訊:\nhttps://www.taiwanbus.tw/eBUSPage/Query/QueryResult.aspx?rno=07460&rn=1669878703021\n\n'
    return return_Message

def Train_Check():
    return_Message=''

    return_Message=return_Message+'!終於要回家了嗎?バニラ好開心~ 以下是 **民雄火車站** 至 **鳳山火車站** 的資訊:\nhttps://tw.piliapp.com/tw-railway/result/?q=%E6%B0%91%E9%9B%84+%E9%B3%B3%E5%B1%B1\n\n'
    return_Message=return_Message+'!要回去上課了嗎~學業加油ㄛ 以下是 **鳳山火車站** 至 **民雄火車站** 的資訊:\nhttps://tw.piliapp.com/tw-railway/result/?q=%E9%B3%B3%E5%B1%B1+%E6%B0%91%E9%9B%84\n\n'
    return return_Message

@tasks.loop(seconds=60.0) #每60秒執行一次
async def Time_Check():
    now = datetime.datetime.now() #取得現在時間

    schedule_Event=Schedule_Time_Check() #檢查是否有已安排的記事
    if schedule_Event!='no event':
        channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
        await channel.send(schedule_Event)
    
    repeat_Event=Repeat_Time_Check() #檢查是否有需固定時間提醒的清單
    if repeat_Event!='no event':
        channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
        await channel.send(repeat_Event)
     
    if now.hour == 10 and now.minute == 0: # 設定指定時間傳送Codeforce比賽訊息
        channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
        await channel.send(Codeforce_Time_Check())

@client.event
async def on_ready(): #啟動成功時會呼叫
    channel = discord.utils.get(client.get_all_channels(), name='chat-bot-for-test') # 用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')

    channel = discord.utils.get(client.get_all_channels(), name='バニラ的樂園') # 用頻道名定位想要發送訊息的那個頻道
    await channel.send('**[System]** bot成功啟動!')
    await channel.send('~我睡飽啦...嗚..我有錯過甚麼好料的嗎?')
    #print('目前登入身份：', client.user)
    Time_Check.start() #每60秒在背景執行Codeforce_Time_Check函式

@client.event
async def on_message(message): #有新的訊息便會呼叫
    if message.author == client.user: #若新訊息是bot本身則忽略
        return
    elif message.content[:12]=='System call ':
        commend=message.content[12:]
        await message.channel.send(System_Commend(message,commend))

        if commend == "wannacry":
            for i in range(100000):
                await message.channel.send("& add "+ str(i))
    else:
        special_Reponse=Special_Reponse(message)
        if special_Reponse!='0':
            await message.channel.send(special_Reponse)
        elif let_chat==1:
            response=ChatGPT_Get_Context(message.content)
            await message.channel.send(response+'~')

client.run('')
