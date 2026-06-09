import streamlit as st
import pandas as pd
import plotly.express as px

from datetime import datetime
from io import BytesIO

from scraper.load_speedhome import load_speedhome_from_har
from utils.calculations import calculate_summary

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="Property Price Intelligence",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>

img {
    border-radius:12px;
}

.property-card{
    border:1px solid #e5e7eb;
    border-radius:12px;
    padding:12px;
    background:white;
}

</style>
""",
unsafe_allow_html=True)



# ==================================================
# RESPONSIVE CSS
# ==================================================

st.markdown("""
<style>

.block-container{
    padding-top:1rem;
    padding-bottom:2rem;
}

@media (max-width:768px){

    .block-container{
        padding-left:0.5rem;
        padding-right:0.5rem;
    }

    h1{
        font-size:1.8rem !important;
    }

    h2{
        font-size:1.4rem !important;
    }

    h3{
        font-size:1.2rem !important;
    }
}

.property-card{
    border:1px solid #EAEAEA;
    border-radius:12px;
    padding:12px;
    margin-bottom:15px;
    background-color:white;
}

.metric-card{
    border-radius:10px;
    padding:12px;
}

</style>
""", unsafe_allow_html=True)

# ==================================================
# LOAD DATA
# ==================================================

listing_df = load_speedhome_from_har()

# ==================================================
# DATA CLEANING
# ==================================================

listing_df = listing_df.copy()

listing_df["Monthly Price"] = pd.to_numeric(
    listing_df["Monthly Price"],
    errors="coerce"
)

listing_df["Size Sqft"] = pd.to_numeric(
    listing_df["Size Sqft"],
    errors="coerce"
)

listing_df["Bedroom"] = pd.to_numeric(
    listing_df["Bedroom"],
    errors="coerce"
)

listing_df["Bathroom"] = pd.to_numeric(
    listing_df["Bathroom"],
    errors="coerce"
)

# ==================================================
# RM PER SQFT
# ==================================================

listing_df["RM_per_Sqft"] = (
    listing_df["Monthly Price"]
    /
    listing_df["Size Sqft"]
)

# ==================================================
# HEADER
# ==================================================

st.title("🏠 Property Price Intelligence App")

st.markdown(
"""
Analyze rental market pricing using SPEEDHOME public listings.
"""
)

st.caption(
"📱 Mobile Responsive • Interactive Analytics • Export Ready"
)

# ==================================================
# SEARCHABLE DROPDOWN
# ==================================================

property_options = sorted(
    listing_df["Listing Title"]
    .dropna()
    .unique()
)

selected_property = st.selectbox(
    "🔍 Search Area / Property",
    ["All Areas"] + property_options,
    index=0
)

# ==================================================
# FILTERS
# ==================================================

with st.expander("🎯 Filters", expanded=False):

    col1, col2, col3 = st.columns(
        [1,1,1]
    )

    with col1:

        bedroom_filter = st.multiselect(
            "Bedroom",
            sorted(
                listing_df["Bedroom"]
                .dropna()
                .unique()
            )
        )

    with col2:

        furnishing_filter = st.multiselect(
            "Furnishing",
            sorted(
                listing_df["Furnishing"]
                .dropna()
                .unique()
            )
        )

    with col3:

        sort_option = st.selectbox(
            "Sort By",
            [
                "Default",
                "Price Low → High",
                "Price High → Low",
                "Largest Size",
                "Best Value"
            ]
        )

# ==================================================
# PRICE RANGE
# ==================================================

price_range = st.slider(
    "Monthly Rent Range (RM)",
    int(listing_df["Monthly Price"].min()),
    int(listing_df["Monthly Price"].max()),
    (
        int(listing_df["Monthly Price"].min()),
        int(listing_df["Monthly Price"].max())
    )
)

# ==================================================
# FILTER DATA
# ==================================================

filtered_df = listing_df.copy()

if selected_property != "All Areas":

    filtered_df = filtered_df[
        filtered_df["Listing Title"]
        == selected_property
    ]

if bedroom_filter:

    filtered_df = filtered_df[
        filtered_df["Bedroom"]
        .isin(bedroom_filter)
    ]

if furnishing_filter:

    filtered_df = filtered_df[
        filtered_df["Furnishing"]
        .isin(furnishing_filter)
    ]

filtered_df = filtered_df[
    (
        filtered_df["Monthly Price"]
        >= price_range[0]
    )
    &
    (
        filtered_df["Monthly Price"]
        <= price_range[1]
    )
]

# ==================================================
# SORTING
# ==================================================

if sort_option == "Price Low → High":

    filtered_df = filtered_df.sort_values(
        "Monthly Price"
    )

elif sort_option == "Price High → Low":

    filtered_df = filtered_df.sort_values(
        "Monthly Price",
        ascending=False
    )

elif sort_option == "Largest Size":

    filtered_df = filtered_df.sort_values(
        "Size Sqft",
        ascending=False
    )

elif sort_option == "Best Value":

    filtered_df = filtered_df.sort_values(
        "RM_per_Sqft"
    )

# ==================================================
# EMPTY RESULT CHECK
# ==================================================

if len(filtered_df) == 0:

    st.warning(
        "No listings found with current filters."
    )

    st.stop()

# ==================================================
# KPI
# ==================================================

st.divider()

col1, col2, col3 = st.columns(
    [1,1,1],
    gap="small"
)

with col1:

    st.metric(
        "Total Listings",
        len(filtered_df)
    )

with col2:

    st.metric(
        "Average Rent",
        f"RM {filtered_df['Monthly Price'].mean():,.0f}"
    )

with col3:

    st.metric(
        "Average Size",
        f"{filtered_df['Size Sqft'].mean():,.0f} sqft"
    )
# ==================================================
# MARKET SNAPSHOT
# ==================================================

st.subheader("📸 Market Snapshot")

avg_price = filtered_df["Monthly Price"].mean()
median_price = filtered_df["Monthly Price"].median()
max_price = filtered_df["Monthly Price"].max()
min_price = filtered_df["Monthly Price"].min()

st.info(
f"""
📊 A total of {len(filtered_df)} listings were analyzed.

