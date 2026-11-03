TITLE: [Warehouse] [Finding] Real-world WR6-09 · Carry a per-client tax treatment so exempt storage is not billed at 18%
LABELS: task,warehouse,gap-real-world,phase-p5,warehouse-3pl
issue: 759
---
Part of #10 · Module **`warehouse-3pl`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #21, #35 · Source: real-world gap check 2026-11-03, lane WR6

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Storing unprocessed agricultural produce is exempt, while the same STORAGE charge for an FMCG client is 18%. Storing seeds for sowing was recommended for exemption in Oct 2026. The charge code carries one tax code, so a cold-store or agri client is invoiced with GST it should not pay, or the operator clones every charge code.

## Scope

Add an optional tax treatment override on a client rate-card line (or a client goods tax class), carried on the AR envelope line in place of the charge code's default. Accounting still computes the tax (FR-294).

## Acceptance

- A client card line with an EXEMPT_AGRI override emits that tax code on the envelope. Another client on the same charge code emits the default.
- The override is effective-dated with the card version.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Entry 54(e) N.12/2017-CT(R): https://taxclue.in/guide/gst-on-warehouse ; 57th GSTC seeds item wr4_57th.txt l.690 (UNVERIFIED). Plan: FR-286 tax code on the charge code. P5-02 overrides are keyed `(charge_code, uom, basis, tier)` with no tax field. grep `exempt|agri` in p5-0*.md returns nothing.

## Depends on

#21
