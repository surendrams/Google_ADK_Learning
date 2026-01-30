import os
from PIL import Image


def add_padding_to_image(input_path, output_path):
    """
    Adds whitespace padding to an image to make it a 9:16 aspect ratio.
    """
    try:
        img = Image.open(input_path)
        width, height = img.size

        target_aspect_ratio = 9.0 / 16.0
        current_aspect_ratio = float(width) / float(height)

        if abs(current_aspect_ratio - target_aspect_ratio) < 1e-6:
            img.save(output_path)
            return

        if current_aspect_ratio > target_aspect_ratio:
            new_height = int(width / target_aspect_ratio)
            new_width = width
        else:
            new_width = int(height * target_aspect_ratio)
            new_height = height

        new_img = Image.new("RGB", (new_width, new_height), (255, 255, 255))

        paste_x = (new_width - width) // 2
        paste_y = (new_height - height) // 2

        new_img.paste(img, (paste_x, paste_y))
        new_img.save(output_path)

    except Exception as e:
        print(f"Error processing {input_path}: {e}")


def process_images_in_folder(input_folder, output_folder):
    """
    Processes all images in the input folder and saves them to the output folder.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            add_padding_to_image(input_path, output_path)
            print(f"Processed {filename}")


if __name__ == "__main__":
    input_folder = "static/uploads/products"
    output_folder = "static/generated/padded_products"
    process_images_in_folder(input_folder, output_folder)
