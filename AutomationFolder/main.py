import sys
import os
import cupy
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QLabel, QLineEdit, QPushButton, 
    QCheckBox, QSpinBox, QProgressBar, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import l2r
from segment import StopFlag as Cellpose
from mastersheet import genmasterSheet
from PIL import Image
import re

# Helper functions
def get_image_format(file_path):
    """Get the image format from file path using PIL."""
    try:
        img = Image.open(file_path)
        return img.format
    except Exception as e:
        print(f"Error determining image format: {e}")
        return ''

def check_cuda_availability():
    """Check if CUDA Toolkit is available using cupy."""
    try:
        return cupy.is_available()
    except Exception as e:
        print(f"Error checking CUDA availability: {e}")
        return False

class WorkerThread(QThread):
    cellpose_progress = pyqtSignal(float)
    labels2rois_progress = pyqtSignal(float)
    finished = pyqtSignal()

    def __init__(self, base_dir, output_dir, diameter, run_segmentation, run_labels2rois):
        super().__init__()
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.diameter = diameter
        self.run_segmentation = run_segmentation
        self.run_labels2rois = run_labels2rois
        self.cellpose = Cellpose()  # Initialize Cellpose class

    def run(self):
        if self.run_segmentation:
            print(f"Running segmentation in directory: {self.base_dir}")
            self.cellpose.segment(self.base_dir, diameter=int(self.diameter), progress_callback=self.update_cellpose_progress)
        
        if self.run_labels2rois:
            masks = [os.path.join(self.base_dir, f) for f in os.listdir(self.base_dir) if "cp_masks" in f]
            total_masks = len(masks)
            print(f"Found {total_masks} masks for processing.")

            if total_masks == 0:
                self.labels2rois_progress.emit(100)  # If no masks, set progress to 100%
                return

            self.labels2rois_progress.emit(0)  # Initialize Labels2ROIs progress to 0
            for idx, mask in enumerate(masks):
                print(f"Processing mask file: {mask}")
                
                # Determine paths
                label_image_path = mask
                original_image_path = self.get_original_image_path(mask)
                plot_output_path = os.path.join(self.output_dir, f"{self.get_file_base_name(mask)}_ROI.png")
                excel_output_path = os.path.join(self.output_dir, f"{self.get_file_base_name(mask)}.xlsx")

                print(f"Original image path: {original_image_path}")
                print(f"Plot output path: {plot_output_path}")
                print(f"Excel output path: {excel_output_path}")
                
                if not os.path.exists(original_image_path):
                    print(f"Error: Original image file does not exist: {original_image_path}")
                    continue
                
                visualizer = l2r.ROIVisualizer(
                    label_image_path, original_image_path, excel_output_path, plot_output_path, 
                    show_labels=True, progress_callback=self.update_labels2rois_progress
                )
                visualizer.save_rois_to_excel()

                # Update progress after each mask processed
                self.labels2rois_progress.emit(((idx + 1) / total_masks) * 100)

            summary_dir = os.path.join(self.output_dir, "SummarySheet")
            os.makedirs(summary_dir, exist_ok=True)
            master_excel_save_path = os.path.join(summary_dir, "Summary.xlsx")
            genmasterSheet(directory=self.output_dir, savePath=master_excel_save_path)

        self.finished.emit()

    def get_original_image_path(self, mask_path):
        """Generate the path for the original image based on the mask path."""
        # Extract the base name of the mask file
        mask_base_name = self.get_file_base_name(mask_path)
        
        # Generate possible patterns to match
        pattern = re.sub(r'_cp_masks$', '', mask_base_name)  # Remove '_cp_masks' to find the pattern
        
        original_image_path = None
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                if pattern in file:
                    possible_path = os.path.join(root, file)
                    # Check if it's a supported image format
                    if possible_path.lower().endswith(('.tif', '.tiff', '.png', '.jpg', '.jpeg')):
                        original_image_path = possible_path
                        break
            if original_image_path:
                break

        if not original_image_path:
            print(f"Warning: Original image not found for mask file: {mask_path}")

        return original_image_path

    def get_file_base_name(self, file_path):
        """Get the base name of the file without extension."""
        return os.path.splitext(os.path.basename(file_path))[0]

    def update_cellpose_progress(self, progress):
        self.cellpose_progress.emit(progress)

    def update_labels2rois_progress(self, progress):
        self.labels2rois_progress.emit(progress)

class ImageSegmentationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Segmentation Pipeline")
        self.base_dir = ''
        self.output_dir = ''
        self.diameter = 0
        self.image_list = []
        self.image_index = 0
        self.cuda_available = check_cuda_availability()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        base_dir_layout = QHBoxLayout()
        base_dir_label = QLabel("Base Directory:")
        self.base_dir_entry = QLineEdit()
        base_dir_button = QPushButton("Browse")
        base_dir_button.clicked.connect(self.select_base_dir)
        base_dir_layout.addWidget(base_dir_label)
        base_dir_layout.addWidget(self.base_dir_entry)
        base_dir_layout.addWidget(base_dir_button)
        layout.addLayout(base_dir_layout)
        
        output_dir_layout = QHBoxLayout()
        output_dir_label = QLabel("Output Directory:")
        self.output_dir_entry = QLineEdit()
        output_dir_button = QPushButton("Browse")
        output_dir_button.clicked.connect(self.select_output_dir)
        output_dir_layout.addWidget(output_dir_label)
        output_dir_layout.addWidget(self.output_dir_entry)
        output_dir_layout.addWidget(output_dir_button)
        layout.addLayout(output_dir_layout)
        
        self.segmentation_checkbox = QCheckBox("Run Segmentation")
        self.labels2rois_checkbox = QCheckBox("Run Label to ROI")
        layout.addWidget(self.segmentation_checkbox)
        layout.addWidget(self.labels2rois_checkbox)
        
        self.diameter_spinbox = QSpinBox()
        self.diameter_spinbox.setRange(0, 100)
        self.diameter_spinbox.setValue(0)
        self.diameter_spinbox.valueChanged.connect(self.update_diameter)
        layout.addWidget(QLabel("Cellpose Diameter:"))
        layout.addWidget(self.diameter_spinbox)
        
        run_button = QPushButton("Run Process")
        run_button.clicked.connect(self.run_process)
        layout.addWidget(run_button)
        
        # Progress bars
        self.cellpose_progress_bar = QProgressBar()
        self.labels2rois_progress_bar = QProgressBar()
        layout.addWidget(QLabel("Cellpose Progress:"))
        layout.addWidget(self.cellpose_progress_bar)
        layout.addWidget(QLabel("Labels2ROIs Progress:"))
        layout.addWidget(self.labels2rois_progress_bar)
        
        # CUDA Status Label
        self.cuda_status_label = QLabel("CUDA is detected." if self.cuda_available else "CUDA is not detected.")
        layout.addWidget(self.cuda_status_label)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        if not self.cuda_available:
            QMessageBox.warning(
                self, "CUDA Toolkit Not Found",
                "CUDA Toolkit is not detected on your system. The process will run slower without CUDA support.\n\n"
                "Do you want to continue without CUDA?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

    def select_base_dir(self):
        self.base_dir = QFileDialog.getExistingDirectory(self, "Select Base Directory")
        self.base_dir_entry.setText(self.base_dir)
        
    def select_output_dir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        self.output_dir_entry.setText(self.output_dir)
        
    def update_diameter(self):
        self.diameter = self.diameter_spinbox.value()
        
    def run_process(self):
        if not self.base_dir or not self.output_dir:
            QMessageBox.warning(self, "Input Error", "Please select both base and output directories.")
            return
        
        self.worker_thread = WorkerThread(
            self.base_dir, self.output_dir, self.diameter,
            self.segmentation_checkbox.isChecked(),
            self.labels2rois_checkbox.isChecked()
        )
        self.worker_thread.cellpose_progress.connect(self.update_cellpose_progress)
        self.worker_thread.labels2rois_progress.connect(self.update_labels2rois_progress)
        self.worker_thread.finished.connect(self.process_finished)
        self.worker_thread.start()

    def update_cellpose_progress(self, progress):
        self.cellpose_progress_bar.setValue(progress)

    def update_labels2rois_progress(self, progress):
        self.labels2rois_progress_bar.setValue(progress)

    def process_finished(self):
        QMessageBox.information(self, "Process Complete", "The image processing is complete.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSegmentationApp()
    window.show()
    sys.exit(app.exec())
