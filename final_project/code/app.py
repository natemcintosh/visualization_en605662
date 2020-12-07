import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

fig = go.Figure()
fig.add_scatter(x = [1,2,3], y = [1,2,3])

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    [
        html.H1("Homebrew Analytics", style=dict(textAlign="center")),
        html.Div(
            ["Input: ", dcc.Input(id="my-input", value="initial value", type="text")]
        ),
        html.Br(),
        html.Div(id="my-output"),
        html.Div(
            [dcc.Graph(id="figure1", figure=fig),],
            style={
                "width": "49%",
                "display": "inline-block",
                "vertical-align": "middle",
            },
        ),
    ],
)


@app.callback(
    Output(component_id="my-output", component_property="children"),
    Input(component_id="my-input", component_property="value"),
)
def update_output_div(input_value):
    return f"Output: {input_value}"


if __name__ == "__main__":
    app.run_server(debug=True)
