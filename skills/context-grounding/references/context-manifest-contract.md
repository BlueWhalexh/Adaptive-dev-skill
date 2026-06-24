# Context Manifest Contract

`context_manifest.json` 是机器校验入口。

```json
{
  "context_manifest_id": "ctx-001",
  "repo_commit": "HEAD_SHA",
  "spec_version": "spec-001-v1",
  "allowed_paths": ["src/orders/OrderDetail.tsx"],
  "forbidden_paths": ["secrets/**"],
  "context_files": [
    {
      "path": "src/orders/OrderDetail.tsx",
      "sha256": "file hash",
      "reason": "entry point"
    }
  ],
  "runtime_audit": {
    "read_events": []
  }
}
```

Use `skills/adaptive-dev-workflow/schemas/context-manifest.schema.json` as the canonical schema.
