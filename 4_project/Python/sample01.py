import os

import pandas as pd
import plotly.express as px


def main():
    this_dir = os.path.dirname(__file__)
    file = os.path.join(this_dir, "../Sample01/course_evals.csv")
    df = pd.read_csv(file)
    df.price_detail__amount.loc[df.price_detail__amount.isna()] = 0
    fig = px.scatter(
        df,
        x="num_published_lectures",
        y="avg_rating",
        facet_row="is_paid",
        color="price_detail__amount",
    )
    fig.write_html(os.path.join(this_dir, "../Sample01/Index01.html"))


if __name__ == "__main__":
    df = main()
