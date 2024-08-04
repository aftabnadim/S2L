import os
import shutil
from PIL import Image

# Define the base directory
#base_dir = r"F:\Yersinia_project\Spark_cyto\Jyoti\231214_Kinetics_cell_tox_MEFs\PI_MEF_96_well_Tecan_Falcon (Modified)_20231213_181312\Images"


def copy(base_dir):
    
    # List of folder names to be created
    folders = []
    for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        for number in range(1, 13):
            folders.append(f"{letter}{number}_TIFF_iLastik")

    # Iterate over each folder
    for folder in folders:
        source_folder = os.path.join(base_dir, folder.replace("_TIFF_iLastik", ""))
        destination_folder = os.path.join(base_dir, folder)

        # Create the destination folder if it doesn't exist
        os.makedirs(destination_folder, exist_ok=True)

        # Iterate over each file in the source folder
        for filename in os.listdir(source_folder):
            if "_O_R_" in filename and filename.endswith(".tiff"):
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

    print("Files copied successfully.")
