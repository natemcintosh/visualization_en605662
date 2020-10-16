import plotly.graph_objects as go

import pandas as pd

# load dataset
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/volcano.csv")

# Create figure
fig = go.Figure()

# Add surface trace
fig.add_trace(go.Heatmap(z=df.values.tolist(), colorscale="Viridis"))

# Update plot sizing
fig.update_layout(
    width=800, height=900, autosize=False, margin=dict(t=100, b=0, l=0, r=0)
)

# Update 3D scene options
fig.update_scenes(aspectratio=dict(x=1, y=1, z=0.7), aspectmode="manual")

# Add dropdowns
button_layer_1_height = 1.08
fig.update_layout(
    updatemenus=[
        dict(
            buttons=list(
                [
                    dict(
                        args=["colorscale", "Viridis"],
                        label="Viridis",
                        method="restyle",
                    ),
                    dict(
                        args=["colorscale", "Cividis"],
                        label="Cividis",
                        method="restyle",
                    ),
                    dict(args=["colorscale", "Blues"], label="Blues", method="restyle"),
                    dict(
                        args=["colorscale", "Greens"], label="Greens", method="restyle"
                    ),
                ]
            ),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.1,
            xanchor="left",
            y=button_layer_1_height,
            yanchor="top",
        ),
        dict(
            buttons=list(
                [
                    dict(args=["reversescale", False], label="False", method="restyle"),
                    dict(args=["reversescale", True], label="True", method="restyle"),
                ]
            ),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.37,
            xanchor="left",
            y=button_layer_1_height,
            yanchor="top",
        ),
        dict(
            buttons=list(
                [
                    dict(
                        args=[{"contours.showlines": False, "type": "contour"}],
                        label="Hide lines",
                        method="restyle",
                    ),
                    dict(
                        args=[{"contours.showlines": True, "type": "contour"}],
                        label="Show lines",
                        method="restyle",
                    ),
                ]
            ),
            direction="down",
            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.58,
            xanchor="left",
            y=button_layer_1_height,
            yanchor="top",
        ),
    ]
)

fig.update_layout(
    annotations=[
        dict(
            text="colorscale",
            x=0,
            xref="paper",
            y=1.06,
            yref="paper",
            align="left",
            showarrow=False,
        ),
        dict(
            text="Reverse<br>Colorscale",
            x=0.25,
            xref="paper",
            y=1.07,
            yref="paper",
            showarrow=False,
        ),
        dict(text="Lines", x=0.54, xref="paper", y=1.06, yref="paper", showarrow=False),
    ]
)

fig.show()
