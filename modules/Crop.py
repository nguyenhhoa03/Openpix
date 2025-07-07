#!/usr/bin/env python3
"""
Image Crop and Edit Tool with CustomTkinter GUI
Usage: python crop.py -i <input_image_path> -o <output_image_path>
"""

import argparse
import sys
import os
from PIL import Image, ImageTk
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import math

class ImageCropTool:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.original_image = None
        self.current_image = None
        self.display_image = None
        self.photo = None
        self.canvas_width = 800
        self.canvas_height = 600
        self.scale_factor = 1.0
        
        # Crop variables
        self.crop_start_x = None
        self.crop_start_y = None
        self.crop_end_x = None
        self.crop_end_y = None
        self.crop_rect = None
        self.is_cropping = False
        
        # Initialize GUI
        self.setup_gui()
        self.load_image()
        
    def setup_gui(self):
        """Initialize the GUI with CustomTkinter"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Main window
        self.root = ctk.CTk()
        self.root.title("Image Crop & Edit Tool")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure grid weights for resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Control panel
        self.create_control_panel(main_frame)
        
        # Canvas frame
        canvas_frame = ctk.CTkFrame(main_frame)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        canvas_frame.grid_columnconfigure(0, weight=1)
        canvas_frame.grid_rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.canvas = tk.Canvas(canvas_frame, bg="gray20", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical", command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        h_scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="horizontal", command=self.canvas.xview)
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.canvas.configure(xscrollcommand=h_scrollbar.set)
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.start_crop)
        self.canvas.bind("<B1-Motion>", self.update_crop)
        self.canvas.bind("<ButtonRelease-1>", self.end_crop)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Bind resize event
        self.root.bind("<Configure>", self.on_window_resize)
        
    def create_control_panel(self, parent):
        """Create the control panel with buttons"""
        control_frame = ctk.CTkFrame(parent)
        control_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        control_frame.grid_columnconfigure(7, weight=1)
        
        # Rotation buttons
        rotate_left_btn = ctk.CTkButton(control_frame, text="Rotate Left", command=self.rotate_left, width=100)
        rotate_left_btn.grid(row=0, column=0, padx=5, pady=5)
        
        rotate_right_btn = ctk.CTkButton(control_frame, text="Rotate Right", command=self.rotate_right, width=100)
        rotate_right_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Mirror buttons
        mirror_h_btn = ctk.CTkButton(control_frame, text="Mirror H", command=self.mirror_horizontal, width=100)
        mirror_h_btn.grid(row=0, column=2, padx=5, pady=5)
        
        mirror_v_btn = ctk.CTkButton(control_frame, text="Mirror V", command=self.mirror_vertical, width=100)
        mirror_v_btn.grid(row=0, column=3, padx=5, pady=5)
        
        # Angle rotation
        angle_label = ctk.CTkLabel(control_frame, text="Angle:")
        angle_label.grid(row=0, column=4, padx=5, pady=5)
        
        self.angle_entry = ctk.CTkEntry(control_frame, width=60, placeholder_text="0")
        self.angle_entry.grid(row=0, column=5, padx=5, pady=5)
        
        rotate_angle_btn = ctk.CTkButton(control_frame, text="Rotate", command=self.rotate_by_angle, width=80)
        rotate_angle_btn.grid(row=0, column=6, padx=5, pady=5)
        
        # Crop and Done buttons
        crop_btn = ctk.CTkButton(control_frame, text="Crop", command=self.apply_crop, width=100)
        crop_btn.grid(row=0, column=8, padx=5, pady=5)
        
        done_btn = ctk.CTkButton(control_frame, text="Done", command=self.save_and_exit, width=100, fg_color="green", hover_color="darkgreen")
        done_btn.grid(row=0, column=9, padx=5, pady=5)
        
        # Reset button
        reset_btn = ctk.CTkButton(control_frame, text="Reset", command=self.reset_image, width=100)
        reset_btn.grid(row=0, column=10, padx=5, pady=5)
        
    def load_image(self):
        """Load the input image"""
        try:
            self.original_image = Image.open(self.input_path)
            self.current_image = self.original_image.copy()
            self.update_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.root.quit()
            
    def update_display(self):
        """Update the canvas with the current image"""
        if self.current_image is None:
            return
            
        # Calculate scale factor to fit image in canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.update_display)
            return
            
        img_width, img_height = self.current_image.size
        
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        self.scale_factor = min(scale_x, scale_y, 1.0)  # Don't scale up
        
        # Resize image for display
        display_width = int(img_width * self.scale_factor)
        display_height = int(img_height * self.scale_factor)
        
        self.display_image = self.current_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.display_image)
        
        # Clear canvas and display image
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.photo, anchor="center")
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def start_crop(self, event):
        """Start cropping selection"""
        self.is_cropping = True
        self.crop_start_x = self.canvas.canvasx(event.x)
        self.crop_start_y = self.canvas.canvasy(event.y)
        
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            
    def update_crop(self, event):
        """Update cropping selection"""
        if not self.is_cropping:
            return
            
        self.crop_end_x = self.canvas.canvasx(event.x)
        self.crop_end_y = self.canvas.canvasy(event.y)
        
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y,
            self.crop_end_x, self.crop_end_y,
            outline="red", width=2
        )
        
    def end_crop(self, event):
        """End cropping selection"""
        self.is_cropping = False
        
    def apply_crop(self):
        """Apply the crop operation"""
        if not self.crop_rect or self.crop_start_x is None:
            messagebox.showwarning("Warning", "Please select an area to crop first")
            return
            
        # Calculate actual image coordinates
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Get image position on canvas
        img_width, img_height = self.display_image.size
        img_x = (canvas_width - img_width) // 2
        img_y = (canvas_height - img_height) // 2
        
        # Convert canvas coordinates to image coordinates
        crop_x1 = max(0, int((self.crop_start_x - img_x) / self.scale_factor))
        crop_y1 = max(0, int((self.crop_start_y - img_y) / self.scale_factor))
        crop_x2 = min(self.current_image.width, int((self.crop_end_x - img_x) / self.scale_factor))
        crop_y2 = min(self.current_image.height, int((self.crop_end_y - img_y) / self.scale_factor))
        
        if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
            messagebox.showwarning("Warning", "Invalid crop area")
            return
            
        # Apply crop
        self.current_image = self.current_image.crop((crop_x1, crop_y1, crop_x2, crop_y2))
        
        # Clear crop selection
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None
            
        self.update_display()
        
    def rotate_left(self):
        """Rotate image 90 degrees counter-clockwise"""
        self.current_image = self.current_image.rotate(90, expand=True)
        self.update_display()
        
    def rotate_right(self):
        """Rotate image 90 degrees clockwise"""
        self.current_image = self.current_image.rotate(-90, expand=True)
        self.update_display()
        
    def mirror_horizontal(self):
        """Mirror image horizontally"""
        self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.update_display()
        
    def mirror_vertical(self):
        """Mirror image vertically"""
        self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.update_display()
        
    def rotate_by_angle(self):
        """Rotate image by specified angle"""
        try:
            angle = float(self.angle_entry.get() or 0)
            self.current_image = self.current_image.rotate(angle, expand=True, fillcolor=(255, 255, 255, 0))
            self.update_display()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid angle")
            
    def reset_image(self):
        """Reset image to original"""
        self.current_image = self.original_image.copy()
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None
        self.update_display()
        
    def save_and_exit(self):
        """Save the image and exit"""
        try:
            # Get the original format
            original_format = self.original_image.format
            
            # Save with original format
            if original_format:
                self.current_image.save(self.output_path, format=original_format)
            else:
                # If format is unknown, use the file extension
                self.current_image.save(self.output_path)
                
            # Exit immediately without any message
            self.root.quit()
            sys.exit(0)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save image: {str(e)}")
            
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.update_display()
        
    def on_window_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            self.root.after(100, self.update_display)
            
    def run(self):
        """Run the application"""
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description='Image Crop and Edit Tool')
    parser.add_argument('-i', '--input', required=True, help='Input image path')
    parser.add_argument('-o', '--output', required=True, help='Output image path')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found")
        sys.exit(1)
        
    # Check if output directory exists
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Create and run the application
    app = ImageCropTool(args.input, args.output)
    app.run()

if __name__ == "__main__":
    main()
