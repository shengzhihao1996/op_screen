#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import socket
import csv
import os
import base64


'''
对ip和port建立tcp连接，来测试服务存活。
'''
#rs数据存储模块，避免重复查询
def RabbitmqCsData():
    a = [[]]
    b = [[]]
    def CsData(cs, tof):
        if cs != "" and tof == True:
            a[0].append(cs)
        elif cs != "" and tof == False:
            b[0].append(cs)
        elif cs == "" and tof == True:
            return a[0]
        elif cs == "" and tof == False:
            return b[0]
    return CsData

socket.setdefaulttimeout(3)
def RabbitmqCsCheck(ip, port, passwd, correct):
    conn = 1
    try:
        url = "http://"+ip+":"+port+"/api/nodes"
        userinfo = (passwd.split("/")[0]+":"+passwd.split("/")[1]).encode('UTF-8')
        headers = {'Authorization': 'Basic '+ str(base64.b64encode(userinfo))[2:-1]}
        req = requests.get(url, headers=headers)
        repositories_list = json.loads(req.text)
        memberlist = {v['name'] for v in repositories_list}
        hostdict = {}
        label = ""
        for d in repositories_list:
            for e in d['cluster_links']:
                hostdict[e['name']]=e['peer_addr']
        for f in memberlist:
            label += "_"+hostdict[f]
        ipset={hostdict[v] for v in memberlist}
        if [v['running'] for v in repositories_list].count(False) > 0:
            correct(memberlist, False)
            print("error :"+label)
        else:
            correct(ipset, True)
            print("succeed :"+label)
    except Exception as e:
        print("Exception occurred: {}".format(e),ip,port)
        conn = 0
    if conn == 1:
        req.close()

'''
默认端口的逻辑判断
手动添加的端口使用“；”分隔
'''
def RabbitmqCsStatus(ip, port, passwd, correct):
    if port == '-' and passwd != "":
        RabbitmqCsCheck(ip, "15672", passwd, correct)
    elif port.find(";") == -1 and passwd != "":
        RabbitmqCsCheck(ip, port, passwd, correct)
    elif port.find(";") != -1 and passwd != "":
        for item in port.split(";"):
            RabbitmqCsCheck(ip, item, passwd, correct)


def MakeResult(correct):
    t=[]
    for i in correct("",True):
        for j in correct("",True):
            if i - j == set() and not i in t:
                t.append(i)
    f=[]
    for i in correct("",False):
        for j in correct("",False):
            if i - j == set() and not i in f:
                f.append(i)
    for i in t:
        for j in f:
            if i - j == set() :
                t.remove(i)
    s =""
    for i in t:
        endpoint=""
        for j in i:
            endpoint+="_"+j
        s += 'promecrd{name="RabbitMQ'+endpoint+'",check="rabbitmq_cs"} 1\n'
    for i in f:
        endpoint=""
        for j in i:
            endpoint+="_"+j
        s += 'promecrd{name="RabbitMQ'+endpoint+'",check="rabbitmq_cs"} 0\n'
    return s
'''
数据抓取，将所有的条目按string类型抓出，使用”\n“分隔组成一个大的字符串。
'''
def RabbitmqCsMetrics():
    data = open('serverlist.csv')
    f_csv = csv.reader(data)
    correct=RabbitmqCsData()
    for index in f_csv:
        if not index[0] == "mysql_name" and not index[12] == "":
            RabbitmqCsStatus(index[13],index[14],index[15],correct)
    data.close()
    return MakeResult(correct)
