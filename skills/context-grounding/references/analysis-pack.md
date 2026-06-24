# Analysis Pack

Analysis Pack 是编码前的结构化上下文，不是泛泛总结。

## Required Sections

- Problem: 用户目标、非目标、约束、验收标准。
- Entry Points: 页面、路由、组件、API、命令入口。
- Current Flow: 当前链路、数据流、状态流、鉴权点。
- Similar Patterns: 仓库内可复刻的相似实现。
- Context Slice: 本次实现真正需要看的文件和片段。
- Multimodal Notes: 视觉稿、截图、交互状态的文字化描述。
- Risks: 权限、状态机、兼容性、副作用、回滚风险。
- Task Plan: 可独立 review 的小任务列表。
- Evidence Plan: 每一步如何证明真实完成。

## Quality Bar

Context Slice 要小而充分。不要把整个 `src/**` 当作普通 slice；如果确实需要大范围扫描，先解释原因并把它当作 spike 或 architecture scan。
