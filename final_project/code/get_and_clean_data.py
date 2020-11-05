from urllib import request
from urllib.error import HTTPError
import json
import itertools
from typing import Iterable, List
from collections import Counter
from warnings import warn
from multiprocessing import Pool
import os

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


def create_formula_json_url(formula_name: str) -> str:
    return "https://formulae.brew.sh/api/formula/" + formula_name + ".json"


def get_available_formula_json(formula_name: str) -> dict:
    """
    Get the json data if it exists for this formula
    """
    try:
        return get_response(create_formula_json_url(formula_name))
    except HTTPError:
        return dict()
    except:
        warn("Could not read formula API, but not because it didn't exist")
        return dict()


def get_available_formula_json_parallel(formulae: Iterable[str]) -> List[dict]:
    """
    Call get_available_formula_json() on all the formulae in parallel
    """
    with Pool() as p:
        return p.map(get_available_formula_json, formulae)


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
    from time import time

    start_time = time()

    # Build dataframes from the json data at the URLs listed above
    dfs = [build_df_from_items(get_response(url)) for url in install_and_error_urls]

    # From all the formulas in `dfs`, get a list of the unique ones
    formulas_with_args = get_unique_formulas(dfs)

    # Many of the formulas have arguments with them. Get just the name of the formula
    bare_formulas = set(f.split()[0] for f in formulas_with_args)

    # For each formula, try to get it's json data. There are probably a few thousand, so
    # this may take a few minutes
    formula_json = get_available_formula_json_parallel(bare_formulas)

    # Save off the data so I don't have to get it every time I test the script
    this_dir = os.path.dirname(__file__)
    with open(os.path.join(this_dir, "../data/formula_info.json"), "w") as f:
        f.write(json.dumps(formula_json))

    # Count the number of times a formula is used as a dependency
    depended_upon_formulae = Counter(
        itertools.chain.from_iterable(f.get("dependencies", []) for f in formula_json)
    )
    depended_upon_formulae = pd.DataFrame(
        depended_upon_formulae.items(), columns=["formula", "count"]
    )

    run_time = time() - start_time
    print(f"get_and_clean_data.py -- {run_time:.2f}s")
