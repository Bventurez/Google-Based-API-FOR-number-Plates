import os
import cv2
import numpy as np
import pytesseract
import matplotlib.pyplot as plt
import sys

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the Haar Cascade for license plate detection
carplate_haar_cascade = cv2.CascadeClassifier(r'C:\Users\Venturez\Desktop\anpr\haarcascade_russian_plate_number.xml')

# Function to display images at a larger scale
def enlarge_plt_display(image, scale_factor):
    height, width = image.shape[:2]
    plt.figure(figsize=(width * scale_factor / 100, height * scale_factor / 100))
    plt.axis('off')
    plt.imshow(image)
    plt.show()

def preprocess_image(image_path):
    print(f"Loading image from {image_path}")
    image = cv2.imread(image_path)

    if image is None:
        print("Error: Could not open or find the image.")
        return None, None
    
    print("Image loaded successfully.")
    enlarge_plt_display(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), 1.2)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    print("Image converted to grayscale.")
    
    # Improve contrast with histogram equalization
    gray = cv2.equalizeHist(gray)
    print("Histogram equalization applied.")

    # Optional Gaussian Blur to reduce noise
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    print("Gaussian Blur applied.")

    # Apply bilateral filter to reduce noise while keeping edges sharp
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)
    print("Bilateral filter applied.")
    
    # Edge detection
    edged = cv2.Canny(filtered, 30, 200)
    print("Edge detection applied.")

    enlarge_plt_display(edged, 1.2)

    return edged, image  # Return both the processed image and the original

# Function to detect car plate using Haar Cascade
def carplate_detect(image):
    carplate_overlay = image.copy()
    carplate_rects = carplate_haar_cascade.detectMultiScale(carplate_overlay, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in carplate_rects:
        cv2.rectangle(carplate_overlay, (x, y), (x + w, y + h), (255, 0, 0), 5)

    enlarge_plt_display(cv2.cvtColor(carplate_overlay, cv2.COLOR_BGR2RGB), 1.2)
    return carplate_overlay

# Function to extract only the license plate region
def carplate_extract(image):
    carplate_rects = carplate_haar_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in carplate_rects:
        carplate_img = image[y + 15:y + h - 10, x + 15:x + w - 20]
        return carplate_img
    return None

# Function to enlarge the image
def enlarge_img(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    dim = (width, height)
    return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

def recognize_license_plate(image_path):
    # Preprocess the image
    processed_image, original_image = preprocess_image(image_path)
    
    if processed_image is None:
        return "Image processing failed."

    # Detect license plate
    detected_image = carplate_detect(original_image)
    
    # Extract license plate region
    carplate_img = carplate_extract(original_image)
    if carplate_img is None:
        print("No license plate found.")
        return "No license plate found."

    # Enlarge and further process extracted car plate image
    carplate_img = enlarge_img(carplate_img, 150)
    carplate_img_gray = cv2.cvtColor(carplate_img, cv2.COLOR_RGB2GRAY)
    carplate_img_gray_blur = cv2.medianBlur(carplate_img_gray, 3)

    # Display processed license plate for OCR
    enlarge_plt_display(carplate_img_gray_blur, 1.2)
    
    # Recognize text from license plate
    plate_text = pytesseract.image_to_string(
        carplate_img_gray_blur, 
        config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    )
    print(f"Recognized Text: {plate_text.strip()}")

    # Save result image with the detected plate region
    result_image_path = os.path.join(os.path.dirname(image_path), 'output_detected.jpg')
    cv2.imwrite(result_image_path, detected_image)

    # Display recognized text
    print(f"Recognized License Plate: {plate_text.strip()}")
    return plate_text.strip()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        print(f"Recognizing license plate for image: {image_path}")
        recognized_plate = recognize_license_plate(image_path)
    else:
        print("Please provide an image path.")