💰 Average Rent: RM {avg_price:,.0f}

📍 Median Rent: RM {median_price:,.0f}

📈 Highest Rent: RM {max_price:,.0f}

📉 Lowest Rent: RM {min_price:,.0f}

📏 Average Property Size:
{filtered_df['Size Sqft'].mean():,.0f} sqft
"""
)

# ==================================================
# RECOMMENDATION ENGINE
# ==================================================

st.divider()

st.subheader("🤖 Recommendation Engine")

top_recommendations = (
    filtered_df
    .sort_values("RM_per_Sqft")
    .head(3)
)

st.dataframe(
    top_recommendations[
        [
            "Listing Title",
            "Monthly Price",
            "Size Sqft",
            "RM_per_Sqft"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# BEST VALUE PROPERTY
# ==================================================

best_property = (
    filtered_df
    .sort_values("RM_per_Sqft")
    .iloc[0]
)

st.subheader("🏆 Best Value Property")

st.success(
f"""
🏢 {best_property['Listing Title']}

💰 Monthly Rent:
RM {best_property['Monthly Price']:,.0f}

📏 Size:
{best_property['Size Sqft']} sqft

🔥 Cost Efficiency:
RM {best_property['RM_per_Sqft']:.2f}/sqft
"""
)

# ==================================================
# ROI CALCULATOR
# ==================================================

st.divider()

st.subheader("💰 ROI Calculator")

property_price = st.number_input(
    "Property Purchase Price (RM)",
    value=500000
)

avg_annual_rent = (
    filtered_df["Annual Price"]
    .mean()
)

roi = (
    avg_annual_rent /
    property_price
) * 100

st.metric(
    "Estimated Gross Rental Yield",
    f"{roi:.2f}%"
)

# ==================================================
# RENTAL AVAILABILITY
# ==================================================

st.divider()

st.subheader("🏷️ Rental Availability")

availability_df = pd.DataFrame({

    "Rental Type":[
        "Daily",
        "Monthly",
        "Annual"
    ],

    "Status":[
        "Not Available",
        "Available",
        "Available"
    ]
})

st.dataframe(
    availability_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# PRICE SUMMARY
# ==================================================

summary_df = calculate_summary(
    filtered_df
)

st.divider()

st.subheader("📊 Price Summary")

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True
)

# ==================================================
# AREA COMPARISON
# ==================================================

st.divider()

st.subheader("⚖️ Area Comparison")

all_areas = sorted(
    listing_df["Property Area"]
    .dropna()
    .unique()
)

compare_area_1 = st.selectbox(
    "Area A",
    all_areas,
    key="area_a"
)

compare_area_2 = st.selectbox(
    "Area B",
    all_areas,
    key="area_b"
)

if compare_area_1 and compare_area_2:

    area_a_df = listing_df[
        listing_df["Property Area"]
        == compare_area_1
    ]

    area_b_df = listing_df[
        listing_df["Property Area"]
        == compare_area_2
    ]

    comparison_df = pd.DataFrame({

        "Area":[
            compare_area_1,
            compare_area_2
        ],

        "Average Rent":[
            round(area_a_df["Monthly Price"].mean(),0),
            round(area_b_df["Monthly Price"].mean(),0)
        ],

        "Average Size":[
            round(area_a_df["Size Sqft"].mean(),0),
            round(area_b_df["Size Sqft"].mean(),0)
        ],

        "Listings":[
            len(area_a_df),
            len(area_b_df)
        ]
    })

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

# ==================================================
# MARKET ANALYTICS
# ==================================================

st.divider()

st.subheader("📈 Market Analytics")

tab1, tab2, tab3 = st.tabs(
    [
        "Rent Distribution",
        "Rent vs Size",
        "Furnishing Mix"
    ]
)

with tab1:

    fig_hist = px.histogram(
        filtered_df,
        x="Monthly Price",
        nbins=15,
        title="Rent Distribution"
    )

    fig_hist.update_layout(
        height=350
    )

    st.plotly_chart(
        fig_hist,
        use_container_width=True
    )

with tab2:

    fig_scatter = px.scatter(
        filtered_df,
        x="Size Sqft",
        y="Monthly Price",
        color="Bedroom",
        hover_name="Listing Title",
        title="Rent vs Size"
    )

    fig_scatter.update_layout(
        height=350
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

with tab3:

    fig_pie = px.pie(
        filtered_df,
        names="Furnishing",
        title="Furnishing Breakdown"
    )

    fig_pie.update_layout(
        height=350
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )
# ==================================================
# FEATURED PROPERTY CARDS
# ==================================================

st.divider()

st.subheader("🏠 Featured Listings")

card_df = filtered_df.head(12)

for i in range(0, len(card_df), 3):

    cols = st.columns(3)

    for col, (_, row) in zip(
        cols,
        card_df.iloc[i:i+3].iterrows()
    ):

        with col:

            image_url = row["Image URL"]

            if pd.notna(image_url) and image_url != "":

                st.image(
                    image_url,
                    width=320
                )

            st.markdown(
                f"""
