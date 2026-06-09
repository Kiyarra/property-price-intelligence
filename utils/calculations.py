import pandas as pd

def calculate_summary(df):

    summary = []

    for bedroom in sorted(df["Bedroom"].unique()):

        group = df[df["Bedroom"] == bedroom]

        summary.append({
            "Unit Type": f"{int(bedroom)}BR",
            "Listings": len(group),
            "Average Price (RM)": round(group["Monthly Price"].mean(), 0),
            "Median Price (RM)": round(group["Monthly Price"].median(), 0),
            "Mode Price (RM)": (
                group["Monthly Price"].mode().iloc[0]
                if not group["Monthly Price"].mode().empty
                else None
            ),
            "Fair Price (RM)": round(group["Monthly Price"].median(), 0),
            "Average Size (Sqft)": round(group["Size Sqft"].mean(), 0)
        })

    return pd.DataFrame(summary)