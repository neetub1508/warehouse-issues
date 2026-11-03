TITLE: [Warehouse] [Finding] Real-world WR4-02 · Support multi-vehicle movement on one e-way bill
LABELS: task,warehouse,gap-real-world,phase-p4,warehouse-india
issue: 739
---
Part of #8 · Module **`warehouse-india`** · Migrations **next free in the module's band, allocated in `DATA-MODEL.md` at build** · Screens **as named in Scope** · Severity **minor** · Finding type **MISSING-TASK** · Related: #82 · Source: real-world gap check 2026-11-03, lane WR4

> **Statutory content.** Sources are cited under Evidence; anything marked UNVERIFIED there, and every figure, must be confirmed against the law in force at build time.

## Why this task exists

A heavy or over-dimensional consignment (machinery, structural steel, coils) is often split at a transhipment point into several smaller vehicles under one EWB. A rail/ship leg finished by several trucks is split the same way. The portal handles this with a multi-vehicle group on the EWB. With only a single "update vehicle", the transporter cannot record it, and every truck except one runs without a matching vehicle number. Each of those trucks can be stopped and detained.

## Scope

A multi-vehicle group on an EWB has a from-place, a reason and a total quantity. Vehicles are added each with a quantity, and the sum must not exceed the total. Each add/change is a persisted row filed through the provider, with the same idempotency and reconcile pattern as P4-12. The vehicle-update screen gains a "Split across vehicles" action.

## Acceptance

- One EWB of 30 t gets three vehicles of 10 t; a fourth of 1 t is refused
- Each vehicle row has a provider acknowledgement or a reconcile state
- The gate-pass and handover prints list every vehicle of the group

## Evidence (classic HEAD 4843b1648d, 2026-11-03)

Practitioner description https://blog.saginfotech.com/gst-e-way-bill-1-km-distance ; the portal FAQ (docs.ewaybillgst.gov.in) refused the fetch (403), so the exact API is **UNVERIFIED**. Grep `multi.?vehicle|EWB-01|multiple vehicle` = 0 in warehouse-issues and in `warehouse-india/backend`.

## Depends on

#82
