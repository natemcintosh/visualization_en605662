from urllib import request
from urllib.error import HTTPError
import json
import itertools
from typing import Dict, Iterable, List, Tuple
from collections import Counter
from warnings import warn
from multiprocessing import Pool
import os
import re

import pandas as pd
from graphviz import Digraph


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


def create_formula_install_df(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Takes a dictionary of all the data downloaded, and produces a single dataframe with
    the columns
        - formula
        - count
        - pct_on_request
        - percent
        - os
        - n_days
    """
    # Downselect to just the dfs of formula data
    downselected = {
        url: data_dict[url]
        for url in data_dict.keys()
        if ("cask" not in url) and ("build" not in url)
    }

    # Split into install and install on request
    installs = {
        url: downselected[url] for url in downselected.keys() if "on-request" not in url
    }
    titles = set(downselected.keys())
    on_request = {url: downselected[url] for url in titles.difference(installs.keys())}

    # Build up a dataframe from the regular install dataframes
    reg_df = pd.concat(
        [add_desired_cols(url, df) for url, df in installs.items()]
    ).drop("number", axis="columns")

    # Create the same columns for the requested
    on_request_with_cols = pd.concat(
        [add_desired_cols(url, df) for url, df in on_request.items()]
    ).drop("number", axis="columns")

    # Join the two dfs
    main_df = reg_df.merge(
        on_request_with_cols,
        on=["formula", "os", "n_days"],
        suffixes=["_regular", "_on_request"],
    )

    # Calculate percent installed on request
    main_df["pct_on_request"] = main_df.count_on_request / main_df.count_regular * 100

    # Because we can't pull all the data instantaneously, there are some inaccuracies
    # where pct_on_request > 100. Remove these rows
    main_df = main_df.loc[main_df.pct_on_request.le(100)]

    return main_df


def add_desired_cols(url: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Take in a dataframe and add the columns `os` and `n_days`
    """
    # Get the OS
    os = "linux" if "linux" in url else "macos"

    # Get the number of days this set of data is relevant for
    n_days = int(re.findall(r"(\d+)d\.json$", url)[0])

    # Add the columns
    df["os"] = os
    df.os = df.os.astype("string")
    df["n_days"] = n_days
    return df


def create_cask_install_df(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Create a single dataframe of cask install information
    """
    # Filter down to just the cask entries in the dict
    casks = {url: data_dict[url] for url in data_dict.keys() if "cask" in url}

    # Add n_days as a column to each dataframe
    for url, df in casks.items():
        df["n_days"] = int(re.findall(r"(\d+)d\.json$", url)[0])

    # Stack the dfs and return
    return pd.concat(casks.values())


def create_build_errors_df(data_dict: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Create a single dataframe of all the build error info with new columns for n_days, 
    os
    """
    # Get just the build errors
    errors = {url: data_dict[url] for url in data_dict.keys() if "build-error" in url}

    # Create the main dataframe and return it
    return pd.concat([add_desired_cols(url, df) for url, df in errors.items()])


def create_dependencies_graph(
    formula_dict: dict, dependency_key_name: str
) -> List[Tuple[str, str]]:
    """
    Create a list of mappings from package and a single dependency
    """
    return list(
        itertools.chain.from_iterable(
            [(d["name"], dep) for dep in d.get(dependency_key_name, [])]
            for d in formula_dict
        )
    )


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

    # If data exists in a data folder, get it. If not, get the data from the internet
    this_dir = os.path.dirname(__file__)
    data_file = os.path.join(this_dir, "..", "data", "formula_info.json")
    if os.path.isfile(data_file):
        with open(data_file) as f:
            formula_json = json.loads(f.read())
    else:
        # For each formula, try to get it's json data. There are probably a few thousand, so
        # this may take a few minutes
        formula_json = get_available_formula_json_parallel(bare_formulas)

        # Save off the data so I don't have to get it every time I test the script
        with open(data_file, "w") as f:
            f.write(json.dumps(formula_json))

    # Count the number of times a formula is used as a dependency
    depended_upon_formulae = Counter(
        itertools.chain.from_iterable(f.get("dependencies", []) for f in formula_json)
    )
    depended_upon_formulae = pd.DataFrame(
        depended_upon_formulae.items(), columns=["formula", "count"]
    ).sort_values("count", ascending=False)

    # Get a list of dicts mapping a package to one of its dependencies
    dep_graph = create_dependencies_graph(formula_json, "dependencies")

    dot = Digraph(name="dependency graph")
    for d in dep_graph:
        dot.edge(*d)
    
    output_folder = os.path.join(this_dir, "..", "output")
    dot.render(os.path.join(output_folder, "dep_graph.gv"), view=True)

    # Get a list of dicts mapping a package to one of its recommended dependencies
    rec_dep_graph = create_dependencies_graph(formula_json, "recommended_dependencies")

    # Get a list of dicts mapping a package to one of its optional dependencies
    opt_dep_graph = create_dependencies_graph(formula_json, "optional_dependencies")

    # Get a list of dicts mapping a package to one of its requirements
    req_dep_graph = create_dependencies_graph(formula_json, "requirements")

    # Create dict of url: df
    data_dict = dict(zip(install_and_error_urls, dfs))

    # Get all formula install events into a single df with columns:
    # formula, count, pct_on_request, percent, os, n_days
    formula_installs = create_formula_install_df(data_dict)

    # Get all cask install information
    cask_installs = create_cask_install_df(data_dict)

    # Get all the build error information
    build_errors = create_build_errors_df(data_dict)

    run_time = time() - start_time
    print(f"get_and_clean_data.py -- {run_time:.2f}s")
