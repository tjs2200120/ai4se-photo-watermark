#!/usr/bin/env python3
"""
Photo Watermark CLI Tool
Adds date watermarks to images based on EXIF data
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List
import exifread
from PIL import Image, ImageDraw, ImageFont


class WatermarkPosition:
    """Position constants for watermark placement"""
    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"

    @classmethod
    def all_positions(cls):
        return [
            cls.TOP_LEFT, cls.TOP_CENTER, cls.TOP_RIGHT,
            cls.CENTER_LEFT, cls.CENTER, cls.CENTER_RIGHT,
            cls.BOTTOM_LEFT, cls.BOTTOM_CENTER, cls.BOTTOM_RIGHT
        ]


def extract_date_from_exif(image_path: str) -> Optional[str]:
    """
    Extract date from EXIF data and format as YYYY-MM-DD

    Args:
        image_path: Path to the image file

    Returns:
        Date string in YYYY-MM-DD format or None if no date found
    """
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

            # Try different EXIF date tags
            date_tags = [
                'EXIF DateTimeOriginal',
                'EXIF DateTime',
                'Image DateTime'
            ]

            for tag in date_tags:
                if tag in tags:
                    date_str = str(tags[tag])
                    # Parse EXIF date format: "YYYY:MM:DD HH:MM:SS"
                    try:
                        date_obj = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
                        return date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        continue

    except Exception as e:
        print(f"Warning: Could not read EXIF data from {image_path}: {e}")

    return None


def get_watermark_position(image_size: Tuple[int, int], text_size: Tuple[int, int],
                          position: str, margin: int = 20) -> Tuple[int, int]:
    """
    Calculate watermark position coordinates

    Args:
        image_size: (width, height) of the image
        text_size: (width, height) of the text
        position: Position string (e.g., "bottom-right")
        margin: Margin from edges in pixels

    Returns:
        (x, y) coordinates for text placement
    """
    img_width, img_height = image_size
    text_width, text_height = text_size

    # Calculate x coordinate
    if position.endswith('left'):
        x = margin
    elif position.endswith('right'):
        x = img_width - text_width - margin
    else:  # center
        x = (img_width - text_width) // 2

    # Calculate y coordinate
    if position.startswith('top'):
        y = margin
    elif position.startswith('bottom'):
        y = img_height - text_height - margin
    else:  # center
        y = (img_height - text_height) // 2

    return (x, y)


def add_watermark(image_path: str, output_path: str, date_text: str,
                 font_size: int = 36, font_color: str = "white",
                 position: str = WatermarkPosition.BOTTOM_RIGHT) -> bool:
    """
    Add date watermark to image

    Args:
        image_path: Path to input image
        output_path: Path to save watermarked image
        date_text: Date text to add as watermark
        font_size: Size of the font
        font_color: Color of the text
        position: Position of the watermark

    Returns:
        True if successful, False otherwise
    """
    try:
        # Open image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Create drawing context
            draw = ImageDraw.Draw(img)

            # Try to use a system font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except OSError:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
                except OSError:
                    font = ImageFont.load_default()

            # Get text dimensions
            bbox = draw.textbbox((0, 0), date_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Calculate position
            x, y = get_watermark_position(img.size, (text_width, text_height), position)

            # Add text with shadow for better visibility
            shadow_offset = max(1, font_size // 24)
            draw.text((x + shadow_offset, y + shadow_offset), date_text,
                     font=font, fill="black")
            draw.text((x, y), date_text, font=font, fill=font_color)

            # Save image
            img.save(output_path, quality=95)
            return True

    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return False


def process_images(input_path: str, font_size: int, font_color: str, position: str) -> None:
    """
    Process all images in the input directory

    Args:
        input_path: Path to input directory or file
        font_size: Font size for watermark
        font_color: Font color for watermark
        position: Position for watermark
    """
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"Error: Path {input_path} does not exist")
        return

    # Determine input files
    if input_path.is_file():
        if input_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            image_files = [input_path]
            base_dir = input_path.parent
        else:
            print(f"Error: {input_path} is not a supported image file")
            return
    else:
        # Get all image files from directory
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        image_files = [f for f in input_path.iterdir()
                      if f.is_file() and f.suffix.lower() in image_extensions]
        base_dir = input_path

    if not image_files:
        print(f"No image files found in {input_path}")
        return

    # Create output directory
    output_dir = base_dir / f"{base_dir.name}_watermark"
    output_dir.mkdir(exist_ok=True)

    processed = 0
    skipped = 0

    print(f"Processing {len(image_files)} image(s)...")
    print(f"Output directory: {output_dir}")

    for image_file in image_files:
        print(f"Processing: {image_file.name}")

        # Extract date from EXIF
        date_text = extract_date_from_exif(str(image_file))

        if date_text is None:
            print(f"  Warning: No date found in EXIF data, skipping")
            skipped += 1
            continue

        print(f"  Date found: {date_text}")

        # Generate output path
        output_file = output_dir / image_file.name

        # Add watermark
        if add_watermark(str(image_file), str(output_file), date_text,
                        font_size, font_color, position):
            print(f"  ✓ Saved: {output_file}")
            processed += 1
        else:
            print(f"  ✗ Failed to process")
            skipped += 1

    print(f"\nCompleted: {processed} processed, {skipped} skipped")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Add date watermarks to images based on EXIF data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Position options:
  {', '.join(WatermarkPosition.all_positions())}

Examples:
  python watermark.py /path/to/images
  python watermark.py /path/to/image.jpg --font-size 48 --color red --position top-left
  python watermark.py ./photos --font-size 24 --color "rgba(255,255,255,128)" --position bottom-center
        """
    )

    parser.add_argument(
        'path',
        help='Path to image file or directory containing images'
    )

    parser.add_argument(
        '--font-size', '-s',
        type=int,
        default=36,
        help='Font size for watermark (default: 36)'
    )

    parser.add_argument(
        '--color', '-c',
        default='white',
        help='Font color for watermark (default: white). Supports color names, hex (#ffffff), or rgba values'
    )

    parser.add_argument(
        '--position', '-p',
        choices=WatermarkPosition.all_positions(),
        default=WatermarkPosition.BOTTOM_RIGHT,
        help=f'Position of watermark (default: {WatermarkPosition.BOTTOM_RIGHT})'
    )

    args = parser.parse_args()

    # Validate font size
    if args.font_size <= 0:
        print("Error: Font size must be positive")
        sys.exit(1)

    # Process images
    process_images(args.path, args.font_size, args.color, args.position)


if __name__ == '__main__':
    main()