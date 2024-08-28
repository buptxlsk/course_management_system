from tkinter import *
import subprocess
import course_management as cm


class Teacher:
    def __init__(self, TNO):
        self.TNO = TNO
        self.root = Tk()
        self.root.title('课程管理系统')
        self.root.geometry("900x400")

        # Define GUI components
        self.course_label = Label(self.root, text="请选择课程名：")
        self.student_label = Label(self.root, text="已选修此课程的学生：")
        self.student_text = Text(self.root, width=20, height=13)
        self.lb = Listbox(self.root, width=20, height=10)
        Label(self.root, text="学号：").grid(row=3, column=3)
        Label(self.root, text="成绩：").grid(row=5, column=3)
        self.student_id_entry = Entry(self.root, width=5)
        self.student_grape_entry = Entry(self.root, width=5)
        self.student_button = Button(self.root, text="查询", command=self.find_score)
        self.score_button = Button(self.root, text="输入成绩", command=self.change_score)

        # Add Face Registration and Close buttons
        self.face_register_button = Button(self.root, text="人脸录入", command=self.register_face)
        self.close_button = Button(self.root, text="关闭", command=self.root.quit)

        # Center the window
        self.center_window(400, 400)

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
        self.course_label.grid(row=1, column=0)
        self.student_label.grid(row=1, column=1)
        self.student_text.grid(row=2, column=1)
        var = StringVar()
        for item in cm.find_teacher_course(self.TNO):
            self.lb.insert(END, item)
        self.lb.grid(row=2, column=0)
        self.student_id_entry.grid(row=4, column=3)
        self.student_grape_entry.grid(row=6, column=3)
        # Query button
        self.student_button.grid(row=4, column=0)
        # Input grade button
        self.score_button.grid(row=4, column=1)
        # Face registration button
        self.face_register_button.grid(row=5, column=0, padx=10, pady=10)
        # Close button
        self.close_button.grid(row=5, column=1, padx=10, pady=10)

    def find_score(self):
        CNAME = self.lb.get(self.lb.curselection())[0]
        self.student_text.delete(1.0, END)
        cm.find_student_score(self.student_text, CNAME, self.TNO)

    def change_score(self):
        SNO = self.student_id_entry.get()
        GRADE = self.student_grape_entry.get()
        CNAME = self.lb.get(self.lb.curselection())[0]
        cm.change_score(SNO, GRADE, CNAME)
        self.find_score()

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
        self.root.mainloop()


if __name__ == '__main__':
    c = Teacher('刘红')
    c.start()
