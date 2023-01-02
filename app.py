import requests
import math

# itemsPerPage = 10
limit = 3  # Breaks if over 100

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
            "should": [
                {"term": {"is_boosted": True}},
            ],
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

# searchQuery = {
#     "query": {
#         "bool": {
#             "must": [
#                 {"term": {"artist_id": 36198}},
#                 {"term": {"is_public_domain": True}},
#                 {"match": {"place_of_origin": "Spain"}},
#             ],
#             "should": [
#                 {"term": {"is_boosted": True}},
#             ],
#         }
#     }
# }

# searchQuery = {
#     "query": {
#         "bool": {
#             "must": {
#                 "match": {
#                     "place_of_origin": "Spain"
#                 }
#             }
#         }
#     }
# }


# searchQuery = {
#     "query": {
#         "bool": {
#             "must": [
#                 {"term": {"artist_id": 36198}},
#                 {"term": {"place_of_origin": "Spain"}},
#                 {"term": {"is_public_domain": True}},
#             ]
#         }
#     }
# }

print("———————————————————")
r = requests.post(url, headers=headers, json=searchQuery)
art = r.json()
# print(art)
resultSize = art["pagination"]["total"]
pages = int(math.ceil(resultSize / 10))

size = 360
# imageParams = "/full/843,/0/default.jpg"
imageParams = f"/square/{size},/0/bitonal.jpg"  # default.jpg, gray.jpg. Can I get ImageMagick or PIL to work on the monochrome a bit better? Stippling

# Get results
print(
    f"{resultSize} total results across {pages} pages, limited to {len(art['data'])}:"
)
for i in range(len(art["data"])):
    imageId = art["data"][i]["image_id"]
    print(f"{art['data'][i]['title']}, {art['data'][i]['id']}:")
    print(f"https://www.artic.edu/iiif/2/{imageId}{imageParams}")
