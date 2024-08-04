import sys
import os
import argparse
from PIL import Image
import labels2roisTEST as l2r
from Cellpose3_Basset import Cellpose
from mastersheet import genmasterSheet
from concurrent.futures import ThreadPoolExecutor, as_completed

# Helper functions
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
        cellpose.segment(base_dir, diameter=int(diameter), progress_callback=None)  # You can implement a progress callback if needed

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
                show_labels=True, progress_callback=None  # You can implement a progress callback if needed
            )
            visualizer.save_rois_to_excel()

            # Output progress to console
            print(f"Processed mask {idx + 1}/{total_masks}")

        summary_dir = os.path.join(output_dir, "SummarySheet")
        os.makedirs(summary_dir, exist_ok=True)
        master_excel_save_path = os.path.join(summary_dir, "Summary.xlsx")
        genmasterSheet(directory=output_dir, savePath=master_excel_save_path)

    print("Process completed.")

def main():
    parser = argparse.ArgumentParser(description="Run image segmentation and ROI extraction.")
    parser.add_argument('base_dir', type=str, help="Base directory containing images and masks.")
    parser.add_argument('output_dir', type=str, help="Output directory for results.")
    parser.add_argument('--diameter', type=int, default=0, help="Cellpose diameter parameter.")
    parser.add_argument('--segment', action='store_true', help="Run cellpose segmentation.")
    parser.add_argument('--labels2rois', action='store_true', help="Run label to ROI processing.")

    args = parser.parse_args()

    if not os.path.isdir(args.base_dir):
        print(f"Error: Base directory '{args.base_dir}' does not exist.")
        sys.exit(1)

    if not os.path.isdir(args.output_dir):
        print(f"Error: Output directory '{args.output_dir}' does not exist.")
        sys.exit(1)

    segment_and_process(args.base_dir, args.output_dir, args.diameter, args.segment, args.labels2rois)

if __name__ == "__main__":
    main()
