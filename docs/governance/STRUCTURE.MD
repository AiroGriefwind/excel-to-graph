# STRUCTURE

## 目录职责
- `app.py`：Streamlit 入口，负责初始化状态与调用各区域渲染函数。
- `src/tabs/`：主页面各区域的渲染函数（标题、筛选器、图表、内容、侧边栏）。
- `src/utils/`：解析、清洗、筛选、聚合、预设持久化等业务函数。
- `tests/mocks/`：测试 Excel 样本输入。
- `tests/smokes/`：冒烟测试脚本（可直接运行）。
- `docs/governance/`：项目治理文档。

## 当前结构
```text
excel-to-graph/
  app.py
  requirements.txt
  src/
    tabs/
      __init__.py
      header_tab.py
      filter_tab.py
      chart_tab.py
      content_tab.py
      sidebar_tab.py
    utils/
      __init__.py
      constants.py
      excel_loader.py
      filtering.py
      metrics.py
      presets.py
      chart_data.py
      state.py
  tests/
    mocks/
      *.xlsx
    smokes/
      smoke_data_pipeline.py
      smoke_filter_presets.py
  docs/
    governance/
      IMPLEMENTATION_PLAN.MD
      PROGRESS.MD
      STRUCTURE.MD
      PRD.MD
      STARTUP.MD
      TECHSTACK.MD
```

## 命名约定
- Python 文件与函数使用 `snake_case`。
- UI 渲染函数统一以 `render_` 前缀命名。
- DataFrame 内部标准列名固定为：
  - `date`
  - `platform`
  - `title`
  - `format`
  - `link`
  - `views`
  - `interactions`
  - `source_file`

