#!/usr/bin/python3
#coding=utf-8

from socket import *
import sys
import getpass


#創建網絡連接
def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket()
    try:
        s.connect((HOST,PORT))
    except Exception as e:
        print(e)
        return

    while True:
        print('''
            =========Welcome=========
            --1.註冊  2.登入  3.退出--
            =========================
            ''')
        try:    
            cmd = int(input("輸入選項>>"))
        except Exception as e:
            print("命令錯誤")
            continue
        
        if cmd not in [1,2,3]:
            print("請輸入正確選項")
            sys.stdin.flush()  #清除標準輸入，確保每次輸入都會被單獨識別
            continue
        elif cmd == 1:
            r = do_register(s)
            if r == 0:
                print("註冊成功")
                #longin(s,name) #進入二級介面
            elif r == 1:
                print("用戶名已存在")
            else:
                print("註冊失敗")
        elif cmd == 2:
            name = do_login(s)
            if name:
                print("登入成功")
                #進入二級介面，可以循環查詢
                login(s,name)
            else:
                print("用戶名或密碼不正確")
        elif cmd == 3:
            s.send(b'E')
            sys.exit("謝謝使用")

def do_register(s):
    while True:  #怕輸入錯誤，可以重新再來過/循環輸入
        #輸入註冊訊息
        name = input("User:")
        passwd = getpass.getpass()
        passwd1 = getpass.getpass('Again:')  #再次確認輸入密碼是否一致

        if (' ' in name) or (' ' in passwd):
            print("用戶名與密碼不許有空格")
            continue
        if passwd != passwd1:
            print("兩次密碼不一致")
            continue
        
        msg = 'R {} {}'.format(name,passwd)
        #發送請求
        s.send(msg.encode())
        #等待回復
        data = s.recv(128).decode()
        if data == 'OK':
            return 0
        elif data == 'EXISTS':
            return 1
        else:
            return 2

def do_login(s):
    name = input("User:")
    passwd = getpass.getpass()
    msg = "L {} {}".format(name,passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()

    if data == 'OK':
        return name
    else:
        return 

def login(s,name):
    while True:
        print('''
            ===========查詢介面==========
            1.查詞   2.歷史紀錄    3.退出 
            ============================
            ''')
        try:    
            cmd = int(input("輸入選項>>"))
        except Exception as e:
            print("命令錯誤")
            continue
        
        if cmd not in [1,2,3]:
            print("請輸入正確選項")
            sys.stdin.flush()  
            continue
        elif cmd == 1:
            do_query(s,name)
        elif cmd == 2:
            do_hist(s,name)
        elif cmd == 3:
            return

def do_query(s,name):
    while True:
        word = input("單詞:")
        if word == '##':
            break   #輸入##代表退出
        msg = "Q {} {}".format(name,word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            print(data)
        else:
            print("沒有查到該單詞")

def do_hist(s,name):
    msg = 'H {}'.format(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print("無歷史紀錄")

if __name__ == '__main__':
    main()