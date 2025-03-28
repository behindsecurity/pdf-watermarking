# PDF Watermarking Script

This Python script adds a watermark image to all pages of a given PDF file using PyMuPDF and Pillow. The watermark image is centered on each page, and optional transparency and shadow effects can be applied.

## Features
- Add a watermark to all pages of a PDF
- Resize watermark image to fit within page dimensions
- Adjust watermark transparency
- Optionally apply a shadow effect
- Command-line support with `argparse`

## Requirements
Ensure you have the required dependencies installed:

```sh
pip install pymupdf pillow
```

## Usage
Run the script using the following command:

```sh
python script.py input.pdf output.pdf watermark.png [options]
```

### Arguments
| Argument | Description |
|----------|-------------|
| `input_pdf` | Path to the input PDF file |
| `output_pdf` | Path to the output PDF file |
| `watermark_image` | Path to the watermark image file |

### Optional Arguments
| Argument | Description | Default |
|----------|-------------|---------|
| `--image_opacity` | Opacity of the watermark image (0.0 to 1.0) | `0.3` |
| `--shadow_opacity` | Opacity of the shadow effect | `10` |
| `--shadow` | Apply shadow effect (True/False) | `True` |

### Example Usage

```sh
python script.py input.pdf output.pdf watermark.png --image_opacity 0.5 --shadow_opacity 5 --shadow False
```
