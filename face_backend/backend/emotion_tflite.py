try:
    import tflite_runtime.interpreter as tflite  # type: ignore
except ModuleNotFoundError:
    import tensorflow.lite as tflite


class emotion_tflite(object):
    def __init__(
        self,
        model_path="model_data/facial_expression_model.tflite",
    ):
        self.interp = tflite.Interpreter(str(model_path))
        self.interp.allocate_tensors()
        self.input_details = self.interp.get_input_details()
        self.output_details = self.interp.get_output_details()

    def forward(self, img):
        self.interp.set_tensor(self.input_details[0]["index"], img)
        self.interp.invoke()
        res = self.interp.get_tensor(self.output_details[0]["index"])
        return res
