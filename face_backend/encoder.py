from backend import encoder_tflite
import glob, numpy as np, os, cv2
from utils import letterbox_image
import shutil, pathlib


def preprocess(aligned_faces):
    res = []
    for face in aligned_faces:
        face = (
            np.array(
                letterbox_image(
                    np.uint8(face),
                    (160, 160),  # (self.input_shape[2], self.input_shape[1])
                )
            )
            / 255
        )
        face = face.astype(np.float32)
        face = np.expand_dims(face, 0)
        res.append(face)
    return res


def normalize(x, p=2, dim=0):
    norm = np.linalg.norm(x, ord=p, axis=dim, keepdims=True)
    normalized_x = x / norm
    return normalized_x


def faces_distance(known_encodings, face):
    # if len(known_encodings) == 0:
    #     return np.empty((0))
    return np.linalg.norm(known_encodings - face, axis=1)


def faces_compare(known_encodings, face, max_dist=1):
    dis = faces_distance(known_encodings, face)
    return list(dis <= max_dist), dis


class encoder_class(object):
    def __init__(self, home) -> None:
        self.max_dist = 1.0  # higher for easier matching
        self.unknown_name = "Unknown"
        self.home = home
        self.enc = encoder_tflite.encoder_tflite(
            self.home / "model_data/facenet_mobilenet.tflite"
        )
        self.database = {}
        self.load_database()

    def load_database(self):
        self.database = {}
        for dir in glob.glob(str(self.home / "face_data/*")):
            name = os.path.basename(dir)
            encoding = np.loadtxt(self.home / f"face_data/{name}/enc.txt")
            self.database[name] = encoding
        self.names = list(self.database.keys())
        self.encodings = list(self.database.values())
        print(
            f"load_database: {len(self.database)} entries loaded {self.database.keys()}"
        )

    # def encode(self, aligned_faces) -> list[np.ndarray]:
    def encode(self, aligned_faces):
        encodings = []
        pre = preprocess(aligned_faces)
        for face in pre:
            encoding = self.enc.forward(face)
            encoding = normalize(encoding)
            encodings.append(encoding)
        return encodings

    def register_face(self, name, img, encoding, student_id, password):
        os.makedirs(self.home / f"face_data/{name}/", exist_ok=True)
        cv2.imencode(".png", img)[1].tofile(self.home / f"face_data/{name}/face.png")
        np.savetxt(self.home / f"face_data/{name}/enc.txt", encoding)
        self.database[name] = encoding
        self.names = list(self.database.keys())
        self.encodings = list(self.database.values())

        with open(self.home / f"face_data/{name}/data.txt", "w") as f:
            f.write(f"Name: {name}\nStudent ID: {student_id}\nPassword: {password}\n")

    # compare `encodings` with self.database
    # return a list of face names, including `Unknown`
    # def recognize(self, encodings) -> list[str]:
    def recognize(self, encodings):
        known = self.encodings
        names = self.names
        if len(known) == 0:
            return [self.unknown_name] * len(encodings)
        result = []
        for encoding in encodings:
            name = self.unknown_name
            is_match, dist = faces_compare(known, encoding, self.max_dist)
            # print(dist[0])
            idx = np.argmin(dist)
            if is_match[idx]:
                # best match dist <= self.max_dist
                name = names[idx]
            result.append(name)
        return result

    @staticmethod
    def plot_names(letterboxed, names, boxes_conf_landms):
        for e, b in zip(names, boxes_conf_landms):
            b = list(map(int, b))
            #   b[0]-b[3]为人脸框的坐标，b[4]为得分
            cx = b[0]
            cy = b[1] + 36
            cv2.putText(
                letterboxed, e, (cx, cy), cv2.FONT_HERSHEY_DUPLEX, 0.5, (127, 255, 70)
            )
        return letterboxed

    def unregister(self, name) -> bool:
        if name not in self.names:
            return False
        else:
            shutil.rmtree(self.home / f"face_data/{name}")
            self.load_database()
            return True

    # def lists(self) -> list[tuple[str, np.ndarray]]:
    def lists(self):
        result = []
        for name in self.names:
            face = cv2.imdecode(
                np.fromfile(self.home / f"face_data/{name}/face.png", dtype=np.uint8),
                -1,
            )
            result.append((name, face))
        return result

    def purge(self) -> None:
        shutil.rmtree(str(self.home / "face_data/"))
        os.mkdir(str(self.home / "face_data"))
        self.load_database()
