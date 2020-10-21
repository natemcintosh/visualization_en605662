import pandas as pd
import plotly.express as px


def main():
    file = "../Sample01/course_evals.csv"
    df = pd.read_csv(file)
    df.price_detail__amount.loc[df.price_detail__amount.isna()] = 0
    fig = px.scatter(
        df,
        x="num_published_lectures",
        y="avg_rating",
        facet_row="is_paid",
        color="price_detail__amount",
    )
    fig.write_html("../Sample01/Index01.html")
