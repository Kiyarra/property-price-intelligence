import json

with open("data/speedhome.har", "r", encoding="utf-8") as f:
    har = json.load(f)

for entry in har["log"]["entries"]:

    url = entry["request"]["url"]

    if "api/properties/search" in url:

        print("FOUND SEARCH API")
        print(url)

        content = entry["response"]["content"].get("text", "")

        print("\nFIRST 2000 CHARS:\n")
        print(content[:2000])

        break

