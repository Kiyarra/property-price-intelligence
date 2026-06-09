import json
import pandas as pd
import streamlit as st


@st.cache_data
def load_speedhome_from_har():

    with open(
        "data/speedhome.har",
        "r",
        encoding="utf-8"
    ) as f:

        har = json.load(f)

    all_listings = []

    for entry in har["log"]["entries"]:

        try:

            url = entry["request"]["url"]

            if "api/properties/search" not in url:
                continue

            content = (
                entry["response"]["content"]
                .get("text", "")
            )

            if not content:
                continue

            data = json.loads(content)

            properties = data.get(
                "content",
                []
            )

            print(
                f"Found {len(properties)} properties"
            )

            for item in properties:

                property_ref = item.get("ref")

                slug = item.get("slug")

                # ==================================
                # IMAGE EXTRACTION
                # ==================================

                image_url = None

                images = item.get(
                    "images",
                    []
                )

                if images:

                    first_image = images[0]

                    # Format 1
                    if isinstance(
                        first_image,
                        str
                    ):
                        image_url = first_image

                    # Format 2
                    elif isinstance(
                        first_image,
                        dict
                    ):

                        image_url = (
                            first_image.get("imageUrl")
                            or
                            first_image.get("url")
                            or
                            first_image.get("image")
                            or
                            first_image.get("path")
                        )

                # ==================================
                # BUILD IMAGE URL IF PATH ONLY
                # ==================================

                if (
                    image_url
                    and
                    not str(image_url).startswith("http")
                ):

                    image_url = (
                        "https://image.speedhome.com/"
                        f"{image_url}"
                    )

                # ==================================
                # LISTING URL
                # ==================================

                if slug:

                    listing_url = (
                        f"https://speedhome.com/rent/{slug}"
                    )

                else:

                    listing_url = (
                        f"https://speedhome.com/property/{property_ref}"
                    )

                # ==================================
                # APPEND RECORD
                # ==================================

                all_listings.append({

                    "Listing Title":
                    item.get("name"),

                    "Property Area":
                    item.get("address"),

                    "Bedroom":
                    item.get("bedroom"),

                    "Bathroom":
                    item.get("bathroom"),

                    "Monthly Price":
                    item.get("price"),

                    "Annual Price":
                    (
                        item.get("price", 0)
                        * 12
                    ),

                    "Daily Price":
                    None,

                    "Rental Type Available":
                    "Monthly, Annual",

                    "Size Sqft":
                    item.get("sqft"),

                    "Furnishing":
                    item.get("furnishType"),

                    "Latitude":
                    item.get("latitude"),

                    "Longitude":
                    item.get("longitude"),

                    "Image URL":
                    image_url,

                    "Property Ref":
                    property_ref,

                    "Slug":
                    slug,

                    "Listing URL":
                    listing_url

                })

        except Exception as e:

            print(
                "ERROR:",
                e
            )

    df = pd.DataFrame(
        all_listings
    )

    if not df.empty:

        df = df.drop_duplicates(
            subset=["Property Ref"]
        )

    return df


if __name__ == "__main__":

    df = load_speedhome_from_har()

    print("\nTOTAL RECORDS:")
    print(len(df))

    print("\nCOLUMNS:")
    print(df.columns.tolist())

    if not df.empty:

        print("\nSAMPLE:")
        print(
            df[
                [
                    "Listing Title",
                    "Image URL",
                    "Latitude",
                    "Longitude"
                ]
            ].head()
        )