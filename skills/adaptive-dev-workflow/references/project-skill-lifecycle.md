# Project Skill Lifecycle

READ when: a repo is new, a minimum vertical slice has just been delivered, repeated project-specific lessons appear, the user asks to reduce future prompting, or `adaptive-dev-workflow` is asked to initialize or evolve a project harness.

DO NOT READ for Tiny/Small one-off edits, generic library usage, or lessons that belong in this general skill.

## Contents

- Trigger
- Project Harness Init
- Learning Candidate
- Promotion Destinations
- Project Skill Shape
- Promotion Gates
- Lifecycle Exit Gate
- NEVER

## Trigger

Use this lifecycle when project learning is likely to improve future work:

- New repo, new product area, or first serious feature in an existing repo.
- First MVP vertical slice completed with real evidence.
- The same project-specific workflow, pitfall, command, architecture rule, or verification pattern appears at least twice.
- The user corrects the agent in a way that reveals missing project memory.
- A domain-specific SOP would reduce future user prompting.

Do not promote from a single anecdote unless the failure is P0 and broadly reusable.

## Project Harness Init

Prefer existing project conventions. If none exist, propose the smallest useful harness:

```text
.
├── AGENTS.md
├── .agent/
│   ├── agents.md
│   ├── knowledge/
│   │   └── candidates/
│   ├── evals/
│   └── runs/
├── .agent/skills/<project-domain>/
│   ├── SKILL.md
│   └── references/
│       ├── architecture.md
│       ├── testing.md
│       └── lessons.md
├── docs/
│   ├── architecture.md
│   ├── adr/
│   ├── specs/
│   │   ├── <feature-id>/
│   │   │   ├── spec.md
│   │   │   ├── design.md
│   │   │   ├── acceptance.yaml
│   │   │   └── changes/
│   │   └── archived/
│   ├── plans/
│   │   └── <feature-id>.md
│   └── evidence/
│       └── <feature-id>.md
```

Use the standalone `project-harness-init` skill when available to create or repair the harness. Do not keep a second scaffold script in `adaptive-dev-workflow`; this lifecycle file describes where project learning should live, not how to generate the scaffold.

## Learning Candidate

At task exit, capture a learning candidate when the agent learned a project-specific rule, command, test boundary, review pattern, integration pitfall, or docs invariant that would help the next task.

Candidate file:

```text
.agent/knowledge/candidates/KC-YYYYMMDD-HHMMSS.yaml
```

Minimal fields:

```yaml
id:
kind: sop | gotcha | architecture | testing | command | review | delivery | quality
statement:
scope:
  paths: []
trigger:
action:
source:
  task:
  commit:
evidence:
  validators: []
  result:
occurrences:
confidence: low | medium | high
risk: low | medium | high
proposed_destination: project-skill | AGENTS.md | docs | script | ci | adr | reference
last_verified_at:
expires_at:
status: candidate
```

Use `scripts/capture_learning_candidate.py` when available for deterministic creation.

## Promotion Destinations

Choose the smallest durable home for the lesson:

| Lesson Type | Destination | Why |
| --- | --- | --- |
| Stable repo rule every agent must obey | `AGENTS.md` | Always-loaded policy |
| Directory-specific invariant | nested `AGENTS.md` | Scoped policy |
| Repeated project SOP | `.agent/skills/<project-domain>/SKILL.md` | Reusable workflow |
| Detailed background, pitfalls, examples | project skill `references/` | On-demand context |
| Architecture decision | `docs/adr/` | Durable decision record |
| Current architecture truth | `docs/architecture.md` or existing canonical docs | Grounding |
| Mechanical repeat check | script, hook, lint, or CI | Deterministic enforcement |
| Unverified one-off observation | `.agent/knowledge/candidates/` | Not policy yet |

## Project Skill Shape

Project skills should stay lean and route to references:

```text
.agent/skills/<project-domain>/
├── SKILL.md
└── references/
    ├── architecture.md
    ├── testing.md
    ├── lessons.md
    └── delivery.md
```

`SKILL.md` should include:

- What project/task patterns trigger the skill.
- Current project invariants that are not obvious from code.
- Which reference to read for architecture, testing, delivery, or lessons.
- Project-specific NEVER rules learned from real failures.

Language convention for project-internal skills:

- Use a bilingual frontmatter `description`: English triggers plus Chinese triggers.
- Keep `name`, route names, gate names, YAML/schema fields, scripts, and evidence labels in English.
- Use Chinese as the main body language when the repo/team works primarily in Chinese.
- Keep English anchors for stable concepts: `Current Truth`, `Testing Context`, `Evidence`, `Delivery`, `NEVER`.
- Do not write a full Chinese body and a full English body. That doubles context cost without improving routing.

Do not copy Superpowers internals into the project skill. The project skill supplies local domain context; Superpowers supplies execution discipline.

## Promotion Gates

Promote candidate knowledge only when it passes the matching gate:

| Destination | Gate |
| --- | --- |
| `AGENTS.md` | Stable, broad, short, scoped, reviewed, no secrets, no local-only assumptions |
| project skill `SKILL.md` | Repeated SOP, clear trigger, clear output, successful evidence |
| project skill `references/` | Useful background too long for `SKILL.md`, with source and date |
| `docs/architecture.md` | Current truth verified against code |
| `docs/adr/` | Durable architecture choice with alternatives and rollback story |
| script/hook/CI | Mechanically checkable, low false-positive rate |

If a candidate conflicts with current docs or code, do not promote it. Resolve the conflict or keep it as a candidate with a blocker note.

## Lifecycle Exit Gate

Before saying project learning was captured:

```text
Candidate: created or explicitly not needed
Destination: proposed, not silently promoted
Evidence: linked to fresh validator or review finding
Scope: repo/path/task scope stated
Risk: secret/local-env/dated-knowledge risk checked
Next use: how a future agent will find it
```

## NEVER

- NEVER auto-append raw lessons directly to global `AGENTS.md`.
- NEVER promote a workaround that only works on the current machine.
- NEVER store secrets, private tokens, cookies, logs, or credentials in candidates or skills.
- NEVER put generic coding advice in a project skill.
- NEVER let project skills duplicate TDD, debugging, planning, or review workflows already owned by stronger execution skills.
- NEVER allow project memory to grow without scope, evidence, and a deletion path.
