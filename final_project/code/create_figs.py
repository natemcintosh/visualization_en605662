import enum
import json
import os
from typing import Dict, List
import itertools as it
from io import StringIO
from pprint import pprint
import re

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def formula_installs(file: str) -> Dict[str, go.Figure]:
    """
    formula_installs will produce a lineplot of total package installs for a given
    package over 30, 90, and 365 days
    """
    assert os.path.isfile(file), f"Could not find installs csv {file}"
    df = pd.read_csv(file)
    df["normalized_count"] = df.count_regular / df.n_days
    df.n_days = df.n_days * -1

    mac = (
        df.loc[df.os.eq("macos")]
        .groupby("n_days")
        .head(20)
        .sort_values("normalized_count", ascending=False)
    )
    linux = (
        df.loc[df.os.eq("linux")]
        .groupby("n_days")
        .head(20)
        .sort_values("normalized_count", ascending=False)
    )

    mac_fig = px.line(
        mac,
        x="n_days",
        y="normalized_count",
        color="formula",
        line_group="formula",
        labels={"n_days": "Last N Days", "normalized_count": "Installs per Day"},
        title="Top 20 Mac Formula Installs",
    )
    mac_fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[-365, -90, -30],
            ticktext=["365", "90", "30"],
            range=[-380, 0],
        )
    )

    linux_fig = px.line(
        linux,
        x="n_days",
        y="normalized_count",
        color="formula",
        line_group="formula",
        labels={"n_days": "Last N Days", "normalized_count": "Installs per Day"},
        title="Top 20 Linux Formula Installs",
    )
    linux_fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[-365, -90, -30],
            ticktext=["365", "90", "30"],
            range=[-380, 0],
        )
    )

    return dict(macos=mac_fig, linux=linux_fig)


def request_ratio(file: str) -> Dict[str, go.Figure]:
    """
    request_ratio creates two barplots of the ratio of install on request: install
    """
    assert os.path.isfile(file), f"Could not find installs csv {file}"
    df = pd.read_csv(file)
    # Locate the top 20 packages by installs in the last 365 days
    popular_packages = (
        df.groupby("os")
        .apply(
            lambda x: x.loc[df.n_days.eq(365)]
            .sort_values("count_regular", ascending=False)
            .head(20)
            .formula.tolist()
        )
        .to_dict()
    )

    smaller_df = df.loc[df.formula.isin(flatten(popular_packages.values()))]

    figs = []
    for which_os in popular_packages.keys():
        fig = go.Figure(
            data=[
                go.Bar(
                    name="30 days",
                    x=popular_packages[which_os],
                    y=smaller_df.loc[
                        smaller_df.formula.isin(popular_packages[which_os])
                        & smaller_df.os.eq(which_os)
                        & smaller_df.n_days.eq(30)
                    ]
                    .sort_values("count_regular", ascending=False)
                    .pct_on_request,
                ),
                go.Bar(
                    name="90 days",
                    x=popular_packages[which_os],
                    y=smaller_df.loc[
                        smaller_df.formula.isin(popular_packages[which_os])
                        & smaller_df.os.eq(which_os)
                        & smaller_df.n_days.eq(90)
                    ]
                    .sort_values("count_regular", ascending=False)
                    .pct_on_request,
                ),
                go.Bar(
                    name="365 days",
                    x=popular_packages[which_os],
                    y=smaller_df.loc[
                        smaller_df.formula.isin(popular_packages[which_os])
                        & smaller_df.os.eq(which_os)
                        & smaller_df.n_days.eq(365)
                    ]
                    .sort_values("count_regular", ascending=False)
                    .pct_on_request,
                ),
            ]
        )
        fig.update_layout(
            barmode="group",
            title=f"Top 20 Install on Request Ratio: {which_os}",
            yaxis_title="Percent of Installs on Request",
        )
        figs.append(fig)

    return dict(zip(popular_packages.keys(), figs))


def flatten(collection):
    return it.chain.from_iterable(collection)


def dep_matrix(filename: str) -> go.Figure:
    """
    dep_matrix will create a heatmap of dependencies for the top 100
    """
    assert os.path.isfile(filename), f"Could not find file {filename}"
    with open(filename) as fio:
        deps = json.loads(fio.read())
    df = pd.DataFrame(data=deps, columns=["package", "depends_on"])

    top100 = df.depends_on.value_counts().head(100).index.tolist()
    mapping = dict(zip(top100, range(len(top100))))

    smaller_df = df.loc[df.package.isin(top100) | df.depends_on.isin(top100)]

    # Each row of the array is a package, each col is something it depends on
    top100_dep_arr = np.zeros((100, 100))
    for pair in smaller_df.itertuples():
        if (pair.package in mapping) and (pair.depends_on in mapping):
            top100_dep_arr[mapping[pair.package], mapping[pair.depends_on]] = 1
    # Change 0 to None, this will stop it from being filled in during plotting
    top100_dep_arr = np.where(top100_dep_arr == 1, top100_dep_arr, None)

    fig = go.Figure()
    fig.add_heatmap(x=top100, y=top100, z=top100_dep_arr, hoverongaps=False)
    fig.update_layout(
        title="Dependencies Among the Top 100 Most Depended Upon Packages<br>(hover to see which package depends on which other packages)",
        yaxis_title="Package",
        xaxis_title="Depends On",
        xaxis=dict(tickmode="array", tickvals=[], ticktext=[],),
        yaxis=dict(tickmode="array", tickvals=[], ticktext=[],),
    )
    fig.update_traces(showscale=False)
    return fig


def create_dep_tree(filename: str, formula: str) -> go.Figure:
    """
    Create a tree figure of what formulas one formula depends on
    """
    assert os.path.isfile(filename), f"Could not find file {filename}"
    with open(filename) as fio:
        deps = json.loads(fio.read())
    df = pd.DataFrame(data=deps, columns=["package", "depends_on"])

    assert formula in set(df.package).union(
        df.depends_on
    ), f"Package asked for ({formula}) does not exist"

    requirements_list = build_requirements_list(df, formula)
    df_for_plotting = get_pprint_version_df(requirements_list)
    return px.line(
        df_for_plotting, x="x", y="y", text="text", title="Dependency Tree"
    )


def get_pprint_version_df(l: list) -> pd.DataFrame:
    """
    Get what pprint spits out as a string, put into dataframe of cartesian coorinates
    """
    stream = StringIO()
    # Capture the beauty of pprint in a string
    pprint(l, indent=2, stream=stream)
    s = stream.getvalue().splitlines()

    # Clean up the data in the stream
    cleaner_strings = [
        si.replace("[", "").replace("]", "").replace("'", "").replace(",", "").rstrip()
        for si in s
    ]

    return pd.DataFrame(
        [
            dict(x=count_starting_spaces(line), y=-height, text=line)
            for height, line in enumerate(cleaner_strings)
        ]
    )


def count_starting_spaces(line: str) -> int:
    "Count the number of spaces at the start of the string"
    return len(re.findall(r"^(\s*)", line)[0])


def build_requirements_list(df: pd.DataFrame, formula: str) -> list:
    """
    Recursively get the dependencies for a formula
    """
    return [
        formula,
        [
            build_requirements_list(df, li)
            for li in df.depends_on.loc[df.package.eq(formula)]
        ],
    ]


# Look here for instructions to build a chord diagram
# https://plotly.com/python/v3/filled-chord-diagram/
# https://plotly.com/python/v3/chord-diagram/
