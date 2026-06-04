# Case Study: Preventing Scope Drift In A Status Filter

This is an illustrative case study for communicating the workflow. It describes a common pattern rather than a measured benchmark.

## Request

```text
Add a status filter to the issues page.
```

## Failure Mode Without A Workflow

An agent may immediately implement the visible UI and make several hidden choices:

- invent the list of statuses
- change the URL query model
- alter table state management
- touch styling outside the filter
- assume the backend supports filtering
- skip empty-state verification

The user asked for a status filter, but the review now includes state management, styling, API behavior, and unverified edge cases.

## Adaptive Workflow Response

The agent first frames the task:

```text
Outcome: users can filter issues by an existing status value.
Scope: filter control, query state, and request parameter only.
Out of scope: table redesign, new status taxonomy, backend API changes unless explicitly approved.
Evidence: browser check or frontend test covering active filter, reset, and empty state.
Stop condition: pause if the backend does not already accept a status filter.
```

Then it chooses the level:

- Small if the page already has filtering patterns and the backend supports status.
- Medium if query state, data fetching, or empty states need new behavior.
- Stop for user decision if backend API changes are required.

## Review Outcome

The change is easier to review because the agent made fewer hidden decisions. The reviewer can compare the diff against the stated scope and acceptance evidence.
