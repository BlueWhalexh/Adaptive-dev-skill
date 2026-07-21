# AGENTS.md

项目特定协作约定。保持精简；通用开发能力交给模型和按需 Skill。

## Project Truth

- 项目入口、架构地图和事实源：填写真实路径。
- 开发、测试、启动命令：填写可直接执行的命令。
- 安全、数据、权限和生产禁区：填写项目真实边界。

## Outcome Priority

- 新方向先证明 Minimum Real Slice，再建设完整可靠性。
- 当前 slice 按真实影响判断，不继承父项目的最大风险。
- 低优先级流程、观测、文档和 Review finding 不得阻塞当前用户结果，除非它们影响安全或使结果无法判断。
- 仅在长期目标、Basic Usable、AI 行为迭代或流程跑偏时使用 `adaptive-dev-workflow`；普通任务直接执行。

## Verification

- 局部改动运行 focused validator。
- Basic Usable 使用代表场景和最小真实链路。
- Release/Handoff 才运行完整 acceptance、E2E、real external/fresh consumer 和 rollback 验收。
- 明确区分 unit/mock、fake、integration、E2E 和 real external。

## Human Decisions

仅在产品取舍、public contract、数据/权限/安全、不可逆生产操作或继续投入价值不明确时请求人工决定。文件数量、普通测试失败和可恢复实现选择不是停止条件。
