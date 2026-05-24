# This is a simple test to check if Gemini can read an image
# We download a sample shoe image from the web and send it to extractor.py

import requests
import sys
sys.path.append('.')
from src.vision.extractor import extract_attributes

# Download a sample product image
url = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400"
image_bytes = requests.get(url).content

# Send to Gemini
print("Sending image to Gemini...")
result = extract_attributes(image_bytes)
print("Result:", result)