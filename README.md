# Image Processing Script

This Python script offers a versatile image processing toolkit, allowing for operations such as background removal, autocropping, resizing, and adding padding to images. It's designed to process images in bulk, making it an ideal solution for preparing images for web use or personal projects.

## Features

- **Background Removal**: Automatically removes the background from images.
- **Autocropping**: Crops images to remove unnecessary transparent space.
- **Resizing**: Resizes images to specified dimensions, maintaining aspect ratio.
- **Padding**: Adds padding around images, ensuring the final image size matches specified dimensions.

## Installation

To run this script, you'll need Python installed on your system along with the following packages:
- Pillow
- rembg

You can install the required packages using pip:

```sh
pip install Pillow rembg
```

# Usage

Place the images you want to process in the ./input directory.
Run the script with desired options:

```sh
python imager.py -b -c -r 800x600 -p 10
```

## Command-Line Arguments

- `-b, --background_removal`: Enable background removal.
- `-c, --crop`: Enable autocropping.
- `-r, --resize AxB`: Resize the image to fit within AxB pixels, maintaining aspect ratio.
- `-p, --padding PIXELS`: Add PIXELS number of padding around the image. The final image size stays as specified in `-r AxB`.

## Example
To process images by removing the background, autocropping, resizing to 800x600 pixels, and adding 10 pixels of padding:

```sh
python imager.py -b -c -r 800x600 -p 10
```

This command processes all images in the ./input directory and saves the processed images to the ./output directory.

Super Mario original and Super Mario  

<img src="data/supermario.png" alt="alt text" width="320" style="border: 1px solid black;">  
<img src="output/supermario_b_c320x280.png" alt="alt text" width="320" style="border: 1px solid black;">  

# License
This project is open-source and available under the MIT License.

## Contributing

Contributions to improve the script or add new features are welcome. Please feel free to fork the repository and submit pull requests.
