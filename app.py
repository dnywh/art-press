import requests
import math

itemsPerPage = 10
limit = 9

fields = "id,image_id,title,artist_id"
url = f"https://api.artic.edu/api/v1/artworks/search?limit={limit}&fields={fields}"
headers = {"user-agent": "test-app/endless.paces-03@icloud.com"}

searchQuery = {
    "query": {
        "bool": {
            "must": [
                {"term": {"artist_id": 36198}},
                {"term": {"is_public_domain": False}},
                {"match": {"place_of_origin": "Spain"}},
            ],
            "should": [
                {"term": {"is_boosted": True}},
            ],
        }
    }
}

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

imageParams = "/full/843,/0/default.jpg"
# print(resultSize, pages, art)
for i in range(len(art["data"])):
    imageId = art["data"][i]["image_id"]
    print(art["data"][i]["title"], art["data"][i]["id"])
    print(f"https://www.artic.edu/iiif/2/{imageId}{imageParams}")
