import cv2
import numpy as np
import pathlib
from tkinter import Tk, Label, Entry, Button
import sys

from detector import detector_class
from emotion import emotion_class
from encoder import encoder_class
from utils import align_faces


class face_impl(object):
    def __init__(self) -> None:
        home = pathlib.Path(__file__).parent.absolute()
        print(f"setting home at {home}")
        self.detector = detector_class(home)
        self.emotional = emotion_class(home)
        self.encoder = encoder_class(home)

    def recognize(self, img):
        # detect faces
        letterboxed, boxes_conf_landms = self.detector.predict(img)
        if len(boxes_conf_landms) == 0:
            return [], letterboxed  # Return an empty list if no faces are detected

        # preprocess for emotion analysis and face recognition
        aligned_faces = align_faces(boxes_conf_landms, letterboxed)
        # detect emotions
        emotions = self.emotional.predicts(aligned_faces)
        # make face encodings
        encodings = self.encoder.encode(aligned_faces)
        names = self.encoder.recognize(encodings)
        return list(zip(names, emotions, aligned_faces, boxes_conf_landms)), letterboxed

    def register(self, img, name, student_id, password):
        # 检测人脸
        letterboxed, boxes_conf_landms = self.detector.predict(img)
        if len(boxes_conf_landms) == 0:
            return False, "未检测到人脸"
        elif len(boxes_conf_landms) != 1:
            return False, "有多于一个人脸"

        # 预处理以进行情感分析和人脸识别
        aligned_faces = align_faces(boxes_conf_landms, letterboxed)
        # 生成人脸编码
        encodings = self.encoder.encode(aligned_faces)

        # 注册人脸并保存信息
        self.encoder.register_face(name, aligned_faces[0], encodings[0], student_id, password)
        return True, "注册成功"

    def unregister(self, name):
        return self.encoder.unregister(name)

    def lists(self):
        return self.encoder.lists()

    def purge(self):
        return self.encoder.purge()

    @staticmethod
    def plot_recognized(flist, letterboxed):
        if not flist:  # Check if flist is empty
            print("No faces recognized.")
            return letterboxed

        names, emotions, aligned_faces, boxes_conf_landms = zip(*flist)
        letterboxed = detector_class.plot_landmarks(letterboxed, boxes_conf_landms)
        letterboxed = encoder_class.plot_names(letterboxed, names, boxes_conf_landms)
        letterboxed = emotion_class.plot_emotion(
            letterboxed, emotions, boxes_conf_landms
        )
        return letterboxed


def show_registration_window(fb, img):
    def submit():
        name = name_entry.get()
        student_id = student_id_entry.get()
        password = password_entry.get()
        success, msg = fb.register(img, name, student_id, password)
        print(f"register: {msg}")
        reg_window.destroy()
        cv2.destroyAllWindows()  # 关闭所有 OpenCV 窗口
        sys.exit()  # 退出程序

    reg_window = Tk()
    reg_window.title("注册人脸信息")

    # 居中显示窗口
    window_width = 300
    window_height = 300
    screen_width = reg_window.winfo_screenwidth()
    screen_height = reg_window.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (window_width / 2))
    y_cordinate = int((screen_height / 2) - (window_height / 2))
    reg_window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")

    # 创建标签和输入框
    Label(reg_window, text="姓名:").pack(pady=5)
    name_entry = Entry(reg_window)
    name_entry.pack(pady=5)

    Label(reg_window, text="学号:").pack(pady=5)
    student_id_entry = Entry(reg_window)
    student_id_entry.pack(pady=5)

    Label(reg_window, text="密码:").pack(pady=5)
    password_entry = Entry(reg_window, show="*")
    password_entry.pack(pady=5)

    # 提交按钮
    Button(reg_window, text="提交", command=submit).pack(pady=20)

    reg_window.mainloop()


if __name__ == "__main__":
    fb = face_impl()
    cap = cv2.VideoCapture(0)
    while True:
        ok, img = cap.read()
        assert ok
        flist, letterboxed = fb.recognize(img)
        recognized = fb.plot_recognized(flist, letterboxed)

        # Add prompt message to the image
        cv2.putText(
            recognized,
            "Press 's' to register, 'q' to quit",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        # Display the image
        cv2.imshow("Recognized Faces", recognized)
        k = cv2.waitKey(1)

        if k == ord("q"):
            break
        elif k == ord("s") and len(flist) == 1:
            cv2.destroyAllWindows()
            show_registration_window(fb, img)

    cap.release()
    cv2.destroyAllWindows()

