import os

import pandas as pd
import plotly.express as px


def main():
    this_dir = os.path.dirname(__file__)
    file = os.path.join(this_dir, "../Sample02/bestsellers.csv")
    df = pd.read_csv(file)
    df.Genre = df.Genre.astype("category")

    fig = px.box(
        df,
        x="Year",
        y="User Rating",
        color="Genre",
        points="all",
        hover_data=df.columns,
        notched=False,
    )
    fig.write_html(os.path.join(this_dir, "../Sample02/Index02.html"))
    return df


if __name__ == "__main__":
    df = main()
