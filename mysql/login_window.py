from tkinter import *
import course_class
import teacher_class
import pymysql
import sys
import os
import cv2

current_dir = os.path.dirname(os.path.abspath(__file__))
face_backend_path = os.path.join(current_dir, '../face_backend')
sys.path.append(face_backend_path)
from face_impl import face_impl

def judge():
    login = user_entry.get()
    password = password_entry.get()
    db = pymysql.connect(host="localhost", port=3306, user="root", password="123456", charset='utf8mb4', database="student")
    cursor = db.cursor()
    sql = "SELECT S.SNO FROM S where S.LOGN='%s' and S.PSWD='%s'" % (login, password)
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        cursor = db.cursor()
        sql = "SELECT T.TNAME FROM T where T.LOGN='%s' and T.PSWD='%s'" % (login, password)
        cursor.execute(sql)
        result = cursor.fetchall()
    else:
        return result
    return result

def start():
    result = judge()
    if len(result) != 0:
        root.destroy()
        if result[0][0][0] == 'S':
            c = course_class.course(result[0][0])
            c.start()
        else:
            t = teacher_class.Teacher(result[0][0])
            t.start()
    else:
        Label(root, text="用户名或密码错误，请重新输入").grid(row=3, column=1)

def face_recognition_login():
    fb = face_impl()
    cap = cv2.VideoCapture(0)  # Open the default camera

    unknown_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image from camera")
            break

        result = fb.recognize_and_return_info(frame)
        if result:
            user_entry.delete(0, END)
            user_entry.insert(0, result['student_id'])

            password_entry.delete(0, END)
            password_entry.insert(0, result['password'])

            start()  # Automatically call the login function
            break

        if fb.last_name == "Unknown":
            unknown_frames += 1
        else:
            unknown_frames = 0

        if unknown_frames >= 30:
            Label(root, text="人脸识别失败").grid(row=3, column=1)
            break

    cap.release()
    cv2.destroyAllWindows()

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    position_top = int(screen_height / 2 - height / 2)
    position_right = int(screen_width / 2 - width / 2)
    window.geometry(f'{width}x{height}+{position_right}+{position_top}')

root = Tk()
root.title("课程管理系统")

# Set window size
window_width = 400
window_height = 200

# Center the window
center_window(root, window_width, window_height)

# Centering the input section within the window
Label(root, text="用户名").grid(row=0, column=0, padx=10, pady=10)
user_entry = Entry(root, width=15)
user_entry.grid(row=0, column=1, padx=10, pady=10)

Label(root, text="密码").grid(row=1, column=0, padx=10, pady=10)
password_entry = Entry(root, width=15, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

# Add face recognition login button
face_button = Button(root, text="人脸识别登录", command=face_recognition_login)
face_button.grid(row=2, column=0, padx=10, pady=20)

# Add normal login button
star_button = Button(root, text="登陆", command=start)
star_button.grid(row=2, column=1, pady=20)

# Adjusting the padding and alignment
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

root.mainloop()
