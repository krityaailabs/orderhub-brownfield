# Section 3: reference answers

## 3.1 Three questions for "Add returns to OrderHub"

1. Which orders can be returned, and until when (status, time window)?
2. How is the refund calculated, especially when the order had a discount, and who confirms it is right?
3. What is out of scope (payment to the card, exchanges, billing file), and what must not change?

Good questions change the spec. "Which framework should I use?" doesn't; the codebase answers it.

## 3.2 The weak spec, scored

`python tools/spec_check.py labs/s03/weak-spec.md labs/s03/weak-spec.plan.md`:

```
FAIL  weak-spec.md + weak-spec.plan.md
      - spec: missing section: Context
      - spec: missing section: Constraints
      - spec: missing section: Non-goals
      - spec: too few acceptance criteria: 2 (minimum 3)
      - spec: AC-1: needs Given, When and Then in that order
      - spec: AC-2: needs Given, When and Then in that order
      - spec: unresolved TODO
      - plan: S1: ~800 lines is over the 300 line review budget; split it
```

What the rubric can't see: "returns should work properly" has no numbers, so it can't fail; "refunds must be correct" doesn't say correct by which rule. The strong version is `docs/specs/returns.md`.

## 3.3 Interview on Q7: questions worth keeping

Keep (each changes the spec): return window; returnable statuses; refund rule with discounts and rounding; who signs off the refund rule (finance); partial quantities; restocking; whether refunds reach the billing file; whether the card is refunded. Drop (don't change the spec): which module to put it in; whether to use a new table; naming.

## 3.4 Plans

| Plan | Decision | Reason |
|---|---|---|
| A | **Approve** | Matches slice S2 exactly; reads the billing context; failing tests first; runs `make billing-demo`; ~150 lines |
| B | **Reject** | Not a slice (1,100 lines, 14 files); scope creep (Money refactor); **edits existing tests**; **changes the billing CSV**, a non-goal and a contract; no criteria mapping |
| C | **Reject** | Tests written after the implementation; float arithmetic with `round()` (ADR 0001); runs only Python tests; no remainder rule for AC-3 |

## 3.6 Spec approaches (reference judgements)

| Decision | Plain Markdown in the repo | Spec Kit | IDE spec mode (Kiro) |
|---|---|---|---|
| Quality risk | Depends on your template and review; a rubric check helps | Structured phases reduce omissions; generated text still needs review | Structured requirements (EARS) and design docs; generated text still needs review |
| Review effort | Lowest: short, human-written | Higher: more generated artefacts per feature | Higher: requirements, design and tasks per feature |
| Speed to a merged change | Fast for small features | Slower start, faster on large features | Slower start, faster on large features |
| Works across our three tools | Yes: any tool reads Markdown | Designed to work with several agents; check yours is supported | Tied to the Kiro IDE |
| Lock-in and refresh effort | None | Low to medium; commands and file layout change between releases | Medium to high: tied to one product |
| Best fit | Most teams; small to medium features | Teams that want a prescribed process across agents | Teams standardised on Kiro |

## 3.7 Loyalty epic: a reference slicing

| # | Slice | Criteria it covers | Size | Depends on |
|---|---|---|---|---|
| L1 | Points ledger table and balance query (no earning yet) | Balance is 0 for a new customer; ledger entries sum to balance | ~120 | none |
| L2 | Earn points when an order is placed | 1 point per whole unit of total_minor | ~100 | L1 |
| L3 | Reverse points on cancellation | Cancelling removes exactly the earned points | ~60 | L2 |
| L4 | Reverse points on returns, proportionally | Uses the same allocation as refunds | ~120 | L2, returns S3 |
| L5 | Spend points as a discount on an order | 100 points = 100 minor units; cannot overspend; interacts with discount codes | ~180 | L2 |
| L6 | Expiry after 12 months | Expired points no longer spendable; scheduled job | ~150 | L1 |
| L7 | **Refuse to start without a conversation:** points liability in the nightly billing data | Needs finance's agreed format; changes an external contract | — | finance decision |

Last slice: L6 or L7, depending on finance. The rule that most often goes wrong: L5's interaction with discount codes (which applies first?). Write it as an open question with an owner.
