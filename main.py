import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFormLayout, QPushButton, QFileDialog, QCheckBox, QLabel, QLineEdit, QTextEdit, QProgressBar
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
import labels2rois as l2r
import cellpose as cellpose
from mastersheet import genmasterSheet

class WorkerThread(QThread):
    update_progress = pyqtSignal(float)
    append_text = pyqtSignal(str)

    def __init__(self, base_dir, output_dir, run_segmentation, run_labels2rois, diameter, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.run_segmentation = run_segmentation
        self.run_labels2rois = run_labels2rois
        self.diameter = diameter

    def run(self):
        if not self.base_dir or not self.output_dir:
            self.append_text.emit("Please select both base and output directories.\n")
            return

        if self.run_segmentation:
            try:
                self.append_text.emit("Starting segmentation...\n")
                cellpose.segment(self.base_dir, diameter=self.diameter, progress_callback=self.update_progress.emit)
                self.append_text.emit("Segmentation completed.\n")
            except Exception as e:
                self.append_text.emit(f"Error during segmentation: {e}\n")

        if self.run_labels2rois:
            try:
                self.append_text.emit("Processing ROIs...\n")
                masks = [f for f in os.listdir(self.base_dir) if "cp_masks" in f]
                if not masks:
                    self.append_text.emit("No mask files found.\n")
                    return
                
                ProgressCounter = 0
                total_files = len(masks)
                for i in masks:
                    label_image_path = os.path.join(self.base_dir, i)
                    original_image_path = os.path.join(self.base_dir, f"{self.PNG2TIFF(self.findoriginalimage(i))}")
                    plot_output_path = os.path.join(self.output_dir, f"{self.findoriginalimage(i)}_ROI.png")
                    excel_output_path = os.path.join(self.output_dir, f"{i}.xlsx")
                    
                    if not os.path.isfile(label_image_path) or not os.path.isfile(original_image_path):
                        self.append_text.emit(f"Files not found: {label_image_path} or {original_image_path}\n")
                        continue
                    
                    visualizer = l2r.ROIVisualizer(label_image_path, original_image_path, excel_output_path, plot_output_path, show_labels=True, progress_callback=self.update_progress.emit)
                    visualizer.save_rois_to_excel()
                    ProgressCounter += 1
                    self.append_text.emit(f"Processed {ProgressCounter}/{total_files} files\n")
                    
                summaryDir = os.path.join(self.output_dir, "SummarySheet")
                os.makedirs(summaryDir, exist_ok=True)
                master_excel_save_path = os.path.join(summaryDir, "Summary.xlsx")
                genmasterSheet(directory=self.output_dir, savePath=master_excel_save_path)
                self.append_text.emit("ROIs processed and summary sheet generated.\n")
            except Exception as e:
                self.append_text.emit(f"Error during ROI processing: {e}\n")

    def findoriginalimage(self, filename):
        name, extension = os.path.splitext(filename)
        new_name = name[:-9]
        new_filename = new_name + extension
        return new_filename

    def PNG2TIFF(self, filename):
        name, extension = os.path.splitext(filename)
        if extension.lower() == '.png':
            return name + '.tiff'
        return filename

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Segmentation and ROI Processor")

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.form_layout = QFormLayout()
        self.layout.addLayout(self.form_layout)

        self.base_dir_edit = QLineEdit()
        self.output_dir_edit = QLineEdit()
        self.diameter_edit = QLineEdit()
        self.diameter_edit.setText("30")  # Default value

        self.form_layout.addRow("Base Directory:", self.base_dir_edit)
        self.form_layout.addRow("Output Directory:", self.output_dir_edit)
        self.form_layout.addRow("Diameter:", self.diameter_edit)

        self.run_segmentation_check = QCheckBox("Run Cellpose Segmentation")
        self.run_labels2rois_check = QCheckBox("Run ROI Processing")

        self.form_layout.addRow(self.run_segmentation_check, self.run_labels2rois_check)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_processing)

        self.layout.addWidget(self.start_button)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.layout.addWidget(self.text_output)

    def start_processing(self):
        base_dir = self.base_dir_edit.text()
        output_dir = self.output_dir_edit.text()
        diameter = int(self.diameter_edit.text())

        run_segmentation = self.run_segmentation_check.isChecked()
        run_labels2rois = self.run_labels2rois_check.isChecked()

        self.worker = WorkerThread(base_dir, output_dir, run_segmentation, run_labels2rois, diameter)
        self.worker.update_progress.connect(self.update_progress)
        self.worker.append_text.connect(self.append_text)
        self.worker.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def append_text(self, text):
        self.text_output.append(text)
        cursor = self.text_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_output.setTextCursor(cursor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
