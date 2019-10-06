#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import socket
import csv
import os


'''
数据抓取，将所有的条目按string类型抓出，使用”\n“分隔组成一个大的字符串。
'''
def RedisMsMetrics():
    data = open('666.csv')
    f_csv = csv.reader(data)
    s = ""
    for index in f_csv:
        if  index[0] != "mysql_name" and  index[8] != "":
            s += RedisMsStatus(str(index[9]), str(index[10]))
    data.close()
    return s

'''
redis主从状态
'''
def RedisMsCheck(ip, port):
    redis_slave_status={}
    cmd = "redis-cli   -h "+ip+" -p "+port+" info replication|sed '1d'"
    redis_status = os.popen(cmd).read()
    
    for i in redis_status.split("\n"):
        if i == "":
            continue
        redis_slave_status[i.split(":")[0].strip()]=i.split(":")[1].strip()
    if redis_slave_status['role'] == 'slave'and redis_slave_status['master_link_status'] == 'up':
        return "promecrd{name='H:"+redis_slave_status['master_host']+"_S:"+ip+"',check='redis_ms'} 1\n"
    elif redis_slave_status['role'] == 'slave'and redis_slave_status['master_link_status'] != 'up':
        return "promecrd{name='H:"+redis_slave_status['master_host']+"_S:"+ip+"',check='redis_ms'} 0\n"
    else:
        return ""

def RedisMsStatus(ip, port):
    s = ""
    if port == '-':
        return RedisMsCheck(ip, "6379")
    elif port.find(";") == -1:
        return RedisMsCheck(ip, port)
    elif port.find(";") != -1:
        for item in port.split(";"):
            s += RedisMsCheck(ip, item)
        return s
    else:
        return ""