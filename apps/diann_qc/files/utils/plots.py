"""
Shared plotting utilities — thin wrappers around Plotly Express / Graph Objects
that apply consistent theming and group-aware colouring throughout the app.
"""
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

PLOTLY_THEME = "plotly_dark"
AXIS_STYLE = dict(showgrid=True, gridcolor="#2a2d3e", zeroline=False)

def base_layout(**kwargs) -> dict:
    defaults = dict(
        template=PLOTLY_THEME,
        paper_bgcolor="#0f1117",
        plot_bgcolor="#0f1117",
        font=dict(family="IBM Plex Mono, monospace", size=11, color="#c9d1d9"),
        margin=dict(l=50, r=20, t=50, b=50),
    )
    defaults.update(kwargs)
    return defaults

def get_color_for(value: str, color_map: dict, fallback="#00b4d8") -> str:
    return color_map.get(value, fallback)

def placeholder_figure(message: str = "Coming soon") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=f"[ {message} ]",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="#555", family="IBM Plex Mono, monospace"),
    )
    fig.update_layout(
        **base_layout(height=350),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig

def show_placeholder(label: str):
    """Render a placeholder chart with a label."""
    st.plotly_chart(placeholder_figure(label), use_container_width=True)


def show_FWHM():
    pass
