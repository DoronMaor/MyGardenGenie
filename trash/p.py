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

    def assess_health(self, image=None, zipped_b64_image=None, testing=False):
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

        if not response["health_assessment"]["is_healthy"]:
            diseases = response["health_assessment"]["diseases"]
            suggestions = []
            for disease in diseases:
                name = disease["name"]
                description = disease["disease_details"]["description"]
                suggestions.append({"name": name, "description": description})
            return suggestions
        else:
            return [{"Plant is healthy!": "Nothing to worry about"}]

d = PlantHealthDetector("5CHZ8TnzXgrbYOioi0Ewf9jRFwWKCFtH9UbiYkqwjlgdUtBCnl")

with open('aa.jpg', 'rb') as f:
    image_data = f.read()

#m = d.assess_health(image_data)
#print(m)

data = [{'name': 'water-related issue', 'description': 'Water-related abiotic issues refer to abiotic stresses caused by inadequate watering, including water excess, uneven watering, and water deficiency.'}, {'name': 'abiotic', 'description': 'Abiotic disorders are caused by non-living factors - usually by unsuitable environmental conditions, such as drought stress, nutrient deficiency, improper watering, or planting conditions.'}, {'name': 'water deficiency', 'description': 'Water deficiency is similar in its symptoms to over-watering and it is important to identify the cause. Symptoms include slow growth, wilting, discolored leaves and flowers, burning on edges of leaves. The affected plant can also suffer from disrupted nutrient uptake.'}, {'name': 'dead plant', 'description': 'Plant death occurs when all parts of the plant (including stems and roots) irreversibly lose their vitality. The dead plant usually loses its leaves or has brown leaves and mushy stems and roots.'}, {'name': 'water excess or uneven watering', 'description': 'Water excess and uneven watering are abiotic disorders caused by inadequate watering. Water excess may lead to rotting of the roots due to lack of oxygen, and higher susceptibility to infection. Symptoms of over-watering include stunted growth, yellow and brown leaves, wilting and higher susceptibility to leaf burn.'}, {'name': 'Peronosporales', 'description': 'Peronosporales are oomycetes, a group related to fungi, also known as water molds. They cause infectious diseases such as downy mildew.'}, {'name': 'Chromista', 'description': 'Chromista are fungus-like organisms, sometimes called water molds. They are mostly aquatic or soil-borne and cause many plant diseases (such as downy mildew and late blight).'}, {'name': 'root rot', 'description': 'Root rot is an abiotic disorder caused by prolonged exposure to overwatered conditions usually due to overwatering or a poor drainage system. Some roots can eventually start to decay or rot away spreading the rot to other roots even after the conditions are back to normal. Symptoms include wilting and discoloration of leaves, stunted growth, and cankers. However, the symptoms are often not apparent until the disease is advanced.'}, {'name': 'Phytophthora', 'description': 'The Phytophthora genus contains soil-borne plant pathogens similar to fungi, infecting mainly trees and woody plants. It usually spreads through plant roots and leads to weakness and collapse of the plant.'}, {'name': 'Peronosporaceae', 'description': 'Pathogens from the Peronosporaceae family are fungi-like water molds causing infectious plant diseases called downy mildews. They form typical spores-containing structures on the downside of the leaves.'}, {'name': 'Fungi', 'description': 'Fungi take energy from the plants on which they live, causing damage to the plant. Fungal infections are responsible for approximately two-thirds of infectious plant diseases and cause wilting, molding, rusts, scabs, rotted tissue, and other problems.'}, {'name': 'low temperatures and frost damage', 'description': 'Very cold temperatures can cause damage to plant tissue by rupturing plant cells. Some plants (e.g. tropical) are more susceptible to low temperatures and drought - this can pose a problem for indoor plants which are originally used to tropical environments.'}]

print(data[0])
print(data[0]['description'])
