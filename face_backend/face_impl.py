from detector import detector_class
from emotion import emotion_class
from encoder import encoder_class
from utils import align_faces
import numpy as np
import pathlib
import os

class face_impl(object):
    def __init__(self) -> None:
        self.home = pathlib.Path(__file__).parent.absolute()
        print(f"setting home at {self.home}")
        self.detector = detector_class(self.home)
        self.emotional = emotion_class(self.home)
        self.encoder = encoder_class(self.home)
        self.last_name = None
        self.consecutive_frames = 0

    def recognize(self, img):
        # detect faces
        letterboxed, boxes_conf_landms = self.detector.predict(img)
        if len(boxes_conf_landms) == 0:
            self.consecutive_frames = 0
            self.last_name = None
            return [], letterboxed  # Return an empty list if no faces are detected

        # preprocess for emotion analysis and face recognition
        aligned_faces = align_faces(boxes_conf_landms, letterboxed)
        # detect emotions
        emotions = self.emotional.predicts(aligned_faces)
        # make face encodings
        encodings = self.encoder.encode(aligned_faces)
        names = self.encoder.recognize(encodings)
        return list(zip(names, emotions, aligned_faces, boxes_conf_landms)), letterboxed

    def recognize_and_return_info(self, img):
        flist, letterboxed = self.recognize(img)
        if len(flist) == 1:
            name = flist[0][0]  # Get the name from the first recognized face
            if name == self.last_name:
                self.consecutive_frames += 1
            else:
                self.consecutive_frames = 1
                self.last_name = name

            if self.consecutive_frames >= 10:
                # Reset counter and check the information
                self.consecutive_frames = 0
                return self.get_user_info(name)
        else:
            self.consecutive_frames = 0
            self.last_name = None

        return None

    def get_user_info(self, name):
        data_path = self.home / f"face_data/{name}/data.txt"
        if os.path.exists(data_path):
            with open(data_path, "r") as f:
                data = f.readlines()
                info = {}
                for line in data:
                    key, value = line.strip().split(": ")
                    info[key] = value
                return {"student_id": info.get("Student ID"), "password": info.get("Password")}
        return None


face_backend_inst = face_impl()
