import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
from PIL import Image
from vision_utils.get_onnx_model import get_model
import matplotlib.pyplot as plt


def model_exec(image_path: str):

    # detector = get_model('/home/tawerka/Projects/sneaky-vaccine/src/model_zoo/2d106det.onnx')
    # detector.prepare(ctx_id=0, input_size=(640, 640))

    detector = insightface.model_zoo.get_model('/home/tawerka/Projects/sneaky-vaccine/src/model_zoo/2d106det.onnx')
    detector.prepare(ctx_id=0, input_size=(640, 640))

    print(detector)
    print(type(detector))

    image = Image.open(image_path)
    faces = detector.get(image)
    print(faces)
    image.show()
    # image.save("./src/processed_images/ks.jpg")

    pass




if __name__ == "__main__":
    image_path = "test_images/GettyImages-1092658864_hero-1024x575.jpg"


    model_exec(image_path)