from ctypes import resize
from logging import raiseExceptions
from socket import IP_MULTICAST_LOOP
from imutils.perspective import four_point_transform
import pytesseract
import imutils
import cv2
import re

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  # your path may be different


orig = cv2.imread('receipt.jpg')
image = orig.copy()

image = imutils.resize(image, width=500)
ratio = orig.shape[1] / float(image.shape[1])


gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray,(5,5),0)
edged = cv2.Canny(blurred, 75,200)

cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

receiptCnt = None
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)

    if len(approx) ==4:
        receiptCnt = approx
        break

if receiptCnt is None:
    raise Exception(("Could not find receipt outline"))



# cv2.imshow("Input", image)
# cv2.imshow("Edged", edged)
output = image.copy()
cv2.drawContours(output, [receiptCnt], -1, (0, 255,0, 2))
cv2.imshow("Receipt Outline", output)
receipt = four_point_transform(orig, receiptCnt.reshape(4,2) * ratio)
cv2.imshow("Receipt Transform", imutils.resize(receipt, width=500))
cv2.waitKey(0)

options = "--psm 4"
text = pytesseract.image_to_string(cv2.cvtColor(receipt, cv2.COLOR_BGR2RGB), config=options)
print("[INFO] raw output:")
print("==================")
print(text)
print("\n")

# define a regular expression that will match line items that include
# a price component
pricePattern = r'([0-9]+\.[0-9]+)'
print("[INFO] price line items:")
print("========================")

# loop over each of the line items in the OCR'd receipt
for row in text.split("\n"):
	# check to see if the price regular expression matches the current
	# row
	if re.search(pricePattern, row) is not None:
		print(row)