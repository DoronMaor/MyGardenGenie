import base64
import zlib
import requests
import os
import pickle
from plant_identfication.PlantStatLocator import PlantStatLocator


class PlantIdentify:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Api-Key": api_key,
        }
        self.PlantLocator = PlantStatLocator()

    def identify_plant(self, image=None, zipped_b64_image=None, testing=True):
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

        return response["suggestions"][0]

    def format_names(self, api_output):
        names = [api_output["plant_name"]] + api_output["plant_details"]["common_names"] + \
                [api_output["plant_details"]["scientific_name"]]
        lowered_names = []
        for name in names:
            name = name.lower()
            lowered_names.append(name)
        return lowered_names

    def search_for_plant(self, api_output):
        names = self.format_names(api_output)
        plant = self.PlantLocator.search_plants(names)
        return plant


if __name__ == '__main__':
    p = PlantIdentify("fLBl0xbtSnB4UPyp6Qtblo" + "apUFJbQRAbxyAZMrM048ZYTvWw94")
    nms = p.identify_plant()

    p.search_for_plant(nms)
