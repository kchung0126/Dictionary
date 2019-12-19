'''
Name:George
Date:2019-12-18
email:kchung0428@gmail.com
modules: pymysql signal sys os time socket
This is a Dictionary look-up project practice
'''

from socket import *
import os
import time
import signal
import pymysql
import sys

DICT_TEXT = "./dict.txt"
HOST = '0.0.0.0'
PORT = 8000
ADDR = (HOST,PORT)

def main():
	db = pymysql.connect('localhost','root','a123456','dict')
	s = socket()
	s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
	s.bind(ADDR)
	s.listen(5)

	signal.signal(signal.SIGCHLD,signal.SIG_IGN)

	while True:
		try:
			c,addr = s.accept()
			print("Connect from:",addr)
		except KeyboardInterrupt:
			s.close()
			sys.exit('log out')
		except Exception as e:
			print(e)
			continue

		pid = os.fork()
		if pid == 0:
			s.close()
			do_child(c,db)
		else:
			c.close()
			continue

def do_child(c,db):  #循環接收客戶端請求
    while True:
        data = c.recv(123).decode()
        print(c.getpeername(),":",data)
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(c,db,data)
        elif data[0] == 'L':
            do_login(c,db,data)
        elif data[0] == 'Q':
            do_query(c,db,data)
        elif data[0] == 'H':
            do_hist(c,db,data)

#登入
def do_login(c,db,data):
    print("登入操作")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user \
    where name='%s' and passwd='%s'"%(name,passwd)

    cursor.execute(sql)
    r = cursor.fetchone()

    if r == None:
        c.send(b'FALL')
    else:
        print("%s登入成功"%name)
        c.send(b'OK')

#註冊
def do_register(c,db,data):
    print("註冊操作")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()
    #查找是否已經有相同username
    sql = "select * from user where name='%s'"%name
    cursor.execute(sql)
    r = cursor.fetchone()
    #如果存在，就退出
    if r != None:
        c.send(b'EXISTS')
        return
    #如果不存在，就插入
    sql = "insert into user (name,passwd) values \
    ('%s','%s')"%(name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()
        c.send(b'FALL')
    else:
        print("%s註冊成功"%name)
#查詞
def do_query(c,db,data):
    print("查詢操作")
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()

    def insert_history():
        tm = time.ctime()

        sql = "insert into hist (name,word,time) \
        values('%s','%s','%s')"%(name,word,tm)
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()

    #文本查詢方法
    try:
        f = open(DICT_TEXT)
    except:
        c.send(b'FALL')
        return
    #在文本中查單詞，利用首單詞比對
    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:
            c.send(b'FALL')
            f.close()
            return
        elif tmp == word:
            c.send(b'OK')
            time.sleep(0.1)
            c.send(line.encode())
            f.close()
            insert_history()  #查找成功，插入紀錄
            return  #查詢到了，所以沒必要繼續查
    c.send(b'FALL')
    f.close()

#查歷史紀錄
def do_hist(c,db,data):
    print("歷史紀錄操作")
    l = data.split(' ')
    name = l[1]
    cursor = db.cursor()

    sql = "select * from hist where name='%s'"%name
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        c.send(b'FALL')
        return
    else:
        c.send(b'OK')
    
    for i in r:
        time.sleep(0.1)
        msg = "%s %s %s"%(i[1],i[2],i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')

if __name__ == '__main__':
    main()