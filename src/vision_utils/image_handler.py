from distutils.command.install import install

import cv2
import numpy as np
from io import BytesIO


class ImageHandler:
    @staticmethod
    def cv_image_read(image_data: object):
        if isinstance(image_data, str):
            img = cv2.imread(image_data)

        return img

    @staticmethod
    def image_to_bytesIO(image_data: str | np.ndarray):

        if isinstance(image_data, str):
            image = cv2.imread(image_data)
            _, buffer = cv2.imencode(".jpg", image)
            io_buf = BytesIO(buffer)

        elif isinstance(image_data, np.ndarray):
            _, buffer = cv2.imencode(".jpg", image_data)
            io_buf = BytesIO(buffer)

        else:
            raise ValueError("Input must be either a string (file path) or numpy array")

        return io_buf

    @staticmethod
    def bytesio_decode(image_data: BytesIO):
        if isinstance(image_data, BytesIO):
            decoded_image = cv2.imdecode(
                np.frombuffer(image_data.getbuffer(), np.uint8), -1
            )

        return decoded_image
