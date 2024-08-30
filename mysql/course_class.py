import subprocess
from tkinter import *
import course_management as cm

class course:
    def __init__(self, SNO):
        self.root = Tk()
        self.root.wm_title("课程管理系统")
        self.root.geometry("900x400")  # Set initial size
        self.SNO = SNO
        self.student_label = Label(self.root, text="学生详细信息")
        self.course_label = Label(self.root, text="可选课程")
        self.score_label = Label(self.root, text="已修课程成绩")
        self.choose_course_label = Label(self.root, text="已选课程")
        self.course_entry_label = Label(self.root, text="请输入课程号")
        self.student_text = Text(self.root, height=10, width=50, state=DISABLED)
        self.course_text = Text(self.root, height=10, width=70, state=DISABLED)
        self.score_text = Text(self.root, height=10, width=50, state=DISABLED)
        self.choose_course_text = Text(self.root, height=10, width=70, state=DISABLED)
        self.course_entry = Entry(self.root, width=20)
        self.course_button = Button(self.root, text="选课", command=self.choose_course)
        self.course_button2 = Button(self.root, text="退课", command=self.delete_course)
        self.course_button3 = Button(self.root, text="关闭", command=self.root.quit)

        # Add the Face Registration button
        self.face_register_button = Button(self.root, text="人脸录入", command=self.register_face)

        self.center_window(1100,400)  # Center the window

    def center_window(self, width, height):
        # Get the screen dimension
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the center position
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))

        # Set the position of the window
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def inilize(self):
        self.student_label.grid(row=0, column=0, sticky=W)
        self.student_text.grid(row=1, column=0, sticky=E)
        self.course_label.grid(row=0, column=1, sticky=W)
        self.course_text.grid(row=1, column=1, sticky=E)
        self.score_label.grid(row=3, column=0, sticky=W)
        self.score_text.grid(row=4, column=0, sticky=E)
        self.choose_course_label.grid(row=3, column=1, sticky=W)
        self.choose_course_text.grid(row=4, column=1, sticky=E)
        self.course_entry_label.grid(row=0, column=3)
        self.course_entry.grid(row=1, column=3, padx=20)
        self.course_button.grid(row=2, column=3, padx=10)
        self.course_button2.grid(row=3, column=3, padx=10)
        self.course_button3.grid(row=4, column=3, padx=10)
        self.face_register_button.grid(row=5, column=3, padx=10)

    # 选课
    def choose_course(self):
        course_number = self.course_entry.get()
        cm.insert_choose_course(self.SNO, str(course_number), 0)
        self.update_ui()

    # 退课
    def delete_course(self):
        course_number = self.course_entry.get()
        cm.delete_choose_course(str(course_number))
        self.update_ui()

    # 更新ui
    def update_ui(self):
        # Clear the text widgets and update with new data
        self.student_text.config(state=NORMAL)
        self.course_text.config(state=NORMAL)
        self.score_text.config(state=NORMAL)
        self.choose_course_text.config(state=NORMAL)

        self.student_text.delete(1.0, END)
        self.course_text.delete(1.0, END)
        self.score_text.delete(1.0, END)
        self.choose_course_text.delete(1.0, END)

        cm.display_student(self.student_text, self.SNO)
        cm.display_course(self.course_text, self.SNO)
        cm.display_score(self.score_text, self.SNO)
        cm.display_choose_course(self.choose_course_text, self.SNO)

        self.student_text.config(state=DISABLED)
        self.course_text.config(state=DISABLED)
        self.score_text.config(state=DISABLED)
        self.choose_course_text.config(state=DISABLED)

    # Face registration method
    def register_face(self):
        try:
            # Run the face_input.py script
            subprocess.run(
                ["python", "D:\\Code\\course_management_system\\face_backend\\face_input.py"],
                shell=True,
            )
        except Exception as e:
            print(f"Error during face registration: {e}")

    def start(self):
        self.inilize()
        self.update_ui()
        self.root.mainloop()


if __name__ == '__main__':
    c = course('S5')
    c.start()
