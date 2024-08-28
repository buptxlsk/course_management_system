#!/usr/bin/python3
# coding=utf-8
import pymysql
import numpy as np
from tkinter import *

#选课
def insert_choose_course(SNO, CNO, GRADE):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "INSERT IGNORE INTO SC (SNO, CNO, GRADE) VALUES ('%s', '%s', %d)" % (SNO, CNO, GRADE)
    cursor.execute(sql)
    db.commit()
    db.close()

#退课
def delete_choose_course(SNO, CNO):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "DELETE FROM SC WHERE SNO = '%s' AND CNO = '%s'" % (SNO, CNO)
    cursor.execute(sql)
    db.commit()
    db.close()

#打印学生信息
def display_student(text, LOGN):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "SELECT SNO, SNAME, SEX, AGE, SDEPT FROM S WHERE LOGN='%s'" % LOGN
    cursor.execute(sql)
    col = [desc[0] for desc in cursor.description]
    text.insert(END, ' '.join(col))
    text.insert(END, '\n')
    result = cursor.fetchall()
    for row in result:
        text.insert(END, ' '.join(str(x) for x in row))
        text.insert(END, '\n')
    db.close()

#显示可选课程
def display_course(text, SNO):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "SELECT * FROM C WHERE CNO NOT IN (SELECT CNO FROM SC WHERE SNO='%s')" % SNO
    cursor.execute(sql)
    col = [desc[0] for desc in cursor.description]
    text.insert(END, ' '.join(col))
    text.insert(END, '\n')
    result = cursor.fetchall()
    for row in result:
        text.insert(END, ' '.join(str(x) for x in row))
        text.insert(END, '\n')
    db.close()

#显示已选课程
def display_choose_course(text, SNO):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "SELECT C.CNO, C.CNAME, C.CREDI, C.CDEPT, C.TNAME FROM C JOIN SC ON C.CNO = SC.CNO WHERE SC.SNO='%s'" % SNO
    cursor.execute(sql)
    col = [desc[0] for desc in cursor.description]
    text.insert(END, ' '.join(col))
    text.insert(END, '\n')
    result = cursor.fetchall()
    for row in result:
        text.insert(END, ' '.join(str(x) for x in row))
        text.insert(END, '\n')
    db.close()

#显示学生成绩
def display_score(text, SNO):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "SELECT C.CNO, C.CNAME, SC.GRADE FROM C JOIN SC ON C.CNO = SC.CNO WHERE SC.SNO='%s'" % SNO
    cursor.execute(sql)
    col = [desc[0] for desc in cursor.description]
    text.insert(END, ' '.join(col))
    text.insert(END, '\n')
    result = cursor.fetchall()
    for row in result:
        text.insert(END, ' '.join(str(x) for x in row))
        text.insert(END, '\n')
    db.close()

#老师所上的课程
def find_teacher_course(name):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "SELECT CNAME FROM C WHERE TNAME='%s'" % name
    cursor.execute(sql)
    result = cursor.fetchall()
    db.close()
    return result

#查询选了该老师该课的学生
def find_student_score(text, CNAME, TNAME):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "SELECT S.SNO, S.SNAME, SC.GRADE FROM S JOIN SC ON S.SNO = SC.SNO JOIN C ON SC.CNO = C.CNO WHERE C.CNAME='%s' AND C.TNAME='%s'" % (CNAME, TNAME)
    cursor.execute(sql)
    col = [desc[0] for desc in cursor.description]
    text.insert(END, ' '.join(col))
    text.insert(END, '\n')
    result = cursor.fetchall()
    for row in result:
        text.insert(END, ' '.join(str(x) for x in row))
        text.insert(END, '\n')
    db.close()

#老师修改成绩
def change_score(SNO, GRADE, CNAME):
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4',
                         database="student")
    cursor = db.cursor()

    # 使用参数化查询获取课程编号
    sql = "SELECT CNO FROM C WHERE CNAME=%s"
    cursor.execute(sql, (CNAME,))
    result = cursor.fetchone()

    if result:
        CNO = result[0]
        # 使用参数化查询更新成绩
        sql = "REPLACE INTO SC (SNO, CNO, GRADE) VALUES (%s, %s, %s)"
        cursor.execute(sql, (SNO, CNO, int(GRADE)))
        db.commit()
    else:
        print(f"未找到课程 {CNAME} 对应的课程编号")

    db.close()

