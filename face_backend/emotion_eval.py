print("loading libs...", end="", flush=True)
import cv2, numpy as np
from detector import detector_class
from emotion import emotion_class
from encoder import encoder_class
import utils, io, csv

print("done")

emotional = emotion_class()

cnt = 0
faults = 0
# fer2013 dataset
with open("train.csv", "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        emotion = int(row[0])
        pixels = [int(x) for x in row[1].split()]
        img = np.array(pixels, dtype=np.uint8)
        img = np.reshape(img, (48, 48))
        cv2.imshow("1", img)
        img = img.astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        img = np.expand_dims(img, axis=3)
        res = emotional.predict(img)
        emotion_pred = np.argmax(res)
        if emotion_pred != emotion:
            faults += 1
            print(f"whoops! {0 if cnt == 0 else faults / cnt}")
        cv2.waitKey(1)
        cnt += 1
        if cnt % 10 == 0:
            print(f"cnt = {cnt}, {0 if cnt == 0 else faults / cnt}")
        if cnt == 10000:
            exit(0)

