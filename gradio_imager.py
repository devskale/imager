import gradio as gr
from PIL import Image
import tempfile
import os
from image_processor import process_image


def gradio_interface(image, crop, remove_bg, resize, padding, background):
    # Convert resize string to tuple (if provided)
    resize_dimensions = None
    if resize:
        try:
            width, height = map(int, resize.split('x'))
            resize_dimensions = (width, height)
        except ValueError:
            return "Invalid format for resize dimensions. Please use 'AxB'.", "original"

    # Use a temporary file to save the input image from Gradio
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_input:
        image.save(tmp_input, format="PNG")
        tmp_input_path = tmp_input.name

    # Prepare a temporary file for the output image
    tmp_output_path = tempfile.mktemp(suffix=".png")

    # Process the image
    process_image(tmp_input_path, tmp_output_path, crop,
                  remove_bg, resize_dimensions, padding, background)

    # Load and return the processed image
    processed_image = Image.open(tmp_output_path)

    # Clean up temporary files
    os.remove(tmp_input_path)
    os.remove(tmp_output_path)

    return processed_image


    # Define the Gradio interface with updated component imports
interface = gr.Interface(fn=gradio_interface,
                         inputs=[
                             gr.components.Image(type="pil"),
                             gr.components.Checkbox(label="Crop"),
                             gr.components.Checkbox(
                                 label="Remove Background"),
                             gr.components.Textbox(
                                 label="Resize (WxH)", placeholder="Example: 100x100"),
                             gr.components.Slider(
                                 minimum=0, maximum=200, label="Padding", default=0),
                             gr.components.Textbox(
                                 label="Background", placeholder="Color name or hex code")
                         ],
                         outputs=gr.components.Image(type="pil"),
                         title="Image Processor",
                         description="Upload an image and select processing options.")


if __name__ == "__main__":
    interface.launch()
