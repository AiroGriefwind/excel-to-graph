# TECHSTACK

## 语言与运行时
- Python 3.10+

## 核心库
- `streamlit`：Web UI 框架
- `pandas`：Excel 读取与数据处理
- `openpyxl`：`.xlsx` 引擎
- `plotly`：交互图表（饼图、折线图）
- `python-docx`：导出 Word（.docx）统计报告

## 测试与脚本
- Python 脚本式 smoke tests（`tests/smokes/`）

## 依赖管理
- `requirements.txt`：记录运行与开发所需依赖

## 持久化策略
- 本地 JSON 文件（`.streamlit/filter_presets.json`）存储筛选预设

## 选型理由（简版）
- Streamlit 可快速交付数据交互 UI；
- pandas 适配 Excel 解析/清洗；
- plotly 图表观感与交互能力较好；
- JSON 方案实现成本低，满足单机场景。

