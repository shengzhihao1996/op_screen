#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import socket
import csv
import os

'''
对ip和port建立tcp连接，来测试服务存活。
'''
socket.setdefaulttimeout(3)
def PortCheck(host, port):
    result = "1"
    try:
        s = socket.socket()
        s.connect((host, port))
    except Exception as e:
        print("Exception occurred: {}".format(e),host,port)
        result = "0"
    if result == "1":
        s.close()
    return result

'''
默认端口的逻辑判断
手动添加的端口使用“；”分隔
'''
def IfDefaultPort(id, name, ip, port):
    s = ""
    #mysql
    if port == '-' and id == 0:
        s += 'promecrd{name="'+name+'_3306",check="port"} '+PortCheck(ip, 3306)+'\n'
    #mongo
    elif port == '-' and id == 4:
        s += 'promecrd{name="'+name+'_27017",check="port"} '+PortCheck(ip, 27017)+'\n'
    #redis
    elif port == '-' and id == 8:
        s += 'promecrd{name="'+name+'_6379",check="port"} '+PortCheck(ip, 6379)+'\n'
    #rabbitmq
    elif port == '-' and id == 12:
        s += 'promecrd{name="'+name+'_5672",check="port"} '+PortCheck(ip, 5672)+'\n'
    #memcache
    elif port == '-' and id == 16:
        s += 'promecrd{name="'+name+'_11211",check="port"} '+PortCheck(ip, 11211)+'\n'
        s += 'promecrd{name="'+name+'_11212",check="port"} '+PortCheck(ip, 11212)+'\n'
        s += 'promecrd{name="'+name+'_11213",check="port"} '+PortCheck(ip, 11213)+'\n'
    #crd,字符串查找，有：返回所查开始索引；无，返回-1。
    elif port.find(";") == -1:
        s += 'promecrd{name="'+name+'_'+port+'",check="port"} '+PortCheck(ip, int(port))+'\n'
    elif not port.find(";") == -1:
        for item in port.split(";"):
            s += 'promecrd{name="'+name+'_'+item+'",check="port"} '+PortCheck(ip, int(item))+'\n'
    return s

'''
数据抓取，将所有的条目按string类型抓出，使用”\n“分隔组成一个大的字符串。
'''
def PortMetrics():
    data = open('serverlist.csv')
    f_csv = csv.reader(data)
    s = ""
    for index in f_csv:
        for i in 0,4,8,12,16:
            if not index[0] == "mysql_name" and not index[i] == "":
                s += IfDefaultPort(i,index[i],index[i+1],index[i+2])
    data.close()
    return s