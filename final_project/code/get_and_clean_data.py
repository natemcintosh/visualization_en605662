from urllib import request
import json
import itertools
from typing import List

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
    - formula/cask
    - count
    - percent
    """
    formula_or_cask = get_formula_or_cask(json_dict.get("items")[0].keys())

    df = pd.DataFrame(json_dict["items"])
    df[formula_or_cask] = df[formula_or_cask].astype("string")
    df["count"] = df["count"].str.replace(",", "").astype("int")
    df.percent = df.percent.astype("float")
    return df


def get_unique_formulas(dfs: List[pd.DataFrame]) -> set:
    return set(
        itertools.chain.from_iterable(
            df.formula.to_list() for df in dfs if "formula" in df.columns
        )
    )


def create_formula_json_url(package_name: str) -> str:
    return "https://formulae.brew.sh/api/formula/" + package_name + ".json"


def get_formula_or_cask(dict_keys) -> str:
    if "formula" in dict_keys:
        return "formula"
    elif "cask" in dict_keys:
        return "cask"
    else:
        raise KeyError("Could not find 'formula' or 'cask' in the keys")


install_and_error_urls = [
    "https://formulae.brew.sh/api/analytics/install/30d.json",
    "https://formulae.brew.sh/api/analytics/install/90d.json",
    "https://formulae.brew.sh/api/analytics/install/365d.json",
    "https://formulae.brew.sh/api/analytics/install-on-request/30d.json",
    "https://formulae.brew.sh/api/analytics/install-on-request/90d.json",
    "https://formulae.brew.sh/api/analytics/install-on-request/365d.json",
    "https://formulae.brew.sh/api/analytics/cask-install/30d.json",
    "https://formulae.brew.sh/api/analytics/cask-install/90d.json",
    "https://formulae.brew.sh/api/analytics/cask-install/365d.json",
    "https://formulae.brew.sh/api/analytics/build-error/30d.json",
    "https://formulae.brew.sh/api/analytics/build-error/90d.json",
    "https://formulae.brew.sh/api/analytics/build-error/365d.json",
    "https://formulae.brew.sh/api/analytics-linux/install/30d.json",
    "https://formulae.brew.sh/api/analytics-linux/install/90d.json",
    "https://formulae.brew.sh/api/analytics-linux/install/365d.json",
    "https://formulae.brew.sh/api/analytics-linux/install-on-request/30d.json",
    "https://formulae.brew.sh/api/analytics-linux/install-on-request/90d.json",
    "https://formulae.brew.sh/api/analytics-linux/install-on-request/365d.json",
    "https://formulae.brew.sh/api/analytics-linux/build-error/30d.json",
    "https://formulae.brew.sh/api/analytics-linux/build-error/90d.json",
    "https://formulae.brew.sh/api/analytics-linux/build-error/365d.json",
]

if __name__ == "__main__":
    dfs = [build_df_from_items(get_response(url)) for url in install_and_error_urls]
    formulas = get_unique_formulas(dfs)
