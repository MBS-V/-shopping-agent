# upload_images.py
# Uploads product images to GCS in parallel using threading
import sys
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append('.')
from src.search.catalogue import CATALOGUE

BUCKET = "gs://shopping-agent-images/products"
IMAGE_DIR = "data/fashion-dataset/images"

def upload_image(pid):
    src = f"{IMAGE_DIR}/{pid}.jpg"
    if not os.path.exists(src):
        return pid, False
    result = subprocess.run(
        f'gsutil cp {src} {BUCKET}/{pid}.jpg',
        shell=True, capture_output=True
    )
    return pid, result.returncode == 0

ids = [p['id'] for p in CATALOGUE]
print(f"Uploading {len(ids)} images in parallel...")

uploaded = 0
failed = 0

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(upload_image, pid): pid for pid in ids}
    for i, future in enumerate(as_completed(futures)):
        pid, success = future.result()
        if success:
            uploaded += 1
        else:
            failed += 1
        if (i+1) % 100 == 0:
            print(f"{i+1}/{len(ids)} processed — {uploaded} uploaded, {failed} failed")

print(f"Done. {uploaded} uploaded, {failed} failed.")