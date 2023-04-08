import cv2


def calculate_plant_growth(image_path):
    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to isolate plant pixels
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Find contours of plant pixels
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour with the largest area (i.e. the plant)
    plant_contour = max(contours, key=cv2.contourArea)

    # Calculate the height of the plant in centimeters
    plant_height_pixels = cv2.boundingRect(plant_contour)[3]

    return plant_height_pixels

    pixel_height = initial_height / plant_height_pixels
    plant_height_cm = plant_height_pixels * pixel_height

    # Calculate the percentage growth relative to the initial height
    growth_percentage = (plant_height_cm / initial_height - 1) * 100

    # Round the growth percentage to two decimal places
    growth_percentage = round(growth_percentage, 2)

