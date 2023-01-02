import requests
import math
import random

# itemsPerPage = 10
limit = 10  # Breaks if over 100

fields = "id,image_id,title,artist_id,medium_display"
url = f"https://api.artic.edu/api/v1/artworks/search?limit={limit}&fields={fields}"
headers = {"user-agent": "test-app/endless.paces-03@icloud.com"}

searchQuery = {
    "query": {
        "bool": {
            "must": [
                {"term": {"is_public_domain": True}},
                {"match": {"term_titles": "woodcut"}},
                # {"match": {"classification_titles": "etching"}},
                # {"match": {"subject_titles": "geometric"}},
                # {"range": {"color.h": {"lt": 2}}},
            ],
            # "should": [
            #     {"term": {"is_boosted": True}},
            # ],
            # "must_not": [
            #     {"match": {"medium_display": "Ceramic and pigment"}},
            #     {"match": {"medium_display": "Plant fibers"}},
            #     {"match": {"term_titles": "metalwork"}},
            # ],
        }
    }
}

# term_titles: "woodcut"
# classification_titles: "etching"
# foul-biting


print("———————————————————")
r = requests.post(url, headers=headers, json=searchQuery)
art = r.json()
# print(art)
resultSize = art["pagination"]["total"]
pages = int(math.ceil(resultSize / 10))  # Fixed to 10 items per page?

# Crop...
canvasSize = 360
# imageParams = "/full/843,/0/default.jpg"
imageParams = f"/square/{canvasSize},/0/bitonal.jpg"  # default.jpg, gray.jpg. Can I get ImageMagick or PIL to work on the monochrome a bit better? Stippling

# Get results
print(f"Randomly selecting one of {resultSize} possible choices...")


randomPage = random.randint(1, pages)
print(f"Randomly selected page {randomPage} of {pages}")

url = f"https://api.artic.edu/api/v1/artworks/search?limit={limit}&page={randomPage}&fields={fields}"
r = requests.post(url, headers=headers, json=searchQuery)
art = r.json()
randomArt = random.randint(0, limit)
print(f"Randomly selected item {randomArt} of {limit}")

imageId = art["data"][randomArt]["image_id"]
print(f"{art['data'][randomArt]['title']}, {art['data'][randomArt]['id']}:")
print(f"https://www.artic.edu/iiif/2/{imageId}{imageParams}")
