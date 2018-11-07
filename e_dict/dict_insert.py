#coding = utf-8
'''
此程序用于将字典导入mysql数据库中
'''

import pymysql
import re

def fun(i):
    vol = None
    try:
        pattern = r'(?P<word>^\S+)\s+(?P<statement>.+)'
        vol = re.match(pattern,i).groupdict()
        
    except Exception as e:
        print('error:',e)
        err.append(i)
    if vol is None:
        return None
    return vol

db = pymysql.connect(host = 'localhost',
                    user = 'root',
                    password = '123456',
                    database = 'e_dict',
                    charset = 'utf8')
cursor = db.cursor()
f = open('/home/tarena/aid1808/project/e_dict/dict.txt')
n = 0
for i in f:
    vol = fun(i)  #匹配单词及释义
    if vol is None:
        continue
    n += 1
    #将内容导入数据库中
    try:
        ins = 'insert into dictionary(word,statement) values(%s,%s)'
        cursor.execute(ins,[vol['word'],vol['statement']])
        db.commit()
        print('完成导入第%d个' % n,vol['word'])        
    except Exception as e:
        db.rollback()
        print('Faile',e)
    
f.close()
# cursor.close()
# db.close()