#dict.py
import pymysql
import re

f = open('dict.txt')
db = pymysql.connect('localhost','root','a123456','dict')
cursor = db.cursor()

for line in f:
    l = re.split(r'\s+',line)  #切割dict.txt，把單詞跟解釋分開
    word = l[0]
    interpret = ' '.join(l[1:])
    sql = "insert into words (word,interpret) values('%s','%s')"%(word,interpret)

    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()
f.close()