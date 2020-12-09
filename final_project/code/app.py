import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

fig = go.Figure()
fig.add_scatter(x=[1, 2, 3], y=[1, 2, 3])

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
            [dcc.Graph(id="figure1", figure=fig), dcc.Graph(id="figure2", figure=fig),],
            style={
                "width": "49%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
        html.Div(
            [dcc.Graph(id="figure3", figure=fig), dcc.Graph(id="figure4", figure=fig),],
            style={
                "width": "49%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
    ],
)


if __name__ == "__main__":
    # Collect and save all the relevant data
    # from get_and_clean_data import main as data_main
    # data_main()

    # Create the figures to be displayed
    # from create_figs import main as plot_main
    # plot_main()

    # Run the server
    app.run_server(debug=True)
