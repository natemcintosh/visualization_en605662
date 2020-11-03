from collections import namedtuple
import os
from typing import Tuple
import re

import pandas as pd
import plotly.express as px


def main():
    this_dir = os.path.dirname(__file__)
    file = os.path.join(this_dir, "../Sample03/covid_impact_on_airport_traffic.csv")
    df = pd.read_csv(file, parse_dates=[1])
    df.columns = df.columns.str.lower()
    obj_to_category(df)
    # Can't animate with datetime objects, so convert to day of year
    df["day_of_year"] = df.date.dt.dayofyear
    df.sort_values("day_of_year", inplace=True)

    # Get the lat/lon out of the centroid column
    ll = [get_lat_lon(p) for p in df.centroid.astype("string")]
    df["lat"], df["lon"] = zip(*ll)

    # Create the plotly figure
    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="airportname",
        size="percentofbaseline",
        animation_frame="day_of_year",
        animation_group="airportname",
        projection="natural earth",
    )
    # Save to file
    fig.write_html(os.path.join(this_dir, "../Sample03/Index03.html"))

    return df


def obj_to_category(df: pd.DataFrame):
    """
    Find all the non-numeric columns that have nunique/n <= 0.10 and convert them to 
    categories
    """
    str_col_names = [c for c in df.columns if pd.api.types.is_object_dtype(df[c])]

    cols_under_threshold = [
        c for c in str_col_names if df[c].nunique() / len(df) <= 0.10
    ]

    for c in cols_under_threshold:
        df[c] = df[c].astype("category")


LatLon = namedtuple("LatLon", "lat, lon")


def get_lat_lon(s: str) -> LatLon:
    """
    Take a single row from the `centroid` column and get the lat/lon out of it
    """
    lon = float(re.findall(r"POINT\((-?\d+\.\d+)\s", s)[0])
    lat = float(re.findall(r"\s(-?\d+\.\d+)\)", s)[0])
    return LatLon(lat, lon)


if __name__ == "__main__":
    df = main()
