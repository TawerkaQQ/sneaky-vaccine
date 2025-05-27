import cv2
import numpy as np

from src.vision_utils import get_model

#TODO Work with base64 image!
def model_exec(image_path: str) -> np.ndarray:

    image = cv2.imread(image_path)
    detector = get_model("./src/model_zoo/det_10g125.onnx")
    detector.prepare(ctx_id=0, input_size=(640, 640))

    if detector is None:
        raise Exception("Model is None")

    if image is None:
        raise ValueError(f"Could not read image: {image}")

    det, landmarks = detector.detect(image)

    # prind bbox
    # for f in det:
    #     x1, x2 = int(f[0]), int(f[1])
    #     y1, y2 = int(f[2]), int(f[3])
    #     image = cv2.rectangle(image, (x1,x2), (y1, y2), (0,0,255), 2)

    for landmark in landmarks:
        for point in landmark:
            print("point", point)
            print(type(point))
            x, y = int(point[0]), int(point[1])
            cv2.circle(image, (x, y), 2, (0, 0, 255), -3)

    return image


if __name__ == "__main__":
    image_path = "./test_images/Baby-Face-02.jpg"
    model_exec(image_path)
