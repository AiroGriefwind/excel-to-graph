from __future__ import annotations

import streamlit as st


def render_sidebar_upload():
    st.sidebar.header("Excel 上传")
    if "excluded_files" not in st.session_state:
        st.session_state.excluded_files = set()

    uploaded_files = st.sidebar.file_uploader(
        "可同时上传多个 .xlsx 文件",
        type=["xlsx"],
        accept_multiple_files=True,
    )
    uploaded_files = uploaded_files or []
    visible_files = [f for f in uploaded_files if f.name not in st.session_state.excluded_files]

    st.sidebar.markdown("### 当前文件列表")
    if not visible_files:
        st.sidebar.caption("暂无可用文件")
    else:
        for f in visible_files:
            c1, c2 = st.sidebar.columns([3, 1])
            c1.caption(f.name)
            if c2.button("移除", key=f"remove_{f.name}"):
                st.session_state.excluded_files.add(f.name)
                st.rerun()

    if st.sidebar.button("恢复全部文件", use_container_width=True):
        st.session_state.excluded_files = set()
        st.rerun()

    return visible_files

