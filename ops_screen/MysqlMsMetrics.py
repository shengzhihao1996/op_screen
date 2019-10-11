#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import requests
import socket
import csv
import os

'''
mysql主从状态
'''
def MysqlMsCheck(ip, port, passwd):
    mysql_slave_status={}
    cmd = 'mysql -h '+ip+' -P '+port+' -u'+passwd.split("/")[0]+' -p'+passwd.split("/")[1]+' -e "show slave status\G" |grep -E "Master_Host|Master_Port|Slave_IO_Running|Slave_SQL_Running:|Last_SQL_Errno"'
    mysql_status = os.popen(cmd).read()
    if mysql_status != "" and mysql_status.find("Can't connect to MySQL server") == -1:
        for i in mysql_status.split("\n"):
            if i == "":
                continue
            mysql_slave_status[i.split(":")[0].strip()]=i.split(":")[1].strip()
        if mysql_slave_status['Last_SQL_Errno'] != '0' or mysql_slave_status['Slave_IO_Running'] != 'Yes' or mysql_slave_status['Slave_SQL_Running'] != 'Yes' :
            print("S:"+ip, mysql_slave_status)
            return 'promecrd{name="H:'+mysql_slave_status['Master_Host']+'_S:'+ip+'",check="mysql_ms"} 0\n'
        else:
            return 'promecrd{name="H:'+mysql_slave_status['Master_Host']+'_S:'+ip+'",check="mysql_ms"} 1\n'
    else:
        return ""

def MysqlMsStatus(ip, port, passwd):
    s = ""
    if port == '-' and passwd != "":
        return MysqlMsCheck(ip, "3306", passwd)
    elif port.find(";") == -1 and passwd != "":
        return MysqlMsCheck(ip, port, passwd)
    elif port.find(";") != -1 and passwd != "":
        for item in port.split(";"):
            s += MysqlMsCheck(ip, item, passwd)
        return s
    else:
        return ""

'''
数据抓取，将所有的条目按string类型抓出，使用”\n“分隔组成一个大的字符串。
'''
def MysqlMsMetrics():
    data = open('serverlist.csv')
    f_csv = csv.reader(data)
    s = ""
    for index in f_csv:
        if index[0] != "mysql_name" and index[0] != "":
            s += MysqlMsStatus(str(index[1]), str(index[2]), str(index[3]))
    data.close()
    return s