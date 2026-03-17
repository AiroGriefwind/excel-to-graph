from __future__ import annotations

import streamlit as st

from .filtering import DEFAULT_FILTERS


def init_state() -> None:
    if "raw_df" not in st.session_state:
        st.session_state.raw_df = None
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = None
    if "active_filters" not in st.session_state:
        st.session_state.active_filters = DEFAULT_FILTERS.copy()
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

