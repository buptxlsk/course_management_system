try:
    import tflite_runtime.interpreter as tflite  # type: ignore
except ModuleNotFoundError:
    import tensorflow.lite as tflite


class detector_tflite(object):
    def __init__(self, model_path="model_data/Retinaface_mobilenet0.25.tflite"):
        self.interp = tflite.Interpreter(str(model_path))
        self.interp.allocate_tensors()
        self.input_details = self.interp.get_input_details()
        self.output_details = self.interp.get_output_details()

    def forward(self, img):
        # start = time.time()
        self.interp.set_tensor(self.input_details[0]["index"], img)
        self.interp.invoke()
        # 人脸关键点、得分、预测框
        # todo: support for sizes other than 640
        landms = (
            self.interp.get_tensor(self.output_details[0]["index"])
            .transpose((0, 2, 1))
            .squeeze(0)
        )
        conf = (
            self.interp.get_tensor(self.output_details[1]["index"])
            .transpose((0, 2, 1))
            .squeeze(0)
        )
        loc = (
            self.interp.get_tensor(self.output_details[2]["index"])
            .transpose((0, 2, 1))
            .squeeze(0)
        )
        return landms, conf, loc
