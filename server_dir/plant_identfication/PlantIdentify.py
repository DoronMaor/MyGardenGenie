import base64
import zlib
import requests
import os
import pickle
from plant_identfication.PlantStatLocator import PlantStatLocator


class PlantIdentify:
    def __init__(self, api_key):
        """
        Initializes the PlantIdentify class with the provided API key.

        Args:
            api_key (str): API key for accessing the plant identification service.
        """
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key,
        }
        self.PlantLocator = PlantStatLocator()

    def identify_plant(self, image=None, zipped_b64_image=None, testing=True):
        """
        Identifies a plant based on the provided image.

        Args:
            image (bytes): Image data as bytes (optional).
            zipped_b64_image (bytes): Zipped and base64-encoded image data as bytes (optional).
            testing (bool): Flag indicating whether testing mode is enabled (default: True).

        Returns:
            tuple: A tuple containing the identified plant suggestion and formatted plant names.
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
            "https://api.plant.id/v2/identify",
            json={
                "images": b64_image,
                "modifiers": ["similar_images"],
                "plant_details": ["common_names", "url"],
            },
            headers=self.headers
        ).json()
        print(response)

        if testing:
            with open("test_plant", "wb") as f:
                pickle.dump(response, f)

        return (response["suggestions"][0], self.format_names(response["suggestions"][0]))

    def format_names(self, api_output):
        """
        Formats the plant names from the API response.

        Args:
            api_output (dict): API response for a plant suggestion.

        Returns:
            list: A list of formatted plant names.
        """
        plant_name = api_output.get('plant_name', '')
        common_names = api_output.get('plant_details', {}).get('common_names', [])
        scientific_name = api_output.get('plant_details', {}).get('scientific_name', '')
        names = [plant_name] + (common_names if common_names is not None else []) + [scientific_name]

        lowered_names = []
        for name in names:
            name = name.lower()
            lowered_names.append(name)
        return lowered_names

    def search_for_plant(self, api_output):
        """
        Searches for a plant using the formatted plant names.

        Args:
            api_output (dict): API response for a plant suggestion.

        Returns:
            object: The searched plant object.
        """
        names = self.format_names(api_output)
        plant = self.PlantLocator.search_plants(names)
        return plant
