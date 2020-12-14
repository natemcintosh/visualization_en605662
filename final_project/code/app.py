import os

import dash
import dash_core_components as dcc
from dash_core_components.Graph import Graph
import dash_html_components as html
from dash.dependencies import Input, Output
from dash_html_components.Div import Div
import plotly.graph_objects as go

import create_figs

data_dir = os.path.join(os.path.dirname(__file__), "..", "data")

installs_dict = create_figs.formula_installs(
    os.path.join(data_dir, "formula_installs.csv")
)

ratios_dict = create_figs.request_ratio(os.path.join(data_dir, "formula_installs.csv"))

dep_heatmap = create_figs.dep_matrix(os.path.join(data_dir, "dep_graph.json"))

dep_tree = create_figs.create_dep_tree(os.path.join(data_dir, "dep_graph.json"), "trimage")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1(
            "Homebrew Analytics: EN 605.462 Final Project",
            style=dict(textAlign="center"),
        ),
        html.H6("Nathan McIntosh", style=dict(textAlign="center")),
        html.Div(
            [
                dcc.Graph(id="dep-matrix", figure=dep_heatmap),
                dcc.Dropdown(
                    id="popularity-line-dropdown",
                    options=[
                        dict(label="MacOS", value="macos"),
                        dict(label="Linux", value="linux"),
                    ],
                    value="macos",
                    clearable=False,
                ),
                dcc.Graph(id="popularity-line-figure"),
            ],
            style={
                "width": "49%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        html.Div(
            [
                dcc.Graph(id="dep-tree", figure=dep_tree),
                dcc.Dropdown(
                    id="request-ratio-dropdown",
                    options=[
                        dict(label="MacOS", value="macos"),
                        dict(label="Linux", value="linux"),
                    ],
                    value="macos",
                    clearable=False,
                ),
                dcc.Graph(id="request-ratio-figure"),
            ],
            style={
                "width": "49%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
    ],
)


@app.callback(
    Output("popularity-line-figure", "figure"),
    [Input("popularity-line-dropdown", "value")],
)
def update_line_chart(which_os):
    fig = installs_dict[which_os]
    return fig


@app.callback(
    Output("request-ratio-figure", "figure"), [Input("request-ratio-dropdown", "value")]
)
def update_ratio_chart(which_os):
    fig = ratios_dict[which_os]
    return fig


if __name__ == "__main__":
    # Collect and save all the relevant data
    # from get_and_clean_data import main as data_main
    # data_main()

    # Run the server
    app.run_server(debug=True)
