import pandas as pd
import plotly.express as px


def main():
    file = "../Sample02/Groceries_dataset.csv"
    df = pd.read_csv(file, parse_dates=["Date"])
    counts = (
        df.itemDescription.value_counts()
        .reset_index()
        .rename(columns={"index": "itemDescription", "itemDescription": "count"})
    )
