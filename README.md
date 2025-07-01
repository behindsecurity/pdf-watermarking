# PDF Watermarker

A simple command-line tool to add image or text watermarks to PDF files (powered by [PyMuPDF](https://pypi.org/project/PyMuPDF/) and [Pillow](https://pypi.org/project/Pillow/)).  
Supports:
- **Image watermarks** (PNG, JPEG, etc.) with adjustable opacity and optional drop shadow  
- **Text watermarks** with custom font, size, color, opacity, and optional drop shadow  
- **PDF metadata** editing (title, author, subject, keywords, creator, producer)

---

## Features

- Auto-centers watermark on each page (scaled to 90% of the smallest page dimension)  
- Transparent PNG output for both image and text watermarks  
- Shadow support for better readability  
- Bulk-applies watermark to all pages in a PDF  
- Update PDF metadata in one go

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/pdf-watermarker.git
   cd pdf-watermarker
````

2. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install PyMuPDF Pillow
   ```

---

## Usage

```bash
python watermark.py input.pdf output.pdf [options]
```

* **Positional arguments:**

  * `input.pdf` Path to the source PDF file
  * `output.pdf` Path where the watermarked PDF will be saved

* **Mutually exclusive watermark options (one required):**

  * `--watermark_image PATH` Path to an image file (PNG, JPG, etc.)
  * `--watermark_text "TEXT"` Text to render as a watermark

---

### Image Watermark Options

| Option             | Type  | Default | Description                                 |
| ------------------ | ----- | ------- | ------------------------------------------- |
| `--image_opacity`  | float | 0.3     | Opacity of the watermark image (0.0 to 1.0) |
| `--shadow`         | flag  | off     | Enable drop-shadow under the watermark      |
| `--shadow_opacity` | float | 0.3     | Opacity of the drop-shadow (0.0 to 1.0)     |

### Text Watermark Options

| Option             | Type   | Default   | Description                                                |
| ------------------ | ------ | --------- | ---------------------------------------------------------- |
| `--watermark_text` | string | —         | Text string to render as watermark (e.g. `"CONFIDENTIAL"`) |
| `--font_path`      | string | system    | Path to a `.ttf` font file (uses built-in if omitted)      |
| `--font_size`      | int    | 36        | Font size in points                                        |
| `--text_color`     | HEX    | `#000000` | Text color in `#RRGGBB` format                             |
| `--text_opacity`   | float  | 0.3       | Opacity of the text (0.0 to 1.0)                           |
| `--shadow`         | flag   | off       | Enable drop-shadow under the text                          |
| `--shadow_opacity` | float  | 0.3       | Opacity of the drop-shadow (0.0 to 1.0)                    |

---

### PDF Metadata Options

You can update one or more metadata fields in the same command:

| Option       | Description                      |
| ------------ | -------------------------------- |
| `--title`    | PDF title                        |
| `--author`   | PDF author                       |
| `--subject`  | PDF subject/description          |
| `--keywords` | Comma-separated list of keywords |
| `--creator`  | PDF creator                      |
| `--producer` | PDF producer                     |

---

## Examples

1. **Add a semi-transparent “CONFIDENTIAL” text watermark with shadow:**

   ```bash
   python watermark.py report.pdf report_confidential.pdf \
     --watermark_text "CONFIDENTIAL" \
     --font_size 48 \
     --text_color "#FF0000" \
     --text_opacity 0.2 \
     --shadow \
     --shadow_opacity 0.4
   ```

2. **Stamp all pages with a logo image at 50% opacity:**

   ```bash
   python watermark.py slides.pdf slides_watermarked.pdf \
     --watermark_image logo.png \
     --image_opacity 0.5
   ```

3. **Add watermark and update metadata in one go:**

   ```bash
   python watermark.py thesis.pdf thesis_final.pdf \
     --watermark_text "DRAFT" \
     --title "My Thesis" \
     --author "Alice Smith" \
     --keywords "thesis,watermark,PyMuPDF"
   ```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m "Add YourFeature"`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a pull request

Please follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python code style.

---

## License

This project is licensed under the [MIT License](LICENSE).
Feel free to use, modify, and distribute as you see fit.
