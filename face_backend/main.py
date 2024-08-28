"""
    THIS FILE IS DEPRECATED, USE face_impl.py INSTEAD
"""

print("loading libs...", end="", flush=True)
import cv2, numpy as np
from detector import detector_class
from emotion import emotion_class  # , plot_emotions
from encoder import encoder_class
import utils, io

print("done")

detector = detector_class()
emotional = emotion_class()
encoder = encoder_class()

cap = cv2.VideoCapture(0)
while True:
    ok, img = cap.read()
    assert ok
    # detect faces
    letterboxed, boxes_conf_landms = detector.predict(img)
    # plot face rectangle and landmarks
    detected = detector.plot_landmarks(letterboxed.copy(), boxes_conf_landms)
    # preprocess for emotion analysis and face recognition
    aligned_faces = utils.align_faces(boxes_conf_landms, letterboxed)
    # detect emotions
    emotions = emotional.predicts(aligned_faces)
    emotional.plot_emotion(detected, emotions, boxes_conf_landms)
    # make face encodings
    encodings = encoder.encode(aligned_faces)
    names = encoder.recognize(encodings)
    encoder.plot_names(detected, names, boxes_conf_landms)
    cv2.imshow("", detected)
    utils.show_faces_aligned(aligned_faces)

    k = cv2.waitKey(1)

    if k == ord("q"):
        break
    elif k == ord("s"):
        if len(encodings) != 1:
            continue
        name = input("your name: ")
        encoder.register_face(name, aligned_faces[0], encodings[0])
