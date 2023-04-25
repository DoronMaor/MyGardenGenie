import os
from datetime import datetime
import base64
import zlib


def compress_encode_images(images_list):
    compressed_images = []
    for image_path, _ in images_list:
        with open(image_path, 'rb') as image_file:
            image_bytes = image_file.read()
            encoded_image = base64.b64encode(image_bytes).decode('ascii')
            compressed_image = zlib.compress(encoded_image.encode())
            compressed_images.append(compressed_image)
    return compressed_images


class PlantHealthSupport:
    def __init__(self, server_handler):
        self.server_handler = server_handler
        self.images_path = "plant_analysis_pictures\\"

    def load_recent_images(self):
        images = []
        for file in os.listdir(self.images_path):
            if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
                filepath = os.path.join(self.images_path, file)
                creation_time = os.path.getctime(filepath)
                creation_datetime = datetime.fromtimestamp(creation_time)
                images.append((filepath, creation_datetime))
        images.sort(key=lambda x: x[1], reverse=True)
        return images[:2]

    def run(self):
        images_lst = self.load_recent_images()
        compressed_lst = compress_encode_images(images_lst)
        self.server_handler.send_plant_health(compressed_lst)
