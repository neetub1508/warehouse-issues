TITLE: [Warehouse] [Finding] Real-world WR7-06 · Trace ITC reversal for produced and WIP lots to the inputs consumed
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 767
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **PLANNED-WRONG** · Related: #32, #27, #601, #605 · Source: real-world gap check 2026-11-03, lane WR7

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

When finished goods made in-house are destroyed, stolen or written off, the credit to reverse is the tax on the raw materials and packing inside them. No "receipt that brought the lot in" exists for a produced lot. #32's chain therefore finds nothing for a factory's own output, or returns uncomputable, and the manufacturer under-reverses credit on its largest loss category.

## Scope

For a lot whose origin is a production receipt (or a job-work receipt), walk the production receipt's consumption lines (backflush or issue) to their cost layers and source receipts, recursively for semi-finished goods, and pro-rate the input tax by the quantity lost. Keep the job-worker's processing charge credit separate. A chain that cannot be resolved is named, never zero.

## Acceptance

- A destroyed FG lot made from 2 RM lots computes reversal from both RM receipts' input tax, pro-rata
- A two-level (SFG → FG) loss walks both levels
- A lot with an unresolvable chain reports `ITC_CHAIN_UNRESOLVED` with the break point

## Evidence (classic HEAD 4843b1648d, 2026-11-03)


- s.17(5)(h) blocks credit on goods lost, stolen, destroyed, written off, gifted or given as free samples. r.56(12) requires a monthly production account of raw materials consumed per goods manufactured [R56].
- The practice of reversing credit on the inputs embedded in lost finished goods is **UNVERIFIED by URL** this session: it is standard CA practice, but no fetched source states it.
- Plan: #32 resolves only "the receipt that brought that lot in". grep `manufactur|produc|bom|wip|finished` in p4-04.md = 0.

## Depends on

#32, #601
