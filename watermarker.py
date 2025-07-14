from PIL import Image
from math import sqrt
import os
import typer
from pathlib import Path

# Watermarker CLI application
# This application allows users to add watermarks to images with various options for positioning, scaling,
app = typer.Typer(help="A powerful tool to apply watermarks to your images, either one by one or in batch.")

def add_watermark(input_path, watermark_path, output_dir, margin, position=(0,0), opacity = 1.0, proportion=1/10, type_of_rescaling="LINEAR", mode = "SINGLE", tile_padding=10):
    """
    Adds a watermark to an image.

    :param image_path: Path to the original image.
    :param watermark_path: Path to the watermark image.
    :param output_path: Path to save the watermarked image.
    :param margin: Margin in pixels from the edges of the image.
    :type position: tuple or str for predefined positions like "UPPER_LEFT", "UPPER_RIGHT", "LOWER_LEFT", "LOWER_RIGHT", "MIDDLE".
    :param proportion: Proportion of the original image width to scale the watermark.
    :param opacity: Opacity of the watermark (0.0 to 1.0).
    :param type_of_rescaling: Type of rescaling for the watermark ('LINEAR' or 'AREA').
    :param mode: Mode of watermark application ('SINGLE' or 'TILE').
    :param tile_padding: Padding between tiles in TILE mode.    
    """
    # Input validation
    if proportion <= 0:
        raise ValueError("Proportion must be greater than 0")
    if proportion > 1:
        raise ValueError("Proportion must be less than or equal to 1")
    
    # File path validation
    if not isinstance(input_path, str) or not isinstance(watermark_path, str) or not isinstance(output_dir, str):
        raise ValueError("Paths must be strings")
    if not input_path or not watermark_path or not output_dir:
        raise ValueError("Image paths cannot be empty")
    if not input_path.lower().endswith(('.png', '.jpg', '.jpeg')) or not watermark_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise ValueError("Image paths must end with .png, .jpg, or .jpeg")
    
    if not isinstance(margin, int) or margin < 0:
        raise ValueError("Margin must be a non-negative integer")
    
    # Personalized positioning
    if position in ["UPPER_LEFT", "UPPER_RIGHT", "LOWER_LEFT", "LOWER_RIGHT","MIDDLE"]:
        pass
    elif not isinstance(position, tuple) or len(position) != 2:
        raise ValueError("Position must be a tuple of (x, y) coordinates")
    elif not position[0] >= 0 or not position[1] >= 0:
        raise ValueError("Position coordinates must be non-negative")

    if type_of_rescaling not in ["LINEAR", "AREA"]:
        raise ValueError("Type of rescaling must be 'LINEAR' or 'AREA'")
    
    if not isinstance(mode, str) or mode not in ["SINGLE", "TILE"]:
        raise ValueError("Mode must be 'SINGLE' or 'TILE'")
    
    if not isinstance(opacity, (float, int)) or not (0 <= opacity <= 1):
        raise ValueError("Opacity must be a float between 0.0 and 1.0")
    
    if not isinstance(tile_padding, int) or tile_padding < 0:
        raise ValueError("Tile padding must be a non-negative integer")
    
    try:
        # Open the original image and ensure it's in RGBA mode
        original = Image.open(input_path).convert("RGBA") 
        
        # Open the watermark image and ensure it's in RGBA mode
        watermark_img = Image.open(watermark_path).convert("RGBA")
        
        width, height = original.size
        print(f"Original image size: {width}x{height}")
        
        watermark_width, watermark_height = watermark_img.size
        print(f"Watermark image size: {watermark_width}x{watermark_height}")
        
        # Validate watermark dimensions
        if watermark_width == 0 or watermark_height == 0:
            raise ValueError("Watermark image dimensions cannot be zero.")

        scale_factor = 1.0 

        if type_of_rescaling == "LINEAR":
            print("Using linear rescaling for watermark.")
            scale_factor = width*proportion/watermark_width
            print(f"Scale factor: {scale_factor}")
        elif type_of_rescaling == "AREA":
            print("Using area rescaling for watermark.")
            scale_factor = sqrt(height*width*proportion/(watermark_height * watermark_width))
            print(f"Scale factor: {scale_factor}")

        new_size = (int(watermark_width*scale_factor), int(watermark_height*scale_factor))
        
        # Check if new_size is valid before resizing
        if new_size[0] > 0 and new_size[1] > 0:
            watermark_img = watermark_img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"Watermark resized to: {new_size[0]}x{new_size[1]}")
        else:
            print("Warning: Watermark size is too small after scaling. Skipping resize.")

        # Opacity application
        if opacity < 1.0:
            # Get the alpha channel
            alpha = watermark_img.getchannel('A')
            # Modulate the alpha channel by the desired opacity
            new_alpha = alpha.point(lambda i: int(i * opacity))
            # Put the new alpha channel back into the watermark image
            watermark_img.putalpha(new_alpha)
            print(f"Applied {opacity*100}% opacity to watermark.")

        # Create a transparent layer for watermarks
        watermark_layer = Image.new("RGBA", original.size, (0,0,0,0))

        if mode == "TILE":
            print("Tiling watermark across the image.")

            x_step = new_size[0] + tile_padding
            y_step = new_size[1] + tile_padding

            # Indices to control the chessboard logic
            row_index = 0
            y = 0
            while y < height:
                col_index = 0
                x = 0
                while x < width:
                    if (row_index + col_index) % 2 == 0:
                        # Paste the watermark onto the transparent layer
                        watermark_layer.paste(watermark_img, (x, y), mask=watermark_img)
                    x += x_step
                    col_index += 1
                y += y_step
                row_index += 1
        else:
            # Personalized positioning
            margin = margin if margin >= 0 else 0
            wm_width, wm_height = watermark_img.size # Use size of the possibly-resized watermark
            
            if position == "UPPER_LEFT": pos = (margin, margin)
            elif position == "UPPER_RIGHT": pos = (width - wm_width - margin, margin)
            elif position == "LOWER_LEFT": pos = (margin, height - wm_height - margin)
            elif position == "MIDDLE": pos = ((width - wm_width) // 2, (height - wm_height) // 2)
            elif isinstance(position, tuple): pos = position
            else: pos = (width - wm_width - margin, height - wm_height - margin) # Default to LOWER_RIGHT
            
            # Paste the watermark onto the transparent layer
            watermark_layer.paste(watermark_img, pos, mask=watermark_img)
            print(f"Watermark placed on layer at position: {pos}")

        # Composite the watermark layer over the original image 
        final_image = Image.alpha_composite(original, watermark_layer)
        
        # Save the result
        if output_dir.lower().endswith(('.jpg', '.jpeg')):
            # Save as JPEG, which doesn't support transparency, so convert to RGB
            final_image.convert('RGB').save(output_dir, quality=95)
        else:
            # Save in a format that supports transparency, like PNG
            final_image.save(output_dir)
                
    except FileNotFoundError as e:
        print(f"Error opening images: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
# ==============================================================================
# CLI Command to run the watermarker
# ==============================================================================
# This command allows users to apply a watermark to a single image or all images in a directory

@app.command(name="run", help="Applies a watermark to an image or a directory of images.")
def run_watermarker(
    input_path: Path = typer.Argument(..., help="Path to the image or directory of images."),
    watermark_path: Path = typer.Argument(..., help="Path to the watermark image."),
    output_dir: Path = typer.Option("output", "-o", help="Directory to save the watermarked images."),
    mode: str = typer.Option("SINGLE", help="Mode: 'SINGLE' or 'TILE'."),
    position: str = typer.Option("LOWER_RIGHT", help="Position for SINGLE mode: 'UPPER_LEFT', 'UPPER_RIGHT', 'LOWER_LEFT', 'LOWER_RIGHT', 'MIDDLE'."),
    proportion: float = typer.Option(0.1, help="Proportion of the original image to scale the watermark (0.0 to 1.0)."),
    margin: int = typer.Option(20, help="Margin for SINGLE mode (pixels)."),
    tile_padding: int = typer.Option(50, help="Padding between tiles in TILE mode (pixels)."),
    rescaling_type: str = typer.Option("LINEAR", help="Type of rescaling for the watermark: 'LINEAR' or 'AREA'."),
    opacity: float = typer.Option(0.5, help="Opacity of the watermark (0.0 to 1.0).")
):
    """
    Main function to run the watermarker application.
    """
    if not watermark_path.is_file():
        typer.secho(f"Error: Watermark's path not found in '{watermark_path}'", fg=typer.colors.RED)
        raise typer.Abort()

    os.makedirs(output_dir, exist_ok=True)
    typer.secho(f"Output directory: '{output_dir}'", fg=typer.colors.BLUE)

    valid_extensions = ['.png', '.jpg', '.jpeg']

    if input_path.is_dir():
        typer.secho(f"Processing directory: '{input_path}'", fg=typer.colors.CYAN)
        image_files = [f for f in input_path.iterdir() if f.suffix.lower() in valid_extensions]
        
        if not image_files:
            typer.secho("No valid image found in directory.", fg=typer.colors.YELLOW)
            raise typer.Exit()

        with typer.progressbar(image_files, label="Applying watermarks.") as progress:
            for image_file in progress:
                output_filename = f"{image_file.stem}_watermarked.png" # Save as PNG to ensure transparency
                output_filepath = output_dir / output_filename
                
                add_watermark(
                    input_path=str(image_file),
                    watermark_path=str(watermark_path),
                    output_dir=str(output_filepath),
                    margin=margin,
                    position=position,
                    opacity=opacity,
                    proportion=proportion,
                    type_of_rescaling=rescaling_type,
                    mode=mode,
                    tile_padding=tile_padding
                )
    elif input_path.is_file():
        if input_path.suffix.lower() not in valid_extensions:
            typer.secho("Error: Input file is not a valid image.", fg=typer.colors.RED)
            raise typer.Abort()
        
        typer.secho(f"Processing single file: '{input_path}'", fg=typer.colors.CYAN)
        output_filename = f"{input_path.stem}_watermarked.png"
        output_filepath = output_dir / output_filename

        add_watermark(
            input_path=str(input_path),
            watermark_path=str(watermark_path),
            output_dir=str(output_filepath),
            margin=margin,
            position=position,
            opacity=opacity,
            proportion=proportion,
            type_of_rescaling=rescaling_type,
            mode=mode,
            tile_padding=tile_padding
        )
        
    else:
        typer.secho(f"Error: The input path '{input_path}' does not exist.", fg=typer.colors.RED)
        raise typer.Abort()

    typer.secho("\n Process successfully finished!", fg=typer.colors.GREEN)

if __name__ == "__main__":
    app()