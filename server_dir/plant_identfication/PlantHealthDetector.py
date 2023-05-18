import base64
import os
import pickle
import zlib

import requests


class PlantHealthDetector:
    def __init__(self, api_key):
        """
        Initializes the PlantHealthDetector with the provided API key.

        Args:
            api_key (str): The API key for accessing the plant health assessment API.
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key,
        }

    def assess_health(self, image=None, zipped_b64_image=None, testing=True):
        """
        Assess the health of a plant based on an image.

        Args:
            image (bytes): The image data as bytes (optional).
            zipped_b64_image (bytes): The zipped and base64 encoded image data as bytes (optional).
            testing (bool): Set to True if testing mode is enabled (optional).

        Returns:
            dict: A dictionary containing the assessment results with the name and description of the suggested action.

        Note:
            - Either `image` or `zipped_b64_image` should be provided.
            - If `testing` is True and a test file exists, it returns the stored response for testing purposes.
            - If the plant is healthy, it returns a dictionary with the name "Plant is healthy!" and description "Nothing to worry about".
        """
        if testing:
            if os.path.isfile("test_plant"):
                with open("test_plant", "rb") as f:
                    response = pickle.load(f)
                    print("test file")
                    return response["suggestions"][0]

        if image:
            b64_image = [base64.b64encode(image).decode("ascii")]
        elif zipped_b64_image:
            b64_image = [zlib.decompress(zipped_b64_image).decode()]
        else:
            return

        response = requests.post(
            "https://api.plant.id/v2/health_assessment",
            json={
                "images": b64_image,
                "modifiers": ["similar_images"],
                "disease_details": ["description", "treatment"],
            },
            headers=self.headers
        ).json()

        print(response)

        if not response["health_assessment"]["is_healthy"]:
            diseases = response["health_assessment"]["diseases"]
            suggestions = []
            for disease in diseases:
                name = disease["name"]
                description = disease["disease_details"]["description"]
                suggestions.append({"name": name, "description": description})
            return suggestions[0]
        else:
            return [{"name": "Plant is healthy!", "description": "Nothing to worry about"}][0]
