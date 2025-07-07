# Openpix - Modular Image Editor

A modern, extensible image editor built with Python and CustomTkinter, featuring a modular architecture for easy customization and plugin development.

![Openpix Interface](https://via.placeholder.com/800x400?text=Openpix+Interface)

## Features

- **Modern Dark UI**: Built with CustomTkinter for a sleek, modern interface
- **Modular Architecture**: Extensible plugin system for custom image processing modules
- **Interactive Image Viewer**: 
  - Zoom in/out with mouse wheel
  - Pan images by dragging
  - Fit to window or view at actual size
- **Non-destructive Editing**: Undo/redo functionality preserves edit history
- **Module Organization**: Hierarchical module organization with search functionality
- **Multiple Format Support**: JPEG, PNG, BMP, GIF, TIFF, and more
- **Batch Processing Ready**: Modular design allows for easy batch processing implementation

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Required Dependencies

```bash
pip install customtkinter pillow
```

### Clone Repository

```bash
git clone https://github.com/nguyenhhoa03/Openpix.git
cd Openpix
```

### Directory Structure

Ensure your project has the following structure:

```
Openpix/
├── app.py              # Main application file
├── setting.py          # Settings configuration (optional)
├── modules/            # Image processing modules
│   ├── filters/        # Filter modules
│   ├── effects/        # Effect modules
│   └── tools/          # Tool modules
├── icons/              # Module icons (PNG format)
├── temp/               # Temporary files (auto-created)
└── README.md
```

## Usage

### Running the Application

```bash
python app.py
```

Or with an image file:

```bash
python app.py path/to/image.jpg
```

### Basic Operations

1. **Open Image**: Click "Open" or run with image path as argument
2. **Navigate**: Use zoom controls or mouse wheel to navigate
3. **Apply Modules**: Click module buttons in the right panel
4. **Undo/Redo**: Use the undo/redo buttons to navigate edit history
5. **Save**: Save changes to original file or save as new file

### Keyboard Shortcuts

- **Mouse Wheel**: Zoom in/out
- **Left Click + Drag**: Pan image
- **Search Bar**: Filter modules by name

## Module Development

### Creating Custom Modules

Modules are Python scripts that process images. They should follow this structure:

```python
#!/usr/bin/env python3
import argparse
from PIL import Image

def process_image(input_path, output_path):
    """
    Process the image from input_path and save to output_path
    """
    try:
        # Open input image
        image = Image.open(input_path)
        
        # Your processing logic here
        # Example: Convert to grayscale
        processed_image = image.convert('L')
        
        # Save processed image
        processed_image.save(output_path)
        return True
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Image processing module')
    parser.add_argument('-i', '--input', required=True, help='Input image path')
    parser.add_argument('-o', '--output', required=True, help='Output image path')
    
    args = parser.parse_args()
    
    success = process_image(args.input, args.output)
    if not success:
        exit(1)

if __name__ == "__main__":
    main()
```

### Module Guidelines

- **Input/Output**: Use `-i` for input and `-o` for output arguments
- **Error Handling**: Handle errors gracefully and return appropriate exit codes
- **File Formats**: Preserve original format when possible
- **Documentation**: Include docstrings and comments
- **Icons**: Add corresponding PNG icons in the `icons/` directory

### Module Organization

Organize modules in subdirectories within the `modules/` folder:

```
modules/
├── filters/
│   ├── blur.py
│   ├── sharpen.py
│   └── vintage.py
├── effects/
│   ├── sepia.py
│   ├── vignette.py
│   └── glow.py
└── tools/
    ├── crop.py
    ├── resize.py
    └── rotate.py
```

### Adding Icons

Place PNG icons in the `icons/` directory with the same name as your module:

```
icons/
├── blur.py.png
├── sharpen.py.png
├── sepia.py.png
└── crop.py.png
```

## Configuration

### Settings

The application can be configured through `setting.py` (if present). Access settings through the Settings button in the toolbar.

### Themes

The application uses CustomTkinter's dark theme by default. This can be modified in the `main()` function:

```python
ctk.set_appearance_mode("dark")  # "light", "dark", "system"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
```

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the Repository**: Create your own fork of the project
2. **Create Feature Branch**: `git checkout -b feature/new-feature`
3. **Follow Code Style**: Maintain consistent code formatting
4. **Test Your Changes**: Ensure all functionality works correctly
5. **Submit Pull Request**: Provide clear description of changes

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/Openpix.git
cd Openpix

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install customtkinter pillow

# Run in development mode
python app.py
```

## Troubleshooting

### Common Issues

1. **Missing Directories Error**: Ensure `modules/`, `icons/`, and `temp/` directories exist
2. **Module Not Working**: Check module follows the required argument structure (`-i`, `-o`)
3. **Icon Not Loading**: Verify PNG icon exists in `icons/` directory with correct name
4. **Permission Errors**: Ensure write permissions for temp directory

### Debug Mode

Run with Python's debug flag for detailed error information:

```bash
python -u app.py
```

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) for modern UI
- Image processing powered by [Pillow](https://pillow.readthedocs.io/)
- Inspired by modern image editing workflows

## Support

- **GitHub Issues**: Report bugs and request features
- **Discussions**: Share ideas and get help from the community
- **Wiki**: Additional documentation and tutorials

---

**Made with ❤️, Free and open source forever**
