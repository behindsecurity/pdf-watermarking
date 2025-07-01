#!/usr/bin/env python3
import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageDraw, ImageFont
import io
import argparse
import os
import tempfile

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
    canvas = Image.new("RGBA", (int(max_width), int(max_height)), (255, 255, 255, 0))
    draw = ImageDraw.Draw(canvas)

    if font_path:
        if not os.path.isfile(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
        font = ImageFont.truetype(font_path, font_size)
    else:
        try:
            font = ImageFont.truetype("./fonts/dejavu-sans.bold.ttf", font_size)
        except IOError:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (max_width - text_w) / 2
    y = (max_height - text_h) / 2

    if shadow:
        shadow_color = (0, 0, 0, int(255 * shadow_opacity))
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=shadow_color)

    r, g, b = text_color
    fill = (r, g, b, int(255 * text_opacity))
    draw.text((x, y), text, font=font, fill=fill)

    return canvas


def create_pdf_from_markdown(md_path: str, output_pdf: str):
    """
    Read a Markdown file and produce a simple styled PDF.
    Headings (#, ##, ###, ####) get larger font sizes; lists (- ) become bullet points.
    """
    doc = fitz.open()  # new empty PDF
    font_name = "helv"  # built-in Helvetica
    margin = 50
    line_height_factor = 1.2
    default_size = 12

    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    page = doc.new_page()
    y = margin

    for raw in lines:
        line = raw.rstrip('\n')
        # Determine style
        if not line.strip():
            # blank line: add vertical space
            y += default_size * line_height_factor
            # check overflow after blank line
            if y > page.rect.height - margin:
                page = doc.new_page()
                y = margin
            continue

        if line.startswith('# '):
            size, text = 24, line[2:].strip()
        elif line.startswith('## '):
            size, text = 20, line[3:].strip()
        elif line.startswith('### '):
            size, text = 18, line[4:].strip()
        elif line.startswith('#### '):
            size, text = 16, line[5:].strip()
        elif line.startswith('- '):
            size, text = default_size, u'\u2022 ' + line[2:].strip()
        else:
            size, text = default_size, line

        # page-break if next line won't fit
        if y + size > page.rect.height - margin:
            page = doc.new_page()
            y = margin

        # create the text box spanning from (margin, y) to (right-margin, bottom-margin)
        rect = fitz.Rect(margin, y, page.rect.width - margin, page.rect.height - margin)
        page.insert_textbox(
            rect,
            text,
            fontsize=size,
            fontname=font_name,
            align=fitz.TEXT_ALIGN_LEFT,
        )
        y += size * line_height_factor

    doc.save(output_pdf)
    doc.close()


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
    # metadata
    title: str = None,
    author: str = None,
    subject: str = None,
    keywords: str = None,
    creator: str = None,
    producer: str = None,
):
    # open existing PDF
    doc = fitz.open(input_pdf)

    # compute max watermark size
    max_w = min(p.rect.width for p in doc) * 0.9
    max_h = min(p.rect.height for p in doc) * 0.9

    # prepare watermark image
    if watermark_text:
        rgb = hex_to_rgb(text_color)
        wm = create_text_image(
            watermark_text, max_w, max_h,
            font_path, font_size, rgb,
            text_opacity, shadow, shadow_opacity
        )
    else:
        wm = Image.open(watermark_image).convert("RGBA")
        wm.thumbnail((max_w, max_h))
        if image_opacity < 1.0:
            alpha = wm.split()[3]
            alpha = ImageEnhance.Brightness(alpha).enhance(image_opacity)
            wm.putalpha(alpha)
        if shadow:
            off = 5
            sh = Image.new("RGBA", (wm.width + off, wm.height + off),
                           (0, 0, 0, int(255 * shadow_opacity)))
            sh.paste(wm, (off, off), wm)
            wm = sh

    # convert to PNG bytes
    bio = io.BytesIO()
    wm.save(bio, format="PNG")
    wm_bytes = bio.getvalue()

    # stamp each page
    for page in doc:
        r = page.rect
        w, h = wm.size
        x = (r.width - w) / 2
        y = (r.height - h) / 2
        page.insert_image(
            fitz.Rect(x, y, x + w, y + h),
            stream=wm_bytes,
            overlay=True,
        )

    # update metadata
    meta = doc.metadata
    for key, val in {
        "title": title,
        "author": author,
        "subject": subject,
        "keywords": keywords,
        "creator": creator,
        "producer": producer,
    }.items():
        if val is not None:
            meta[key] = val
    doc.set_metadata(meta)

    # save and close
    doc.save(output_pdf)
    doc.close()
    print(f"Output written to {output_pdf}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Markdown to PDF and/or add image/text watermark + metadata."
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--input_pdf", help="Path to an existing PDF to watermark."
    )
    input_group.add_argument(
        "--markdown", help="Path to a Markdown file to convert (then watermark)."
    )

    parser.add_argument(
        "output_pdf", help="Path to the output PDF file."
    )

    wm_group = parser.add_mutually_exclusive_group(required=True)
    wm_group.add_argument(
        "--watermark_image", help="Path to the watermark image file."
    )
    wm_group.add_argument(
        "--watermark_text", help="Text string to use as the watermark."
    )

    # watermark options
    parser.add_argument(
        "--image_opacity", type=float, default=0.3,
        help="Opacity of the watermark image (0.0 to 1.0)."
    )
    parser.add_argument(
        "--font_path", help="Path to a .ttf font for text watermark."
    )
    parser.add_argument(
        "--font_size", type=int, default=36,
        help="Font size for text watermark."
    )
    parser.add_argument(
        "--text_color", type=str, default="#000000",
        help="Text color in HEX format."
    )
    parser.add_argument(
        "--text_opacity", type=float, default=0.3,
        help="Opacity of the text watermark."
    )
    parser.add_argument(
        "--shadow", action="store_true", default=False,
        help="Apply a drop-shadow under the watermark."
    )
    parser.add_argument(
        "--shadow_opacity", type=float, default=0.3,
        help="Opacity of the shadow."
    )

    # metadata options
    parser.add_argument("--title",    help="PDF title metadata.")
    parser.add_argument("--author",   help="PDF author metadata.")
    parser.add_argument("--subject",  help="PDF subject/description metadata.")
    parser.add_argument("--keywords", help="PDF keywords (comma-separated).")
    parser.add_argument("--creator",  help="PDF creator metadata.")
    parser.add_argument("--producer", help="PDF producer metadata.")

    args = parser.parse_args()

    # If markdown, generate a temp PDF first
    if args.markdown:
        tmp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False).name
        create_pdf_from_markdown(args.markdown, tmp_pdf)
        src_pdf = tmp_pdf
    else:
        src_pdf = args.input_pdf

    try:
        add_watermark(
            src_pdf,
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
    finally:
        if args.markdown:
            os.remove(tmp_pdf)
