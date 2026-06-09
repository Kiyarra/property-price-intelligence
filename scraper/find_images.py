import json

with open("data/speedhome.har","r",encoding="utf-8") as f:
    har = json.load(f)

for entry in har["log"]["entries"]:

    url = entry["request"]["url"]

    if "image.speedhome.com" in url:
        print(url)