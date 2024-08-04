import os

# Define the base directory


def generateFiles(base_dir):
    #base_dir = r"F:\Yersinia_project\Spark_cyto\Jyoti\231214_Kinetics_cell_tox_MEFs\PI_MEF_96_well_Tecan_Falcon (Modified)_20231213_181312\Images"

    # List of folder names to be created
    folders = []
    for letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
        for number in range(1, 13):
            folders.append(f"{letter}{number}_TIFF_iLastik")

    # Create each folder in the base directory
    for folder in folders:
        os.makedirs(os.path.join(base_dir, folder), exist_ok=True)

    print("Folders created successfully.")



