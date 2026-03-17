# IMPLEMENTATION PLAN

## 执行前置要求（强制）
- 任意 LLM 或开发者开始任务前，必须完整阅读以下文档：
  - `docs/governance/IMPLEMENTATION_PLAN.MD`
  - `docs/governance/PROGRESS.MD`
  - `docs/governance/STRUCTURE.MD`
  - `docs/governance/PRD.MD`
  - `docs/governance/STARTUP.MD`
  - `docs/governance/TECHSTACK.MD`
- 未完成阅读，不得开始编码、重构或测试变更。
- 每个可感知功能变更完成后，先更新 `PROGRESS.MD`，再进入下一任务。

## 分阶段目标
1. 治理文档落地：明确目标、结构、流程与技术栈。
2. 核心数据层：实现 Excel 解析、清洗、筛选、聚合、预设持久化。
3. UI 分层：完成主页面、筛选器、图表、卡片内容、侧边栏上传。
4. 测试与验证：完成数据与筛选的冒烟脚本并可复现执行。
5. 文档回填：同步进度、结构与选型变更。

## 代码组织约束
- 入口仅保留 `app.py`（薄入口）。
- 页面区域渲染函数统一放在 `src/tabs/`。
- 纯功能函数放在 `src/utils/`。
- 测试样本在 `tests/mocks/`，冒烟脚本在 `tests/smokes/`。

## 交付验收（最小）
- 可同时上传多个 Excel。
- 可按平台/日期/标题关键字/形式筛选。
- 可展示条数、浏览量、互动量。
- 可展示至少 1 个饼图和 1 个折线图。
- 可保存、读取、应用筛选预设。
- 可在内容区折叠/展开并卡片化浏览贴文。

