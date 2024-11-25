# Import necessary packages
from skimage.segmentation import clear_border
import pytesseract
import numpy as np
import imutils
import cv2
import sys
import os

# Set the tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class PyImageSearchANPR:
    def __init__(self, minAR=2.5, maxAR=6.0, debug=False):
        self.minAR = minAR
        self.maxAR = maxAR
        self.debug = debug

    def locate_license_plate_candidates(self, gray, keep=10):
        rectKern = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 7))
        blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rectKern)

        squareKern = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        light = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, squareKern)
        light = cv2.threshold(light, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        gradX = cv2.Sobel(blackhat, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        gradX = np.absolute(gradX)
        gradX = 255 * ((gradX - np.min(gradX)) / (np.max(gradX) - np.min(gradX)))
        gradX = gradX.astype("uint8")

        gradX = cv2.GaussianBlur(gradX, (5, 5), 0)
        gradX = cv2.morphologyEx(gradX, cv2.MORPH_CLOSE, rectKern)
        thresh = cv2.threshold(gradX, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)

        thresh = cv2.bitwise_and(thresh, thresh, mask=light)
        thresh = cv2.dilate(thresh, None, iterations=2)
        thresh = cv2.erode(thresh, None, iterations=1)

        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:keep]

        return cnts

    def locate_license_plate(self, gray, candidates, clearBorder=False):
        for i, c in enumerate(candidates):
            (x, y, w, h) = cv2.boundingRect(c)
            ar = w / float(h)

            if self.minAR <= ar <= self.maxAR:
                licensePlate = gray[y:y + h, x:x + w]
                roi = cv2.threshold(licensePlate, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

                if clearBorder:
                    roi = clear_border(roi)

                # Save and print the ROI for debugging
                if self.debug:
                    roi_path = f"roi_debug_{i}.jpg"
                    cv2.imwrite(roi_path, roi)
                    print(f"[DEBUG] Saved ROI as {roi_path}")

                return roi

        return None

    def build_tesseract_options(self, psm=7):
        alphanumeric = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        options = f"-c tessedit_char_whitelist={alphanumeric} --psm {psm}"
        return options

    def find_and_ocr(self, imagePath, psm=7, clearBorder=False):
        image = cv2.imread(imagePath)
        if image is None:
            print(f"[ERROR] Could not read image at path: {imagePath}")
            return None

        image = imutils.resize(image, width=600)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Load the Haar cascade for license plate detection
        carplate_haar_cascade_path = r'C:\Users\Venturez\Desktop\Licence\ANPR\storage\resources\ocr\haarcascade_russian_plate_number.xml'
        if not os.path.exists(carplate_haar_cascade_path):
            print(f"[ERROR] Haar cascade file not found at: {carplate_haar_cascade_path}")
            return None

        carplate_haar_cascade = cv2.CascadeClassifier(carplate_haar_cascade_path)
        candidates = self.locate_license_plate_candidates(gray)
        roi = self.locate_license_plate(gray, candidates, clearBorder=clearBorder)

        if roi is not None:
            options = self.build_tesseract_options(psm=psm)
            lpText = pytesseract.image_to_string(roi, config=options)
            return lpText.strip()

        return None

# Entry point for a single image
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python anpr.py <image_path>")
        sys.exit(1)

    imagePath = sys.argv[1]
    anpr = PyImageSearchANPR(debug=False)
    licensePlateText = anpr.find_and_ocr(imagePath)

    if licensePlateText:
        print("[RESULT] License Plate Text:", licensePlateText)
    else:
        print("[RESULT] No license plate detected.")
