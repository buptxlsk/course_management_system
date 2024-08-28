# detect facial expression
# model from DeepFace
from backend import emotion_tflite
import cv2, numpy as np
# import matplotlib.pyplot as plt
from PIL import Image
import io

EMOTION_LABELS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


def resize_image(img: np.ndarray, target_size) -> np.ndarray:
    """
    Resize an image to expected size of a ml model with adding black pixels.
    Args:
        img (np.ndarray): pre-loaded image as numpy array
        target_size (tuple): input shape of ml model
    Returns:
        img (np.ndarray): resized input image
    """
    factor_0 = target_size[0] / img.shape[0]
    factor_1 = target_size[1] / img.shape[1]
    factor = min(factor_0, factor_1)

    dsize = (
        int(img.shape[1] * factor),
        int(img.shape[0] * factor),
    )
    img = cv2.resize(img, dsize)

    diff_0 = target_size[0] - img.shape[0]
    diff_1 = target_size[1] - img.shape[1]

    # Put the base image in the middle of the padded image
    img = np.pad(
        img,
        (
            (diff_0 // 2, diff_0 - diff_0 // 2),
            (diff_1 // 2, diff_1 - diff_1 // 2),
            # (0, 0),
        ),
        "constant",
    )

    # double check: if target image is not still the same size with target.
    if img.shape[0:2] != target_size:
        img = cv2.resize(img, target_size)

    # make it 4-dimensional how ML models expect
    # img = np.expand_dims(img, axis=0)

    if img.max() > 1:
        img = (img.astype(np.float32) / 255.0).astype(np.float32)

    return img


def preprocess(img):
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_gray = resize_image(img_gray, (48, 48))
    img_gray = np.expand_dims(img_gray, axis=0)
    img_gray = np.expand_dims(img_gray, axis=3)
    return img_gray


def postprocess(res):
    res = np.squeeze(res)
    idx = np.argmax(res)

    print(f"{idx}:{res[idx]:.4f}={EMOTION_LABELS[idx]}")


def plot_emotions_vector(img, emotion_confidences):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # 创建一个包含两个子图的图表
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # 在第一个子图上显示图像
    ax1.imshow(img)
    ax1.axis("off")  # 不显示坐标轴
    ax1.set_title("Face Image")
    print(emotion_confidences.tolist())

    # 在第二个子图上绘制柱状图
    ax2.bar(EMOTION_LABELS, emotion_confidences.tolist())
    ax2.set_ylim([0, 1])  # 置信度的范围是0到1
    ax2.set_title("Emotion Confidences")
    ax2.set_ylabel("Confidence")
    ax2.set_xlabel("Emotions")
    ax2.set_xticklabels(EMOTION_LABELS, rotation=45)  # 旋转标签以便显示清晰

    # 显示整个图表
    plt.tight_layout()
    # plt.show()
    buffer = io.BytesIO()
    plt.savefig(buffer)
    plt.clf()
    # 获取图
    image = Image.open(buffer)
    image = np.asarray(image)
    image = image[:, :, :3]
    # matplotlib RGB 转 OpenCV BGR
    image = image[:, :, ::-1]
    # print(image.shape)
    # cv2.imwrite("test.jpg", image)
    return image


class emotion_class(object):
    def __init__(self, home) -> None:
        print("loading emotion model...", end="", flush=True)
        self.home = home
        self.emotion = emotion_tflite.emotion_tflite(
            self.home / "model_data/facial_expression_model.tflite"
        )

        print("done")

    def predict(self, face):
        # face = preprocess(face)
        res = self.emotion.forward(face)
        res = np.squeeze(res)
        # postprocess(res)
        return res

    def predicts(self, faces):
        emotions = []
        for face in faces:
            face = preprocess(face)
            conf = self.predict(face)
            emotion = EMOTION_LABELS[np.argmax(conf)]
            emotions.append(emotion)
        return emotions

    @staticmethod
    def plot_emotion(letterboxed, emotions, boxes_conf_landms):
        for e, b in zip(emotions, boxes_conf_landms):
            b = list(map(int, b))
            #   b[0]-b[3]为人脸框的坐标，b[4]为得分
            cx = b[0]
            cy = b[1] + 24
            cv2.putText(
                letterboxed, e, (cx, cy), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 127, 70)
            )
        return letterboxed
