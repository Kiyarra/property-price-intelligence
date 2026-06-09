import requests
import pandas as pd


def get_mont_kiara_data():

    url = "https://speedhome.com/_next/data/build-1780918065278/en/rent/mont-kiara.json?loc=mont-kiara"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print("Status:", response.status_code)
    print(response.text)

    data = response.json()

    print(data["pageProps"]["propertyList"].keys())


if __name__ == "__main__":
    get_mont_kiara_data()