
import os
import cv2
import shutil
import json
from request_form import RequestForm

form = RequestForm()

request = form.get_request()
# -------------------------------
# CREATE REQUEST FOLDER
# -------------------------------

# Get the project root (one level above the scripts folder)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

request_folder = os.path.join(
    project_root,
    "outputs",
    "requests",
    request["request_id"]
)

os.makedirs(request_folder, exist_ok=True)

print("Request folder created successfully!")
print("Folder Path:", request_folder)

# -------------------------------
# LOAD IMAGE
# -------------------------------

image = cv2.imread(request["image_path"])

if image is None:
    print("❌ Error: Image could not be loaded.")
    exit()

print("✅ Image loaded successfully!")

height, width, channels = image.shape

print("Image Width :", width)
print("Image Height:", height)
print("Channels    :", channels)

if width < 100 or height < 100:
    print("❌ Image is too small.")
    exit()

print("✅ Image size is valid.")

file_name = os.path.basename(request["image_path"])
extension = os.path.splitext(file_name)[1].lower()

print("File Name :", file_name)
print("Extension :", extension)

allowed_formats = [".jpg", ".jpeg", ".png"]

if extension not in allowed_formats:
    print("❌ Unsupported image format.")
    exit()

print("✅ Supported image format.")

# -------------------------------
# COPY ORIGINAL IMAGE
# -------------------------------

destination = os.path.join(
    request_folder,
    file_name
)

shutil.copy(
    request["image_path"],
    destination
)

print("✅ Original image copied successfully!")
print("Saved at:", destination)

# -------------------------------
# IMAGE METADATA
# -------------------------------

metadata = {
    "file_name": file_name,
    "format": extension.replace(".", "").upper(),
    "width": width,
    "height": height,
    "channels": channels
}

metadata_path = os.path.join(
    request_folder,
    "image_metadata.json"
)

with open(metadata_path, "w") as file:
    json.dump(metadata, file, indent=4)

print("✅ Image metadata saved successfully!")
print("Saved at:", metadata_path)

# -------------------------------
# RESIZE IMAGE
# -------------------------------

processed_image = cv2.resize(image, (640, 640))

processed_image_path = os.path.join(
    request_folder,
    "processed_image" + extension
)

cv2.imwrite(
    processed_image_path,
    processed_image
)

print("✅ Processed image saved successfully!")
print("Saved at:", processed_image_path)

# -------------------------------
# REQUEST SUMMARY
# -------------------------------

request_summary = {
    "request_id": request["request_id"],
    "image_name": file_name,
    "length_mm": request["length"],
    "width_mm": request["width"],
    "height_mm": request["height"]
}

request_summary_path = os.path.join(
    request_folder,
    "request_summary.json"
)

with open(request_summary_path, "w") as file:
    json.dump(request_summary, file, indent=4)

print("✅ Request summary saved successfully!")
print("Saved at:", request_summary_path)