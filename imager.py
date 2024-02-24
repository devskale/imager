import argparse
# Ensure this is the function intended for directory processing
from image_processor import process_images


def main():
    parser = argparse.ArgumentParser(
        description="Process multiple images from a directory with options for cropping, background removal, resizing, and adding a background.")
    parser.add_argument("-i", "--input_dir", type=str, required=True,
                        help="Directory containing the images to be processed.")
    parser.add_argument("-o", "--output_dir", type=str, required=True,
                        help="Directory where processed images will be saved.")
    parser.add_argument("-c", "--crop", action="store_true",
                        help="Crop the images.")
    parser.add_argument("-b", "--background_removal", action="store_true",
                        help="Remove the background from the images.")
    parser.add_argument("-r", "--resize", type=str,
                        help="Resize the image to fit within AxB pixels while maintaining aspect ratio. Format: 'AxB'")
    parser.add_argument("-p", "--padding", type=int, default=0,
                        help="Number of padding pixels to add around the image.")
    parser.add_argument("-bg", "--background", type=str, default=None,
                        help="Add a background to the image. Accepts color names, hex codes, or paths to image files.")

    args = parser.parse_args()

    resize_dimensions = None
    if args.resize:
        try:
            width, height = map(int, args.resize.split('x'))
            resize_dimensions = (width, height)
        except ValueError:
            print("Invalid format for resize dimensions. Please use 'AxB'.")
            return

    process_images(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        crop=args.crop,
        remove_bg=args.background_removal,
        resize=resize_dimensions,
        padding=args.padding,
        background=args.background
    )


if __name__ == "__main__":
    main()
