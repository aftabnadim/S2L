import os
from PIL import Image
import labels2roisTEST as l2r
from Cellpose3_Basset import Cellpose
from mastersheet import genmasterSheet

# Hardcoded arguments
BASE_DIR = '/path/to/base_dir'
OUTPUT_DIR = '/path/to/output_dir'
DIAMETER = 30
RUN_SEGMENTATION = True
RUN_LABELS2ROIS = True

def findoriginalimage(filename):
    name, extension = os.path.splitext(filename)
    new_name = name[:-9]
    return new_name + extension

def PNG2TIFF(filename):
    name, _ = os.path.splitext(filename)
    return name

def segment_and_process(base_dir, output_dir, diameter, run_segmentation, run_labels2rois):
    cellpose = Cellpose()  # Initialize Cellpose class

    if run_segmentation:
        cellpose.segment(base_dir, diameter=int(diameter), progress_callback=None)  # Implement progress callback if needed

    if run_labels2rois:
        masks = [f for f in os.listdir(base_dir) if "cp_masks" in f]
        total_masks = len(masks)
        if total_masks == 0:
            print("No masks found.")
            return

        for idx, mask in enumerate(masks):
            label_image_path = os.path.join(base_dir, mask)
            original_image_path = os.path.join(base_dir, f"{PNG2TIFF(findoriginalimage(mask))}.tiff")
            plot_output_path = os.path.join(output_dir, f"{findoriginalimage(mask)}_ROI.png")
            excel_output_path = os.path.join(output_dir, f"{mask}.xlsx")

            visualizer = l2r.ROIVisualizer(
                label_image_path, original_image_path, excel_output_path, plot_output_path, 
                show_labels=True, progress_callback=None  # Implement progress callback if needed
            )
            visualizer.save_rois_to_excel()

            # Output progress to console
            print(f"Processed mask {idx + 1}/{total_masks}")

        summary_dir = os.path.join(output_dir, "SummarySheet")
        os.makedirs(summary_dir, exist_ok=True)
        master_excel_save_path = os.path.join(summary_dir, "Summary.xlsx")
        genmasterSheet(directory=output_dir, savePath=master_excel_save_path)

    print("Process completed.")

# Call the function with hardcoded arguments
segment_and_process(BASE_DIR, OUTPUT_DIR, DIAMETER, RUN_SEGMENTATION, RUN_LABELS2ROIS)
