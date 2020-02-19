import pornhub

search_keywords = []

#client = pornhub.PornHub("5.135.164.72", 3128, search_keywords)
#With proxy, given a Proxy IP and Port. For the countries with restricted access like Turkey, etc.

client = pornhub.PornHub(keywords=search_keywords, pro=True, sort="mv")

for star in client.getStars(10):
    print(star)
    print(star["name"])

for video in client.getVideos(10, page=1):
    print(video)

# for photo_url in client.getPhotos(5):
#     print(photo_url)