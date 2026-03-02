import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image, ImageTk
import rasterio
from rasterio.plot import reshape_as_image
import os


class BandThresholdAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-band TIF File Threshold Analysis Tool")
        self.root.geometry("1070x800")

        self.band1 = None
        self.band2 = None
        self.band3 = None
        self.norm_band1 = None
        self.norm_band2 = None
        self.norm_band3 = None
        self.rows = 0
        self.cols = 0
        self.all_bands = None
        self.src_profile = None
        self.current_mask = None

        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        file_frame = ttk.LabelFrame(main_frame, text="File Operations", padding="10")
        file_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.load_button = ttk.Button(file_frame, text="Load TIF File", command=self.load_tif_file)
        self.load_button.grid(row=0, column=0, padx=(0, 10))

        self.file_path_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.file_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        band_select_frame = ttk.LabelFrame(main_frame, text="Band Selection", padding="10")
        band_select_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(band_select_frame, text="Band 1:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.band1_var = tk.StringVar(value="1")
        self.band1_combo = ttk.Combobox(band_select_frame, textvariable=self.band1_var, width=5, state="readonly")
        self.band1_combo.grid(row=0, column=1, padx=(0, 20))

        ttk.Label(band_select_frame, text="Band 2:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.band2_var = tk.StringVar(value="2")
        self.band2_combo = ttk.Combobox(band_select_frame, textvariable=self.band2_var, width=5, state="readonly")
        self.band2_combo.grid(row=0, column=3, padx=(0, 20))

        ttk.Label(band_select_frame, text="Band 3:").grid(row=0, column=4, sticky=tk.W, padx=(0, 10))
        self.band3_var = tk.StringVar(value="3")
        self.band3_combo = ttk.Combobox(band_select_frame, textvariable=self.band3_var, width=5, state="readonly")
        self.band3_combo.grid(row=0, column=5, padx=(0, 20))

        control_frame = ttk.LabelFrame(main_frame, text="Band Threshold Settings", padding="10")
        control_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Label(control_frame, text="Band 1:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        ttk.Label(control_frame, text="Min:").grid(row=0, column=1, sticky=tk.W)
        self.band1_min_var = tk.DoubleVar(value=0)
        self.band1_min_entry = ttk.Entry(control_frame, textvariable=self.band1_min_var, width=8)
        self.band1_min_entry.grid(row=0, column=2, padx=(5, 10))
        self.band1_min_slider = ttk.Scale(
            control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
            length=150, command=self.update_band1_min_slider
        )
        self.band1_min_slider.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 10))

        ttk.Label(control_frame, text="Max:").grid(row=0, column=4, sticky=tk.W)
        self.band1_max_var = tk.DoubleVar(value=255)
        self.band1_max_entry = ttk.Entry(control_frame, textvariable=self.band1_max_var, width=8)
        self.band1_max_entry.grid(row=0, column=5, padx=(5, 10))
        self.band1_max_slider = ttk.Scale(
            control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
            length=150, command=self.update_band1_max_slider
        )
        self.band1_max_slider.grid(row=0, column=6, sticky=(tk.W, tk.E), padx=(5, 10))

        ttk.Label(control_frame, text="Band 2:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(control_frame, text="Min:").grid(row=1, column=1, sticky=tk.W)
        self.band2_min_var = tk.DoubleVar(value=0)
        self.band2_min_entry = ttk.Entry(control_frame, textvariable=self.band2_min_var, width=8)
        self.band2_min_entry.grid(row=1, column=2, padx=(5, 10))
        self.band2_min_slider = ttk.Scale(
            control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
            length=150, command=self.update_band2_min_slider
        )
        self.band2_min_slider.grid(row=1, column=3, sticky=(tk.W, tk.E), padx=(5, 10))

        ttk.Label(control_frame, text="Max:").grid(row=1, column=4, sticky=tk.W)
        self.band2_max_var = tk.DoubleVar(value=255)
        self.band2_max_entry = ttk.Entry(control_frame, textvariable=self.band2_max_var, width=8)
        self.band2_max_entry.grid(row=1, column=5, padx=(5, 10))
        self.band2_max_slider = ttk.Scale(
            control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
            length=150, command=self.update_band2_max_slider
        )
        self.band2_max_slider.grid(row=1, column=6, sticky=(tk.W, tk.E), padx=(5, 10))

        ttk.Label(control_frame, text="Band 3:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Label(control_frame, text="Min:").grid(row=2, column=1, sticky=tk.W)
        self.band3_min_var = tk.DoubleVar(value=0)
        self.band3_min_entry = ttk.Entry(control_frame, textvariable=self.band3_min_var, width=8)
        self.band3_min_entry.grid(row=2, column=2, padx=(5, 10))
        self.band3_min_slider = ttk.Scale(
            control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
            length=150, command=self.update_band3_min_slider
        )
        self.band3_min_slider.grid(row=2, column=3, sticky=(tk.W, tk.E), padx=(5, 10))

        ttk.Label(control_frame, text="Max:").grid(row=2, column=4, sticky=tk.W)
        self.band3_max_var = tk.DoubleVar(value=255)
        self.band3_max_entry = ttk.Entry(control_frame, textvariable=self.band3_max_var, width=8)
        self.band3_max_entry.grid(row=2, column=5, padx=(5, 10))
        self.band3_max_slider = ttk.Scale(
            control_frame, from_=0, to=255, orient=tk.HORIZONTAL,
            length=150, command=self.update_band3_max_slider
        )
        self.band3_max_slider.grid(row=2, column=6, sticky=(tk.W, tk.E), padx=(5, 10))

        control_frame.columnconfigure(3, weight=1)
        control_frame.columnconfigure(6, weight=1)

        self.bind_entry_events()

        calc_frame = ttk.Frame(main_frame, padding="10")
        calc_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.calc_button = ttk.Button(calc_frame, text="Calculate by Thresholds", command=self.calculate_with_thresholds)
        self.calc_button.grid(row=0, column=0, padx=(0, 10))

        self.calc_status_label = ttk.Label(calc_frame, text="Click 'Calculate by Thresholds' to start analysis", foreground="gray")
        self.calc_status_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        result_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        result_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.total_pixels_label = ttk.Label(result_frame, text="Total pixels: 0")
        self.total_pixels_label.grid(row=0, column=0, padx=(0, 20))

        self.valid_pixels_label = ttk.Label(result_frame, text="Valid pixels: 0")
        self.valid_pixels_label.grid(row=0, column=1, padx=(0, 20))

        self.percentage_label = ttk.Label(result_frame, text="Valid percentage: 0.00%")
        self.percentage_label.grid(row=0, column=3)

        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        self.output_button = ttk.Button(button_frame, text="Output Valid TIF File", command=self.output_result_tif)
        self.output_button.grid(row=0, column=0, padx=(0, 10))
        self.output_button.config(state=tk.DISABLED)

        self.output_status_label = ttk.Label(button_frame, text="", foreground="blue")
        self.output_status_label.grid(row=0, column=1, sticky=(tk.W, tk.E))

        viz_frame = ttk.LabelFrame(main_frame, text="Visualization Results", padding="10")
        viz_frame.grid(row=6, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.canvas = tk.Canvas(viz_frame, width=600, height=400, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        main_frame.rowconfigure(6, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.band1_var.trace_add("write", self.on_band_selection_change)

    def bind_entry_events(self):
        def validate_and_update(entry, var, slider):
            def callback(*args):
                try:
                    val = float(var.get())
                    if val < 0:
                        val = 0
                    elif val > 255:
                        val = 255
                    var.set(val)
                    slider.set(val)
                except ValueError:
                    pass

            entry.bind('<FocusOut>', lambda e: callback())
            entry.bind('<Return>', lambda e: callback())

        validate_and_update(self.band1_min_entry, self.band1_min_var, self.band1_min_slider)
        validate_and_update(self.band1_max_entry, self.band1_max_var, self.band1_max_slider)
        validate_and_update(self.band2_min_entry, self.band2_min_var, self.band2_min_slider)
        validate_and_update(self.band2_max_entry, self.band2_max_var, self.band2_max_slider)
        validate_and_update(self.band3_min_entry, self.band3_min_var, self.band3_min_slider)
        validate_and_update(self.band3_max_entry, self.band3_max_var, self.band3_max_slider)

    def update_band1_min_slider(self, val):
        self.band1_min_var.set(float(val))

    def update_band1_max_slider(self, val):
        self.band1_max_var.set(float(val))

    def update_band2_min_slider(self, val):
        self.band2_min_var.set(float(val))

    def update_band2_max_slider(self, val):
        self.band2_max_var.set(float(val))

    def update_band3_min_slider(self, val):
        self.band3_min_var.set(float(val))

    def update_band3_max_slider(self, val):
        self.band3_max_var.set(float(val))

    def load_tif_file(self):
        file_path = filedialog.askopenfilename(
            title="Select TIF File",
            filetypes=[("TIF files", "*.tif *.tiff"), ("All files", "*.*")]
        )

        if not file_path:
            return

        try:
            with rasterio.open(file_path) as src:
                self.src_profile = src.profile.copy()

                self.all_bands = src.read()
                self.rows, self.cols = src.height, src.width

                num_bands = src.count
                band_options = [str(i + 1) for i in range(min(num_bands, 10))]

                self.band1_combo['values'] = band_options
                self.band2_combo['values'] = band_options
                self.band3_combo['values'] = band_options

                if num_bands >= 1:
                    self.band1_var.set("1")
                if num_bands >= 2:
                    self.band2_var.set("2")
                if num_bands >= 3:
                    self.band3_var.set("3")

                self.file_path_label.config(text=os.path.basename(file_path))

                self.load_selected_bands()

                self.reset_slider_ranges()

                self.calc_status_label.config(text="Please set thresholds and click 'Calculate by Thresholds'", foreground="orange")

        except Exception as e:
            messagebox.showerror("Error", f"Cannot load TIF file:\n{str(e)}")

    def reset_slider_ranges(self):
        for band_name, band_data, min_slider, max_slider, min_var, max_var in [
            ("Band 1", self.band1, self.band1_min_slider, self.band1_max_slider, self.band1_min_var, self.band1_max_var),
            ("Band 2", self.band2, self.band2_min_slider, self.band2_max_slider, self.band2_min_var, self.band2_max_var),
            ("Band 3", self.band3, self.band3_min_slider, self.band3_max_slider, self.band3_min_var, self.band3_max_var)
        ]:
            if band_data is None:
                continue

            min_val = float(np.nanmin(band_data))
            max_val = float(np.nanmax(band_data))

            if np.isnan(min_val) or np.isnan(max_val):
                min_val, max_val = 0.0, 255.0
                messagebox.showwarning("Data Warning", f"{band_name} data is all invalid values (NaN), using default range 0-255")
            elif min_val == max_val:
                offset = max(1.0, abs(min_val) * 0.1) if min_val != 0 else 1.0
                min_val = min_val - offset
                max_val = max_val + offset

            safe_min = min(min_val, max_val - 0.1)
            safe_max = max(max_val, min_val + 0.1)

            min_slider.configure(from_=safe_min, to=safe_max)
            max_slider.configure(from_=safe_min, to=safe_max)
            min_var.set(safe_min)
            max_var.set(safe_max)

    def load_selected_bands(self):
        if self.all_bands is not None:
            try:
                band1_idx = int(self.band1_var.get()) - 1
                band2_idx = int(self.band2_var.get()) - 1
                band3_idx = int(self.band3_var.get()) - 1

                if band1_idx >= self.all_bands.shape[0]:
                    raise IndexError(f"Band 1 index out of range, max available bands: {self.all_bands.shape[0]}")
                if band2_idx >= self.all_bands.shape[0]:
                    raise IndexError(f"Band 2 index out of range, max available bands: {self.all_bands.shape[0]}")
                if band3_idx >= self.all_bands.shape[0]:
                    raise IndexError(f"Band 3 index out of range, max available bands: {self.all_bands.shape[0]}")

                self.band1 = self.all_bands[band1_idx, :, :].astype(np.float32)
                self.band2 = self.all_bands[band2_idx, :, :].astype(np.float32)
                self.band3 = self.all_bands[band3_idx, :, :].astype(np.float32)

                self.norm_band1 = self.normalize_band(self.band1)
                self.norm_band2 = self.normalize_band(self.band2)
                self.norm_band3 = self.normalize_band(self.band3)

            except Exception as e:
                messagebox.showerror("Error", f"Error loading bands:\n{str(e)}")

    def normalize_band(self, band):
        min_val = np.nanmin(band)
        max_val = np.nanmax(band)

        if np.isnan(min_val) or np.isnan(max_val) or min_val == max_val:
            return np.zeros_like(band, dtype=np.uint8)

        band_clean = np.where(np.isnan(band), min_val, band)
        normalized = (band_clean - min_val) / (max_val - min_val) * 255
        normalized = np.nan_to_num(normalized, nan=0.0, posinf=255.0, neginf=0.0)
        return normalized.astype(np.uint8)

    def on_band_selection_change(self, *args):
        self.load_selected_bands()
        self.reset_slider_ranges()
        self.calc_status_label.config(text="Please set thresholds and click 'Calculate by Thresholds'", foreground="orange")
        self.output_button.config(state=tk.DISABLED)
        self.clear_visualization()

    def clear_visualization(self):
        img_array = np.zeros((400, 600, 3), dtype=np.uint8)
        img = Image.fromarray(img_array, 'RGB')
        self.photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(300, 200, image=self.photo)

        self.total_pixels_label.config(text="Total pixels: 0")
        self.valid_pixels_label.config(text="Valid pixels: 0")
        self.percentage_label.config(text="Valid percentage: 0.00%")

    def calculate_with_thresholds(self):
        if self.band1 is None:
            messagebox.showwarning("Warning", "Please load a TIF file first!")
            return

        result = self.calculate_valid_pixels()
        self.current_mask = result['mask']

        self.total_pixels_label.config(text=f"Total pixels: {result['total']:,}")
        self.valid_pixels_label.config(text=f"Valid pixels: {result['valid']:,}")
        self.percentage_label.config(text=f"Valid percentage: {result['percentage']:.2f}%")

        photo = self.create_visualization_image(result['mask'])

        self.photo = photo

        self.canvas.delete("all")
        self.canvas.create_image(300, 200, image=photo)

        self.calc_status_label.config(text="Calculation completed, ready to output results", foreground="green")

        self.output_button.config(state=tk.NORMAL)

    def calculate_valid_pixels(self):
        if self.band1 is None or self.band2 is None or self.band3 is None:
            return {'total': 0, 'valid': 0, 'percentage': 0, 'area': 0,
                    'mask': np.zeros((self.rows, self.cols), dtype=bool)}

        try:
            b1_min, b1_max = float(self.band1_min_var.get()), float(self.band1_max_var.get())
            b2_min, b2_max = float(self.band2_min_var.get()), float(self.band2_max_var.get())
            b3_min, b3_max = float(self.band3_min_var.get()), float(self.band3_max_var.get())
        except (ValueError, TypeError):
            messagebox.showerror("Parameter Error", "Invalid threshold input, please check values")
            return {'total': self.rows * self.cols, 'valid': 0, 'percentage': 0, 'area': 0,
                    'mask': np.zeros((self.rows, self.cols), dtype=bool)}

        if b1_min > b1_max: b1_min, b1_max = b1_max, b1_min
        if b2_min > b2_max: b2_min, b2_max = b2_max, b2_min
        if b3_min > b3_max: b3_min, b3_max = b3_max, b3_min

        band1_clean = np.where(np.isnan(self.band1), -np.inf, self.band1)
        band2_clean = np.where(np.isnan(self.band2), -np.inf, self.band2)
        band3_clean = np.where(np.isnan(self.band3), -np.inf, self.band3)

        valid_mask = (
                (band1_clean >= b1_min) & (band1_clean <= b1_max) &
                (band2_clean >= b2_min) & (band2_clean <= b2_max) &
                (band3_clean >= b3_min) & (band3_clean <= b3_max)
        )

        total_pixels = self.rows * self.cols
        valid_pixels = int(np.sum(valid_mask))
        percentage = (valid_pixels / total_pixels * 100) if total_pixels > 0 else 0.0
        area = valid_pixels * 0.15

        return {
            'total': total_pixels,
            'valid': valid_pixels,
            'percentage': percentage,
            'area': area,
            'mask': valid_mask
        }

    def create_visualization_image(self, mask):
        if self.norm_band1 is None:
            img_array = np.zeros((400, 600, 3), dtype=np.uint8)
            img = Image.fromarray(img_array, 'RGB')
            return ImageTk.PhotoImage(img)

        img_array = np.zeros((self.rows, self.cols, 3), dtype=np.uint8)

        img_array[mask, 0] = 0
        img_array[mask, 1] = 255
        img_array[mask, 2] = 0

        invalid_mask = ~mask
        avg_values = (self.norm_band1 + self.norm_band2 + self.norm_band3) // 3
        img_array[invalid_mask, 0] = avg_values[invalid_mask]
        img_array[invalid_mask, 1] = avg_values[invalid_mask]
        img_array[invalid_mask, 2] = avg_values[invalid_mask]

        img = Image.fromarray(img_array, 'RGB')
        img = img.resize((600, 400), Image.Resampling.LANCZOS)

        return ImageTk.PhotoImage(img)

    def output_result_tif(self):
        if self.current_mask is None:
            messagebox.showwarning("Warning", "Please click 'Calculate by Thresholds' to analyze first!")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Valid TIF File",
            defaultextension=".tif",
            filetypes=[("TIF files", "*.tif"), ("All files", "*.*")]
        )

        if not output_path:
            return

        try:
            output_data = np.zeros((1, self.rows, self.cols), dtype=np.uint8)
            output_data[0, self.current_mask] = 1

            profile = self.src_profile.copy()
            profile.update({
                'count': 1,
                'dtype': 'uint8',
                'compress': 'lzw'
            })

            profile.pop('nodata', None)

            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(output_data)

            self.output_status_label.config(text=f"Successfully saved to: {os.path.basename(output_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save TIF file:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BandThresholdAnalyzer(root)
    root.mainloop()
