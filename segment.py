import torch
import numpy as np
import time
import threading
import os
from cellpose import io, models, transforms
import tqdm

from PIL import Image as PILImage
import numpy as np

class StopFlag:
    def __init__(self):
        self.stop = False
        self.model = models.Cellpose(gpu=torch.cuda.is_available(), model_type='cyto')  # Initialize Cellpose model

    def segment(self, directory, diameter, sharpen_radius, smooth_radius, tile_norm_blocksize, tile_norm_smooth3D, norm3D, invert, progress_callback=None):
        start_time = time.time()

        files = [filename.path for filename in os.scandir(directory) if filename.is_file()]
        total_files = len(files)

        if total_files == 0:
            if progress_callback:
                progress_callback(100)  # If no files, set progress to 100%
            print("No files to process.")
            return

        channels = [[0, 0]]

        for idx, filename in enumerate(tqdm.tqdm(files)):
            if self.stop:
                break
            for chan in channels:
                # Load image with PIL
                img = PILImage.open(filename).convert('RGB')  # Convert image to RGB
                img = np.array(img)  # Convert PIL image to numpy array
                
                img_smoothed = transforms.smooth_sharpen_img(img, smooth_radius=smooth_radius, sharpen_radius=sharpen_radius)
                img_normalized = transforms.normalize_img(
                    img_smoothed, normalize=True, tile_norm_blocksize=tile_norm_blocksize,
                    tile_norm_smooth3D=tile_norm_smooth3D, norm3D=norm3D, invert=invert
                )

                masks, flows, styles, diams = self.model.eval(img_normalized, diameter=diameter, channels=chan, flow_threshold=0.3, cellprob_threshold=0)

                def save_masks_with_timeout(img, masks, flows, filename):
                    stop_flag_local = StopFlag()

                    def save_masks_thread(img):
                        io.save_masks(img, masks, flows, filename, save_txt=False)

                    t = threading.Timer(30.0, lambda: setattr(stop_flag_local, "stop", True))
                    t.start()
                    thread = threading.Thread(target=save_masks_thread, args=(img,))
                    thread.start()
                    thread.join(timeout=30.0)
                    t.cancel()

                    if thread.is_alive():
                        print("Saving masks taking too long, skipping...")
                    else:
                        pass

                save_masks_with_timeout(img, masks, flows, filename)

            if progress_callback:
                progress = ((idx + 1) / total_files) * 100
                progress_callback(progress)

        if progress_callback:
            progress_callback(100)  # Ensure progress is set to 100% after completion

        print(f"Segmentation completed in {time.time() - start_time:.2f} seconds")
