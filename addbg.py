import sys
import argparse
from PIL import Image, ImageStat, ImageEnhance


def adjust_background_brightness(bg_image, mode):
    """
    Adjusts the brightness of the background image based on the specified mode.

    Args:
    - bg_image (Image): The PIL Image object of the background.
    - mode (str): The mode for background adjustment ('lighter', 'darker').

    Returns:
    - Image: The adjusted PIL Image object.
    """
    enhancer = ImageEnhance.Brightness(bg_image)
    if mode == 'lighter':
        return enhancer.enhance(1.5)  # Increase brightness
    elif mode == 'darker':
        return enhancer.enhance(0.5)  # Decrease brightness
    return bg_image  # Return unmodified if mode is not recognized


def generate_complementary_background(image_path, guidance):
    """
    Generates a complementary background image based on guidance.

    Args:
    - image_path (str): Path to the input image.
    - guidance (str): Guidance for background generation ('lighter', 'darker', 'color').

    Returns:
    - Image: A PIL Image object of the generated background.
    """
    with Image.open(image_path) as img:
        # Assuming a simplistic approach to generate a solid color background
        background = Image.new(
            'RGB', img.size, (255, 255, 255) if guidance == 'lighter' else (0, 0, 0))

        # Adjust the background based on guidance
        if guidance in ['lighter', 'darker']:
            background = adjust_background_brightness(background, guidance)
        # For color or other guidance, additional logic can be implemented

    return background


def blend_images(foreground_path, output_path, guidance):
    """
    Blends an input image with a dynamically generated background image based on guidance.

    Args:
    - foreground_path (str): Path to the input image with a transparent background.
    - output_path (str): Path where the blended image will be saved.
    - guidance (str): Guidance for background generation.
    """
    background = generate_complementary_background(foreground_path, guidance)
    with Image.open(foreground_path).convert("RGBA") as foreground:
        background = background.convert("RGBA")
        blended_image = Image.alpha_composite(background, foreground)
        blended_image.convert("RGB").save(output_path, "PNG")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Blends an input image with a dynamically generated background image based on guidance.")
    parser.add_argument(
        "foreground", help="Path to the input image with a transparent background.")
    parser.add_argument("output", nargs='?', default="out.png",
                        help="Path where the blended image will be saved. Defaults to 'out.png'.")
    parser.add_argument("--guidance", choices=['lighter', 'darker', 'color'], default='darker',
                        help="Guidance for the type of background to generate ('lighter', 'darker', 'color'). Defaults to 'darker'.")

    args = parser.parse_args()
    blend_images(args.foreground, args.output, args.guidance)
