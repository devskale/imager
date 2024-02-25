import argparse
import os
import shutil
from rembg import remove
from PIL import Image
import io


def add_background(image, background, default_color="#FFFFFF"):
    """
    Adds a background to an image, with a fallback to a default color if the specified background is not available.

    Args:
    - image (PIL.Image.Image): Image with a transparent background.
    - background (str or PIL.Image.Image): Background color (as a hex code) or a PIL Image to be used as background.
    - default_color (str): Fallback color if the specified background is not valid. Defaults to white.

    Returns:
    - PIL.Image.Image: The image with the new background.
    """
    foreground = image.convert("RGBA")

    if isinstance(background, str) and (background.startswith("#") or background.isalpha()):
        # Background is a color
        try:
            Image.new("RGBA", (1, 1), background)  # Test if valid color
            background_layer = Image.new("RGBA", foreground.size, background)
        except ValueError:
            print(
                f"Invalid color '{background}'. Using default color '{default_color}'.")
            background_layer = Image.new(
                "RGBA", foreground.size, default_color)
    elif isinstance(background, Image.Image):
        # Background is an image
        bg_img = background.convert("RGBA")
        background_layer = bg_img.resize(foreground.size)
    else:
        # Fallback to default color
        background_layer = Image.new("RGBA", foreground.size, default_color)

    final_img = Image.alpha_composite(
        background_layer, foreground).convert("RGB")

    return final_img


def autocrop_image(image):
    """
    Autocrops an image, focusing on the non-transparent pixels.

    Args:
    - image (PIL.Image.Image): Image to be autocropped.

    Returns:
    - PIL.Image.Image: The autocropped image.
    """
    bbox = image.getbbox()
    if bbox:
        return image.crop(bbox)
    return image


def remove_bg_func(image):
    """
    Removes the background from an image using the rembg library.

    Args:
    - image (PIL.Image.Image): Image object from which to remove the background.

    Returns:
    - PIL.Image.Image: New image object with the background removed.
    """
    # Convert the PIL Image to bytes
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()

    # Use rembg to remove the background
    result_bytes = remove(img_byte_arr)

    # Convert the result bytes back to a PIL Image
    result_image = Image.open(io.BytesIO(result_bytes))

    return result_image


def process_image(image_data, crop=False, remove_bg=False, resize=None, padding=0, background=None):
    """
    Processes a single image based on the provided options.

    Args:
    - image_data (PIL.Image.Image): The input image.
    - crop (bool): Whether to autocrop the image.
    - remove_bg (bool): Whether to remove the background of the image.
    - resize (tuple): Optional dimensions (width, height) to resize the image.
    - padding (int): Number of padding pixels to add around the image.
    - background (str): Optional background color (hex code or name) or path to an image file to set as the background.

    Returns:
    - PIL.Image.Image: The processed image.
    """
    # Assume image_data is a PIL.Image.Image object

    if remove_bg:
        # Assuming remove_bg function returns a PIL image
        image_data = remove_bg_func(image_data)

    if crop:
        # Assuming autocrop_image function modifies the image in place or returns a new PIL image
        image_data = autocrop_image(image_data)

    if resize:
        # Assuming resize_and_pad_image function modifies the image in place or returns a new PIL image
        image_data = resize_and_pad_image(image_data, resize, padding)

    if background:
        # Assuming add_background function modifies the image in place or returns a new PIL image
        image_data = add_background(image_data, background)

    return image_data


def resize_and_pad_image(image, dimensions, padding=0):
    """
    Resizes an image to fit the specified dimensions and adds padding.

    Args:
    - image (PIL.Image.Image): Image object to be resized and padded.
    - dimensions (tuple): Target dimensions (width, height).
    - padding (int): Padding to add around the resized image.

    Returns:
    - PIL.Image.Image: Resized and padded image object.
    """
    target_width, target_height = dimensions
    content_width, content_height = target_width - \
        2*padding, target_height - 2*padding

    # Determine new size, preserving aspect ratio
    img_ratio = image.width / image.height
    target_ratio = content_width / content_height

    if target_ratio > img_ratio:
        new_height = content_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = content_width
        new_height = int(new_width / img_ratio)

    # Resize the image
    resized_img = image.resize(
        (new_width, new_height), Image.Resampling.LANCZOS)

    # Create a new image with the target dimensions and a transparent background
    new_img = Image.new(
        "RGBA", (target_width, target_height), (255, 255, 255, 0))

    # Calculate the position to paste the resized image to center it
    paste_position = ((target_width - new_width) // 2,
                      (target_height - new_height) // 2)

    # Paste the resized image onto the new image, centered
    new_img.paste(resized_img, paste_position,
                  resized_img if resized_img.mode == 'RGBA' else None)

    return new_img


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
