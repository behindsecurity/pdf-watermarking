import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter
import io
import argparse


def add_watermark(input_pdf, output_pdf, watermark_image, image_opacity=0.3, shadow_opacity=10, shadow=True):
    # Open the input PDF
    doc = fitz.open(input_pdf)

    # Open the watermark image
    img = Image.open(watermark_image).convert("RGBA")

    # Resize image to fit within the PDF page while maintaining aspect ratio
    max_width = min(page.rect.width for page in doc) * 0.9
    max_height = min(page.rect.height for page in doc) * 0.9
    img.thumbnail((max_width, max_height))

    # Apply transparency
    if image_opacity < 1.0:
        alpha = img.split()[3]  # Get alpha channel
        alpha = ImageEnhance.Brightness(alpha).enhance(image_opacity)
        img.putalpha(alpha)

    # Apply shadow effect
    if shadow:
        shadow_offset = 5  # Shadow offset in pixels
        shadow_img = Image.new("RGBA", (img.width + shadow_offset, img.height + shadow_offset), (0, 0, 0, shadow_opacity))
        shadow_img.paste(img, (shadow_offset, shadow_offset), img)
        img = shadow_img

    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")

    # Add watermark to each page
    for page in doc:
        rect = page.rect
        img_width, img_height = img.size

        # Centering the image on the page
        x_offset = (rect.width - img_width) / 2
        y_offset = (rect.height - img_height) / 2
        img_rect = fitz.Rect(x_offset, y_offset, x_offset + img_width, y_offset + img_height)

        # Insert the image
        page.insert_image(img_rect, stream=img_byte_arr.getvalue())

    # Save the output PDF
    doc.save(output_pdf)
    doc.close()
    print(f"Watermark added successfully: {output_pdf}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add a watermark to a PDF file.")
    parser.add_argument("input_pdf", help="Path to the input PDF file.")
    parser.add_argument("output_pdf", help="Path to the output PDF file.")
    parser.add_argument("watermark_image", help="Path to the watermark image file.")
    parser.add_argument("--image_opacity", type=float, default=0.3, help="Opacity of the watermark image (0.0 to 1.0, default: 0.3).")
    parser.add_argument("--shadow_opacity", type=int, default=3, help="Opacity of the shadow effect (default: 10).")
    parser.add_argument("--shadow", type=bool, default=True, help="Apply shadow effect (default: True).")
    
    args = parser.parse_args()
    
    add_watermark(args.input_pdf, args.output_pdf, args.watermark_image, args.image_opacity, args.shadow_opacity, args.shadow)
