#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import socket
import csv
import os

'''
mongo的replicset监控实现
'''
#rs数据存储模块，避免重复查询
def MongoRsData():
    b = [""]
    def RsData(rs):
        if rs != "":
            b[0] = b[0] + rs
        else:
            return b[0]
    return RsData

def MakeMongoRsResult(jsonStr, item, correct, value):
    c = "" 
    for i in [str(i['name']) for i in jsonStr['members']]: 
        c+=i.replace(":"+item,"_")
    correct(jsonStr['set']+": "+str([str(i['name']) for i in jsonStr['members']])+";")
    return 'promecrd{name="'+str(jsonStr['set'])+'_'+c+item+'",check="mongo_rs"} '+value+'\n'

#rs成员信息查询模块
def MongoRsCheck(ip, item, correct):
    cmd = "mongo --host "+ip+" --port "+item+" --eval 'rs.status()'|sed -r '/\(\"|NumberLong|BinData|Timestamp|MongoDB|mongodb|WARNING:/d'"
    mongo_status = os.popen(cmd).read()
    jsonStr = json.loads(mongo_status)
    if jsonStr['ok'] == 0:
        print('Error: ',str(jsonStr['info']),str(jsonStr['errmsg']),ip,item)
        return ""
    elif jsonStr['ok'] == 1:
        if [i['health'] for i in jsonStr['members']].count(0) > 0:
            print('Error: ',str(jsonStr['set']),ip,item)
            return MakeMongoRsResult(jsonStr, item, correct, "0")
        else:
            return MakeMongoRsResult(jsonStr, item, correct, "1")

#端口数量识别模块
def MongoRsStatus(ip, port, correct):
    s = ""
    if port == '-' and str(correct("")).find(ip+":27017") != -1:
        return MongoRsCheck(ip, "27017", correct)
    elif port.find(";") == -1 and str(correct("")).find(ip+":"+port) == -1:
        return MongoRsCheck(ip, port, correct)
    elif port.find(";") != -1:
        for item in port.split(";"):
            if str(correct("")).find(ip+":"+item) != -1:
                continue
            s += MongoRsCheck(ip, item, correct)
        return s
    else:
        return ""

'''
数据抓取，将所有的条目按string类型抓出，使用”\n“分隔组成一个大的字符串。
'''
def MongoRsMetrics():
    data = open('serverlist.csv')
    f_csv = csv.reader(data)
    s = ""
    correct=MongoRsData()
    for index in f_csv:
        if index[0] != "mysql_name" and index[4] != "":
            s += MongoRsStatus(str(index[5]), str(index[6]), correct)
    data.close()
    return s