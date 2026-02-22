import streamlit as st

DEFAULTS = {
    "report": None,
    "metadata": None,
    "regex_pattern": r"(?:.*[\\/])?(.+?)(?:\.\w+)?$",
    "has_im": False,
    "group_col": "group",
    "color_map": {},
}

def init_session_state():
    for key, val in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val

