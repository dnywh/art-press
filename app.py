# General imports
import sys
import os
import logging
from datetime import datetime
from PIL import Image, ImageDraw


import requests
import math
import random
import urllib.request  # For saving the artwork image

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Prepare directories so they can be reached from anywhere
appDir = os.path.dirname(os.path.realpath(__file__))
# Get required items from other root-level directories
parentDir = os.path.dirname(appDir)
libDir = os.path.join(parentDir, "lib")
if os.path.exists(libDir):
    sys.path.append(libDir)
# Change the below to whatever Waveshare model you have, or add a different display's driver to /lib
from waveshare_epd import (
    epd7in5_V2,
)

# Set design basics
canvasSize = 360
bufferX = 4
bufferY = 14
imageQuality = "bitonal"  # default.jpg, gray.jpg, bitonal.jpg. Can I get ImageMagick or PIL to work on the monochrome a bit better? Stippling
preferCrop = True
imageWidth = 843  # Preferred width as per ARTIC API documentation
exportImages = True  # Save both the input and output image in an exports folder

criteria = {
    "query": {
        "bool": {
            "must": [
                {"term": {"is_public_domain": True}},
                {"match": {"classification_title": "woodcut"}},
                # {"match": {"term_titles": "woodcut"}},
                # {"match": {"classification_titles": "etching"}},
                # {"match": {"subject_titles": "geometric"}},
                # {"range": {"color.h": {"lt": 2}}},
            ],
            "should": [
                {"term": {"is_boosted": True}},
            ],
            "must_not": [
                {"match": {"medium_display": "Ceramic and pigment"}},
                {"match": {"medium_display": "Plant fibers"}},
                {"match": {"term_titles": "metalwork"}},
            ],
        }
    }
}


try:
    # Local time
    timeStampNice = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Kicking off at {timeStampNice}")
    # Fields to include in data
    fields = "api_link,image_id,title,artist_id,artist_title,medium_display,thumbnail"  # Make sure to include any fields that are queried later on
    limit = 10  # Breaks if over 100
    url = f"https://api.artic.edu/api/v1/artworks/search?limit={limit}&fields={fields}"
    headers = {"user-agent": "test-app/endless.paces-03@icloud.com"}

    r = requests.post(url, headers=headers, json=criteria)
    art = r.json()
    resultSize = art["pagination"]["total"]
    pages = int(math.ceil(resultSize / 10))  # Fixed to 10 items per page?

    # Get results
    logging.info(f"There are {resultSize} possible choices for your criteria")

    randomPage = random.randint(0, pages - 1)
    logging.info(f"Randomly selected page {randomPage + 1} of {pages}")

    url = f"https://api.artic.edu/api/v1/artworks/search?limit={limit}&page={randomPage}&fields={fields}"
    r = requests.post(url, headers=headers, json=criteria)
    art = r.json()
    randomArt = random.randint(0, limit - 1)
    logging.info(f"Randomly selected item {randomArt + 1} of {limit}")

    apiLink = art["data"][randomArt]["api_link"]
    imageId = art["data"][randomArt]["image_id"]
    imageTitle = art["data"][randomArt]["title"]
    imageArtist = art["data"][randomArt]["artist_title"]

    # Crop
    if preferCrop == True:
        # Calculate center crop of image
        imageWidth = art["data"][randomArt]["thumbnail"]["width"]
        imageHeight = art["data"][randomArt]["thumbnail"]["height"]
        cropStartX = int((imageWidth - canvasSize) / 2)
        cropStartY = int((imageHeight - canvasSize) / 2)
        # Pass this crop region into the image parameters
        cropRegion = f"{cropStartX},{cropStartY},{canvasSize},{canvasSize}"
        imageParams = f"/{cropRegion}/{canvasSize},/0/{imageQuality}.jpg"
    else:
        # Just get the square version of the image, resized to canvas size
        imageParams = f"/square/{canvasSize},/0/{imageQuality}.jpg"

    artworkUrl = f"https://www.artic.edu/iiif/2/{imageId}{imageParams}"
    canonicalArtworkUrl = (
        f"https://www.artic.edu/iiif/2/{imageId}/full/843,/0/default.jpg"
    )

    logging.info(f"Artwork URL: {artworkUrl}")

    timeStampSlugToMin = datetime.today().strftime("%Y-%m-%d-%H-%M")
    # Prepare directory for saving image(s), if applicable
    exportsDir = os.path.join(appDir, "exports")
    imageDir = os.path.join(exportsDir, timeStampSlugToMin)
    if exportImages == True:
        if not os.path.exists(exportsDir):
            os.makedirs(exportsDir)
        if not os.path.exists(imageDir):
            os.mkdir(imageDir)

    # Download a temporary copy of the artwork to render to screen. Store it locally
    artworkImagePath = os.path.join(appDir, "artwork.jpg")
    urllib.request.urlretrieve(
        artworkUrl,
        artworkImagePath,
    )

    # Prepare versions of image
    artwork = Image.open(artworkImagePath)
    # Throw away original artwork image since new versions have been made
    os.remove(artworkImagePath)

    # Save out
    if exportImages == True:
        # Save out image in its directory
        artwork.save(os.path.join(imageDir, f"{timeStampSlugToMin}.jpg"))

    # Log information, including a URL for the original artwork
    output = f"Printed at:\t{timeStampNice}\nTitle:\t\t{imageTitle}\nArtist:\t\t{imageArtist}\nAPI URL:\t{apiLink}\nImage URL:\t{canonicalArtworkUrl}"
    # ...to console
    logging.info(f"\n{output}")
    # ...to image directory, if applicable
    if exportImages == True:
        with open(os.path.join(imageDir, f"{timeStampSlugToMin}.txt"), "w") as f:
            f.write(output)

    # Start rendering
    epd = epd7in5_V2.EPD()
    epd.init()
    epd.Clear()

    canvas = Image.new("1", (epd.width, epd.height), "white")
    draw = ImageDraw.Draw(canvas)

    # Center grid
    offsetX = int((epd.width - canvasSize) / 2) + bufferX
    offsetY = int((epd.height - canvasSize) / 2) + bufferY

    canvas.paste(artwork, (offsetX, offsetY))

    # Render all of the above to the display
    epd.display(epd.getbuffer(canvas))

    # Put display on pause, keeping what's on screen
    epd.sleep()
    logging.info(f"Finishing printing. Enjoy.")

    # Exit application
    exit()

except IOError as e:
    logging.info(e)

# Exit plan
except KeyboardInterrupt:
    logging.info("Exited.")
    epd7in5_V2.epdconfig.module_exit()
    exit()
