import os
import shutil
from PIL import Image
import tqdm

source_folder = r'F:\Segmentation_project\THP1_SN_20240703_221049\Images'
destination_folder = r'F:\Segmentation_project\THP1_SN_20240703_221049\Images_TIFF'
 

for filename in tqdm.tqdm(os.listdir(source_folder)):
    if "_O_B_Raw_" in filename and filename.endswith(".tiff"):
        # Check if the file is already in TIFF format
        if "tif" in filename.lower():
            # File is already in TIFF format, no need to convert
            shutil.copy(os.path.join(source_folder, filename), os.path.join(destination_folder, filename))

        else:
            # Open the file
            image = Image.open(os.path.join(source_folder, filename))

            # Create the TIFF filename
            tiff_filename = os.path.splitext(filename)[0] + ".tif"
            tiff_path = os.path.join(destination_folder, tiff_filename)

            # Save the file as TIFF
            image.save(tiff_path, format="TIFF")