# PyWatermarker: An Advanced Image Watermarking Tool
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A versatile command-line tool, built in Python with Pillow and Typer, to apply watermarks to images with advanced options for tiling, opacity, positioning, and rescaling.

This project was developed as a hands-on exercise to deepen my understanding of image processing, robust software development practices, and professional command-line interface design.

![Example of a watermarked image](https://github.com/felipegluck/python-image-watermarkerer/blob/main/examples/output_example.png)

## ✨ Key Features

This tool goes beyond simple image overlay, offering granular control over the final result:

* **Dual Application Modes:**
    * **`SINGLE`**: Applies a single watermark at a specific position.
    * **`TILE`**: Applies the watermark in a repeating "chessboard" pattern across the entire image for maximum coverage.
* **Opacity Control:** Finely adjust the watermark's transparency, from fully opaque to subtly visible.
* **Intelligent Rescaling:**
    * **`LINEAR`**: Resizes the watermark to a proportion of the main image's **width**, while maintaining the watermark's original aspect ratio.
    * **`AREA`**: Resizes the watermark to a proportion of the main image's **total area**, preserving the aspect ratio.
* **Flexible Positioning:** In `SINGLE` mode, place the watermark at predefined corners (`UPPER_LEFT`, `UPPER_RIGHT`, `LOWER_LEFT`, `LOWER_RIGHT`), in the `MIDDLE`, or at exact `(x, y)` coordinates.
* **Batch Processing:** Apply a watermark to a single image or to all valid images within a directory in one command.
* **Robust & User-Friendly CLI:** Built with Typer, featuring a progress bar, colored feedback, and a comprehensive `--help` menu.

## 🚀 Getting Started

### Prerequisites

* Python 3.8+

### Installation & Setup

1.  **Clone this repository:**
    ```bash
    git clone [https://github.com/felipegluck/python-image-watermarker.git](https://github.com/felipegluck/python-image-watermarker.git)
    cd python-image-watermarker
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv .venv

    # Activate on Windows (PowerShell)
    .\.venv\Scripts\activate

    # Activate on macOS/Linux
    source .venv/bin/activate
    ```
3.  **Install dependencies from the requirements file:**
    ```bash
    pip install -r requirements.txt
    ```    

## Usage

This tool is designed to be used from your command line. The main command structure is:
`python watermarker.py <input_path> <watermark_path> [OPTIONS]`

### Examples

**1. Apply a single watermark to the center of an image:**
```bash
python watermarker.py "examples/pet.jpg" "examples/logo.png" --output "output_folder" --position MIDDLE --opacity 0.5 --proportion 0.25
```
*This will place the logo at 50% opacity in the middle of `pet.jpg`, with the logo's width being 25% of the main image's width.*

**2. Apply a tiled watermark to all images in a folder:**
```bash
python watermarker.py "./source_images" "logo.png" -o "batch_output" --mode TILE --opacity 0.1 --proportion 0.1 --tile-padding 50
```
*This command processes every image in the `source_images` folder, applying a tiled watermark at 10% opacity. Each tile is 10% of the image's width with 50px of padding between them.*

**3. Get help and see all available options:**
```bash
python watermarker.py --help
```

## 🧠 Key Technical Learnings

This project served as a deep dive into several important software engineering and image processing concepts:

* **Pillow (PIL):** Mastered core image manipulation techniques, including `open`, `resize`, `paste`, and handling different image formats and modes.
* **RGBA Color Mode & Alpha Compositing:** The most significant challenge was correctly handling transparency. The solution involved ensuring all images were converted to `RGBA` mode and using `Image.alpha_composite` for a robust, layer-based composition, which prevents common artifacts when pasting transparent images.
* **Alpha Channel Manipulation:** Learned to isolate an image's alpha channel (`getchannel('A')`), apply mathematical operations to each pixel to control opacity (`point()`), and reintegrate it (`putalpha()`).
* **CLI Design with Typer:** Built a professional, user-friendly command-line interface, learning how to use Options, Arguments, Progress Bars, and colored feedback for an enhanced user experience.
* **Defensive Programming:** Implemented `guard clauses` at the beginning of the core function to validate all user inputs, making the tool reliable and preventing runtime errors.
* **Batch Processing with `pathlib`:** Used Python's modern `pathlib` library to handle file system paths in an object-oriented and cross-platform compatible way.

## 🔮 Future Development

This tool has a solid foundation. Potential future features include:
* [ ] Adding text-based watermarks, allowing users to specify custom text, font, and color.
* [ ] Implementing watermark rotation.
* [ ] Creating a simple GUI (Graphical User Interface) using a framework like Tkinter or PyQt.
* [ ] Packaging the tool for distribution via PyPI, so it can be installed with a simple `pip install pywatermarker`.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---
*Built with Python & ☕ by [Felipe Glücksman]*