### {row['Listing Title']}

💰 **RM {row['Monthly Price']:,.0f}/month**

🛏 {row['Bedroom']} Bedroom

🛁 {row['Bathroom']} Bathroom

📏 {row['Size Sqft']} sqft

🛋 {row['Furnishing']}
"""
            )

            st.link_button(
                "🔗 View Listing",
                row["Listing URL"]
            )

# ==================================================
# TOP 5 CHEAPEST
# ==================================================

st.divider()

st.subheader("🏅 Top 5 Cheapest Properties")

cheap_df = filtered_df.nsmallest(
    5,
    "Monthly Price"
)

st.dataframe(
    cheap_df[
        [
            "Listing Title",
            "Monthly Price",
            "Bedroom",
            "Size Sqft"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# TOP 5 PREMIUM
# ==================================================

st.subheader("💎 Top 5 Premium Properties")

premium_df = filtered_df.nlargest(
    5,
    "Monthly Price"
)

st.dataframe(
    premium_df[
        [
            "Listing Title",
            "Monthly Price",
            "Bedroom",
            "Size Sqft"
        ]
    ],
    use_container_width=True,
    hide_index=True
)

# ==================================================
# PROPERTY LOCATION INTELLIGENCE
# ==================================================

st.divider()

st.subheader(
    "🗺️ Property Location Intelligence"
)

map_df = filtered_df.dropna(
    subset=[
        "Latitude",
        "Longitude"
    ]
)

if len(map_df) > 0:

    fig_map = px.scatter_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        hover_name="Listing Title",
        hover_data=[
            "Monthly Price",
            "Bedroom",
            "Bathroom",
            "Size Sqft",
            "Furnishing"
        ],
        zoom=11,
        height=450
    )

    fig_map.update_layout(
        mapbox_style="open-street-map",
        margin=dict(
            l=0,
            r=0,
            t=30,
            b=0
        )
    )

    st.plotly_chart(
        fig_map,
        use_container_width=True
    )

# ==================================================
# BEST VALUE PROPERTY LOCATION
# ==================================================

recommend_df = filtered_df.copy()

recommend_df["Score"] = (
    recommend_df["Size Sqft"]
    /
    recommend_df["Monthly Price"]
) * 1000

best_property = recommend_df.loc[
    recommend_df["Score"].idxmax()
]

st.divider()

st.subheader(
    "🏆 Best Value Property"
)

st.success(
    f"""
{best_property['Listing Title']}

