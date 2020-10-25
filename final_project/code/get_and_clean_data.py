from urllib import request
import json

import pandas as pd


def get_response(url: str) -> dict:
    """
    Get a dict from a JSON API
    """
    json_data = dict()

    oper_url = request.urlopen(url)
    if oper_url.getcode() == 200:
        data = oper_url.read()
        json_data = json.loads(data)
    else:
        print("Error receiving data", oper_url.getcode())
    return json_data


def build_df_from_items(json_dict: dict) -> pd.DataFrame:
    """
    Assuming the input dictionary has the key "items", this will create a DataFrame from
    the list of items in "items"

    These usually come with the columns
    - number
    - formula
    - count
    - percent
    """
    df = pd.DataFrame(json_dict["items"])
    df.formula = df.formula.astype("string")
    df["count"] = df["count"].str.replace(",", "").astype("int")
    df.percent = df.percent.astype("float")
    return df

