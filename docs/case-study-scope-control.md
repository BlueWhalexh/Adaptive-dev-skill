# Case Study：防止状态筛选功能的 scope drift

这是一个用于沟通 workflow 的 illustrative case study。它描述的是常见模式，不是 measured benchmark。

## 请求

```text
Add a status filter to the issues page.
```

## 没有 workflow 时的失败模式

agent 可能会立即实现可见 UI，同时做出几个隐藏决策：

- 发明 status 列表。
- 改 URL query model。
- 改 table state management。
- 修改 filter 之外的 styling。
- 假设 backend 支持 filtering。
- 跳过 empty-state verification。

用户要求的是 status filter，但 review 现在要覆盖 state management、styling、API behavior 和未验证的边界条件。

## Adaptive Workflow 的响应

agent 先框定任务：

```text
Outcome: users can filter issues by an existing status value.
Scope: filter control, query state, and request parameter only.
Out of scope: table redesign, new status taxonomy, backend API changes unless explicitly approved.
Evidence: browser check or frontend test covering active filter, reset, and empty state.
Stop condition: pause if the backend does not already accept a status filter.
```

然后选择 level：

- 如果页面已有 filtering patterns 且 backend 支持 status，则是 Small。
- 如果 query state、data fetching 或 empty states 需要新行为，则是 Medium。
- 如果需要 backend API 变更，则停下来让用户决策。

## Review 结果

这个改动更容易 review，因为 agent 做了更少隐藏决策。Reviewer 可以直接用声明过的 scope 和 acceptance evidence 对照 diff。
