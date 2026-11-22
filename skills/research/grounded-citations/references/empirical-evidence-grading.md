# Grading Empirical / Test Evidence

Use when asked to check whether test or validation conclusions are correct —
"are these results right?", "which version is updated?", "did the test really
pass?". The main SKILL.md covers prose claims backed by URLs; this file covers
empirical artifacts: API call logs, step JSONs, RequestIds, result tables.

## Evidence tiers (highest → lowest)

| Tier | What it is | What it supports |
|---|---|---|
| 1. Execution with verdict | Recorded result / assertion tied to the action (status code, Success flag, Denied/allow, pass/fail) | A real pass/fail conclusion |
| 2. Execution receipt | A RequestId / call id proving the call was made, no verdict field | "The call happened" — NOT pass/fail |
| 3. Documentation retrieval | Action / resource lists scraped from official docs | "What the docs say" — NOT what the API did |
| 4. Self-report | A table or report asserting results with no attached artifact | An unverified claim |

## Rules

- **A RequestId is a receipt, not a verdict.** Only a recorded result field
  supports pass/fail. If step JSONs carry only a call id, report "real calls
  were made, outcome unverified" — never upgrade a receipt into a passed test.
- **Documentation retrieval is not a test.** Counts scraped from docs describe
  documented actions; they cannot confirm runtime behavior. Label them
  "documented", never "verified".
- **Treat result tables as self-reports** until reconciled with tier-1/2
  artifacts. Name every cell with no backing evidence explicitly instead of
  implying full coverage.
- **State coverage before conclusions.** "N of M items have real execution
  evidence" — a verdict on the whole set is only as strong as that ratio.
- **A wording diff is not a behavior change.** When comparing two versions of
  a claims table, reconcile each differing cell against the evidence set before
  calling a version "updated". An empty confirmation/acceptance column means
  the final version is undetermined — say so rather than inferring from a
  filename or date.
- **Separate口径变化 from实测支撑.** A changed cell backed only by tier 3 is a
  documentation/interpretation change, not a validated correction.

## Pitfalls

- Don't let a timestamp on an artifact stand in for a verdict — a dated
  RequestId proves when a call ran, not that it passed.
- Don't infer "final version" from a filename; require a confirmed status field.
- Don't average tiers into one "looks correct" — report the tier per claim so
  the reader sees which conclusions are solid.
- Don't claim "verified" for the whole set when only a subset has real tests;
  scope the verdict to what was actually exercised.
