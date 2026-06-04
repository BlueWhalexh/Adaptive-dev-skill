# Manifesto: Less Chaos, Better Quality

Agentic coding is powerful because it compresses implementation time. It is risky because it can also compress the time between misunderstanding and repository damage.

The answer is not to slow every task down. The answer is to make the agent choose the right amount of process for the actual risk.

## The Principle

Use the lightest process that still protects correctness.

That means:

- move quickly on obvious, low-risk edits
- clarify vague requests before implementation
- plan when the change affects multiple moving parts
- use tests or explicit validators for behavior changes
- pause before expanding scope
- verify before claiming completion

## Why Agents Drift

Agents drift because they are optimized to continue. A helpful assistant wants to make progress, and progress often looks like writing code.

In real software work, progress also means refusing to code before the acceptance criteria are clear. It means noticing that a "small change" would require an API decision. It means stopping before a security-sensitive edit turns into a guess.

Adaptive Dev Workflow gives the agent permission to stop at those points.

## The System, Not A Prompt

A prompt says "be careful".

A checklist says "do all these things".

A system says "choose the right gate for this situation".

Adaptive Dev Workflow is a system because it routes the task:

- Tiny tasks should not inherit ceremony.
- Risky tasks should not be treated as quick patches.
- Debugging should use debugging discipline.
- Completion should require fresh evidence.

The result is not bureaucracy. The result is fewer hidden decisions.
