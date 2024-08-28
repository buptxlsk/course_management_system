# detect faces using RetinaFace
import numpy as np
import cv2
from backend import detector_tflite
from math import ceil
from itertools import product
from utils import letterbox_image


def preprocess(img, size=640):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = letterbox_image(img, (size, size))
    letterboxed = np.array(img, np.uint8)
    letterboxed = cv2.cvtColor(letterboxed, cv2.COLOR_RGB2BGR)
    preprocessed = img.astype(dtype=np.float32)
    preprocessed -= np.array((104, 117, 123), np.float32)
    # img = img.transpose(2, 0, 1)
    preprocessed = np.expand_dims(img, axis=0)
    preprocessed = preprocessed.astype(np.float32)  # redundant?
    return (
        preprocessed,
        letterboxed,
    )  # preprocessed as model input, letterboxed for plotting


def postprocess(landms, conf, loc, anchors):
    def decode(loc, priors, variances=[0.1, 0.2]):
        boxes = np.concatenate(
            (
                priors[:, :2] + loc[:, :2] * variances[0] * priors[:, 2:],
                priors[:, 2:] * np.exp(loc[:, 2:] * variances[1]),
            ),
            1,
        )
        boxes[:, :2] -= boxes[:, 2:] / 2
        boxes[:, 2:] += boxes[:, :2]
        return boxes

    def decode_landm(pre, priors, variances=[0.1, 0.2]):
        return np.concatenate(
            (
                priors[:, :2] + pre[:, :2] * variances[0] * priors[:, 2:],
                priors[:, :2] + pre[:, 2:4] * variances[0] * priors[:, 2:],
                priors[:, :2] + pre[:, 4:6] * variances[0] * priors[:, 2:],
                priors[:, :2] + pre[:, 6:8] * variances[0] * priors[:, 2:],
                priors[:, :2] + pre[:, 8:10] * variances[0] * priors[:, 2:],
            ),
            1,
        )

    def pynms(dets, thresh):  # 非极大抑制
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        areas = (y2 - y1) * (x2 - x1)
        scores = dets[:, 4]
        keep = []
        index = scores.argsort()[::-1]  # 置信度从大到小排序（下标）

        while index.size > 0:
            i = index[0]
            keep.append(i)

            x11 = np.maximum(x1[i], x1[index[1:]])  # 计算相交面积
            y11 = np.maximum(y1[i], y1[index[1:]])
            x22 = np.minimum(x2[i], x2[index[1:]])
            y22 = np.minimum(y2[i], y2[index[1:]])

            w = np.maximum(
                0, x22 - x11
            )  # 当两个框不想交时x22 - x11或y22 - y11 为负数，
            # 两框不相交时把相交面积置0
            h = np.maximum(0, y22 - y11)  #

            overlaps = w * h
            ious = overlaps / (areas[i] + areas[index[1:]] - overlaps)  # 计算IOU

            idx = np.where(ious <= thresh)[0]  # IOU小于thresh的框保留下来
            index = index[idx + 1]

        return keep

    def filter_box(org_box, conf_thres, iou_thres):  # 过滤掉无用的框
        conf = org_box[..., 4] > conf_thres  # 删除置信度小于conf_thres的BOX
        # print(conf)
        box = org_box[conf == True]
        output = []
        curr_cls_box = np.array(box)
        curr_cls_box[:, :4] = curr_cls_box[:, :4] * 640
        curr_cls_box[:, 5:] = curr_cls_box[:, 5:] * 640
        curr_out_box = pynms(curr_cls_box, iou_thres)  # 经过非极大抑制后输出的BOX下标
        for k in curr_out_box:
            output.append(curr_cls_box[k])  # 利用下标取出非极大抑制后的BOX
        output = np.array(output)
        return output

    boxes = decode(loc, anchors)
    landms = decode_landm(landms, anchors)
    conf = conf[:, 1:2]
    boxes_conf_landms = np.concatenate((boxes, conf, landms), -1)
    boxes_conf_landms = filter_box(boxes_conf_landms, 0.5, 0.45)
    return boxes_conf_landms


def get_anchors(
    size=640, min_sizes=[[16, 32], [64, 128], [256, 512]], steps=[8, 16, 32]
):
    feature_maps = [[ceil(size / step), ceil(size / step)] for step in steps]
    anchors = []
    for k, f in enumerate(feature_maps):
        # -----------------------------------------#
        #   对特征层的高和宽进行循环迭代
        # -----------------------------------------#
        for i, j in product(range(f[0]), range(f[1])):
            for min_size in min_sizes[k]:
                s_kx = min_size / size
                s_ky = min_size / size
                dense_cx = [x * steps[k] / size for x in [j + 0.5]]
                dense_cy = [y * steps[k] / size for y in [i + 0.5]]
                for cy, cx in product(dense_cy, dense_cx):
                    anchors += [cx, cy, s_kx, s_ky]
    output_np = np.array(anchors).reshape(-1, 4)
    return output_np


class detector_class(object):
    def __init__(self, home) -> None:
        print("loading detector model...", end="", flush=True)
        self.home = home
        self.retinaface = detector_tflite.detector_tflite(
            self.home / "model_data/Retinaface_mobilenet0.25.tflite"
        )
        self.anchors = get_anchors()
        print("done")

    def predict(self, img):
        img, letterboxed = preprocess(img)
        landms, conf, loc = self.retinaface.forward(img)
        boxes_conf_landms = postprocess(landms, conf, loc, self.anchors)
        return letterboxed, boxes_conf_landms

    @staticmethod
    def plot_landmarks(letterboxed, boxes_conf_landms):
        for b in boxes_conf_landms:
            text = f"{b[4]}"
            b = list(map(int, b))
            #   b[0]-b[3]为人脸框的坐标，b[4]为得分
            cv2.rectangle(letterboxed, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
            cx = b[0]
            cy = b[1] + 12
            cv2.putText(
                letterboxed,
                text,
                (cx, cy),
                cv2.FONT_HERSHEY_DUPLEX,
                0.5,
                (255, 255, 255),
            )
            #   b[5]-b[14]为人脸关键点的坐标
            cv2.circle(letterboxed, (b[5], b[6]), 1, (0, 0, 255), 4)
            cv2.circle(letterboxed, (b[7], b[8]), 1, (0, 255, 255), 4)
            cv2.circle(letterboxed, (b[9], b[10]), 1, (255, 0, 255), 4)
            cv2.circle(letterboxed, (b[11], b[12]), 1, (0, 255, 0), 4)
            cv2.circle(letterboxed, (b[13], b[14]), 1, (255, 0, 0), 4)
        return letterboxed
