# ExO - Expert Opinion Webapp

A FastAPI-based web application for pairwise image comparison and selection. Designed for lightweight expert input collection through a simple web interface, the app shows randomized pairs of images and records user preferences, while avoiding repeated combinations. Additionally, it provides on-the-fly TIFF-to-PNG conversion for compatibility with web formats.

## Features

- Randomly display two unique images from a local folder
- Prevent repetition of image pairs
- Record user selections in a CSV file
- Convert TIFF images to PNG for browser display
- Automatically archive selections when all combinations are exhausted

## Requirements

- Python 3.8+
- pip

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/exo-webapp.git
   cd exo-webapp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Folder Structure

```
.
├── images/           # Place your TIFF image files here
├── static/           # Optional static assets (CSS, JS)
├── templates/        # HTML templates (Jinja2)
├── selections.csv    # Auto-generated CSV file for selections
├── main.py           # Main FastAPI application
├── LICENSE
└── README.md
```

## Usage

1. Add your `.tiff` images to the `images/` folder.

2. Start the application:
   ```bash
   uvicorn main:app --reload
   ```

3. Open your browser and go to:
   ```
   http://127.0.0.1:8000
   ```

4. Select one image from each pair. Once all unique pairs have been shown, the app will:
   - Archive the current `selections.csv` with a timestamped filename.
   - Clear the original `selections.csv` file.
   - Reset the comparison session.
  The selection.csv will remain active if you want to create other session. Beware that this version the csv is not tracking the sets, so if you restart the server you wipe out the combination tracker.

5. You can find your results in the root folder as `.csv` files.

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

## Author

**Marco Prenassi**  
Laboratory of Data Engineering  
Istituto di ricerca per l'innovazione tecnologica (RIT)  
Area Science Park, Trieste, Italy
