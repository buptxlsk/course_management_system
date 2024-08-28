from detector import detector_class
from emotion import emotion_class  # , plot_emotions
from encoder import encoder_class
from utils import align_faces
import numpy as np
import pathlib


class face_impl(object):
    def __init__(self) -> None:
        home = pathlib.Path(__file__).parent.absolute()
        print(f"setting home at {home}")
        self.detector = detector_class(home)
        self.emotional = emotion_class(home)
        self.encoder = encoder_class(home)

    # def recognize(self, img) -> list[tuple[str, str, np.ndarray, np.ndarray]]:
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

    # def register(self, img, name) -> tuple[bool, str]:
    def register(self, img, name):
        # detect faces
        letterboxed, boxes_conf_landms = self.detector.predict(img)
        if len(boxes_conf_landms) == 0:
            return False, "未检测到人脸"
        elif len(boxes_conf_landms) != 1:
            return False, "有多于一个人脸"
        # preprocess for emotion analysis and face recognition
        aligned_faces = align_faces(boxes_conf_landms, letterboxed)
        # make face encodings
        encodings = self.encoder.encode(aligned_faces)
        self.encoder.register_face(name, aligned_faces[0], encodings[0])
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


face_backend_inst = face_impl()

if __name__ == "__main__":
    import cv2

    fb = face_impl()
    cap = cv2.VideoCapture(0)
    while True:
        ok, img = cap.read()
        assert ok
        flist, letterboxed = fb.recognize(img)
        recognized = fb.plot_recognized(flist, letterboxed)

        # 显示识别后的图像
        cv2.imshow("Recognized Faces", recognized)
        k = cv2.waitKey(1)

        if k == ord("q"):
            break
        elif k == ord("s") and len(flist) == 1:
            cv2.destroyAllWindows()
            name = input("register: enter name: ")
            success, msg = fb.register(img, name)
            print(f"register: {msg}")
        elif k == ord("d"):
            cv2.destroyAllWindows()
            name = input("unregister: enter name: ")
            res = fb.unregister(name)
            if res:
                print(f"removed user {name}")
            else:
                print(f"user {name} doesn't exist")
        elif k == ord("l"):
            cv2.destroyAllWindows()
            for n, p in fb.lists():
                cv2.imshow(f"{n}", p)
            cv2.waitKey(-1)
            cv2.destroyAllWindows()
        elif k == ord("p"):
            fb.purge()

    cap.release()
    cv2.destroyAllWindows()

