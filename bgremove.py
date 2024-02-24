from rembg import remove
import os
import shutil

# Ensure the output and processed input directories exist
processed_input_dir = "./input/processed"
output_dir = "./output"
os.makedirs(processed_input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# List all images in the "image" folder
image_folder = "./input"
inputs = [os.path.join(image_folder, f) for f in os.listdir(
    image_folder) if os.path.isfile(os.path.join(image_folder, f))]

# Process each image
total_images = len(inputs)
for i, input_path in enumerate(inputs, start=1):
    print(f"Processing image {i}/{total_images}...")

    # Construct output path in the "./output" folder
    output_path = os.path.join(output_dir, os.path.basename(input_path))

    # Read, process, and write the image
    with open(input_path, 'rb') as input_file:
        output = remove(input_file.read())
        with open(output_path, 'wb') as output_file:
            output_file.write(output)

    # Move processed input images to the "./input/processed" directory
    shutil.move(input_path, os.path.join(
        processed_input_dir, os.path.basename(input_path)))

print("All images have been processed.")
