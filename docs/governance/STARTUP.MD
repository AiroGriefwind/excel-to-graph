# STARTUP

## 给每个 worktree LLM 的开场白模板

你将继续开发 `excel-to-graph` 项目。开始前必须执行以下步骤：

1. 完整阅读以下治理文档并遵守其约束：
   - `docs/governance/IMPLEMENTATION_PLAN.MD`
   - `docs/governance/PROGRESS.MD`
   - `docs/governance/STRUCTURE.MD`
   - `docs/governance/PRD.MD`
   - `docs/governance/TECHSTACK.MD`
2. 明确本次任务目标与范围，避免超范围实现。
3. 如有新增文件或目录，先回写 `STRUCTURE.MD`。
4. 实现完成后必须更新 `PROGRESS.MD`，写清验证与下一步。

### 工作原则
- 优先保证可运行、可验证、可复现。
- 先数据正确，再做 UI 细节优化。
- 保持 `app.py` 薄入口，业务逻辑沉淀在 `src/utils/`。

### 自检清单
- [ ] 是否读取了全部治理文档
- [ ] 是否遵守目录职责分层
- [ ] 是否完成基础验证（至少冒烟脚本或手工检查）
- [ ] 是否更新了 `PROGRESS.MD`

