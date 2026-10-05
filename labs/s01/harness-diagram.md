# Exercise 1.2: label the harness

Fill in the blanks (A to F), then draw the trust boundary.

```
 You ──request──▶ [ A ] ◀──instructions── [ B: context files ]
                    │  proposes a tool call
                    ▼
               [ C: checks ] ──denied──▶ back to A
                    │ allowed
                    ▼
               [ D: tools ] ── read / search / edit / run ──▶ [ E: your repository and machine ]
                    │ result
                    ▼
               [ F ] ── appended, then back to A until done or a limit is hit
```
