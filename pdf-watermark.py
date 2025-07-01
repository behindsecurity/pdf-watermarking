import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import io
import argparse
import os


def hex_to_rgb(hex_color: str):
    """Convert HEX color (e.g. '#RRGGBB') to an (R, G, B) tuple."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Invalid HEX color. Use format #RRGGBB.")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def create_text_image(
    text: str,
    max_width: float,
    max_height: float,
    font_path: str,
    font_size: int,
    text_color: tuple,
    text_opacity: float,
    shadow: bool,
    shadow_opacity: float,
    shadow_offset: int = 5,
):
    """
    Render `text` onto a transparent PIL image of size (max_width, max_height),
    center it, apply optional shadow, and return the RGBA image.
    """
    # Create blank transparent image
    canvas = Image.new("RGBA", (int(max_width), int(max_height)), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    if font_path:
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
        font = ImageFont.truetype(font_path, font_size)
    else:
        # Try a built-in TrueType font so size actually works
        try:
            font = ImageFont.truetype("./fonts/dejavu-sans.bold.ttf", font_size)
        except IOError:
            # Fallback to the default bitmap font if TTF not found
            font = ImageFont.load_default()

    # Measure text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Center coordinates
    x = (max_width - text_w) / 2
    y = (max_height - text_h) / 2

    # Draw shadow if requested
    if shadow:
        shadow_color = (0, 0, 0, int(255 * shadow_opacity))
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)

    # Draw main text
    r, g, b = text_color
    fill = (r, g, b, int(255 * text_opacity))
    draw.text((x, y), text, font=font, fill=fill)

    return canvas


def add_watermark(
    input_pdf: str,
    output_pdf: str,
    watermark_image: str = None,
    watermark_text: str = None,
    image_opacity: float = 0.3,
    shadow_opacity: float = 0.3,
    shadow: bool = True,
    font_path: str = None,
    font_size: int = 36,
    text_color: str = "#000000",
    text_opacity: float = 0.3,
    # new metadata params
    title: str = None,
    author: str = None,
    subject: str = None,
    keywords: str = None,
    creator: str = None,
    producer: str = None,
):
    # Open the input PDF
    doc = fitz.open(input_pdf)

    # Compute maximum watermark size (90% of smallest page dimension)
    max_width = min(page.rect.width for page in doc) * 0.9
    max_height = min(page.rect.height for page in doc) * 0.9

    if watermark_text:
        # --- TEXT WATERMARK MODE ---
        rgb = hex_to_rgb(text_color)
        img = create_text_image(
            watermark_text,
            max_width,
            max_height,
            font_path,
            font_size,
            rgb,
            text_opacity,
            shadow,
            shadow_opacity,
        )
    else:
        # --- IMAGE WATERMARK MODE ---
        # Open and convert image
        img = Image.open(watermark_image).convert("RGBA")

        # Resize image to fit
        img.thumbnail((max_width, max_height))

        # Adjust image opacity
        if image_opacity < 1.0:
            alpha = img.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(image_opacity)
            img.putalpha(alpha)

        # Apply shadow under the image if desired
        if shadow:
            shadow_offset = 5
            shadow_layer = Image.new(
                "RGBA",
                (img.width + shadow_offset, img.height + shadow_offset),
                (0, 0, 0, int(255 * shadow_opacity)),
            )
            shadow_layer.paste(img, (shadow_offset, shadow_offset), img)
            img = shadow_layer

    # Convert final watermark (PIL image) to a PNG byte stream
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    watermark_bytes = img_byte_arr.getvalue()

    # Stamp each page
    for page in doc:
        rect = page.rect
        w, h = img.size
        x = (rect.width - w) / 2
        y = (rect.height - h) / 2
        page.insert_image(
            fitz.Rect(x, y, x + w, y + h),
            stream=watermark_bytes,
            overlay=True,
        )

    # ——— UPDATE PDF METADATA ———
    meta = doc.metadata  # dict with keys: title, author, subject, keywords, creator, producer, etc.
    if title is not None:
        meta["title"] = title
    if author is not None:
        meta["author"] = author
    if subject is not None:
        meta["subject"] = subject
    if keywords is not None:
        meta["keywords"] = keywords
    if creator is not None:
        meta["creator"] = creator
    if producer is not None:
        meta["producer"] = producer

    doc.set_metadata(meta)

    # Save out
    doc.save(output_pdf)
    doc.close()
    print(f"Watermark added successfully: {output_pdf}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add an image or text watermark to a PDF.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_pdf", help="Path to the output PDF file.")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--watermark_image",
        help="Path to the watermark image file (PNG, JPG, etc.).",
    )
    group.add_argument(
        "--watermark_text",
        help="Text string to use as the watermark (e.g. 'CONFIDENTIAL').",
    )

    # Image watermark options
    parser.add_argument(
        "--image_opacity",
        type=float,
        default=0.3,
        help="Opacity of the watermark image (0.0 to 1.0).",
    )
    # Text watermark options
    parser.add_argument(
        "--font_path",
        help="Path to a .ttf font file for text watermark (defaults to PIL's built-in font).",
    )
    parser.add_argument(
        "--font_size",
        type=int,
        default=36,
        help="Font size for text watermark.",
    )
    parser.add_argument(
        "--text_color",
        type=str,
        default="#000000",
        help="Text color in HEX format, e.g. '#FF0000'.",
    )
    parser.add_argument(
        "--text_opacity",
        type=float,
        default=0.3,
        help="Opacity of the text watermark (0.0 to 1.0).",
    )

    # Shared shadow options
    parser.add_argument(
        "--shadow",
        action="store_true",
        default=False,
        help="Apply a drop-shadow effect under the watermark.",
    )
    parser.add_argument(
        "--shadow_opacity",
        type=float,
        default=0.3,
        help="Opacity of the shadow (0.0 to 1.0).",
    )

    # ——— PDF Metadata options ———
    parser.add_argument("--title",    help="PDF title metadata.")
    parser.add_argument("--author",   help="PDF author metadata.")
    parser.add_argument("--subject",  help="PDF subject/description metadata.")
    parser.add_argument("--keywords", help="PDF keywords (comma-separated).")
    parser.add_argument("--creator",  help="PDF creator metadata.")
    parser.add_argument("--producer", help="PDF producer metadata.")

    args = parser.parse_args()

    add_watermark(
        args.input_pdf,
        args.output_pdf,
        watermark_image=args.watermark_image,
        watermark_text=args.watermark_text,
        image_opacity=args.image_opacity,
        shadow_opacity=args.shadow_opacity,
        shadow=args.shadow,
        font_path=args.font_path,
        font_size=args.font_size,
        text_color=args.text_color,
        text_opacity=args.text_opacity,
        title=args.title,
        author=args.author,
        subject=args.subject,
        keywords=args.keywords,
        creator=args.creator,
        producer=args.producer,
    )
