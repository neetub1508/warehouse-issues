TITLE: [Warehouse] [Finding] Real-world WR1-06 · Let a transit loss claim name the carrier or insurer, not only the supplier
LABELS: task,warehouse,gap-real-world,phase-p5
issue: 726
---
Part of #10 · Module **`warehouse`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **major** · Finding type **MISSING-TASK** · Related: #123, #565, #28 · Source: real-world gap check 2026-11-03, lane WR1

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

Under ex-works or FCA terms, or when the buyer arranges freight, damage or shortage in transit is not the supplier's fault. The claim lies with the transporter or the transit insurer, on the basis of the LR remark and a damage or shortage certificate. Claims against carriers are also time-barred if notice is late. The one claim register is supplier-only, so these losses go untracked or are wrongly chased against the vendor.

## Scope

Claim `counterparty_kind` = `SUPPLIER` / `CARRIER` / `INSURER`, with a default from the PO Incoterm / freight terms (buyer-arranged → CARRIER). Evidence: LR number, LR remark, damage / shortage certificate attachment, surveyor reference. A notice-due date per kind, configurable. Ageing by counterparty kind.

## Acceptance

- A damage GRN line on an EXW PO proposes a CARRIER claim against the transporter on the gate entry.
- An insurer claim records the policy and surveyor number and ages separately.
- An FOR-destination PO still defaults to SUPPLIER.

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

#123 (p5-23.md): "a claim against a supplier", header `supplier`; claim types short / damage / quality / price. Grep of `transporter claim|carrier claim|insurance claim` in issues/FRD/contracts finds no task. Carriage by Road Act 2007 notice period: UNVERIFIED (not searched within budget).

## Global setting

`WAREHOUSE_CLAIM_CARRIER_NOTICE_DAYS` default=UNVERIFIED-set-from-legal-review alternatives=install value

The default is the recommendation; the alternatives are selectable per install through the settings page.

## Depends on

#123
