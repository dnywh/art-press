# General imports
import sys
import os
import logging
from datetime import datetime
import math
import random

from PIL import Image, ImageDraw
import requests  # For retrieving artwork data and image

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Prepare directories so they can be reached from anywhere
appDir = os.path.dirname(os.path.realpath(__file__))
assetsDir = os.path.join(appDir, "assets")
# Get required items from other root-level directories
parentDir = os.path.dirname(appDir)
libDir = os.path.join(parentDir, "lib")
if os.path.exists(libDir):
    sys.path.append(libDir)

# Change the below import to match your display's driver
from waveshare_epd import epd5in83_V2 as display

# Adjust your optical offsets from one place
# import layout
# See Pi Frame for usage:
# https://github.com/dnywh/pi-frame

# Settings
# Shared optical sizing and offsets with Pi Frame
# containerSize = layout.size
# offsetX = layout.offsetX
# offsetY = layout.offsetY
# Manual optical sizing and offsets
containerSize = 360
offsetX = 0
offsetY = 16

imageQuality = "bitonal"  # Options are "default", "gray", "bitonal"
preferCrop = True  # Crop to center of original image if true
imageWidth = 843  # Preferred width as per ARTIC API documentation
exportImages = True  # Save both the input and output image in an exports folder
headers = {"AIC-User-Agent": "art-box (endless.paces-03@icloud.com)"}  # As a courtesy
pageItemLimit = 10  # 100 or less per page

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
    # Post a bare minimum query to find out the amount of pages the criteria returns
    url = f"https://api.artic.edu/api/v1/artworks/search?limit=0"
    r = requests.post(url, headers=headers, json=criteria)
    art = r.json()
    # Get results
    resultSize = art["pagination"]["total"]
    pages = int(math.ceil(resultSize / 10))  # Fixed to 10 items per page?
    logging.info(f"There are {resultSize} possible choices for your criteria")
    # Select a random page
    randomPage = random.randint(0, pages - 1)
    logging.info(f"Randomly selected page {randomPage + 1} of {pages}")

    # Post the full query into this page
    # Fields to include in data
    fields = "api_link,image_id,title,artist_id,artist_title,medium_display,thumbnail"  # Make sure to include any fields that are queried later on
    url = f"https://api.artic.edu/api/v1/artworks/search?limit={pageItemLimit}&page={randomPage}&fields={fields}"
    r = requests.post(url, headers=headers, json=criteria)
    art = r.json()
    # Select a random item
    randomArt = random.randint(0, pageItemLimit - 1)
    logging.info(f"Randomly selected item {randomArt + 1} of {pageItemLimit}")
    # Parse random item
    apiLink = art["data"][randomArt]["api_link"]
    imageId = art["data"][randomArt]["image_id"]
    imageTitle = art["data"][randomArt]["title"]
    imageArtist = art["data"][randomArt]["artist_title"]

    # Crop artwork
    if preferCrop == True:
        # Calculate center crop of image
        imageWidth = art["data"][randomArt]["thumbnail"]["width"]
        imageHeight = art["data"][randomArt]["thumbnail"]["height"]
        cropStartX = int((imageWidth - containerSize) / 2)
        cropStartY = int((imageHeight - containerSize) / 2)
        # Pass this crop region into the image parameters
        cropRegion = f"{cropStartX},{cropStartY},{containerSize},{containerSize}"
        imageParams = f"/{cropRegion}/{containerSize},/0/{imageQuality}.jpg"
    else:
        # Just get the square version of the image, resized to canvas size
        imageParams = f"/square/{containerSize},/0/{imageQuality}.jpg"

    artworkUrl = f"https://www.artic.edu/iiif/2/{imageId}{imageParams}"
    canonicalArtworkUrl = (
        f"https://www.artic.edu/iiif/2/{imageId}/full/843,/0/default.jpg"
    )

    logging.info(f"Artwork URL: {artworkUrl}")

    # Download a temporary copy of the map tile from the API to render to screen
    r = requests.get(artworkUrl, headers=headers)
    # Store it locally
    artworkImagePath = os.path.join(appDir, "artwork.jpg")
    with open(artworkImagePath, "wb") as f:
        f.write(r.content)

    # Prepare versions of image
    artwork = Image.open(artworkImagePath)
    # Throw away original artwork image since new versions have been made
    os.remove(artworkImagePath)

    # Log information, including a URL for the original artwork
    output = f"Printed at:\t{timeStampNice}\nTitle:\t\t{imageTitle}\nArtist:\t\t{imageArtist}\nAPI URL:\t{apiLink}\nImage URL:\t{canonicalArtworkUrl}"
    # ...to console
    logging.info(f"\n{output}")

    # Save out
    if exportImages == True:
        # Prepare directory for saving image(s)
        exportsDir = os.path.join(appDir, "exports")
        timeStampSlugToMin = datetime.today().strftime("%Y-%m-%d-%H-%M")
        imageDir = os.path.join(exportsDir, timeStampSlugToMin)
        if not os.path.exists(exportsDir):
            os.makedirs(exportsDir)
        if not os.path.exists(imageDir):
            os.mkdir(imageDir)
        # Save image in its directory
        artwork.save(os.path.join(imageDir, f"{timeStampSlugToMin}.jpg"))
        # Also save text output
        with open(os.path.join(imageDir, f"{timeStampSlugToMin}.txt"), "w") as f:
            f.write(output)

    # Start rendering
    epd = display.EPD()
    epd.init()
    epd.Clear()

    canvas = Image.new("1", (epd.width, epd.height), "white")
    draw = ImageDraw.Draw(canvas)

    # Calculate top-left starting position
    startX = offsetX + int((epd.width - containerSize) / 2)
    startY = offsetY + int((epd.height - containerSize) / 2)

    canvas.paste(artwork, (startX, startY))

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
    display.epdconfig.module_exit()
    exit()
