import base64
import os
import pickle
import zlib

import requests


class PlantHealthDetector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key,
        }

    def assess_health(self, image=None, zipped_b64_image=None, testing=True):
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
            return suggestions
        else:
            return "Plant is healthy!"
