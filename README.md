# Photo Watermark CLI Tool

A command-line tool that adds date watermarks to images based on their EXIF data.

## Features

- Reads EXIF date information from images (DateTimeOriginal, DateTime, etc.)
- Adds date watermark in YYYY-MM-DD format
- Customizable font size, color, and position
- Supports multiple image formats (JPEG, PNG, BMP, TIFF)
- Creates output in `{original_directory}_watermark` subdirectory
- Processes single files or entire directories

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python watermark.py /path/to/images
```

### Advanced Options
```bash
python watermark.py /path/to/images --font-size 48 --color red --position top-left
```

### Options

- `path`: Path to image file or directory containing images (required)
- `--font-size, -s`: Font size for watermark (default: 36)
- `--color, -c`: Font color (default: white). Supports:
  - Color names: `red`, `blue`, `white`, `black`, etc.
  - Hex values: `#ffffff`, `#ff0000`, etc.
  - RGBA values: `rgba(255,255,255,128)` for transparency
- `--position, -p`: Watermark position (default: bottom-right)

### Position Options

- `top-left`, `top-center`, `top-right`
- `center-left`, `center`, `center-right`
- `bottom-left`, `bottom-center`, `bottom-right`

## Examples

1. Process all images in a directory with default settings:
```bash
python watermark.py ./photos
```

2. Process a single image with custom font size:
```bash
python watermark.py image.jpg --font-size 48
```

3. Use custom color and position:
```bash
python watermark.py ./vacation_photos --color "rgba(255,255,255,180)" --position top-right
```

4. Large font in center position:
```bash
python watermark.py ./images --font-size 60 --color yellow --position center
```

## Output

- Watermarked images are saved in a new directory: `{original_directory}_watermark`
- Original images are not modified
- Only images with valid EXIF date information are processed
- Images without date information are skipped with a warning

## Requirements

- Python 3.6+
- Pillow (PIL) for image processing
- exifread for EXIF data extraction
- click for command-line interface (optional, using argparse instead)

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)