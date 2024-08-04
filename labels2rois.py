import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import os
import sys

class ROIVisualizer:
    def __init__(self, label_image_path, original_image_path, excel_output_path, plot_output_path, show_labels=False):
        self.label_image_path = label_image_path
        self.original_image_path = original_image_path
        self.excel_output_path = excel_output_path
        self.plot_output_path = plot_output_path
        self.label_rois = show_labels
        self.label_overlay = None
        self.roi_areas = {}
        self.zoom_factor = 1.0
        self.zoom_center = (0.5, 0.5)
        self.combined_image = None
        self.roi_image = None
        self.setup_plot()

    def setup_plot(self):
        try:
            self.fig, self.ax = plt.subplots(figsize=(10, 10))
            plt.subplots_adjust(left=0.1, bottom=0.1)
            self.update_plot()
        except Exception as e:
            print(f"Error setting up plot: {e}")

    def create_overlays(self):
        try:
            # Verify if files exist
            if not os.path.exists(self.label_image_path):
                raise FileNotFoundError(f"Label image file not found: {self.label_image_path}")
            if not os.path.exists(self.original_image_path):
                raise FileNotFoundError(f"Original image file not found: {self.original_image_path}")

            # Read images
            label_image = cv2.imread(self.label_image_path, cv2.IMREAD_UNCHANGED)
            original_image = cv2.imread(self.original_image_path, cv2.IMREAD_COLOR)

            if label_image is None or original_image is None:
                raise ValueError("One or both images could not be loaded. Check the file paths.")

            unique_labels = np.unique(label_image)
            unique_labels = unique_labels[unique_labels > 0]
            colors = np.random.randint(0, 256, (len(unique_labels), 3), dtype=np.uint8)

            overlay_image_np = np.zeros_like(original_image)
            label_overlay_np = np.zeros_like(original_image)

            for idx, label in tqdm(enumerate(unique_labels), total=len(unique_labels), desc="Processing Labels"):
                mask = label_image == label
                overlay_image_np[mask] = colors[idx]
                label_overlay_np[mask] = colors[idx]

                label_color = colors[idx].astype(np.uint8)
                coords = np.nonzero(mask)
                if coords[0].size > 0:
                    center_y, center_x = int(np.mean(coords[0])), int(np.mean(coords[1]))
                    cv2.putText(label_overlay_np, str(label), (center_x, center_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

            self.roi_image = overlay_image_np
            self.label_roi_image = label_overlay_np
            alpha = 0.2
            self.combined_image = cv2.addWeighted(original_image, alpha, self.label_roi_image, 1 - alpha, 0)
        except Exception as e:
            print(f"Error creating overlays: {e}")

    def update_plot(self):
        if self.combined_image is None:
            self.create_overlays()
        image_to_show = self.combined_image if self.label_rois else self.roi_image

        if image_to_show is None:
            print("No image to show.")
            return

        self.ax.clear()
        h, w, _ = image_to_show.shape
        cx, cy = int(w * self.zoom_center[0]), int(h * self.zoom_center[1])
        zoom_w, zoom_h = int(w / self.zoom_factor), int(h / self.zoom_factor)
        zoom_x1, zoom_x2 = max(0, cx - zoom_w // 2), min(w, cx + zoom_w // 2)
        zoom_y1, zoom_y2 = max(0, cy - zoom_h // 2), min(h, cy + zoom_h // 2)
        zoom_image = image_to_show[zoom_y1:zoom_y2, zoom_x1:zoom_x2]

        self.ax.imshow(cv2.cvtColor(zoom_image, cv2.COLOR_BGR2RGB))
        self.ax.set_title('ROIs Overlay')
        self.ax.axis('off')
        try:
            self.fig.savefig(self.plot_output_path, dpi=300)
        except Exception as e:
            print(f"Error saving plot: {e}")

    def save_rois_to_excel(self):
        try:
            if not os.path.exists(self.label_image_path):
                raise FileNotFoundError(f"Label image file not found: {self.label_image_path}")
            if not os.path.exists(self.original_image_path):
                raise FileNotFoundError(f"Original image file not found: {self.original_image_path}")

            label_image = cv2.imread(self.label_image_path, cv2.IMREAD_UNCHANGED)
            original_image = cv2.imread(self.original_image_path, cv2.IMREAD_GRAYSCALE)
            if label_image is None or original_image is None:
                raise ValueError("Unable to load image(s) at provided path(s).")

            unique_labels = np.unique(label_image)
            unique_labels = unique_labels[unique_labels > 0]

            areas = []
            integrated_densities = []

            for label in unique_labels:
                mask = label_image == label
                area = np.sum(mask)
                integrated_density = np.sum(original_image[mask])
                areas.append(area)
                integrated_densities.append(integrated_density)

            roi_data = {
                'Label': unique_labels,
                'Area': areas,
                'Integrated Density': integrated_densities
            }
            df = pd.DataFrame(roi_data)

            df.to_excel(self.excel_output_path, index=False, engine='openpyxl')
            print(f"ROI information saved to {self.excel_output_path}")
        except Exception as e:
            print(f"Error saving ROIs to Excel: {e}")

def process_labels2rois(label_image_path, original_image_path, excel_output_path, plot_output_path, show_labels):
    visualizer = ROIVisualizer(
        label_image_path=label_image_path,
        original_image_path=original_image_path,
        excel_output_path=excel_output_path,
        plot_output_path=plot_output_path,
        show_labels=show_labels
    )
    visualizer.save_rois_to_excel()
    visualizer.update_plot()
