from imageai.Detection import ObjectDetection
from PIL import Image
import os


class PlantDetector:
    def __init__(self):
        self.execution_path = os.getcwd()
        self.detector = ObjectDetection()
        self.detector.setModelTypeAsRetinaNet()
        self.detector.setModelPath(
            os.path.join(self.execution_path, "plant_recognition_files\\Models\\retinanet_resnet50_fpn_coco-eeacb38b.pth"))
        self.detector.loadModel()

    def detect_plants(self, input_image_path, output_image_path, num_plants=2):
        detections = self.detector.detectObjectsFromImage(input_image=input_image_path,
                                                          output_image_path=output_image_path)
        original_image = Image.open(input_image_path)
        i = 0
        for eachObject in detections:
            print(eachObject["name"], " : ", eachObject["percentage_probability"])
            if "plant" not in eachObject["name"] and "vase" not in eachObject["name"]:
                continue

            # Get the bounding box coordinates
            x1, y1, x2, y2 = eachObject["box_points"]
            if "vase" in eachObject["name"]:
                x1 -= 5
                y1 -= 180
                x2 += 5
                y2 += 10
            # Crop the image based on the bounding box
            crop_img = original_image.crop((x1, y1, x2, y2))

            # Save the cropped image
            crop_img.save(f"detection_{i}.jpg")
            i += 1
            if i == num_plants:
                return i
        return i


if __name__ == '__main__':
    # Example usage:
    detector = PlantDetector()
    detector.detect_plants("all_plants.jpg", "all_plants_with_bounding_box.jpg", 2)
