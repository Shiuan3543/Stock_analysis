# -*- coding: utf-8 -*-
"""
Created on Mon May 20 15:26:03 2019

@author: A
"""

def get_setting(): #將讀取檔寫成函式, 可讓程式易讀易用
    res = [] #準備一個空串列來存放讀取及解析的結果
    try: # 使用 try 來預防開檔或讀檔錯誤
        with open('stock.txt') as f: # with 以讀取模式開啟檔案
            slist = f.readlines() # 以行為單位讀取所有資料
            print('讀入：', slist) # 輸出讀到的資料以供確認
            for lst in slist: #走訪每一張股票字串
                s = lst.split(',') #將股票字串以逗號切割為串列
                res.append([s[0].strip(),float(s[1]),float(s[2])]) #將切割結果加 res
    except: #去除左右空白將股價轉換為 float
        print('stock.txt 讀取錯誤')
    return res #傳回解析結果, 開檔/讀檔錯則傳 []
stock = get_setting() # 呼叫上面的函式
print('傳回：', stock) # 輸出傳回的結果


import twstock
def get_price(stockid): #取得股票名稱,及時股價
    rt = twstock.realtime.get(stockid) # 取得台積電
    print(rt)
    if rt['success']: # 如果讀取成功
        return (rt['info']['name'], #傳回(名稱,及時價格)
        float(rt['realtime']['latest_trade_price']))
    else:
        return (False, False)
name, price = get_price('2610')#用 name 及 price 來承接傳回的 tuple
print(name, price)
name, price = get_price('2002')#用 name 及 price 來承接傳回的 tuple
print(name, price)
name, price = get_price('2498')#用 name 及 price 來承接傳回的 tuple
print(name, price)

import requests # 匯入 requests 套件
def send_ifttt(v1, v2, v3):# 定義函式來向 IFTTT 發送 HTTP 要求
    url = ('https://maker.ifttt.com/trigger/to_line/with/' + 'key/dzJ48-qSKbtj9VxDxhylYm' + '?value1='+str(v1) + '&value2='+str(v2) + '&value3='+str(v3))
    r = requests.get(url)# 送出 HTTP GET 並取得網站的回應資料
    if r.text[:5] == 'Congr':# 回應的文字若以 Congr 開頭就表示成功了
        print('已傳送 (' +str(v1)+', '+str(v2)+', '+str(v3)+ ') 到 Line')
        return r.text
#ret = send_ifttt('台積電', 99, '建議買進')#傳送 HTTP 請求到 IFTTT
#print('IFTTT 的回應訊息：', ret)

def get_best(stockid): # 檢查是否符合四大買賣點
    stock = twstock.Stock(stockid)
    bp = twstock.BestFourPoint(stock).best_four_point()
    print(bp)
    if(bp):
        return ('買進' if bp[0] else '賣出', bp[1])#←傳回買進或賣出的建議
    else:
        return (False, False) #←都不符合
name, price = get_price('2610')#用 name 及 price 來承接傳回的 tuple
act, why = get_best('2610')#用 act 及 why 來承接傳回的四大買賣點 tuple
print(act,why,sep="\t|\t")
print(name, price, act, why, sep=' | ')
name, price = get_price('2002')#用 name 及 price 來承接傳回的 tuple
act, why = get_best('2002')#用 act 及 why 來承接傳回的四大買賣點 tuple
print(act,why,sep="\t|\t")
print(name, price, act, why, sep=' | ')
name, price = get_price('2498')#用 name 及 price 來承接傳回的 tuple
act, why = get_best('2498')#用 act 及 why 來承接傳回的四大買賣點 tuple
print(act,why,sep="\t|\t")
print(name, price, act, why, sep=' | ')


import time
slist = get_setting() # 呼叫匯入模組中的函式取得股票設定資料
cnt = len(slist) # 計算有幾支股票
log1 = [] # 記錄曾傳過股票高或低於期望價,避免重複傳送
log2 = [] # 記錄曾傳過符合四大買賣點訊息, 避免重複傳送
for i in range(cnt): #}
    log1.append('') #}為每支股票加入一個對應的元素
    log2.append('') #}
check_cnt = 20# 指定要檢查幾次 (20*3分鐘 = 60分鐘)
while True:
    for i in range(cnt): # 走訪每一支股票
        id, low, high = slist[i]#讀出股票的代號、期望買進價格、期望賣出
        print(id, low, high)
        name, price = get_price(id)#讀取股票的名稱和即時價格
        print('檢查：',name, '股價：',price, '區間：',low,'~',high)
        if price <= low: #←如果即時股價到達期望買點
            if log1[i] != '買進': # 檢查前次傳送訊息, 避免重複傳送
                send_ifttt(name, price, '買進 (股價低於 '+str(low)+')')
                log1[i]= '買進' # 記錄傳送訊息, 以避免重複傳送
        elif price >= high: #←如果即時股價到達期望賣點
            if log1[i] != '賣出': # 檢查前次傳送訊息, 避免重複傳送
                send_ifttt(name, price, '賣出 (股價高於 '+str(low)+')')
                log1[i]= '賣出' # 記錄傳送訊息, 以避免重複傳送
        act, why = get_best(id) # 檢查四大買賣點
        if why: #←如果符合四大買賣點
            if log2[i] != why: # 檢查前次傳訊息, 避免重複傳送
                send_ifttt(name, price, act + ' (' +why+ ')')
                log2[i] = why # 記錄傳送訊息, 避免重複傳送
                print('--------------')
        check_cnt -= 1 # 將計數器減 1
        if check_cnt == 0: 
            break# 檢查計數器為 0 時即離開迴圈、結束程式
    time.sleep(180) # 每 3 分鐘 (180 秒) 檢查一遍