import base64
import requests
# import the opencv library
import cv2

# define a video capture object
vid = cv2.VideoCapture(0)

while (True):

    # Capture the video frame
    # by frame
    ret, frame = vid.read()

    # Display the resulting frame
    cv2.imshow('frame', frame)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

import plantcv as pcv

# Read in the image
img, path, filename = pcv.readimage("path/to/image")

# Segment the image using the KMeans clustering method
segmented_img = pcv.kmeans_segmentation(img)

# Identify individual plants in the segmented image
plant_contours, hierarchy = pcv.find_objects(segmented_img, segmented_img)

# Loop through each plant and save an image of it
i = 1
for plant in plant_contours:
    # Crop the plant out of the original image
    plant_img = pcv.roi.rectangle(img, plant)
    # Save the image
    pcv.print_image(plant_img, 'path/to/save/image/plant'+str(i)+'.jpg')
    i += 1



# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()

# encode images to base64
with open("image.png", "rb") as file:
    images = [base64.b64encode(file.read()).decode("ascii")]

response = requests.post(
    "https://api.plant.id/v2/identify",
    json={
        "images": images,
        "modifiers": ["similar_images"],
        "plant_details": ["common_names", "url"],
    },
    headers={
        "Content-Type": "application/json",
        "Api-Key": "fLBl0xbtSnB4UPyp6QtbloapUFJbQRAbxyAZMrM048ZYTvWw94",
    }).json()

for suggestion in response["suggestions"]:
    print(suggestion["plant_name"])    # Taraxacum officinale
    print(suggestion["plant_details"]["common_names"])    # ["Dandelion"]
    print(suggestion["plant_details"]["url"])    # https://en.wikipedia.org/wiki/Taraxacum_officinale