# Copyright (c) 2025 Marco Prenassi,
# Laboratory of Data Engineering, Istituto di ricerca per l'innovazione tecnologica (RIT),
# Area Science Park, Trieste, Italy.
# Licensed under the MIT License. See LICENSE file in the project root for full license information.

# Author: Marco Prenassi
# Date: 2025-03-25
# Description: ExO - Expert Opinion Webapp
# This FastAPI module serves an interactive image comparison web application.
# It displays randomized image pairs from a dataset, records user selections,
# and prevents duplicate comparisons. A simple image conversion endpoint is also provided.

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import UploadFile, File
import shutil

from PIL import Image
import pandas as pd
import random
import os
import io
import datetime
from typing import List


app = FastAPI()

# Mount folders for static assets and image files
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = os.path.join(BASE_DIR, "images")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "output")
CSV_FILE = os.path.join(OUTPUT_FOLDER, "selections.csv")

# Ensure folders exist
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# Global variable to store the last archived file
latest_archive = None

# Track image combinations already presented to the user
used_combinations = set()

# Create the CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["selected", "other"]).to_csv(CSV_FILE, index=False)

# Select two unique images that haven't been shown together before
def get_two_unique_images():
    images = os.listdir(IMAGES_FOLDER)
    total_possible = (len(images) * (len(images) - 1)) // 2

    if len(used_combinations) >= total_possible:
        return None, None

    while True:
        img1, img2 = random.sample(images, 2)
        combination = tuple(sorted([img1, img2]))
        if combination not in used_combinations:
            used_combinations.add(combination)
            return img1, img2

# Display two random images or show a completion message if all combinations are used
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    img1, img2 = get_two_unique_images()

    if img1 is None or img2 is None:
        global latest_archive
        # Archive the current CSV with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
        archive_filename = os.path.join("output", f"selection_{timestamp}.csv")
        latest_archive = archive_filename

        with open(CSV_FILE, 'r') as src, open(archive_filename, 'w') as dst:
            dst.write(src.read())

        # Reset the CSV and combinations
        with open(CSV_FILE, 'w') as clear_file:
            clear_file.write("")

        used_combinations.clear()
        return templates.TemplateResponse("finished.html", {"request": request})

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "img1": img1, "img2": img2}
    )

# Save the selected image pair to the CSV file
@app.post("/select", response_class=HTMLResponse)
async def select_image(selected: str = Form(...), other: str = Form(...)):
    df = pd.DataFrame([[selected, other]], columns=["selected", "other"])
    df.to_csv(CSV_FILE, mode="a", header=False, index=False)
    return RedirectResponse(url="/", status_code=303)

# Convert TIFF to PNG and return the result as a binary stream
@app.get("/tiff/{image_name}")
async def convert_tiff(image_name: str):
    image_path = os.path.join(IMAGES_FOLDER, image_name)
    image = Image.open(image_path)

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    return Response(content=buffer.getvalue(), media_type="image/png")

@app.get("/download_csv")
async def download_csv():
    if latest_archive and os.path.exists(latest_archive):
        return FileResponse(path=latest_archive, filename=latest_archive, media_type='text/csv')
    return Response(content="No archived file available.", status_code=404)

@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})


@app.post("/upload")
async def upload_image(files: List[UploadFile] = File(...)):
    for file in files:
        if not file.filename.lower().endswith((".tif", ".tiff")):
            return Response(content=f"File {file.filename} is not a TIFF.", status_code=400)

        destination_path = os.path.join(IMAGES_FOLDER, file.filename)
        with open(destination_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    return RedirectResponse(url="/upload", status_code=303)

@app.post("/delete_images")
async def delete_all_images():
    for filename in os.listdir(IMAGES_FOLDER):
        file_path = os.path.join(IMAGES_FOLDER, filename)
        try:
            os.remove(file_path)
        except Exception as e:
            return Response(content=f"Error deleting {filename}: {e}", status_code=500)

    return RedirectResponse(url="/upload", status_code=303)

@app.post("/force_finish")
async def force_finish(request: Request):
    global latest_archive

    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    archive_filename = os.path.join("output", f"selection_{timestamp}.csv")
    latest_archive = archive_filename

    with open(CSV_FILE, 'r') as src, open(archive_filename, 'w') as dst:
        dst.write(src.read())

    with open(CSV_FILE, 'w') as clear_file:
        clear_file.write("")

    used_combinations.clear()

    return templates.TemplateResponse("finished.html", {"request": request})