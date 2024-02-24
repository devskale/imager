import argparse
import os
import shutil
from rembg import remove
from PIL import Image, ImageOps


def add_background(image_path, background, output_path):
    """
    Adds a background to an image. The background can be a solid color or an image.

    Args:
    - image_path (str): Path to the input image with transparent background.
    - background (str): Background color (as a name or hex code) or path to a background image file.
    - output_path (str): Path where the image with the new background should be saved.
    """
    with Image.open(image_path).convert("RGBA") as foreground:
        # If background is a hex code or color name
        if background.startswith("#") or background.isalpha():
            background_layer = Image.new("RGBA", foreground.size, background)
        else:  # If background is an image file
            with Image.open(background).convert("RGBA") as bg_img:
                bg_img = bg_img.resize(foreground.size)
                background_layer = bg_img

        # Composite the foreground over the background
        with Image.alpha_composite(background_layer, foreground) as final_img:
            # Convert to RGB to save in formats other than PNG
            final_img = final_img.convert("RGB")
            final_img.save(output_path)


def autocrop_image(image_path, output_path):
    """
    Autocrops an image, focusing on the non-transparent pixels and saves as PNG.

    Args:
    - image_path (str): Path to the input image.
    - output_path (str): Path where the cropped image should be saved.
    """
    with Image.open(image_path).convert("RGBA") as image:
        bbox = image.getbbox()
        if bbox:
            cropped_image = image.crop(bbox)
            cropped_image.save(output_path, format='PNG')
        else:
            image.save(output_path, format='PNG')


def process_image(input_path, output_path, crop=False, remove_bg=False, resize=None, padding=0, background=None):
    """
    Processes a single image based on the provided options and saves it.

    Args:
    - input_path (str): Path to the input image.
    - output_path (str): Path where the processed image should be saved.
    - crop (bool): Whether to autocrop the image.
    - remove_bg (bool): Whether to remove the background of the image.
    - resize (tuple): Optional dimensions (width, height) to resize the image.
    - padding (int): Number of padding pixels to add around the image.
    - background (str): Optional background color (hex code or name) or path to an image file to set as the background.
    """
    need_processing = crop or resize or remove_bg or background
    temp_path = output_path + ".tmp.png"

    if remove_bg:
        with open(input_path, 'rb') as input_file:
            image_data = input_file.read()
        image_data = remove(image_data)
        with open(temp_path, 'wb') as temp_file:
            temp_file.write(image_data)
    else:
        # Copy original image to temp_path if no background removal
        shutil.copy(input_path, temp_path)

    if crop:
        autocrop_image(temp_path, temp_path)

    if resize:
        adjusted_resize = (resize[0] - 2*padding,
                           resize[1] - 2*padding) if padding else resize
        resize_and_pad_image(temp_path, temp_path, adjusted_resize, padding)

    if background:
        add_background(temp_path, background, temp_path)

    # Finalize the process: move from temp_path to output_path
    os.rename(temp_path, output_path)


def resize_and_pad_image(image_path, output_path, dimensions, padding=0):
    """
    Resizes an image to fit within specified dimensions (AxB) and adds padding to make it exactly AxB,
    ensuring the image content is centered within these dimensions.

    Args:
    - image_path (str): Path to the input image.
    - output_path (str): Path where the resized and padded image should be saved.
    - dimensions (tuple): Target dimensions (width, height) in pixels, before adding padding.
    - padding (int): Number of padding pixels to add around the image.
    """
    target_width, target_height = dimensions
    content_width, content_height = target_width - \
        2*padding, target_height - 2*padding

    with Image.open(image_path) as img:
        # Resize the image, preserving the aspect ratio
        img.thumbnail((content_width, content_height),
                      Image.Resampling.LANCZOS)

        # Create a new image with the target dimensions and a transparent background
        new_img = Image.new("RGBA", dimensions, (255, 255, 255, 0))

        # Calculate the position to paste the resized image to center it
        paste_position = ((target_width - img.width) // 2,
                          (target_height - img.height) // 2)

        # Paste the resized image onto the new image, centered
        new_img.paste(img, paste_position, img if img.mode == 'RGBA' else None)

        # Save the output
        new_img.save(output_path, format='PNG')


def generate_output_filename(input_path, remove_bg=False, crop=False, resize=None, background=None):
    """
    Generates an output filename based on the input path and processing options applied.
    Appends specific suffixes based on the operations: '_b' for background removal, '_c' for crop,
    and '_bg' if a background is added. It ensures the file extension is '.png'.

    Args:
    - input_path (str): Path to the input image.
    - remove_bg (bool): Indicates if background removal was applied.
    - crop (bool): Indicates if autocrop was applied.
    - resize (tuple): Optional dimensions (width, height) for resizing the image.
    - background (str): Indicates if a background was added (None if not used).

    Returns:
    - (str): Modified filename with appropriate suffix and '.png' extension.
    """
    base, _ = os.path.splitext(os.path.basename(input_path))
    suffix = ""

    if remove_bg:
        suffix += "_b"
    if crop:
        suffix += "_c"
    if resize:
        width, height = resize
        suffix += f"_{width}x{height}"
    if background:
        suffix += "_bg"  # Append "_bg" if the background option was used

    # Ensure the file saves as PNG, accommodating for transparency or added backgrounds
    return f"{base}{suffix}.png"


# The main and process_images functions remain the same, but ensure to update them to handle the new PNG output correctly.

# Update the process_images and main functions to include the new autocrop functionality
# Ensure to pass the crop argument to process_image and adjust the output filename generation accordingly


def process_images(input_dir="./input", output_dir="./output", crop=False, remove_bg=False, resize=None, padding=0, background=None):
    """
    Processes images in the specified directory based on the provided options.

    Args:
    - input_dir (str): Directory containing the images to be processed.
    - output_dir (str): Directory where processed images will be saved.
    - crop (bool): Whether to crop the images.
    - remove_bg (bool): Whether to remove the background of the images.
    - resize (tuple): Optional dimensions (width, height) to resize the image.
    - padding (int): Number of padding pixels to add around the image.
    - background (str): Optional background color (hex code or name) or path to an image file to set as the background.
    """
    processed_input_dir = os.path.join(input_dir, "processed")
    os.makedirs(processed_input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    inputs = [os.path.join(input_dir, f) for f in os.listdir(
        input_dir) if os.path.isfile(os.path.join(input_dir, f))]

    # if images are not in the input directory, print a message and return
    if not inputs:
        print("No images found in the input directory.")
        return

    for i, input_path in enumerate(inputs, start=1):
        filename = os.path.basename(input_path)
        output_filename = generate_output_filename(
            input_path, remove_bg=remove_bg, crop=crop, resize=resize, background=background)
        output_path = os.path.join(output_dir, output_filename)
        print(f"Processing image {i}/{len(inputs)}...{filename}")

        # Update the call to process_image with all parameters including background
        process_image(input_path, output_path, crop=crop, remove_bg=remove_bg,
                      resize=resize, padding=padding, background=background)

        shutil.move(input_path, os.path.join(processed_input_dir, filename))

    print("All images have been processed.")
