from math import sqrt
from imageai.Detection import ObjectDetection
from PIL import Image
import os
import mgg_functions as mgf

class PlantDetector:
    def __init__(self):
        self.execution_path = os.getcwd()
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsRetinaNet()
        self.detector.setModelPath(
            os.path.join(self.execution_path,
                         "plant_recognition_files\\Models\\retinanet_resnet50_fpn_coco-eeacb38b.pth"))
        self.detector.loadModel()

    def detect_plants(self, input_image_path, output_image_path, num_plants=2, distance_threshold=10):
        detections = self.detector.detectObjectsFromImage(input_image=input_image_path,
                                                          output_image_path=output_image_path)
        original_image = Image.open(input_image_path)
        i = 0
        detected_objects = []
        for eachObject in detections:
            print(eachObject["name"], " : ", eachObject["percentage_probability"], "%")
            if "plant" not in eachObject["name"] and "vase" not in eachObject["name"]:
                continue
            detected_object = {}
            detected_object["name"] = eachObject["name"]
            detected_object["percentage_probability"] = eachObject["percentage_probability"]
            detected_object["box_points"] = eachObject["box_points"]
            x1, y1, x2, y2 = eachObject["box_points"]
            if "vase" in eachObject["name"]:
                x1 -= 5
                y1 -= 180
                x2 += 5
                y2 += 10
            # Calculate the center of the bounding box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            detected_object["center"] = (center_x, center_y)

            # Check if the detection is too close to any previous detection
            too_close = False
            for prev_obj in detected_objects:
                distance = sqrt((center_x - prev_obj["center"][0]) ** 2 + (center_y - prev_obj["center"][1]) ** 2)
                if distance < distance_threshold and prev_obj["name"] != detected_object["name"]:
                    too_close = True
                    break
            if too_close:
                continue

            # Crop the image based on the bounding box
            crop_img = original_image.crop((x1, y1, x2, y2))

            # Save the cropped image
            crop_img.save(f"detection_{i}.jpg")
            i += 1
            detected_objects.append(detected_object)
            if i == num_plants:
                original_image.close()
                os.remove(input_image_path)
                return i
        original_image.close()
        os.remove(input_image_path)
        return i

    def detect_plants_for_analysis(self, input_image_path, output_image_path, num_plants=2, distance_threshold=10):
        detections = self.detector.detectObjectsFromImage(input_image=input_image_path,
                                                          output_image_path=output_image_path)
        original_image = Image.open(input_image_path)
        i = 0
        detected_objects = []
        letters_map = {0: 'A', 1: 'B', 2: 'C'}

        for eachObject in detections:
            print(eachObject["name"], " : ", eachObject["percentage_probability"], "%")
            if "plant" not in eachObject["name"] and "vase" not in eachObject["name"]:
                continue
            detected_object = {}
            detected_object["name"] = eachObject["name"]
            detected_object["percentage_probability"] = eachObject["percentage_probability"]
            detected_object["box_points"] = eachObject["box_points"]
            x1, y1, x2, y2 = eachObject["box_points"]
            if "vase" in eachObject["name"]:
                x1 -= 5
                y1 -= 180
                x2 += 5
                y2 += 10
            # Calculate the center of the bounding box
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            detected_object["center"] = (center_x, center_y)

            # Check if the detection is too close to any previous detection
            too_close = False
            for prev_obj in detected_objects:
                distance = sqrt((center_x - prev_obj["center"][0]) ** 2 + (center_y - prev_obj["center"][1]) ** 2)
                if distance < distance_threshold and prev_obj["name"] != detected_object["name"]:
                    too_close = True
                    print("Too close")
                    break
            if too_close:
                continue

            # Crop the image based on the bounding box
            crop_img = original_image.crop((x1, y1, x2, y2))

            # Save the cropped image
            try:
                p = mgf.get_plant_name(letters_map[i])
                crop_img.save(output_image_path[:-4] + "_" + (p if p is not None else "") + ".jpg")
            finally:
                i += 1
            if i == num_plants:
                return i
        return i


if __name__ == '__main__':
    # Example usage:
    detector = PlantDetector()
    detector.detect_plants("all_plants.jpg", "all_plants_with_bounding_box.jpg", 2)
