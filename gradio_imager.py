import gradio as gr
from PIL import Image
import tempfile
import os
from image_processor import process_image


def apply_standard_settings(setting):
    """Returns the parameters for the selected standard setting."""
    settings_dict = {
        "S light": (True, True, "240x240", 48, "whitesmoke"),
        "M light": (True, True, "480x480", 96, "whitesmoke"),
        "L light": (True, True, "960x960", 128, "whitesmoke"),
        "S dark": (True, True, "240x240", 48, "#2A373D"),
        "M dark": (True, True, "480x480", 96, "#2A373D"),
        "L dark": (True, True, "960x960", 128, "#2A373D"),
    }
    # Default to no special settings
    return settings_dict.get(setting, (None, None, None, None, None))


def settings_description(crop, remove_bg, resize, padding, background):
    """Generate an HTML text description of the current settings in a smaller font and list format."""
    description = f"""
    <ul style="font-size:small;">
        <li>Crop: {crop}</li>
        <li>Remove Background: {remove_bg}</li>
        <li>Resize: {resize if resize else 'No resize'}</li>
        <li>Padding: {padding}</li>
        <li>Background: {background}</li>
    </ul>
    """
    return description


def gradio_interface(image, standard_settings, crop=False, remove_bg=False, resize=None, padding=0, background="white"):
    # Apply standard settings if selected and not "None"
    if image is None:
        # Load the standard image from the specified path if no image is uploaded
        standard_image_path = './data/examples/supermario.png'
        image = Image.open(standard_image_path)

    if standard_settings and standard_settings != "None":
        crop, remove_bg, resize, padding, background = apply_standard_settings(
            standard_settings)

    # Generate settings description
    applied_settings = settings_description(
        crop, remove_bg, resize, padding, background)

    # Convert resize string to tuple (if provided)
    resize_dimensions = None
    if resize:
        try:
            width, height = map(int, resize.split('x'))
            resize_dimensions = (width, height)
        except ValueError:
            return "Invalid format for resize dimensions. Please use 'WxH'.", "original", applied_settings
    # Process the image directly
    processed_image = process_image(
        image, crop, remove_bg, resize_dimensions, padding, background)

    # Generate settings description
    applied_settings = settings_description(
        crop, remove_bg, resize, padding, background)

    return processed_image, applied_settings


example_images = [
    [os.path.join("data", "examples", "supermario.png"),
     "S light", True, True, "480x420", 10, "whitesmoke"],
    [os.path.join("data", "examples",
                  "depositphotos_520707962-stock-photo-fujifilm-s10-body-black-fujifilm.jpg"), "None", True, True, "480x320", 48, "blue"],
    [os.path.join("data", "examples", "batman_b_c_320x280_bg.png"),
     "None", True, True, "360x360", 48, "yellow"],


]

# Define the Gradio interface
interface = gr.Interface(fn=gradio_interface,
                         inputs=[
                             gr.components.Image(
                                 type="pil", label="Input Image"),
                             gr.components.Radio(choices=[
                                                 "None", "S light", "M light", "L light", "S dark", "M dark", "L dark"], label="Settings"),
                             gr.components.Checkbox(label="Crop"),
                             gr.components.Checkbox(label="Remove Background"),
                             gr.components.Textbox(
                                 label="Resize (WxH)", placeholder="Example: 100x100"),
                             gr.components.Slider(
                                 minimum=0, maximum=200, label="Padding"),
                             gr.components.Textbox(
                                 label="Background", placeholder="Color name or hex code")
                         ],
                         outputs=[
                             gr.components.Image(type="pil"),
                             gr.components.HTML(label="Applied Settings")
                         ],
                         examples=example_images,
                         title="IMAGER ___ Image Processor",
                         description="Upload an image and select processing options or choose a standard setting. Supports crop, autoremove background, resize, add padding, and set the background color.",)

if __name__ == "__main__":
    interface.launch()
