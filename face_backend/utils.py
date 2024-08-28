import numpy as np, math, cv2, base64

def letterbox_image(image, size):
    ih, iw, _ = np.shape(image)
    w, h = size
    scale = min(w / iw, h / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)

    image = cv2.resize(image, (nw, nh))
    new_image = np.ones([size[1], size[0], 3]) * 128
    new_image[
        (h - nh) // 2 : nh + (h - nh) // 2, (w - nw) // 2 : nw + (w - nw) // 2
    ] = image
    return new_image


# get cropped images of aligned faces
# use letterbox before feeding to models
def align_faces(boxes_conf_landms, letterboxed):
    def align_face(img, landmark):
        if landmark.shape[0] == 68:
            x = landmark[36, 0] - landmark[45, 0]
            y = landmark[36, 1] - landmark[45, 1]
        elif landmark.shape[0] == 5:
            x = landmark[0, 0] - landmark[1, 0]
            y = landmark[0, 1] - landmark[1, 1]
        # 眼睛连线相对于水平线的倾斜角
        if x == 0:
            angle = 0
        else:
            # 计算它的弧度制
            angle = math.atan(y / x) * 180 / math.pi
        center = (img.shape[1] // 2, img.shape[0] // 2)
        RotationMatrix = cv2.getRotationMatrix2D(center, angle, 1)
        # 仿射函数
        new_img = cv2.warpAffine(
            img,
            RotationMatrix,
            (img.shape[1], img.shape[0]),
            borderValue=(128, 128, 128),
        )
        RotationMatrix = np.array(RotationMatrix)
        new_landmark = []
        for i in range(landmark.shape[0]):
            pts = []
            pts.append(
                RotationMatrix[0, 0] * landmark[i, 0]
                + RotationMatrix[0, 1] * landmark[i, 1]
                + RotationMatrix[0, 2]
            )
            pts.append(
                RotationMatrix[1, 0] * landmark[i, 0]
                + RotationMatrix[1, 1] * landmark[i, 1]
                + RotationMatrix[1, 2]
            )
            new_landmark.append(pts)

        new_landmark = np.array(new_landmark)

        return new_img, new_landmark

    aligned_faces = []
    for boxes_conf_landm in boxes_conf_landms:
        # ----------------------#
        #   图像截取，人脸矫正
        # ----------------------#
        boxes_conf_landm = np.maximum(boxes_conf_landm, 0)
        crop_img = np.array(letterboxed)[
            int(boxes_conf_landm[1]) : int(boxes_conf_landm[3]),
            int(boxes_conf_landm[0]) : int(boxes_conf_landm[2]),
        ]
        landmark = np.reshape(boxes_conf_landm[5:], (5, 2)) - np.array(
            [int(boxes_conf_landm[0]), int(boxes_conf_landm[1])]
        )
        crop_img, _ = align_face(crop_img, landmark)
        # crop_img = (
        #         np.array(
        #             letterbox_image(
        #                 np.uint8(crop_img), (160,160) # (self.input_shape[2], self.input_shape[1])
        #             )
        #         )
        #         / 255
        #     )
        # crop_img = crop_img.astype(np.float32)
        # crop_img = np.expand_dims(crop_img, 0)
        aligned_faces.append(crop_img)
    return aligned_faces


def show_faces_aligned(aligned_faces):
    for i, face in enumerate(aligned_faces):
        cv2.imshow(f"{i}", face)

def base64_to_image(base64_str):
    # 将Base64字符串解码为二进制数据
    img_data = base64.b64decode(base64_str)
    # 将二进制数据转换为NumPy数组
    np_arr = np.frombuffer(img_data, np.uint8)
    # 将NumPy数组解码为图像
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return img

def image_to_base64(image):
    # 将图像编码为JPEG格式
    _, buffer = cv2.imencode(".jpg", image)
    # 将图像转换为Base64编码
    img_base64 = base64.b64encode(buffer).decode("utf-8")
    return img_base64