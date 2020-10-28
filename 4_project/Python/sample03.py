import os

import pandas as pd
import plotly.express as px


def main():
    this_dir = os.path.dirname(__file__)
    file = os.path.join(this_dir, "../Sample03/realestate.csv")
    df = pd.read_csv(file)
    new_names = [
        "crime_rate",
        "proportion_large_lots",
        "proportion_industry",
        "on_river",
        "nox_concentration",
        "avg_rooms",
        "proportion_prior_1940",
        "employment_center_dist",
        "highway_access",
        "tax",
        "pupil_teacher_ratio",
        "proportion_blacks",
        "pct_lower_status",
        "med_value_thou",
    ]
    df.rename(columns=dict(zip(df.columns, new_names)), inplace=True)

    fig = px.scatter_matrix(df, dimensions=new_names)
    fig.write_html(os.path.join(this_dir, "../Sample03/Index03.html"))
    return df


if __name__ == "__main__":
    df = main()
