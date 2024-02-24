import argparse
import os
import shutil
from rembg import remove
from PIL import Image, ImageOps


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


def process_image(input_path, output_path, crop=False, remove_bg=False, resize=None, padding=0):
    """
    Processes a single image based on the provided options and saves it.

    Args:
    - input_path (str): Path to the input image.
    - output_path (str): Path where the processed image should be saved.
    - crop (bool): Whether to autocrop the image.
    - remove_bg (bool): Whether to remove the background of the image.
    - resize (tuple): Optional dimensions (width, height) to resize the image.
    - padding (int): Number of padding pixels to add around the image.
    """
    need_processing = crop or resize or remove_bg
    # Define temp_path for all processing scenarios
    temp_path = output_path + ".tmp.png"

    with open(input_path, 'rb') as input_file:
        image_data = input_file.read()

    # Ensure any processing writes initially to a temporary file
    if need_processing or padding:
        if remove_bg:
            image_data = remove(image_data)
            # Write post-background removal image data to temp_path
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(image_data)
        else:
            # Copy original image to temp_path if no background removal
            with open(temp_path, 'wb') as temp_file:
                temp_file.write(image_data)

    if crop:
        autocrop_image(temp_path, temp_path)

    if resize:
        # Adjust for padding only if resize is specified
        adjusted_resize = (resize[0] - 2*padding,
                           resize[1] - 2*padding) if padding else resize
        resize_and_pad_image(temp_path, output_path, adjusted_resize, padding)
        os.remove(temp_path)  # Cleanup after resizing
    elif crop:
        # Finalize cropping without resizing; handle padding if specified
        if padding > 0:
            resize_and_pad_image(
                temp_path, output_path, (crop_width - 2*padding, crop_height - 2*padding), padding)
            os.remove(temp_path)  # Cleanup after padding is added
        else:
            os.rename(temp_path, output_path)
    elif need_processing:
        # If there was any processing but not crop or resize specifically, finalize it
        os.rename(temp_path, output_path)
    else:
        # Directly copy the original image to output if no processing and no padding
        shutil.copy(input_path, output_path)


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


def generate_output_filename(input_path, remove_bg=False, crop=False, resize=None):
    """
    Generates an output filename based on the input path. Appends '_b', '_c', '_bcr', or '_c[WIDTH]x[HEIGHT]' 
    before the file extension and ensures the extension is '.png' for images with background removal, cropping, 
    or resizing.

    Args:
    - input_path (str): Path to the input image.
    - remove_bg (bool): Indicates if background removal was applied.
    - crop (bool): Indicates if autocrop was applied.
    - resize (tuple): Optional dimensions (width, height) to resize the image, affects the filename if cropping is applied.

    Returns:
    - (str): Modified filename with appropriate suffix and '.png' extension.
    """
    base, _ = os.path.splitext(os.path.basename(input_path))
    suffix = ""

    if remove_bg:
        suffix += "_b"
    if crop:
        suffix += "_c"
    if resize and crop:  # Only modify the filename for resize if cropping is also applied
        width, height = resize
        suffix += f"{width}x{height}"

    # If there's no specific processing applied, keep the original filename but ensure it saves as PNG
    if not (remove_bg or crop or resize):
        suffix = ""

    return f"{base}{suffix}.png"


# The main and process_images functions remain the same, but ensure to update them to handle the new PNG output correctly.

# Update the process_images and main functions to include the new autocrop functionality
# Ensure to pass the crop argument to process_image and adjust the output filename generation accordingly


def process_images(input_dir="./input", output_dir="./output", crop=False, remove_bg=False, resize=None, padding=0):
    """
    Processes images in the specified directory based on the provided options.

    Args:
    - input_dir (str): Directory containing the images to be processed.
    - output_dir (str): Directory where processed images will be saved.
    - crop (bool): Whether to crop the images.
    - remove_bg (bool): Whether to remove the background of the images.
    - resize (tuple): Optional dimensions (width, height) to resize the image.
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
            input_path, remove_bg=remove_bg, crop=crop, resize=resize)
        output_path = os.path.join(output_dir, output_filename)
        print(f"Processing image {i}/{len(inputs)}...{filename}")
        process_image(input_path, output_path, crop=crop,
                      remove_bg=remove_bg, resize=resize, padding=padding)  # Pass padding here
        shutil.move(input_path, os.path.join(processed_input_dir, filename))

    print("All images have been processed.")


def main():
    parser = argparse.ArgumentParser(
        description="Image processing script with options for cropping, background removal, and resizing.")
    parser.add_argument("-c", "--crop", action="store_true",
                        help="Crop the images.")
    parser.add_argument("-b", "--background_removal", action="store_true",
                        help="Remove the background from the images.")
    parser.add_argument("-r", "--resize", type=str,
                        help="Resize the image to fit within AxB pixels while maintaining aspect ratio. Format: 'AxB'")
    parser.add_argument("-p", "--padding", type=int, default=0,
                        help="Number of padding pixels to add around the image. The image size stays the same as specified in -c AxB.")

    args = parser.parse_args()

    # Extract resize dimensions and padding
    if args.resize:
        try:
            width, height = map(int, args.resize.split('x'))
            resize_dimensions = (width, height)
        except ValueError:
            raise ValueError(
                "Invalid format for resize dimensions. Please use 'AxB'.")
    else:
        resize_dimensions = None

    # Now include padding in the process_images call
    process_images(
        crop=args.crop,
        remove_bg=args.background_removal,
        resize=resize_dimensions,
        padding=args.padding  # Include padding here
    )


if __name__ == "__main__":
    main()
