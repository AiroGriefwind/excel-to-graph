from __future__ import annotations

import html

import pandas as pd
import streamlit as st


CARD_STYLE = """
<style>
.post-card {
  border: 1px solid rgba(120,120,120,0.25);
  border-radius: 12px;
  padding: 14px 16px;
  margin: 10px 0;
  background: linear-gradient(145deg, rgba(35,35,45,0.6), rgba(20,20,25,0.8));
  animation: fadeInCard 0.32s ease-out;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.22);
}
.post-title {
  font-weight: 600;
  margin-bottom: 8px;
}
.post-meta {
  opacity: 0.9;
  font-size: 0.92rem;
  line-height: 1.45;
}
@keyframes fadeInCard {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
"""


def _render_card(row: pd.Series) -> None:
    title = html.escape(str(row.get("title", "")))
    platform = html.escape(str(row.get("platform", "")))
    date = html.escape(str(row.get("date", "")))
    # 展示原始形式；筛选分类在 format，不覆盖卡片展示
    form = html.escape(str(row.get("format_raw") or row.get("format", "")))
    link = html.escape(str(row.get("link", "")))
    views = f"{float(row.get('views', 0)):,.0f}"
    interactions = f"{float(row.get('interactions', 0)):,.0f}"
    source = html.escape(str(row.get("source_file", "")))

    st.markdown(
        f"""
        <div class="post-card">
          <div class="post-title">{title}</div>
          <div class="post-meta">
            日期：{date}<br/>
            平台：{platform} ｜ 形式：{form}<br/>
            浏览量：{views} ｜ 互动量：{interactions}<br/>
            源文件：{source}<br/>
            链接：<a href="{link}" target="_blank">打开原文</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_content_section(filtered_df: pd.DataFrame) -> None:
    st.subheader("内容展示区域")
    st.markdown(CARD_STYLE, unsafe_allow_html=True)

    total = len(filtered_df)
    with st.expander(f"共 {total} 条内容（点击展开）", expanded=False):
        if filtered_df.empty:
            st.info("当前筛选条件下暂无内容。")
            return

        for _, row in filtered_df.iterrows():
            _render_card(row)

