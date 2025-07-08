import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys
import shutil
import subprocess
from PIL import Image, ImageTk
import glob
import re

class ImageViewer(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create canvas for image display
        self.canvas = tk.Canvas(self, bg="gray20", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Image variables
        self.image = None
        self.photo = None
        self.canvas_image = None
        self.zoom_factor = 1.0
        self.original_size = (0, 0)
        self.fit_to_window = True
        
        # Update variables
        self.update_pending = False
        self.last_canvas_size = (0, 0)
        
        # Bind events
        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-4>", self.zoom)  # Linux
        self.canvas.bind("<Button-5>", self.zoom)  # Linux
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Drag variables
        self.start_x = 0
        self.start_y = 0
        
    def load_image(self, image_path):
        """Load and display image"""
        try:
            self.image = Image.open(image_path)
            self.original_size = self.image.size
            self.zoom_factor = 1.0
            self.fit_to_window = True
            self.schedule_update()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load image: {str(e)}")
            
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        if self.image and self.fit_to_window:
            current_size = (event.width, event.height)
            if current_size != self.last_canvas_size:
                self.last_canvas_size = current_size
                self.schedule_update()
    
    def schedule_update(self):
        """Schedule display update to avoid multiple rapid updates"""
        if not self.update_pending:
            self.update_pending = True
            self.after(50, self.update_display)
            
    def update_display(self):
        """Update image display with current zoom"""
        self.update_pending = False
        
        if not self.image:
            return
            
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.schedule_update()
            return
            
        try:
            # Calculate display size
            if self.fit_to_window:
                # Fit image to canvas
                img_width, img_height = self.image.size
                scale_x = canvas_width / img_width
                scale_y = canvas_height / img_height
                scale = min(scale_x, scale_y, 1.0)  # Don't upscale initially
                
                display_width = max(1, int(img_width * scale))
                display_height = max(1, int(img_height * scale))
            else:
                # Use zoom factor
                display_width = max(1, int(self.original_size[0] * self.zoom_factor))
                display_height = max(1, int(self.original_size[1] * self.zoom_factor))
                
            # Limit maximum size to prevent memory issues
            max_size = 4000
            if display_width > max_size or display_height > max_size:
                scale = min(max_size / display_width, max_size / display_height)
                display_width = int(display_width * scale)
                display_height = int(display_height * scale)
                
            # Resize image
            display_image = self.image.resize((display_width, display_height), Image.Resampling.LANCZOS)
            self.photo = ImageTk.PhotoImage(display_image)
            
            # Clear canvas and display image
            self.canvas.delete("all")
            self.canvas_image = self.canvas.create_image(
                canvas_width//2, canvas_height//2, 
                anchor="center", image=self.photo
            )
            
        except Exception as e:
            print(f"Error updating display: {e}")
            # Try with smaller image if resize fails
            try:
                smaller_image = self.image.resize((100, 100), Image.Resampling.LANCZOS)
                self.photo = ImageTk.PhotoImage(smaller_image)
                self.canvas.delete("all")
                self.canvas_image = self.canvas.create_image(
                    canvas_width//2, canvas_height//2, 
                    anchor="center", image=self.photo
                )
            except:
                pass
        
    def start_drag(self, event):
        """Start dragging image"""
        self.start_x = event.x
        self.start_y = event.y
        
    def drag(self, event):
        """Drag image"""
        if self.canvas_image:
            dx = event.x - self.start_x
            dy = event.y - self.start_y
            self.canvas.move(self.canvas_image, dx, dy)
            self.start_x = event.x
            self.start_y = event.y
            
    def zoom(self, event):
        """Zoom image"""
        if not self.image:
            return
            
        # Get mouse position relative to canvas
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Store old zoom factor
        old_zoom = self.zoom_factor
        
        # Determine zoom direction
        if event.delta > 0 or event.num == 4:  # Zoom in
            self.zoom_factor *= 1.2
        elif event.delta < 0 or event.num == 5:  # Zoom out
            self.zoom_factor /= 1.2
            
        # Limit zoom
        self.zoom_factor = max(0.1, min(self.zoom_factor, 10.0))
        
        # Disable fit to window when zooming
        if self.zoom_factor != old_zoom:
            self.fit_to_window = False
            self.schedule_update()
            
    def fit_image(self):
        """Fit image to window"""
        if self.image:
            self.fit_to_window = True
            self.zoom_factor = 1.0
            self.schedule_update()
            
    def zoom_in(self):
        """Zoom in programmatically"""
        if self.image:
            self.zoom_factor *= 1.2
            self.zoom_factor = min(self.zoom_factor, 10.0)
            self.fit_to_window = False
            self.schedule_update()
            
    def zoom_out(self):
        """Zoom out programmatically"""
        if self.image:
            self.zoom_factor /= 1.2
            self.zoom_factor = max(self.zoom_factor, 0.1)
            self.fit_to_window = False
            self.schedule_update()
            
    def actual_size(self):
        """Show image at actual size"""
        if self.image:
            self.zoom_factor = 1.0
            self.fit_to_window = False
            self.schedule_update()

class ModuleButton(ctk.CTkButton):
    def __init__(self, master, module_path, display_name, icon_path, callback, **kwargs):
        super().__init__(master, text=display_name, command=lambda: callback(module_path), **kwargs)
        self.module_path = module_path
        self.display_name = display_name
        
        # Try to load icon
        try:
            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                icon_image = icon_image.resize((24, 24), Image.Resampling.LANCZOS)
                
                # Handle transparency properly
                if icon_image.mode in ('RGBA', 'LA') or 'transparency' in icon_image.info:
                    # Convert to RGBA if not already
                    if icon_image.mode != 'RGBA':
                        icon_image = icon_image.convert('RGBA')
                    self.icon = ctk.CTkImage(icon_image, size=(24, 24))
                else:
                    self.icon = ctk.CTkImage(icon_image, size=(24, 24))
                    
                self.configure(image=self.icon, compound="left")
            else:
                self.configure(text=f"? {display_name}")
        except Exception:
            self.configure(text=f"? {display_name}")

class OpenpixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # App configuration
        self.title("Openpix - Image Editor")
        self.geometry("1200x800")
        self.minsize(800, 600)  # Set minimum window size
        
        # Initialize variables
        self.current_image_path = None
        self.original_file_path = None  # Store original file path
        self.temp_dir = "temp"
        self.modules_dir = "modules"
        self.icons_dir = "icons"
        self.current_image_index = 0
        self.max_image_index = 0
        
        # Check required directories
        self.check_directories()
        
        # Clear temp directory
        self.clear_temp_directory()
        
        # Create UI
        self.create_ui()
        
        # Load initial image if provided
        if len(sys.argv) > 1:
            self.load_image(sys.argv[1])
        else:
            self.show_open_dialog()
            
    def check_directories(self):
        """Check if required directories exist"""
        required_dirs = [self.temp_dir, self.modules_dir, self.icons_dir]
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        
        if missing_dirs:
            messagebox.showerror(
                "Missing Directories", 
                f"The following directories are missing: {', '.join(missing_dirs)}\n"
                "Please reinstall the application."
            )
            sys.exit(1)
            
    def clear_temp_directory(self):
        """Clear temp directory"""
        if os.path.exists(self.temp_dir):
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")
                    
    def create_ui(self):
        """Create user interface"""
        # Create menu bar
        self.create_menu_bar()
        
        # Create main layout
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left panel - Image viewer
        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.image_viewer = ImageViewer(self.left_frame)
        self.image_viewer.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Right panel - Modules
        self.right_frame = ctk.CTkFrame(self.main_frame, width=300)
        self.right_frame.pack(side="right", fill="y", padx=(5, 0))
        self.right_frame.pack_propagate(False)
        
        # Modules title
        self.modules_title = ctk.CTkLabel(self.right_frame, text="Modules", font=("Arial", 16, "bold"))
        self.modules_title.pack(pady=(10, 5))
        
        # Search bar
        self.search_frame = ctk.CTkFrame(self.right_frame)
        self.search_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search modules...")
        self.search_entry.pack(fill="x", padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", self.on_search_change)
        
        # Clear search button
        self.clear_search_btn = ctk.CTkButton(self.search_frame, text="Clear", command=self.clear_search, width=60)
        self.clear_search_btn.pack(side="right", padx=5, pady=5)
        
        # Modules scrollable frame
        self.modules_scrollable = ctk.CTkScrollableFrame(self.right_frame)
        self.modules_scrollable.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Store all modules for filtering
        self.all_modules = []
        
        # Load modules
        self.load_modules()
        
    def create_menu_bar(self):
        """Create menu bar"""
        self.menu_frame = ctk.CTkFrame(self)
        self.menu_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Create scrollable frame for menu items
        self.menu_scroll = ctk.CTkScrollableFrame(self.menu_frame, orientation="horizontal", height=50)
        self.menu_scroll.pack(fill="x", expand=True)
        
        # File operations
        self.open_btn = ctk.CTkButton(self.menu_scroll, text="Open", command=self.open_file, width=80)
        self.open_btn.pack(side="left", padx=2, pady=5)
        
        self.save_btn = ctk.CTkButton(self.menu_scroll, text="Save", command=self.save_file, width=80)
        self.save_btn.pack(side="left", padx=2, pady=5)
        
        self.save_as_btn = ctk.CTkButton(self.menu_scroll, text="Save As", command=self.save_as_file, width=80)
        self.save_as_btn.pack(side="left", padx=2, pady=5)
        
        # Separator
        separator1 = ctk.CTkLabel(self.menu_scroll, text="|", width=20)
        separator1.pack(side="left", padx=5, pady=5)
        
        # Edit operations
        self.undo_btn = ctk.CTkButton(self.menu_scroll, text="Undo", command=self.undo, width=80)
        self.undo_btn.pack(side="left", padx=2, pady=5)
        
        self.redo_btn = ctk.CTkButton(self.menu_scroll, text="Redo", command=self.redo, width=80)
        self.redo_btn.pack(side="left", padx=2, pady=5)
        
        # Separator
        separator2 = ctk.CTkLabel(self.menu_scroll, text="|", width=20)
        separator2.pack(side="left", padx=5, pady=5)
        
        # Zoom operations
        self.zoom_in_btn = ctk.CTkButton(self.menu_scroll, text="Zoom In", command=self.zoom_in, width=80)
        self.zoom_in_btn.pack(side="left", padx=2, pady=5)
        
        self.zoom_out_btn = ctk.CTkButton(self.menu_scroll, text="Zoom Out", command=self.zoom_out, width=80)
        self.zoom_out_btn.pack(side="left", padx=2, pady=5)
        
        self.fit_btn = ctk.CTkButton(self.menu_scroll, text="Fit", command=self.fit_image, width=80)
        self.fit_btn.pack(side="left", padx=2, pady=5)
        
        # Separator
        separator3 = ctk.CTkLabel(self.menu_scroll, text="|", width=20)
        separator3.pack(side="left", padx=5, pady=5)
        
        # Settings
        self.settings_btn = ctk.CTkButton(self.menu_scroll, text="Settings", command=self.open_settings, width=80)
        self.settings_btn.pack(side="left", padx=2, pady=5)
        
    def load_modules(self):
        """Load modules from modules directory"""
        self.all_modules = []
        self.scan_modules_directory(self.modules_dir, self.modules_scrollable)
        
    def scan_modules_directory(self, directory, parent_frame, level=0):
        """Recursively scan modules directory"""
        items = []
        
        # Get all items in directory
        if os.path.exists(directory):
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isdir(item_path):
                    # Check if directory has .py files
                    if self.has_python_files(item_path):
                        items.append(("dir", item, item_path))
                elif item.endswith(".py"):
                    items.append(("file", item, item_path))
                    
        # Sort items
        items.sort(key=lambda x: (x[0] == "file", x[1]))
        
        # Create UI elements
        for item_type, item_name, item_path in items:
            if item_type == "dir":
                # Create collapsible section for directory
                self.create_module_group(parent_frame, item_name, item_path, level)
            else:
                # Create button for module
                module_info = self.create_module_button(parent_frame, item_name, item_path, level)
                if module_info:
                    self.all_modules.append(module_info)
                    
    def has_python_files(self, directory):
        """Check if directory has Python files recursively"""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    return True
        return False
        
    def create_module_group(self, parent_frame, group_name, group_path, level):
        """Create a collapsible group for modules"""
        # Group frame
        group_frame = ctk.CTkFrame(parent_frame)
        group_frame.pack(fill="x", pady=2, padx=level*10)
        
        # Group header
        header_frame = ctk.CTkFrame(group_frame)
        header_frame.pack(fill="x", padx=5, pady=2)
        
        # Group icon and name
        icon_path = os.path.join(self.icons_dir, f"{group_name}.png")
        group_btn = ctk.CTkButton(
            header_frame, 
            text=f"📁 {group_name}", 
            command=lambda: self.toggle_group(content_frame),
            height=30
        )
        group_btn.pack(side="left", fill="x", expand=True)
        
        # Content frame (collapsible)
        content_frame = ctk.CTkFrame(group_frame)
        content_frame.pack(fill="x", padx=5, pady=2)
        
        # Scan subdirectory
        self.scan_modules_directory(group_path, content_frame, level + 1)
        
    def create_module_button(self, parent_frame, module_name, module_path, level):
        """Create button for individual module"""
        # Clean display name
        display_name = module_name.replace(".py", "").replace("-", " ")
        
        # Icon path
        icon_path = os.path.join(self.icons_dir, f"{module_name}.png")
        
        # Create button
        btn = ModuleButton(
            parent_frame,
            module_path,
            display_name,
            icon_path,
            self.run_module,
            height=40
        )
        btn.pack(fill="x", pady=2, padx=level*10)
        
        # Return module info for search
        return {
            'button': btn,
            'name': display_name.lower(),
            'path': module_path,
            'frame': parent_frame
        }
        
    def toggle_group(self, content_frame):
        """Toggle visibility of group content"""
        if content_frame.winfo_viewable():
            content_frame.pack_forget()
        else:
            content_frame.pack(fill="x", padx=5, pady=2)
            
    def on_search_change(self, event=None):
        """Handle search input change"""
        search_text = self.search_entry.get().lower().strip()
        self.filter_modules(search_text)
        
    def clear_search(self):
        """Clear search and show all modules"""
        self.search_entry.delete(0, 'end')
        self.filter_modules("")
        
    def filter_modules(self, search_text):
        """Filter modules based on search text"""
        if not search_text:
            # Show all modules
            for module_info in self.all_modules:
                module_info['button'].pack(fill="x", pady=2, padx=0)
        else:
            # Hide non-matching modules
            for module_info in self.all_modules:
                if search_text in module_info['name']:
                    module_info['button'].pack(fill="x", pady=2, padx=0)
                else:
                    module_info['button'].pack_forget()
                    
    def refresh_modules(self):
        """Refresh module list"""
        # Clear existing modules
        for widget in self.modules_scrollable.winfo_children():
            widget.destroy()
        
        # Reload modules
        self.load_modules()
        
        # Apply current search filter
        search_text = self.search_entry.get().lower().strip()
        if search_text:
            self.filter_modules(search_text)
            
    def show_open_dialog(self):
        """Show file open dialog"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
            
    def load_image(self, image_path):
        """Load image into application"""
        try:
            # Store original file path
            self.original_file_path = image_path
            
            # Convert and save as PNG to temp directory
            temp_path = os.path.join(self.temp_dir, "image0.png")
            
            # Open image and convert to PNG
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA'):
                    # Keep transparency for PNG
                    img.save(temp_path, 'PNG')
                else:
                    # Convert to RGB for other formats
                    img.convert('RGB').save(temp_path, 'PNG')
            
            # Update current image
            self.current_image_path = temp_path
            self.current_image_index = 0
            self.max_image_index = 0
            
            # Load in viewer
            self.image_viewer.load_image(temp_path)
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load image: {str(e)}")
            
    def get_current_image_path(self):
        """Get current image path"""
        if not self.current_image_path:
            return None
        return os.path.join(self.temp_dir, f"image{self.current_image_index}.png")
        
    def run_module(self, module_path):
        """Run a module on current image"""
        current_path = self.get_current_image_path()
        if not current_path or not os.path.exists(current_path):
            messagebox.showwarning("Warning", "No image loaded")
            return
            
        try:
            # Prepare next image path
            next_index = self.current_image_index + 1
            next_path = os.path.join(self.temp_dir, f"image{next_index}.png")
            
            # Remove future images (for undo/redo)
            self.remove_future_images(next_index)
            
            # Run module
            cmd = [sys.executable, module_path, "-i", current_path, "-o", next_path]
            print(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Check if output file was actually created
                if os.path.exists(next_path):
                    # Success - update current image
                    self.current_image_index = next_index
                    self.max_image_index = next_index
                    self.image_viewer.load_image(next_path)
                    print(f"Module executed successfully: {module_path}")
                else:
                    # Module ran but no output file created (user cancelled)
                    print(f"Module completed but no output file created: {module_path}")
            else:
                # Error - show message and clean up
                error_msg = result.stderr or result.stdout or "Unknown error"
                messagebox.showerror("Module Error", f"Module failed: {error_msg}")
                print(f"Module error: {error_msg}")
                
                # Remove failed output file if it exists
                if os.path.exists(next_path):
                    os.remove(next_path)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Cannot run module: {str(e)}")
            print(f"Error running module: {str(e)}")
                        
    def remove_future_images(self, from_index):
        """Remove images with index >= from_index"""
        if not self.current_image_path:
            return
        
        for i in range(from_index, self.max_image_index + 10):  # Remove some extra just in case
            image_path = os.path.join(self.temp_dir, f"image{i}.png")
            if os.path.exists(image_path):
                os.remove(image_path)
                
    def undo(self):
        """Undo last operation"""
        if self.current_image_index > 0:
            self.current_image_index -= 1
            current_path = self.get_current_image_path()
            if os.path.exists(current_path):
                self.image_viewer.load_image(current_path)
                
    def redo(self):
        """Redo last undone operation"""
        if self.current_image_index < self.max_image_index:
            self.current_image_index += 1
            current_path = self.get_current_image_path()
            if os.path.exists(current_path):
                self.image_viewer.load_image(current_path)
                
    def actual_size(self):
        """Show image at actual size"""
        if self.image:
            self.zoom_factor = 1.0
            self.fit_to_window = False
            self.schedule_update()
            
    def fit_image(self):
        """Fit image to window"""
        self.image_viewer.fit_image()
        
    def zoom_in(self):
        """Zoom in image"""
        self.image_viewer.zoom_in()
        
    def zoom_out(self):
        """Zoom out image"""
        self.image_viewer.zoom_out()
                
    def open_file(self):
        """Open file dialog"""
        self.show_open_dialog()
        
    def save_file(self):
        """Save current image"""
        current_path = self.get_current_image_path()
        if not current_path or not os.path.exists(current_path):
            messagebox.showwarning("Warning", "No image to save")
            return
            
        if not self.original_file_path:
            messagebox.showwarning("Warning", "No original file path found")
            return
            
        try:
            # Overwrite the original input image
            shutil.copy2(current_path, self.original_file_path)
            messagebox.showinfo("Success", "Image saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot save image: {str(e)}")
            
    def save_as_file(self):
        """Save image as new file"""
        current_path = self.get_current_image_path()
        if not current_path or not os.path.exists(current_path):
            messagebox.showwarning("Warning", "No image to save")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=os.path.splitext(current_path)[1],
            filetypes=[
                ("JPEG files", "*.jpg"),
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                shutil.copy2(current_path, file_path)
                messagebox.showinfo("Success", "Image saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot save image: {str(e)}")
                
    def open_settings(self):
        """Open settings window"""
        settings_path = "setting.py"
        if os.path.exists(settings_path):
            try:
                subprocess.Popen([sys.executable, settings_path])
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open settings: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Settings file not found")

def main():
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Create and run app
    app = OpenpixApp()
    app.mainloop()

if __name__ == "__main__":
    main()