Monthly Rent: RM {best_property['Monthly Price']:,.0f}

Size: {best_property['Size Sqft']} sqft

Bedroom: {best_property['Bedroom']}

Value Score: {best_property['Score']:.2f}
"""
)

if (
    pd.notna(best_property["Latitude"])
    and
    pd.notna(best_property["Longitude"])
):

    st.subheader(
        "📍 Best Value Property Location"
    )

    best_map = pd.DataFrame(
        {
            "lat":[best_property["Latitude"]],
            "lon":[best_property["Longitude"]]
        }
    )

    st.map(best_map)

# ==================================================
# MARKET HEATMAP
# ==================================================

if len(map_df) > 0:

    st.divider()

    st.subheader(
        "🔥 Rental Price Heatmap"
    )

    heatmap_fig = px.density_mapbox(
        map_df,
        lat="Latitude",
        lon="Longitude",
        z="Monthly Price",
        radius=25,
        zoom=10,
        height=500
    )

    heatmap_fig.update_layout(
        mapbox_style="open-street-map"
    )

    st.plotly_chart(
        heatmap_fig,
        use_container_width=True
    )

# ==================================================
# DETAILED LISTINGS
# ==================================================

st.divider()

st.subheader("📋 Detailed Listings")

display_df = filtered_df[
    [
        "Listing Title",
        "Property Area",
        "Bedroom",
        "Bathroom",
        "Monthly Price",
        "Annual Price",
        "Size Sqft",
        "Furnishing",
        "Listing URL"
    ]
]

st.data_editor(
    display_df,
    column_config={
        "Listing URL":
        st.column_config.LinkColumn(
            "Open Listing"
        )
    },
    use_container_width=True,
    hide_index=True
)

# ==================================================
# EXPORT REPORT
# ==================================================

st.divider()

st.subheader("📥 Export Report")

today = datetime.today().strftime(
    "%Y%m%d"
)

area_name = (
    selected_property.replace(" ", "_")
    if selected_property != "All Areas"
    else "All_Areas"
)

csv_filename = (
    f"SPEEDHOME_{area_name}_{today}.csv"
)

excel_filename = (
    f"SPEEDHOME_{area_name}_{today}.xlsx"
)

market_metrics = pd.DataFrame({

    "Metric":[
        "Average Rent",
        "Median Rent",
        "Highest Rent",
        "Lowest Rent",
        "Listings"
    ],

    "Value":[
        avg_price,
        median_price,
        max_price,
        min_price,
        len(filtered_df)
    ]
})

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

excel_buffer = BytesIO()

with pd.ExcelWriter(
    excel_buffer,
    engine="openpyxl"
) as writer:

    market_metrics.to_excel(
        writer,
        sheet_name="Market Snapshot",
        index=False
    )

    summary_df.to_excel(
        writer,
        sheet_name="Price Summary",
        index=False
    )

    filtered_df.to_excel(
        writer,
        sheet_name="Listings",
        index=False
    )

excel_data = excel_buffer.getvalue()

col1, col2 = st.columns(2)

with col1:

    st.download_button(
        "📄 CSV",
        csv_data,
        file_name=csv_filename,
        mime="text/csv"
    )

with col2:

    st.download_button(
        "📊 Excel",
        excel_data,
        file_name=excel_filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "Property Price Intelligence App • Powered by SPEEDHOME Public Listings • Mobile Responsive • Built with Streamlit"
)