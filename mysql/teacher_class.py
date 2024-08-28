from tkinter import *
import course_management as cm
import subprocess

class Teacher:
    def __init__(self, TNO):
        self.TNO = TNO
        self.root = Tk()
        self.root.title("课程管理系统")
        self.root.geometry("700x300")  # 设置初始窗口大小

        self.center_window(550, 400)  # 将窗口居中显示

        self.course_label = Label(self.root, text="请选择课程名：", state=DISABLED)
        self.student_label = Label(self.root, text="已选修此课程的学生：", state=DISABLED)
        self.student_text = Text(self.root, width=30, height=14, state=DISABLED)  # 设置为不可修改
        self.lb = Listbox(self.root, width=30, height=10, state=DISABLED)  # 设置为不可修改
        Label(self.root, text="学号：", state=DISABLED).grid(row=3, column=3)
        Label(self.root, text="成绩：", state=DISABLED).grid(row=5, column=3)
        self.student_id_entry = Entry(self.root, width=10)  # 输入框保持可用
        self.student_grape_entry = Entry(self.root, width=10)  # 输入框保持可用
        self.student_button = Button(self.root, text="查询", command=self.find_score, state=DISABLED)  # 设置为不可用
        self.score_button = Button(self.root, text="输入成绩", command=self.change_score, state=DISABLED)  # 设置为不可用
        self.close_button = Button(self.root, text="关闭", command=self.root.quit, state=DISABLED)  # 设置为不可用

        # 添加录入人脸信息按钮
        self.face_register_button = Button(self.root, text="录入人脸信息", command=self.register_face, state=DISABLED)  # 设置为不可用

    def center_window(self, width, height):
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算窗口的位置，使其居中
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        # 设置窗口的位置
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def inilize(self):
        self.course_label.grid(row=1, column=0)
        self.student_label.grid(row=1, column=1)
        self.student_text.grid(row=2, column=1)
        var = StringVar()
        for item in cm.find_teacher_course(self.TNO):
            self.lb.insert(END, item)
        self.lb.grid(row=2, column=0)
        self.student_id_entry.grid(row=4, column=3)
        self.student_grape_entry.grid(row=6, column=3)
        # 查询
        self.student_button.grid(row=4, column=0)
        # 输入成绩
        self.score_button.grid(row=4, column=1)
        # 关闭按钮
        self.close_button.grid(row=7, column=1)

        # 录入人脸信息按钮
        self.face_register_button.grid(row=7, column=0)

    # 查询选了该老师该课的学生成绩
    def find_score(self):
        selected = self.lb.curselection()
        if selected:
            CNAME = self.lb.get(selected[0])
            self.student_text.config(state=NORMAL)  # 允许更新内容
            self.student_text.delete(1.0, END)
            cm.find_student_score(self.student_text, CNAME, self.TNO)
            self.student_text.config(state=DISABLED)  # 更新后设置为只读
        else:
            print("请选择一个课程")

    # 修改成绩
    def change_score(self):
        SNO = self.student_id_entry.get()
        GRADE = self.student_grape_entry.get()
        selected = self.lb.curselection()
        if selected:
            CNAME = self.lb.get(selected[0])
            cm.change_score(SNO, GRADE, CNAME)
            self.find_score()
        else:
            print("请选择一个课程")

    # 录入人脸信息
    def register_face(self):
        try:
            # 运行 face_input.py 脚本
            subprocess.run(
                ["python", "D:\\Code\\course_management_system\\face_backend\\face_input.py"],
                shell=True,
            )
        except Exception as e:
            print(f"Error during face registration: {e}")

    def start(self):
        self.inilize()
        self.root.mainloop()

if __name__ == '__main__':
    c = Teacher('刘红')
    c.start()
